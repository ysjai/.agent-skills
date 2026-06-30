#!/usr/bin/env python3
"""Merge extracted Xiaomi metrics into observations and canonical facts."""

from __future__ import annotations

import argparse
from pathlib import Path

from csv_utils import (
    append_ingestion_run,
    append_review_issues,
    append_unique_rows,
    accepted_status,
    confidence_priority,
    data_dir,
    format_number,
    now_iso,
    parse_number,
    read_csv_rows,
    register_sources,
    source_priority,
    stable_id,
    write_csv_rows,
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

DEFAULT_DERIVABLE = {
    "total_revenue",
    "net_profit",
    "adjusted_net_profit",
    "r_and_d_expenses",
    "operating_cash_flow",
    "free_cash_flow",
    "sales_and_marketing_expenses",
    "smartphone_revenue",
    "smartphone_shipments",
    "aiot_revenue",
    "air_conditioner_shipments",
    "refrigerator_shipments",
    "washing_machine_shipments",
    "internet_services_revenue",
    "advertising_revenue",
    "gaming_revenue",
    "value_added_services_revenue",
    "smart_ev_revenue",
    "smart_ev_operating_profit",
    "smart_ev_adjusted_profit",
    "smart_ev_deliveries",
    "smart_ev_r_and_d_expenses",
}


def fact_key(row: dict[str, str]) -> str:
    return "|".join(
        [
            row.get("data_period", ""),
            row.get("period_scope", ""),
            row.get("value_kind", ""),
            row.get("as_of_date", ""),
            row.get("segment", ""),
            row.get("metric", ""),
            row.get("unit", ""),
        ]
    )


def observation_key(row: dict[str, str]) -> str:
    return "|".join(
        [
            row.get("source_id", ""),
            row.get("source_location", ""),
            row.get("data_period", ""),
            row.get("period_scope", ""),
            row.get("value_kind", ""),
            row.get("as_of_date", ""),
            row.get("segment", ""),
            row.get("metric", ""),
            row.get("raw_value", ""),
            row.get("raw_unit", ""),
        ]
    )


def load_metric_rules(skill_root: Path) -> dict[tuple[str, str], dict[str, str]]:
    dictionary = skill_root / "references" / "metric-dictionary.md"
    if not dictionary.exists():
        return {}
    rules: dict[tuple[str, str], dict[str, str]] = {}
    for line in dictionary.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line or "metric" in line.split("|")[2:3]:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) >= 5:
            rules[(cells[0], cells[1])] = {
                "unit": cells[2],
                "value_kind": cells[3],
                "can_derive_quarter": cells[4].lower(),
            }
    return rules


def load_derivable_metrics(skill_root: Path) -> set[str]:
    rules = load_metric_rules(skill_root)
    derivable = {metric for (_, metric), rule in rules.items() if rule.get("can_derive_quarter") == "yes"}
    return derivable or DEFAULT_DERIVABLE


def validate_fact_boundary(observation: dict[str, str], rules: dict[tuple[str, str], dict[str, str]]) -> str:
    if observation.get("segment") == "Valuation":
        return "valuation_metric_in_fact_extract"
    if observation.get("value_kind") not in {"actual_flow", "actual_stock"}:
        return "non_actual_value_kind_in_fact_extract"
    rule = rules.get((observation.get("segment", ""), observation.get("metric", "")))
    if not rule:
        return ""
    if rule.get("value_kind") == "forecast":
        return "forecast_metric_in_fact_extract"
    if rule.get("value_kind") and observation.get("value_kind") != rule.get("value_kind"):
        return "value_kind_mismatch"
    if rule.get("unit") and observation.get("unit") != rule.get("unit"):
        return "unit_mismatch"
    return ""


def source_maps(skill_root: Path, observations: list[dict[str, str]]) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    obs_by_id = {row["observation_id"]: row for row in observations}
    sources = read_csv_rows(data_dir(skill_root) / "source_registry.csv", [
        "source_id",
        "source_period",
        "source_type",
        "source_name",
        "source_file",
        "source_url",
        "publication_date",
        "content_hash",
        "first_seen_at",
        "last_processed_at",
        "confidence",
        "review_status",
        "notes",
    ])
    return obs_by_id, {row["source_id"]: row for row in sources}


def observation_priority(observation: dict[str, str], sources_by_id: dict[str, dict[str, str]]) -> tuple[int, int]:
    source = sources_by_id.get(observation.get("source_id", ""), {})
    return source_priority(source.get("source_type", "")), confidence_priority(observation.get("confidence", ""))


def make_review_issue(
    target_table: str,
    natural_key: str,
    existing_row_id: str,
    candidate_row_id: str,
    source_id: str,
    reason: str,
    suggested_action: str = "manual_check",
    status: str = "open",
) -> dict[str, str]:
    return {
        "target_table": target_table,
        "natural_key": natural_key,
        "existing_row_id": existing_row_id,
        "candidate_row_id": candidate_row_id,
        "source_id": source_id,
        "reason": reason,
        "severity": "medium",
        "suggested_action": suggested_action,
        "status": status,
    }


def fact_from_observation(observation: dict[str, str], value: str | None = None) -> dict[str, str]:
    base = {
        "data_period": observation.get("data_period", ""),
        "period_scope": observation.get("period_scope", ""),
        "value_kind": observation.get("value_kind", ""),
        "as_of_date": observation.get("as_of_date", ""),
        "target_period": observation.get("target_period", ""),
        "segment": observation.get("segment", ""),
        "metric": observation.get("metric", ""),
        "value": value if value is not None else observation.get("value", ""),
        "unit": observation.get("unit", ""),
        "yoy": observation.get("yoy", ""),
        "qoq": observation.get("qoq", ""),
        "calculation_method": observation.get("calculation_method", "reported"),
        "is_derived": "false",
        "derived_from_keys": "",
        "primary_observation_id": observation.get("observation_id", ""),
        "confidence": observation.get("confidence", ""),
        "review_status": observation.get("review_status", ""),
        "notes": observation.get("notes", ""),
    }
    base["fact_id"] = stable_id("fact", [fact_key(base)])
    return base


def merge_observations_into_facts(skill_root: Path, observations: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]], int]:
    facts_path = data_dir(skill_root) / "long_metrics.csv"
    facts = read_csv_rows(facts_path, FACT_FIELDS)
    facts_by_key = {fact_key(row): row for row in facts}
    obs_by_id, sources_by_id = source_maps(skill_root, observations)
    metric_rules = load_metric_rules(skill_root)
    issues: list[dict[str, str]] = []
    created = 0

    for observation in observations:
        boundary_error = validate_fact_boundary(observation, metric_rules)
        if boundary_error:
            issues.append(
                make_review_issue(
                    "long_metrics",
                    observation_key(observation),
                    "",
                    observation.get("observation_id", ""),
                    observation.get("source_id", ""),
                    boundary_error,
                )
            )
            continue
        if observation.get("review_status", "") == "rejected":
            continue
        if not accepted_status(observation.get("review_status", "")):
            issues.append(
                make_review_issue(
                    "long_metrics",
                    observation_key(observation),
                    "",
                    observation.get("observation_id", ""),
                    observation.get("source_id", ""),
                    "metric_requires_review",
                )
            )
            continue
        key = "|".join(
            [
                observation.get("data_period", ""),
                observation.get("period_scope", ""),
                observation.get("value_kind", ""),
                observation.get("as_of_date", ""),
                observation.get("segment", ""),
                observation.get("metric", ""),
                observation.get("unit", ""),
            ]
        )
        existing = facts_by_key.get(key)
        candidate = fact_from_observation(observation)
        if existing is None:
            facts.append(candidate)
            facts_by_key[key] = candidate
            created += 1
            continue
        if existing.get("value") == candidate.get("value"):
            continue

        if existing.get("review_status") == "user_approved" and observation.get("review_status") != "user_approved":
            issues.append(
                make_review_issue(
                    "long_metrics",
                    key,
                    existing.get("fact_id", ""),
                    observation.get("observation_id", ""),
                    observation.get("source_id", ""),
                    "candidate_conflicts_with_user_approved_fact",
                )
            )
            continue

        if observation.get("review_status") == "user_approved" and existing.get("review_status") != "user_approved":
            existing.update(candidate)
            continue

        existing_obs = obs_by_id.get(existing.get("primary_observation_id", ""), {})
        existing_priority = observation_priority(existing_obs, sources_by_id)
        candidate_priority = observation_priority(observation, sources_by_id)
        if candidate_priority > existing_priority and existing_priority[0] < 100:
            existing.update(candidate)
            issues.append(
                make_review_issue(
                    "long_metrics",
                    key,
                    existing.get("fact_id", ""),
                    observation.get("observation_id", ""),
                    observation.get("source_id", ""),
                    "replaced_lower_priority_source",
                    "accept_candidate",
                    "resolved",
                )
            )
        else:
            issues.append(
                make_review_issue(
                    "long_metrics",
                    key,
                    existing.get("fact_id", ""),
                    observation.get("observation_id", ""),
                    observation.get("source_id", ""),
                    "conflicting_fact_value",
                )
            )

    write_csv_rows(facts_path, FACT_FIELDS, facts)
    return facts, issues, created


def derive_quarters(skill_root: Path, facts: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]], int]:
    derivable = load_derivable_metrics(skill_root)
    facts_by_key = {fact_key(row): row for row in facts}
    issues: list[dict[str, str]] = []
    created = 0

    def get_fact(period: str, scope: str, base: dict[str, str]) -> dict[str, str] | None:
        key = "|".join(
            [
                period,
                scope,
                base.get("value_kind", ""),
                "",
                base.get("segment", ""),
                base.get("metric", ""),
                base.get("unit", ""),
            ]
        )
        return facts_by_key.get(key)

    formulas = [
        ("H1", "Q1", "Q2", "cumulative", "quarter"),
        ("YTD_Q3", "H1", "Q3", "cumulative", "cumulative"),
        ("FY", "YTD_Q3", "Q4", "cumulative", "cumulative"),
    ]
    years = sorted({row.get("data_period", "")[:4] for row in facts if row.get("data_period", "")[:4].isdigit()})
    for year in years:
        for left_suffix, right_suffix, output_suffix, left_scope, right_scope in formulas:
            left_period = f"{year}{left_suffix}"
            right_period = f"{year}{right_suffix}"
            output_period = f"{year}{output_suffix}"
            left_candidates = [row for row in facts if row.get("data_period") == left_period and row.get("period_scope") == left_scope]
            for left in left_candidates:
                if left.get("metric") not in derivable or left.get("value_kind") != "actual_flow":
                    continue
                right = get_fact(right_period, right_scope, left)
                if right is None:
                    issues.append(
                        make_review_issue(
                            "long_metrics",
                            f"{output_period}|{left.get('segment')}|{left.get('metric')}|{left.get('unit')}",
                            left.get("fact_id", ""),
                            "",
                            "",
                            "missing_parent_for_quarter_derivation",
                        )
                    )
                    continue
                left_value = parse_number(left.get("value"))
                right_value = parse_number(right.get("value"))
                if left_value is None or right_value is None or left.get("unit") != right.get("unit"):
                    issues.append(
                        make_review_issue(
                            "long_metrics",
                            f"{output_period}|{left.get('segment')}|{left.get('metric')}|{left.get('unit')}",
                            left.get("fact_id", ""),
                            right.get("fact_id", ""),
                            "",
                            "invalid_parent_for_quarter_derivation",
                        )
                    )
                    continue
                derived = {
                    "data_period": output_period,
                    "period_scope": "quarter",
                    "value_kind": left.get("value_kind", ""),
                    "as_of_date": "",
                    "target_period": "",
                    "segment": left.get("segment", ""),
                    "metric": left.get("metric", ""),
                    "value": format_number(left_value - right_value),
                    "unit": left.get("unit", ""),
                    "yoy": "",
                    "qoq": "",
                    "calculation_method": "derived_from_cumulative_delta",
                    "is_derived": "true",
                    "derived_from_keys": f"{left.get('fact_id')}|{right.get('fact_id')}",
                    "primary_observation_id": "",
                    "confidence": "medium",
                    "review_status": "auto_accepted",
                    "notes": "由累计数反推",
                }
                derived["fact_id"] = stable_id("fact", [fact_key(derived)])
                key = fact_key(derived)
                existing = facts_by_key.get(key)
                if existing is None:
                    facts.append(derived)
                    facts_by_key[key] = derived
                    created += 1
                elif existing.get("value") != derived.get("value") and existing.get("is_derived") == "true":
                    existing.update(derived)
                elif existing.get("value") != derived.get("value"):
                    issues.append(
                        make_review_issue(
                            "long_metrics",
                            key,
                            existing.get("fact_id", ""),
                            "",
                            "",
                            "conflicting_derived_quarter",
                        )
                    )
    write_csv_rows(data_dir(skill_root) / "long_metrics.csv", FACT_FIELDS, facts)
    return facts, issues, created


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-root", required=True)
    parser.add_argument("--period", required=True)
    args = parser.parse_args()

    skill_root = Path(args.skill_root)
    period = args.period
    extracted_path = skill_root / "workspace" / "periods" / period / "extracted" / "extracted_metrics.csv"
    if not extracted_path.exists():
        print(f"No extracted metrics found for {period}")
        return 0

    started = now_iso()
    rows = read_csv_rows(extracted_path, EXTRACTED_FIELDS)
    run_id = stable_id("run", [period, "metrics", started])
    register_sources(skill_root, rows, period, started)

    observations: list[dict[str, str]] = []
    for row in rows:
        source_id = row.get("source_id") or stable_id("src", [row.get("source_url"), row.get("source_file"), row.get("source_name")])
        raw_value = row.get("raw_value") or row.get("value", "")
        raw_unit = row.get("raw_unit") or row.get("unit", "")
        observation = {
            "observation_id": stable_id(
                "obs",
                [
                    source_id,
                    row.get("source_location"),
                    row.get("data_period"),
                    row.get("period_scope"),
                    row.get("value_kind"),
                    row.get("as_of_date"),
                    row.get("segment"),
                    row.get("metric"),
                    raw_value,
                    raw_unit,
                ],
            ),
            "ingestion_run_id": run_id,
            "source_id": source_id,
            "source_period": row.get("source_period") or period,
            "data_period": row.get("data_period", ""),
            "period_scope": row.get("period_scope", ""),
            "value_kind": row.get("value_kind", ""),
            "as_of_date": row.get("as_of_date", ""),
            "target_period": row.get("target_period", ""),
            "segment": row.get("segment", ""),
            "metric": row.get("metric", ""),
            "raw_value": raw_value,
            "raw_unit": raw_unit,
            "value": row.get("value", ""),
            "unit": row.get("unit", ""),
            "yoy": row.get("yoy", ""),
            "qoq": row.get("qoq", ""),
            "calculation_method": row.get("calculation_method") or "reported",
            "source_location": row.get("source_location", ""),
            "confidence": row.get("confidence", ""),
            "review_status": row.get("review_status", "needs_user_review"),
            "notes": row.get("notes", ""),
        }
        observations.append(observation)

    obs_path = data_dir(skill_root) / "metric_observations.csv"
    created_observations = append_unique_rows(obs_path, OBS_FIELDS, observations, observation_key)
    all_observations = read_csv_rows(obs_path, OBS_FIELDS)
    facts, merge_issues, created_facts = merge_observations_into_facts(skill_root, all_observations)
    _, derive_issues, derived_count = derive_quarters(skill_root, facts)
    review_count = append_review_issues(skill_root, merge_issues + derive_issues)

    append_ingestion_run(
        skill_root,
        {
            "ingestion_run_id": run_id,
            "source_period": period,
            "started_at": started,
            "finished_at": now_iso(),
            "input_count": str(len(rows)),
            "created_observations": str(created_observations),
            "created_facts": str(created_facts + derived_count),
            "created_forecasts": "0",
            "review_items": str(review_count),
            "status": "completed",
            "notes": "metrics merge",
        },
    )
    print(f"Merged {created_observations} observations, {created_facts + derived_count} facts, {review_count} review items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
