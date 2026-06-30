#!/usr/bin/env python3
"""Shared CSV helpers for xiaomi-financial-tracker."""

from __future__ import annotations

import csv
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable


SOURCE_FIELDS = [
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
]

RUN_FIELDS = [
    "ingestion_run_id",
    "source_period",
    "started_at",
    "finished_at",
    "input_count",
    "created_observations",
    "created_facts",
    "created_forecasts",
    "review_items",
    "status",
    "notes",
]

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

SOURCE_PRIORITY = {
    "official_pdf": 100,
    "official_url": 100,
    "official_ir": 100,
    "official_announcement": 100,
    "official_screenshot": 90,
    "user_csv": 80,
    "broker_report": 60,
    "public_web": 50,
    "media_repost": 20,
}

CONFIDENCE_PRIORITY = {"high": 3, "medium": 2, "low": 1, "": 0}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def stable_id(prefix: str, parts: Iterable[object]) -> str:
    payload = "\x1f".join(_normalize(part) for part in parts)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def ensure_csv(path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        write_csv_rows(path, fieldnames, [])


def read_csv_rows(path: Path, fieldnames: list[str]) -> list[dict[str, str]]:
    ensure_csv(path, fieldnames)
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, str]] = []
        for row in reader:
            rows.append({field: (row.get(field) or "") for field in fieldnames})
        return rows


def write_csv_rows(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})
    os.replace(tmp_path, path)


def append_unique_rows(
    path: Path,
    fieldnames: list[str],
    rows: Iterable[dict[str, Any]],
    key_func: Callable[[dict[str, Any]], str],
) -> int:
    existing = read_csv_rows(path, fieldnames)
    seen = {key_func(row) for row in existing}
    appended = 0
    output: list[dict[str, Any]] = list(existing)
    for row in rows:
        key = key_func(row)
        if key in seen:
            continue
        seen.add(key)
        output.append(row)
        appended += 1
    write_csv_rows(path, fieldnames, output)
    return appended


def parse_number(value: object) -> float | None:
    text = _normalize(value).replace(",", "")
    if text in {"", "-", "N/A", "n/a"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def format_number(value: float) -> str:
    rounded = round(value, 6)
    if rounded.is_integer():
        return str(int(rounded))
    return f"{rounded:.6f}".rstrip("0").rstrip(".")


def source_priority(source_type: str) -> int:
    return SOURCE_PRIORITY.get(_normalize(source_type), 0)


def confidence_priority(confidence: str) -> int:
    return CONFIDENCE_PRIORITY.get(_normalize(confidence).lower(), 0)


def data_dir(skill_root: Path) -> Path:
    return skill_root / "workspace" / "data"


def register_sources(skill_root: Path, rows: list[dict[str, str]], source_period: str, processed_at: str) -> None:
    registry_path = data_dir(skill_root) / "source_registry.csv"
    existing = {row["source_id"]: row for row in read_csv_rows(registry_path, SOURCE_FIELDS)}
    for row in rows:
        source_id = row.get("source_id") or stable_id(
            "src",
            [row.get("source_url"), row.get("source_file"), row.get("source_name"), row.get("source_type")],
        )
        row["source_id"] = source_id
        current = existing.get(source_id)
        if current:
            current["last_processed_at"] = processed_at
            continue
        existing[source_id] = {
            "source_id": source_id,
            "source_period": row.get("source_period") or source_period,
            "source_type": row.get("source_type") or "",
            "source_name": row.get("source_name") or "",
            "source_file": row.get("source_file") or "",
            "source_url": row.get("source_url") or "",
            "publication_date": row.get("publication_date") or "",
            "content_hash": stable_id("hash", [row.get("source_url"), row.get("source_file"), row.get("source_name")]),
            "first_seen_at": processed_at,
            "last_processed_at": processed_at,
            "confidence": row.get("confidence") or "",
            "review_status": row.get("review_status") or "",
            "notes": row.get("notes") or "",
        }
    write_csv_rows(registry_path, SOURCE_FIELDS, existing.values())


def append_ingestion_run(skill_root: Path, row: dict[str, Any]) -> None:
    append_unique_rows(
        data_dir(skill_root) / "ingestion_runs.csv",
        RUN_FIELDS,
        [row],
        lambda item: str(item.get("ingestion_run_id", "")),
    )


def append_review_issues(skill_root: Path, issues: Iterable[dict[str, Any]]) -> int:
    normalized: list[dict[str, Any]] = []
    for issue in issues:
        issue_id = issue.get("issue_id") or stable_id(
            "issue",
            [
                issue.get("target_table"),
                issue.get("natural_key"),
                issue.get("existing_row_id"),
                issue.get("candidate_row_id"),
                issue.get("reason"),
            ],
        )
        row = {field: issue.get(field, "") for field in REVIEW_FIELDS}
        row["issue_id"] = issue_id
        row["status"] = row.get("status") or "open"
        normalized.append(row)
    return append_unique_rows(
        data_dir(skill_root) / "review_queue.csv",
        REVIEW_FIELDS,
        normalized,
        lambda item: str(item.get("issue_id", "")),
    )


def accepted_status(status: str) -> bool:
    return _normalize(status).lower() in {"auto_accepted", "llm_reviewed", "user_approved", "resolved"}


def excluded_status(status: str) -> bool:
    return _normalize(status).lower() in {"open", "needs_user_review", "rejected"}
