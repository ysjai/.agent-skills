#!/usr/bin/env python3
"""Merge extracted Xiaomi valuation history."""

from __future__ import annotations

import argparse
from pathlib import Path

from csv_utils import (
    append_ingestion_run,
    append_review_issues,
    append_unique_rows,
    data_dir,
    now_iso,
    read_csv_rows,
    register_sources,
    stable_id,
)


EXTRACTED_FIELDS = [
    "source_id",
    "source_period",
    "source_type",
    "source_name",
    "source_file",
    "source_url",
    "publication_date",
    "source_location",
    "date",
    "metric",
    "value",
    "confidence",
    "review_status",
    "notes",
]

VALUATION_FIELDS = [
    "valuation_id",
    "date",
    "metric",
    "value",
    "source_type",
    "source_name",
    "source_url",
    "confidence",
    "review_status",
    "notes",
]


def valuation_key(row: dict[str, str]) -> str:
    return str(row.get("valuation_id", ""))


def natural_key(row: dict[str, str]) -> str:
    return "|".join([row.get("date", ""), row.get("metric", ""), row.get("source_name", "")])


def make_review_issue(row: dict[str, str], existing_id: str, reason: str) -> dict[str, str]:
    return {
        "target_table": "valuation_history",
        "natural_key": natural_key(row),
        "existing_row_id": existing_id,
        "candidate_row_id": row.get("valuation_id", ""),
        "source_id": "",
        "reason": reason,
        "severity": "medium",
        "suggested_action": "manual_check",
        "status": "open",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-root", required=True)
    parser.add_argument("--period", required=True)
    args = parser.parse_args()

    skill_root = Path(args.skill_root)
    period = args.period
    extracted_path = skill_root / "workspace" / "periods" / period / "extracted" / "extracted_valuation.csv"
    if not extracted_path.exists():
        print(f"No extracted valuation found for {period}")
        return 0

    started = now_iso()
    rows = read_csv_rows(extracted_path, EXTRACTED_FIELDS)
    register_sources(skill_root, rows, period, started)
    existing = read_csv_rows(data_dir(skill_root) / "valuation_history.csv", VALUATION_FIELDS)
    existing_by_natural = {natural_key(row): row for row in existing}
    valuations: list[dict[str, str]] = []
    issues: list[dict[str, str]] = []

    for row in rows:
        valuation = {
            "valuation_id": stable_id("val", [row.get("date"), row.get("metric"), row.get("source_name"), row.get("value")]),
            "date": row.get("date", ""),
            "metric": row.get("metric", ""),
            "value": row.get("value", ""),
            "source_type": row.get("source_type", ""),
            "source_name": row.get("source_name", ""),
            "source_url": row.get("source_url", ""),
            "confidence": row.get("confidence", ""),
            "review_status": row.get("review_status") or "needs_user_review",
            "notes": row.get("notes", ""),
        }
        current = existing_by_natural.get(natural_key(valuation))
        if current and current.get("value") != valuation.get("value"):
            valuation["review_status"] = "needs_user_review"
            issues.append(make_review_issue(valuation, current.get("valuation_id", ""), "conflicting_valuation_value"))
        elif valuation["review_status"] in {"open", "needs_user_review", ""}:
            issues.append(make_review_issue(valuation, "", "valuation_requires_review"))
        valuations.append(valuation)
        existing_by_natural.setdefault(natural_key(valuation), valuation)

    created = append_unique_rows(data_dir(skill_root) / "valuation_history.csv", VALUATION_FIELDS, valuations, valuation_key)
    review_count = append_review_issues(skill_root, issues)
    append_ingestion_run(
        skill_root,
        {
            "ingestion_run_id": stable_id("run", [period, "valuation", started]),
            "source_period": period,
            "started_at": started,
            "finished_at": now_iso(),
            "input_count": str(len(rows)),
            "created_observations": "0",
            "created_facts": "0",
            "created_forecasts": "0",
            "review_items": str(review_count),
            "status": "completed",
            "notes": f"valuation merge created {created} rows",
        },
    )
    print(f"Merged {created} valuation rows, {review_count} review items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
