#!/usr/bin/env python3
"""Build recent FY/H1 wide views for Xiaomi metrics."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

from csv_utils import data_dir, read_csv_rows, write_csv_rows


FACT_FIELDS = [
    "fact_id",
    "data_period",
    "period_scope",
    "value_kind",
    "as_of_date",
    "target_period",
    "segment",
    "metric",
    "value",
    "unit",
    "yoy",
    "qoq",
    "calculation_method",
    "is_derived",
    "derived_from_keys",
    "primary_observation_id",
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

PERIOD_RE = re.compile(r"^(\d{4})(FY|H1)$")
SEGMENT_ORDER = [
    "Group",
    "Smartphone",
    "AIoT",
    "Smart EV, AI and Other New Initiatives",
    "Internet Services",
    "Valuation",
]


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-root", required=True)
    args = parser.parse_args()
    skill_root = Path(args.skill_root)

    facts = read_csv_rows(data_dir(skill_root) / "long_metrics.csv", FACT_FIELDS)
    periods = sorted({row["data_period"] for row in facts if PERIOD_RE.match(row.get("data_period", ""))})
    years = []
    for period in periods:
        match = PERIOD_RE.match(period)
        if match:
            years.append(int(match.group(1)))
    latest_years = sorted(set(years), reverse=True)[:5]
    allowed = []
    for period in periods:
        match = PERIOD_RE.match(period)
        if match and int(match.group(1)) in latest_years:
            allowed.append(period)

    pivot: dict[tuple[str, str, str], dict[str, str]] = defaultdict(dict)
    for row in facts:
        period = row.get("data_period", "")
        if period not in allowed:
            continue
        key = (row.get("segment", ""), row.get("metric", ""), row.get("unit", ""))
        pivot[key][period] = row.get("value", "")

    ordered_periods = sorted(allowed, key=lambda value: (value[:4], 0 if value.endswith("H1") else 1))
    out_fields = ["segment", "metric", "unit"] + ordered_periods + ["latest"]
    out_rows = []
    segment_rank = {segment: index for index, segment in enumerate(SEGMENT_ORDER)}
    for (segment, metric, unit), values in sorted(pivot.items(), key=lambda item: (segment_rank.get(item[0][0], 999), item[0][1])):
        out_rows.append({"segment": segment, "metric": metric, "unit": unit, **{period: values.get(period, "") for period in ordered_periods}, "latest": ""})

    valuation = read_csv_rows(data_dir(skill_root) / "valuation_snapshot.csv", SNAPSHOT_FIELDS)
    for row in valuation:
        metric_name = f"{row['metric']}_{row['window_years']}y_percentile"
        out_rows.append({"segment": "Valuation", "metric": metric_name, "unit": "%", **{period: "" for period in ordered_periods}, "latest": row.get("percentile") or row.get("status", "")})

    views_dir = skill_root / "workspace" / "views"
    views_dir.mkdir(parents=True, exist_ok=True)
    write_csv_rows(views_dir / "recent_5y_fy_h1_wide.csv", out_fields, out_rows)

    md_rows = [[row.get(field, "") for field in out_fields] for row in out_rows]
    md = ["# Recent 5Y FY/H1 Wide Table", "", markdown_table(out_fields, md_rows) if md_rows else "暂无 FY/H1 数据。"]
    md.append("\n## Valuation Snapshot\n")
    if valuation:
        md.append(markdown_table(["metric", "window_years", "percentile", "status"], [[row["metric"], row["window_years"], row["percentile"], row["status"]] for row in valuation]))
    else:
        md.append("估值历史样本不足。")
    (views_dir / "recent_5y_fy_h1_wide.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Wrote {len(out_rows)} wide table rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
