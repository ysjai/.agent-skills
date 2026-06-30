#!/usr/bin/env python3
"""Merge extracted Xiaomi forecasts and official guidance."""

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
    "source_name",
    "source_type",
    "source_file",
    "source_url",
    "publication_date",
    "source_location",
    "forecast_period",
    "metric",
    "segment",
    "value",
    "unit",
    "scenario",
    "assumptions",
    "confidence",
    "review_status",
    "notes",
]

FORECAST_FIELDS = [
    "forecast_id",
    "source_id",
    "source_period",
    "forecast_period",
    "source_name",
    "source_type",
    "publication_date",
    "captured_at",
    "version",
    "metric",
    "segment",
    "value",
    "unit",
    "scenario",
    "assumptions",
    "confidence",
    "review_status",
    "source_location",
    "notes",
]


def forecast_key(row: dict[str, str]) -> str:
    return str(row.get("forecast_id", ""))


def make_review_issue(row: dict[str, str]) -> dict[str, str]:
    natural_key = "|".join(
        [
            row.get("source_id", ""),
            row.get("forecast_period", ""),
            row.get("segment", ""),
            row.get("metric", ""),
            row.get("scenario", ""),
            row.get("unit", ""),
        ]
    )
    return {
        "target_table": "forecasts",
        "natural_key": natural_key,
        "existing_row_id": "",
        "candidate_row_id": row.get("forecast_id", ""),
        "source_id": row.get("source_id", ""),
        "reason": "forecast_requires_review",
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
    extracted_path = skill_root / "workspace" / "periods" / period / "extracted" / "extracted_forecasts.csv"
    if not extracted_path.exists():
        print(f"No extracted forecasts found for {period}")
        return 0

    started = now_iso()
    rows = read_csv_rows(extracted_path, EXTRACTED_FIELDS)
    register_sources(skill_root, rows, period, started)
    forecasts: list[dict[str, str]] = []
    issues: list[dict[str, str]] = []

    for row in rows:
        source_id = row.get("source_id") or stable_id("src", [row.get("source_url"), row.get("source_file"), row.get("source_name")])
        forecast_id = stable_id(
            "fcst",
            [
                source_id,
                row.get("forecast_period"),
                row.get("metric"),
                row.get("segment"),
                row.get("value"),
                row.get("unit"),
                row.get("scenario"),
                row.get("assumptions"),
                row.get("publication_date"),
            ],
        )
        forecast = {
            "forecast_id": forecast_id,
            "source_id": source_id,
            "source_period": row.get("source_period") or period,
            "forecast_period": row.get("forecast_period", ""),
            "source_name": row.get("source_name", ""),
            "source_type": row.get("source_type", ""),
            "publication_date": row.get("publication_date", ""),
            "captured_at": started,
            "version": row.get("version") or "1",
            "metric": row.get("metric", ""),
            "segment": row.get("segment", ""),
            "value": row.get("value", ""),
            "unit": row.get("unit", ""),
            "scenario": row.get("scenario", ""),
            "assumptions": row.get("assumptions", ""),
            "confidence": row.get("confidence", ""),
            "review_status": row.get("review_status") or "needs_user_review",
            "source_location": row.get("source_location", ""),
            "notes": row.get("notes", ""),
        }
        forecasts.append(forecast)
        if forecast["review_status"] in {"open", "needs_user_review", ""}:
            issues.append(make_review_issue(forecast))

    created = append_unique_rows(data_dir(skill_root) / "forecasts.csv", FORECAST_FIELDS, forecasts, forecast_key)
    review_count = append_review_issues(skill_root, issues)
    append_ingestion_run(
        skill_root,
        {
            "ingestion_run_id": stable_id("run", [period, "forecasts", started]),
            "source_period": period,
            "started_at": started,
            "finished_at": now_iso(),
            "input_count": str(len(rows)),
            "created_observations": "0",
            "created_facts": "0",
            "created_forecasts": str(created),
            "review_items": str(review_count),
            "status": "completed",
            "notes": "forecast merge",
        },
    )
    print(f"Merged {created} forecasts, {review_count} review items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
