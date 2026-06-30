#!/usr/bin/env python3
"""Apply approved review queue items."""

from __future__ import annotations

import argparse
from pathlib import Path

from csv_utils import append_review_issues, data_dir, now_iso, read_csv_rows, stable_id, write_csv_rows
from merge_metrics import derive_quarters, load_metric_rules, validate_fact_boundary


REVIEW_FIELDS = [
    "issue_id",
    "target_table",
    "natural_key",
    "existing_row_id",
    "candidate_row_id",
    "source_id",
    "reason",
    "severity",
    "suggested_action",
    "status",
    "resolved_by",
    "resolved_at",
    "resolution_notes",
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

OBS_FIELDS = [
    "observation_id",
    "ingestion_run_id",
    "source_id",
    "source_period",
    "data_period",
    "period_scope",
    "value_kind",
    "as_of_date",
    "target_period",
    "segment",
    "metric",
    "raw_value",
    "raw_unit",
    "value",
    "unit",
    "yoy",
    "qoq",
    "calculation_method",
    "source_location",
    "confidence",
    "review_status",
    "notes",
]

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


def fact_key(row: dict[str, str]) -> str:
    return "|".join([row.get("data_period", ""), row.get("period_scope", ""), row.get("value_kind", ""), row.get("as_of_date", ""), row.get("segment", ""), row.get("metric", ""), row.get("unit", "")])


def approve_row(rows: list[dict[str, str]], id_field: str, candidate_id: str, existing_id: str = "") -> bool:
    if existing_id:
        for row in rows:
            if row.get(id_field) == existing_id:
                row["review_status"] = "rejected"
    for row in rows:
        if row.get(id_field) == candidate_id:
            row["review_status"] = "user_approved"
            return True
    return False


def approve_metric(skill_root: Path, candidate_id: str) -> bool:
    observations_path = data_dir(skill_root) / "metric_observations.csv"
    facts_path = data_dir(skill_root) / "long_metrics.csv"
    observations = read_csv_rows(observations_path, OBS_FIELDS)
    facts = read_csv_rows(facts_path, FACT_FIELDS)
    observation = next((row for row in observations if row.get("observation_id") == candidate_id), None)
    if observation is None:
        return False
    boundary_error = validate_fact_boundary(observation, load_metric_rules(skill_root))
    if boundary_error:
        return False
    observation["review_status"] = "user_approved"
    fact = {
        "data_period": observation.get("data_period", ""),
        "period_scope": observation.get("period_scope", ""),
        "value_kind": observation.get("value_kind", ""),
        "as_of_date": observation.get("as_of_date", ""),
        "target_period": observation.get("target_period", ""),
        "segment": observation.get("segment", ""),
        "metric": observation.get("metric", ""),
        "value": observation.get("value", ""),
        "unit": observation.get("unit", ""),
        "yoy": observation.get("yoy", ""),
        "qoq": observation.get("qoq", ""),
        "calculation_method": observation.get("calculation_method", "reported"),
        "is_derived": "false",
        "derived_from_keys": "",
        "primary_observation_id": candidate_id,
        "confidence": observation.get("confidence", ""),
        "review_status": "user_approved",
        "notes": observation.get("notes", ""),
    }
    fact["fact_id"] = stable_id("fact", [fact_key(fact)])
    key = fact_key(fact)
    replaced = False
    for index, existing in enumerate(facts):
        if fact_key(existing) == key:
            old_observation_id = existing.get("primary_observation_id", "")
            for old_observation in observations:
                if old_observation.get("observation_id") == old_observation_id and old_observation_id != candidate_id:
                    old_observation["review_status"] = "rejected"
            facts[index] = fact
            replaced = True
            break
    if not replaced:
        facts.append(fact)
    write_csv_rows(observations_path, OBS_FIELDS, observations)
    write_csv_rows(facts_path, FACT_FIELDS, facts)
    _, issues, _ = derive_quarters(skill_root, facts)
    append_review_issues(skill_root, issues)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-root", required=True)
    args = parser.parse_args()
    skill_root = Path(args.skill_root)
    queue_path = data_dir(skill_root) / "review_queue.csv"
    queue = read_csv_rows(queue_path, REVIEW_FIELDS)

    forecasts_path = data_dir(skill_root) / "forecasts.csv"
    forecasts = read_csv_rows(forecasts_path, FORECAST_FIELDS)
    valuation_path = data_dir(skill_root) / "valuation_history.csv"
    valuations = read_csv_rows(valuation_path, VALUATION_FIELDS)

    resolved = 0
    for issue in queue:
        if issue.get("status") != "user_approved":
            continue
        candidate_id = issue.get("candidate_row_id", "")
        target = issue.get("target_table", "")
        success = False
        if target == "forecasts":
            success = approve_row(forecasts, "forecast_id", candidate_id, issue.get("existing_row_id", ""))
        elif target == "valuation_history":
            success = approve_row(valuations, "valuation_id", candidate_id, issue.get("existing_row_id", ""))
        elif target == "long_metrics":
            success = approve_metric(skill_root, candidate_id)
        if success:
            issue["status"] = "resolved"
            issue["resolved_by"] = issue.get("resolved_by") or "user"
            issue["resolved_at"] = now_iso()
            issue["resolution_notes"] = issue.get("resolution_notes") or "approved candidate applied"
            resolved += 1
        else:
            issue["resolution_notes"] = "candidate row not found; left unresolved"

    write_csv_rows(forecasts_path, FORECAST_FIELDS, forecasts)
    write_csv_rows(valuation_path, VALUATION_FIELDS, valuations)
    write_csv_rows(queue_path, REVIEW_FIELDS, queue)
    print(f"Resolved {resolved} review items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
