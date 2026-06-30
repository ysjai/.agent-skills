#!/usr/bin/env python3
"""Calculate Xiaomi valuation percentile snapshots."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date
from pathlib import Path

from csv_utils import (
    append_review_issues,
    confidence_priority,
    data_dir,
    excluded_status,
    parse_number,
    read_csv_rows,
    source_priority,
    stable_id,
    write_csv_rows,
)


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

SNAPSHOT_FIELDS = [
    "metric",
    "current_date",
    "current_value",
    "window_years",
    "sample_start",
    "sample_end",
    "sample_count",
    "valid_sample_count",
    "percentile",
    "status",
    "notes",
]

TARGET_METRICS = ["TTM PE", "Adjusted TTM PE", "PB"]
ALIASES = {"ttm_pe": "TTM PE", "adjusted_ttm_pe": "Adjusted TTM PE", "pb": "PB"}
STATUS_PRIORITY = {"user_approved": 4, "llm_reviewed": 3, "auto_accepted": 2, "resolved": 2, "": 1}


def parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def years_before(current: date, years: int) -> date:
    try:
        return current.replace(year=current.year - years)
    except ValueError:
        return current.replace(year=current.year - years, day=28)


def canonical_samples(rows: list[dict[str, str]], skill_root: Path) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    issues: list[dict[str, str]] = []
    for row in rows:
        if excluded_status(row.get("review_status", "")):
            continue
        parsed = parse_date(row.get("date", ""))
        value = parse_number(row.get("value"))
        metric = ALIASES.get(row.get("metric", ""), row.get("metric", ""))
        if parsed is None or value is None:
            continue
        if "pe" in metric.lower() and value <= 0:
            continue
        row = dict(row)
        row["metric"] = metric
        grouped[(row.get("date", ""), metric)].append(row)

    canonical: list[dict[str, str]] = []
    for key, candidates in grouped.items():
        ranked = sorted(
            candidates,
            key=lambda row: (
                STATUS_PRIORITY.get(row.get("review_status", ""), 0),
                source_priority(row.get("source_type", "")),
                confidence_priority(row.get("confidence", "")),
            ),
            reverse=True,
        )
        best = ranked[0]
        best_rank = (
            STATUS_PRIORITY.get(best.get("review_status", ""), 0),
            source_priority(best.get("source_type", "")),
            confidence_priority(best.get("confidence", "")),
        )
        tied = [
            row
            for row in ranked
            if (
                STATUS_PRIORITY.get(row.get("review_status", ""), 0),
                source_priority(row.get("source_type", "")),
                confidence_priority(row.get("confidence", "")),
            )
            == best_rank
        ]
        values = {row.get("value", "") for row in tied}
        if len(values) > 1:
            issues.append(
                {
                    "target_table": "valuation_history",
                    "natural_key": "|".join(key),
                    "existing_row_id": tied[0].get("valuation_id", ""),
                    "candidate_row_id": tied[1].get("valuation_id", ""),
                    "source_id": "",
                    "reason": "same_day_valuation_conflict",
                    "severity": "medium",
                    "suggested_action": "manual_check",
                    "status": "open",
                }
            )
            continue
        canonical.append(best)
    append_review_issues(skill_root, issues)
    return canonical


def percentile(values: list[float], current: float) -> float:
    return round(sum(1 for value in values if value <= current) / len(values) * 100, 2)


def build_markdown(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "# Valuation Snapshot\n\n历史估值序列不足，无法计算 PE/PB 历史百分位。\n"
    lines = ["# Valuation Snapshot", "", "| metric | current_date | current_value | window_years | percentile | status | notes |", "|---|---:|---:|---:|---:|---|---|"]
    for row in rows:
        lines.append(
            f"| {row['metric']} | {row['current_date']} | {row['current_value']} | {row['window_years']} | {row['percentile']} | {row['status']} | {row['notes']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-root", required=True)
    args = parser.parse_args()
    skill_root = Path(args.skill_root)

    history = read_csv_rows(data_dir(skill_root) / "valuation_history.csv", VALUATION_FIELDS)
    samples = canonical_samples(history, skill_root)
    by_metric: dict[str, list[tuple[date, float, dict[str, str]]]] = defaultdict(list)
    for row in samples:
        parsed_date = parse_date(row.get("date", ""))
        parsed_value = parse_number(row.get("value"))
        if parsed_date is None or parsed_value is None:
            continue
        by_metric[row.get("metric", "")].append((parsed_date, parsed_value, row))

    snapshot: list[dict[str, str]] = []
    for metric in TARGET_METRICS:
        values = sorted(by_metric.get(metric, []), key=lambda item: item[0])
        if not values:
            for years in (5, 10):
                snapshot.append(
                    {
                        "metric": metric,
                        "current_date": "",
                        "current_value": "",
                        "window_years": str(years),
                        "sample_start": "",
                        "sample_end": "",
                        "sample_count": "0",
                        "valid_sample_count": "0",
                        "percentile": "",
                        "status": "insufficient_history",
                        "notes": "no valid samples",
                    }
                )
            continue
        current_date, current_value, _ = values[-1]
        for years in (5, 10):
            start = years_before(current_date, years)
            window = [(item_date, item_value) for item_date, item_value, _ in values if start <= item_date <= current_date]
            if not window:
                snapshot.append(
                    {
                        "metric": metric,
                        "current_date": current_date.isoformat(),
                        "current_value": str(current_value),
                        "window_years": str(years),
                        "sample_start": "",
                        "sample_end": current_date.isoformat(),
                        "sample_count": "0",
                        "valid_sample_count": "0",
                        "percentile": "",
                        "status": "insufficient_history",
                        "notes": "no valid samples",
                    }
                )
                continue
            sample_values = [item_value for _, item_value in window]
            actual_start = window[0][0]
            status = "ok" if actual_start <= start else "available_history_only"
            snapshot.append(
                {
                    "metric": metric,
                    "current_date": current_date.isoformat(),
                    "current_value": str(current_value),
                    "window_years": str(years),
                    "sample_start": actual_start.isoformat(),
                    "sample_end": current_date.isoformat(),
                    "sample_count": str(len(window)),
                    "valid_sample_count": str(len(sample_values)),
                    "percentile": str(percentile(sample_values, current_value)),
                    "status": status,
                    "notes": "partial history" if status == "available_history_only" else "",
                }
            )

    write_csv_rows(data_dir(skill_root) / "valuation_snapshot.csv", SNAPSHOT_FIELDS, snapshot)
    views_dir = skill_root / "workspace" / "views"
    views_dir.mkdir(parents=True, exist_ok=True)
    (views_dir / "valuation_snapshot.md").write_text(build_markdown(snapshot), encoding="utf-8")
    print(f"Wrote {len(snapshot)} valuation snapshot rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
