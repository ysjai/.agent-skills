#!/usr/bin/env python3
"""Validate a coding-agent-handbook skill using only the Python standard library.

The parser in this module deliberately accepts a small YAML subset.  Handbook
metadata is data with a long retention period, so accepting a convenient but
ambiguous YAML extension would make the published format less deterministic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


EXIT_OK = 0
EXIT_USAGE = 2
EXIT_VALIDATION = 3
EXIT_TRANSACTION_PENDING = 4

APPLICABILITY_FIELDS = (
    "release_channel",
    "product_form",
    "platforms",
    "deployment",
    "verified_versions",
)
RECORD_FIELDS = {
    "record_id",
    "tool",
    "topic",
    "content_type",
    "learning_level",
    "evidence_class",
    "publication_status",
    "applicability",
    "support_status",
    "support_evidence",
    "last_verified",
}
SOURCE_FIELDS = {
    "source_id",
    "title",
    "publisher",
    "source_kind",
    "normativity",
    "tool",
    "topics",
    "published_at",
    "last_verified",
    "url",
    "notes",
}
EVIDENCE_FIELDS = {
    "source_id",
    "source_locator",
    "accessed_at",
    "review_scope",
    "summary_sha256",
}
APPROVAL_FIELDS = {
    "candidate_id",
    "manifest_hash",
    "approver",
    "approved_at",
    "decision",
    "approved_scope",
    "reason",
    "limitations",
}
EVAL_FIELDS = {
    "id",
    "prompt",
    "expected_records",
    "required_answer_fields",
    "forbidden_claims",
    "manual_review",
}
REPORT_FIELDS = {
    "eval_id",
    "actual_records",
    "required_fields_present",
    "forbidden_claims_found",
    "manual_reviewer",
    "manual_reviewed_at",
    "manual_review_passed",
}
OFFICIAL_SOURCE_KINDS = {
    "official-release",
    "versioned-official-documentation",
    "official-announcement",
    "versioned-official-repository-content",
}
LAB_HEADINGS = (
    "目标",
    "已实测适用范围与前置条件",
    "隔离环境、权限与网络要求",
    "官方机制",
    "最小示例",
    "练习任务",
    "预期可观察结果与验收方式",
    "清理与恢复",
    "常见失败与排查",
    "推荐实践与适用边界",
    "来源与最后确认日期",
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RFC3339_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
RECORD_ID_RE = re.compile(
    r"^(codex|qoder|shared)-[a-z0-9][a-z0-9-]*-\d{4}-\d{2}-\d{2}-r[1-9][0-9]*$"
)
SOURCE_ID_RE = re.compile(r"^SRC-[A-Z0-9][A-Z0-9-]*$")


@dataclass(frozen=True)
class ValidationError:
    path: str
    rule: str
    reason: str

    def render(self) -> str:
        return f"{self.path}: {self.rule}: {self.reason}"


class RestrictedYamlError(ValueError):
    """Raised when metadata is outside the documented YAML subset."""


class _DuplicateJsonKey(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def strict_json_loads(text: str) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise _DuplicateJsonKey(f"duplicate key {key!r}")
            result[key] = value
        return result

    def invalid_constant(value: str) -> None:
        raise ValueError(f"unsupported JSON constant {value}")

    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid_constant)


def _split_flow(value: str) -> list[str]:
    """Split a flow collection while preserving quoted nested values."""
    parts: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None
    index = 0
    while index < len(value):
        character = value[index]
        if quote == "'":
            if character == "'":
                if index + 1 < len(value) and value[index + 1] == "'":
                    index += 1
                else:
                    quote = None
        elif quote == '"':
            if character == "\\":
                index += 1
            elif character == '"':
                quote = None
        elif character in "'\"":
            quote = character
        elif character in "[{":
            depth += 1
        elif character in "]}":
            depth -= 1
            if depth < 0:
                raise RestrictedYamlError("unbalanced flow collection")
        elif character == "," and depth == 0:
            part = value[start:index].strip()
            if not part:
                raise RestrictedYamlError("empty flow collection item")
            parts.append(part)
            start = index + 1
        index += 1
    if quote is not None or depth != 0:
        raise RestrictedYamlError("unterminated flow collection")
    tail = value[start:].strip()
    if not tail:
        raise RestrictedYamlError("empty flow collection item")
    parts.append(tail)
    return parts


def _find_unquoted_colon(value: str) -> int:
    quote: str | None = None
    depth = 0
    for index, character in enumerate(value):
        if quote == "'":
            if character == "'":
                quote = None
            continue
        if quote == '"':
            if character == '"' and (index == 0 or value[index - 1] != "\\"):
                quote = None
            continue
        if character in "'\"":
            quote = character
        elif character in "[{":
            depth += 1
        elif character in "]}":
            depth -= 1
        elif character == ":" and depth == 0:
            return index
    return -1


def _parse_flow_value(value: str) -> Any:
    value = value.strip()
    if not value:
        raise RestrictedYamlError("empty scalar")
    if value.startswith("["):
        if not value.endswith("]"):
            raise RestrictedYamlError("unterminated flow list")
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_flow_value(part) for part in _split_flow(inner)]
    if value.startswith("{"):
        if not value.endswith("}"):
            raise RestrictedYamlError("unterminated flow map")
        inner = value[1:-1].strip()
        if not inner:
            return {}
        result: dict[str, Any] = {}
        for part in _split_flow(inner):
            separator = _find_unquoted_colon(part)
            if separator <= 0:
                raise RestrictedYamlError("flow map item must be key: value")
            key = part[:separator].strip()
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", key):
                raise RestrictedYamlError("unsupported flow map key")
            if key in result:
                raise RestrictedYamlError(f"duplicate field {key}")
            result[key] = _parse_flow_value(part[separator + 1 :])
        return result
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise RestrictedYamlError(f"invalid quoted scalar: {exc.msg}") from exc
        if not isinstance(parsed, str):
            raise RestrictedYamlError("quoted scalar must be a string")
        return parsed
    if value.startswith("'"):
        if not value.endswith("'") or len(value) < 2:
            raise RestrictedYamlError("unterminated single-quoted scalar")
        return value[1:-1].replace("''", "'")
    if value in {"null", "~"}:
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if value[0] in "|>&*!" or value.startswith("-") or " #" in value:
        raise RestrictedYamlError("unsupported YAML scalar syntax")
    if "\t" in value or "\n" in value:
        raise RestrictedYamlError("unsupported scalar whitespace")
    return value


def parse_restricted_yaml(text: str) -> dict[str, Any]:
    """Parse mappings, scalars, and flow lists/maps from the handbook subset."""
    lines = text.splitlines()
    if not lines:
        raise RestrictedYamlError("empty YAML mapping")
    if any("\t" in line for line in lines):
        raise RestrictedYamlError("tabs are not allowed")

    meaningful: list[tuple[int, str, int]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent % 2:
            raise RestrictedYamlError(f"line {line_number}: indentation must be multiples of two")
        meaningful.append((indent, line[indent:], line_number))
    if not meaningful:
        raise RestrictedYamlError("empty YAML mapping")

    def parse_mapping(position: int, indent: int) -> tuple[dict[str, Any], int]:
        result: dict[str, Any] = {}
        while position < len(meaningful):
            current_indent, content, line_number = meaningful[position]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise RestrictedYamlError(f"line {line_number}: unexpected indentation")
            if content.startswith("- ") or content.startswith("["):
                raise RestrictedYamlError(f"line {line_number}: block lists are unsupported")
            match = re.fullmatch(r"([A-Za-z0-9_.-]+):(?:[ ](.*)|)", content)
            if not match:
                raise RestrictedYamlError(f"line {line_number}: expected mapping field")
            key, raw_value = match.groups()
            if key in result:
                raise RestrictedYamlError(f"line {line_number}: duplicate field {key}")
            position += 1
            if raw_value is None:
                if position >= len(meaningful) or meaningful[position][0] <= indent:
                    raise RestrictedYamlError(f"line {line_number}: mapping value is required")
                child_indent = meaningful[position][0]
                if child_indent != indent + 2:
                    raise RestrictedYamlError(f"line {line_number}: nested mapping must indent by two")
                child, position = parse_mapping(position, child_indent)
                result[key] = child
            else:
                result[key] = _parse_flow_value(raw_value)
        return result, position

    if meaningful[0][0] != 0:
        raise RestrictedYamlError("root mapping cannot be indented")
    parsed, consumed = parse_mapping(0, 0)
    if consumed != len(meaningful):
        raise RestrictedYamlError("unsupported trailing YAML")
    return parsed


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise RestrictedYamlError("frontmatter must start on the first line")
    closing = text.find("\n---\n", 4)
    if closing < 0:
        raise RestrictedYamlError("frontmatter closing delimiter is required")
    return parse_restricted_yaml(text[4:closing]), text[closing + 5 :]


def _schema_error(errors: list[ValidationError], path: str, rule: str, message: str) -> None:
    errors.append(ValidationError(path, rule, message))


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _has_symlink_component(path: Path, root: Path) -> bool:
    current = root
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return True
    for part in parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def _safe_posix_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts)


def _read_json(path: Path) -> Any:
    return strict_json_loads(path.read_text(encoding="utf-8"))


def _is_date(value: Any) -> bool:
    return isinstance(value, str) and bool(DATE_RE.fullmatch(value))


def _is_rfc3339(value: Any) -> bool:
    return isinstance(value, str) and bool(RFC3339_RE.fullmatch(value))


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256_RE.fullmatch(value))


def _is_string_list(value: Any, *, allow_empty: bool = True) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(isinstance(item, str) and item for item in value)
        and len(set(value)) == len(value)
    )


def _validate_exact_fields(
    value: Any,
    required: set[str],
    path: str,
    rule: str,
    errors: list[ValidationError],
) -> bool:
    if not isinstance(value, dict):
        _schema_error(errors, path, rule, "metadata must be a mapping")
        return False
    missing = sorted(required - set(value))
    extra = sorted(set(value) - required)
    if missing or extra:
        details: list[str] = []
        if missing:
            details.append(f"missing fields {', '.join(missing)}")
        if extra:
            details.append(f"unsupported fields {', '.join(extra)}")
        _schema_error(errors, path, rule, "; ".join(details))
        return False
    return True


def _validate_applicability(
    scope: Any,
    path: str,
    rule: str,
    errors: list[ValidationError],
    *,
    status: str | None = None,
) -> dict[str, Any] | None:
    if not isinstance(scope, dict) or set(scope) != set(APPLICABILITY_FIELDS):
        _schema_error(errors, path, rule, "applicability must contain exactly the five scope fields")
        return None
    if scope["release_channel"] not in {"stable", "preview", "unspecified"}:
        _schema_error(errors, path, rule, "invalid release_channel")
    if scope["product_form"] not in {"cli", "desktop", "web", "unspecified"}:
        _schema_error(errors, path, rule, "invalid product_form")
    if scope["deployment"] not in {"local", "cloud", "unspecified"}:
        _schema_error(errors, path, rule, "invalid deployment")
    platforms = scope["platforms"]
    if platforms != "unspecified" and not _is_string_list(platforms, allow_empty=False):
        _schema_error(errors, path, rule, "platforms must be unspecified or a unique non-empty list")
    versions = scope["verified_versions"]
    if not _is_string_list(versions, allow_empty=False):
        _schema_error(errors, path, rule, "verified_versions must be a unique non-empty list")
    if status not in {"unverified", "not-covered", "support-not-publicly-confirmed", None} and any(
        scope[name] == "unspecified" for name in ("release_channel", "product_form", "platforms", "deployment")
    ):
        _schema_error(
            errors,
            path,
            "applicability-unspecified",
            "unspecified only supports unverified, not-covered, or support-not-publicly-confirmed status",
        )
    return scope if not errors or isinstance(scope, dict) else None


def _scope_overlaps(first: dict[str, Any], second: dict[str, Any]) -> bool:
    for field in ("release_channel", "product_form", "deployment"):
        if first[field] != "unspecified" and second[field] != "unspecified" and first[field] != second[field]:
            return False
    first_platforms, second_platforms = first["platforms"], second["platforms"]
    if first_platforms != "unspecified" and second_platforms != "unspecified":
        if not set(first_platforms).intersection(second_platforms):
            return False
    if not set(first["verified_versions"]).intersection(second["verified_versions"]):
        return False
    return True


def _scope_within(child: dict[str, Any], parent: dict[str, Any]) -> bool:
    for field in ("release_channel", "product_form", "deployment"):
        if parent[field] != "unspecified" and child[field] != parent[field]:
            return False
    if parent["platforms"] != "unspecified":
        if child["platforms"] == "unspecified" or not set(child["platforms"]).issubset(parent["platforms"]):
            return False
    return set(child["verified_versions"]).issubset(parent["verified_versions"])


class ContentView:
    """A logical handbook tree backed by published files or a candidate projection."""

    def __init__(self, root: Path, mode: str, errors: list[ValidationError]) -> None:
        self.root = root
        self.mode = mode
        self.errors = errors
        self.files: dict[str, Path] = {}

    def add(self, logical_path: str, actual_path: Path, rule: str = "path-safety") -> None:
        if not _safe_posix_path(logical_path):
            _schema_error(self.errors, logical_path or str(actual_path), rule, "logical path must be a safe POSIX relative path")
            return
        if not actual_path.exists() or not actual_path.is_file():
            _schema_error(self.errors, logical_path, rule, "file is missing")
            return
        if actual_path.is_symlink() or _has_symlink_component(actual_path, self.root) or not _is_within(actual_path, self.root):
            _schema_error(self.errors, logical_path, rule, "symbolic links and root escapes are not allowed")
            return
        prior = self.files.get(logical_path)
        if prior is not None and prior.read_bytes() != actual_path.read_bytes():
            _schema_error(self.errors, logical_path, "candidate-evidence-conflict", "multiple candidate files project different bytes to one target")
            return
        self.files[logical_path] = actual_path

    def get(self, logical_path: str) -> Path | None:
        return self.files.get(logical_path)

    def matching(self, prefix: str, suffix: str = "") -> Iterable[tuple[str, Path]]:
        for logical, actual in sorted(self.files.items()):
            if logical.startswith(prefix) and logical.endswith(suffix):
                yield logical, actual


def _walk_files(root: Path, errors: list[ValidationError], label: str) -> list[Path]:
    if not root.exists():
        return []
    if root.is_symlink() or not root.is_dir():
        _schema_error(errors, label, "path-safety", "directory is missing or is a symbolic link")
        return []
    paths: list[Path] = []
    for current, directories, names in os.walk(root, followlinks=False):
        current_path = Path(current)
        for directory in list(directories):
            candidate = current_path / directory
            if candidate.is_symlink():
                _schema_error(errors, _relative(root, candidate), "path-safety", "symbolic links are not allowed")
                directories.remove(directory)
        for name in names:
            candidate = current_path / name
            if candidate.is_symlink():
                _schema_error(errors, _relative(root, candidate), "path-safety", "symbolic links are not allowed")
            elif candidate.is_file():
                paths.append(candidate)
    return paths


def _check_pending_transactions(root: Path, errors: list[ValidationError]) -> None:
    transactions = root / "updates" / "transactions"
    if not transactions.exists():
        return
    for path in sorted(transactions.glob("*.json")):
        relative = _relative(root, path)
        try:
            transaction = _read_json(path)
            state = transaction.get("state") if isinstance(transaction, dict) else None
        except (OSError, ValueError, _DuplicateJsonKey) as exc:
            _schema_error(errors, relative, "publication-transaction-pending", f"unreadable transaction: {exc}")
            continue
        if state not in {"completed", "rolled-back", "recovered"}:
            _schema_error(errors, relative, "publication-transaction-pending", f"transaction state is {state!r}")


def _parse_markdown_frontmatter(path: Path, logical: str, errors: list[ValidationError], rule: str) -> tuple[dict[str, Any], str] | None:
    try:
        return parse_frontmatter(path)
    except (OSError, UnicodeDecodeError, RestrictedYamlError) as exc:
        _schema_error(errors, logical, rule, str(exc))
        return None


def _parse_source_registry(view: ContentView, errors: list[ValidationError]) -> dict[str, dict[str, Any]]:
    logical = "sources/source-registry.md"
    path = view.get(logical)
    if path is None:
        _schema_error(errors, logical, "source-registry", "source registry is required")
        return {}
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        _schema_error(errors, logical, "source-registry", str(exc))
        return {}
    blocks = list(re.finditer(r"```yaml\n(.*?)\n```", text, flags=re.DOTALL))
    without_blocks = re.sub(r"```yaml\n.*?\n```", "", text, flags=re.DOTALL)
    if without_blocks.strip() or not blocks:
        _schema_error(errors, logical, "source-registry", "registry must contain only YAML fenced blocks")
    registry: dict[str, dict[str, Any]] = {}
    ordered_ids: list[str] = []
    for block in blocks:
        try:
            entry = parse_restricted_yaml(block.group(1))
        except RestrictedYamlError as exc:
            _schema_error(errors, logical, "source-registry", str(exc))
            continue
        if not _validate_exact_fields(entry, SOURCE_FIELDS, logical, "source-registry", errors):
            continue
        source_id = entry["source_id"]
        if not isinstance(source_id, str) or not SOURCE_ID_RE.fullmatch(source_id):
            _schema_error(errors, logical, "source-registry", "source_id must use SRC- uppercase form")
            continue
        if source_id in registry:
            _schema_error(errors, logical, "source-registry", f"duplicate source_id {source_id}")
            continue
        if not all(isinstance(entry[field], str) and entry[field] for field in ("title", "publisher", "notes")):
            _schema_error(errors, logical, "source-registry", "title, publisher, and notes must be non-empty strings")
        if entry["source_kind"] not in {
            "official-release",
            "versioned-official-documentation",
            "official-announcement",
            "versioned-official-repository-content",
            "non-normative-official-repository-content",
            "third-party",
        }:
            _schema_error(errors, logical, "source-registry", "unsupported source_kind")
        if entry["normativity"] not in {"normative", "supporting", "non-normative"}:
            _schema_error(errors, logical, "source-registry", "unsupported normativity")
        if entry["tool"] not in {"codex", "qoder", "shared"}:
            _schema_error(errors, logical, "source-registry", "unsupported tool")
        if not _is_string_list(entry["topics"], allow_empty=False):
            _schema_error(errors, logical, "source-registry", "topics must be a unique non-empty list")
        if entry["published_at"] is not None and not _is_date(entry["published_at"]):
            _schema_error(errors, logical, "source-registry", "published_at must be a date or null")
        if not _is_date(entry["last_verified"]):
            _schema_error(errors, logical, "source-registry", "last_verified must be YYYY-MM-DD")
        if not isinstance(entry["url"], str) or not entry["url"].startswith("https://"):
            _schema_error(errors, logical, "source-registry", "url must be an exact HTTPS URL")
        registry[source_id] = entry
        ordered_ids.append(source_id)
    if ordered_ids != sorted(ordered_ids):
        _schema_error(errors, logical, "source-registry", "YAML blocks must be sorted by source_id")
    return registry


def _parse_evidence(view: ContentView, registry: dict[str, dict[str, Any]], errors: list[ValidationError]) -> dict[str, dict[str, Any]]:
    evidence: dict[str, dict[str, Any]] = {}
    for logical, path in view.matching("sources/evidence/", ".md"):
        parsed = _parse_markdown_frontmatter(path, logical, errors, "evidence-schema")
        if parsed is None:
            continue
        frontmatter, body = parsed
        if not _validate_exact_fields(frontmatter, EVIDENCE_FIELDS, logical, "evidence-schema", errors):
            continue
        source_id = frontmatter["source_id"]
        expected_prefix = f"sources/evidence/{source_id}/"
        if not isinstance(source_id, str) or source_id not in registry:
            _schema_error(errors, logical, "evidence-source", "source_id is not in source registry")
        if not logical.startswith(expected_prefix):
            _schema_error(errors, logical, "evidence-schema", "path must be under its source_id directory")
        if not isinstance(frontmatter["source_locator"], str) or not frontmatter["source_locator"].startswith("https://"):
            _schema_error(errors, logical, "evidence-schema", "source_locator must be an HTTPS locator")
        if not _is_rfc3339(frontmatter["accessed_at"]):
            _schema_error(errors, logical, "evidence-schema", "accessed_at must be UTC RFC 3339")
        if not isinstance(frontmatter["review_scope"], str) or not frontmatter["review_scope"]:
            _schema_error(errors, logical, "evidence-schema", "review_scope must be a non-empty string")
        if not _is_sha256(frontmatter["summary_sha256"]):
            _schema_error(errors, logical, "evidence-schema", "summary_sha256 must be lowercase SHA-256")
        elif frontmatter["summary_sha256"] != sha256_bytes(body.encode("utf-8")):
            _schema_error(errors, logical, "evidence-summary-hash", "summary_sha256 does not match the excerpt body")
        evidence[logical] = {
            "frontmatter": frontmatter,
            "file_hash": sha256_file(path),
        }
    return evidence


def _parse_facts(
    body: str,
    record_id: str,
    record_scope: dict[str, Any],
    record_support_status: str,
    logical: str,
    registry: dict[str, dict[str, Any]],
    evidence: dict[str, dict[str, Any]],
    errors: list[ValidationError],
) -> dict[str, dict[str, Any]]:
    pattern = re.compile(
        r"^> \*\*(FACT-[A-Za-z0-9-]+-[0-9]{2})\*\*\n"
        r"> - 断言：(.+)\n"
        r"> - 适用范围（JSON）：`([^`]+)`\n"
        r"> - 最后核对：(\d{4}-\d{2}-\d{2})\n"
        r"> - 证据：`([^`]+)`，(.+)\n"
        r"> - 证据快照：`([^`]+)`，SHA-256 `([^`]+)`$",
        re.MULTILINE,
    )
    facts: dict[str, dict[str, Any]] = {}
    for match in pattern.finditer(body):
        fact_id, assertion, scope_text, last_verified, source_id, locator, snapshot, snapshot_hash = match.groups()
        if fact_id in facts:
            _schema_error(errors, logical, "fact-schema", f"duplicate fact ID {fact_id}")
            continue
        if not fact_id.startswith(f"FACT-{record_id}-"):
            _schema_error(errors, logical, "fact-schema", "FACT ID must belong to its record")
        if not assertion.strip() or not _is_date(last_verified):
            _schema_error(errors, logical, "fact-schema", "assertion and last verification date are required")
        try:
            scope = strict_json_loads(scope_text)
        except (ValueError, _DuplicateJsonKey) as exc:
            _schema_error(errors, logical, "fact-scope", f"invalid canonical JSON: {exc}")
            continue
        if canonical_json(scope).decode("utf-8") != scope_text:
            _schema_error(errors, logical, "fact-scope", "scope JSON must use canonical serialization")
        scope_valid = _validate_applicability(
            scope,
            logical,
            "fact-scope",
            errors,
            status=record_support_status,
        )
        if scope_valid is not None and not _scope_within(scope_valid, record_scope):
            _schema_error(errors, logical, "fact-scope", "FACT scope must be equal to or narrower than record scope")
        if source_id not in registry:
            _schema_error(errors, logical, "fact-source", "source_id is not in source registry")
        else:
            source = registry[source_id]
            if source["source_kind"] not in OFFICIAL_SOURCE_KINDS or source["normativity"] != "normative":
                _schema_error(errors, logical, "fact-source-kind", "official fact requires a normative official source category")
        if not isinstance(locator, str) or not locator.startswith("https://"):
            _schema_error(errors, logical, "fact-source", "FACT locator must be an exact HTTPS locator")
        if not _safe_posix_path(snapshot) or not snapshot.startswith("sources/evidence/"):
            _schema_error(errors, logical, "fact-evidence-path", "snapshot must be a formal sources/evidence path")
        if not _is_sha256(snapshot_hash):
            _schema_error(errors, logical, "fact-evidence-hash", "snapshot SHA-256 must be lowercase hex")
        snapshot_entry = evidence.get(snapshot)
        if snapshot_entry is None:
            _schema_error(errors, logical, "fact-evidence", "snapshot does not exist")
        else:
            snapshot_frontmatter = snapshot_entry["frontmatter"]
            if snapshot_entry["file_hash"] != snapshot_hash:
                _schema_error(errors, logical, "fact-evidence-hash", "snapshot SHA-256 does not match")
            if snapshot_frontmatter["source_id"] != source_id or snapshot_frontmatter["source_locator"] != locator:
                _schema_error(errors, logical, "fact-evidence", "source ID or locator differs from snapshot")
        facts[fact_id] = {"scope": scope, "record_id": record_id, "source_id": source_id}
    return facts


def _validate_lab(body: str, logical: str, errors: list[ValidationError]) -> None:
    headings = re.findall(r"^## (.+)$", body, flags=re.MULTILINE)
    if headings != list(LAB_HEADINGS):
        _schema_error(errors, logical, "lab-required-section", "Lab must contain the eleven required sections in order")
        return
    section_pattern = re.compile(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
    sections = {heading: content.strip() for heading, content in section_pattern.findall(body)}
    required_words = {
        "已实测适用范围与前置条件": ("版本", "平台"),
        "隔离环境、权限与网络要求": ("隔离", "权限", "网络", "真实凭证", "生产"),
        "预期可观察结果与验收方式": ("验收",),
        "清理与恢复": ("清理", "恢复"),
    }
    for section, words in required_words.items():
        content = sections.get(section, "")
        if not content or any(word not in content for word in words):
            _schema_error(errors, logical, "lab-safety-section", f"{section} lacks required safety fields")


def _validate_records_and_indexes(view: ContentView, errors: list[ValidationError]) -> dict[str, dict[str, Any]]:
    registry = _parse_source_registry(view, errors)
    evidence = _parse_evidence(view, registry, errors)
    records: dict[str, dict[str, Any]] = {}
    facts: dict[str, dict[str, Any]] = {}
    for logical, path in view.matching("references/tools/", ".md"):
        if "/records/" not in logical:
            continue
        parsed = _parse_markdown_frontmatter(path, logical, errors, "record-schema")
        if parsed is None:
            continue
        frontmatter, body = parsed
        if not _validate_exact_fields(frontmatter, RECORD_FIELDS, logical, "record-schema", errors):
            continue
        record_id = frontmatter["record_id"]
        if not isinstance(record_id, str) or not RECORD_ID_RE.fullmatch(record_id):
            _schema_error(errors, logical, "record-id", "record_id has an invalid format")
            continue
        if record_id in records:
            _schema_error(errors, logical, "record-id", f"duplicate record_id {record_id}")
            continue
        parts = logical.split("/")
        if len(parts) < 7 or frontmatter["tool"] != parts[2] or frontmatter["topic"] != parts[4]:
            _schema_error(errors, logical, "record-schema", "record tool/topic must match its directory")
        if not record_id.startswith(f"{frontmatter['tool']}-{frontmatter['topic']}-"):
            _schema_error(errors, logical, "record-id", "record_id must match record tool and topic")
        if frontmatter["tool"] not in {"codex", "qoder", "shared"}:
            _schema_error(errors, logical, "record-schema", "invalid tool")
        if not isinstance(frontmatter["topic"], str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", frontmatter["topic"]):
            _schema_error(errors, logical, "record-schema", "topic must be lowercase kebab-case")
        if frontmatter["content_type"] not in {"reference", "lab"}:
            _schema_error(errors, logical, "record-schema", "invalid content_type")
        if frontmatter["learning_level"] not in {"personal", "team", "organization"}:
            _schema_error(errors, logical, "record-schema", "invalid learning_level")
        if frontmatter["evidence_class"] not in {
            "official-fact",
            "established-practice",
            "local-practice",
            "experimental-guidance",
        }:
            _schema_error(errors, logical, "record-schema", "invalid evidence_class")
        if frontmatter["publication_status"] not in {"published", "unverified"}:
            _schema_error(errors, logical, "record-schema", "invalid publication_status")
        support_status = frontmatter["support_status"]
        if support_status not in {"officially-supported", "support-not-publicly-confirmed", "unsupported"}:
            _schema_error(errors, logical, "record-schema", "invalid support_status")
        scope = _validate_applicability(frontmatter["applicability"], logical, "applicability", errors, status=support_status)
        support_evidence = frontmatter["support_evidence"]
        if support_status in {"officially-supported", "unsupported"}:
            if not isinstance(support_evidence, str) or not support_evidence:
                _schema_error(errors, logical, "record-support-evidence", "official support status requires a FACT ID")
        elif support_evidence is not None:
            _schema_error(errors, logical, "record-support-evidence", "unconfirmed support status requires null support_evidence")
        if not _is_date(frontmatter["last_verified"]):
            _schema_error(errors, logical, "record-schema", "last_verified must be YYYY-MM-DD")
        if scope is None:
            continue
        record_facts: dict[str, dict[str, Any]] = {}
        if frontmatter["evidence_class"] == "official-fact":
            record_facts = _parse_facts(
                body,
                record_id,
                scope,
                support_status,
                logical,
                registry,
                evidence,
                errors,
            )
            if not record_facts:
                _schema_error(errors, logical, "fact-schema", "official-fact record requires at least one FACT block")
        if support_status in {"officially-supported", "unsupported"}:
            supporting_fact = record_facts.get(support_evidence) if isinstance(support_evidence, str) else None
            if supporting_fact is None:
                _schema_error(errors, logical, "record-support-evidence", "support_evidence must be a FACT in this record")
            elif not _scope_overlaps(scope, supporting_fact["scope"]):
                _schema_error(errors, logical, "record-support-evidence", "support FACT scope is incompatible with record")
        if frontmatter["content_type"] == "lab":
            _validate_lab(body, logical, errors)
        records[record_id] = {
            "scope": scope,
            "tool": frontmatter["tool"],
            "topic": frontmatter["topic"],
            "facts": record_facts,
            "logical": logical,
        }
        facts.update(record_facts)

    indexes: list[dict[str, Any]] = []
    indexed_record_ids: set[str] = set()
    for logical, path in view.matching("references/tools/", "/index.md"):
        if "/capabilities/" not in logical:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            _schema_error(errors, logical, "capability-index", str(exc))
            continue
        blocks = list(re.finditer(r"```yaml\n(.*?)\n```", text, flags=re.DOTALL))
        if not blocks:
            _schema_error(errors, logical, "capability-index", "one or more YAML blocks are required")
        for block in blocks:
            try:
                index = parse_restricted_yaml(block.group(1))
            except RestrictedYamlError as exc:
                _schema_error(errors, logical, "capability-index", str(exc))
                continue
            required = {"capability_id", "applicability", "capability_status", "record_ids", "status_evidence", "lifecycle"}
            permitted = required | {"reason"}
            if not isinstance(index, dict) or not required.issubset(index) or not set(index).issubset(permitted):
                _schema_error(errors, logical, "capability-index", "index must use the fixed capability fields")
                continue
            status = index["capability_status"]
            if status not in {
                "officially-supported",
                "officially-not-supported",
                "unverified",
                "not-covered",
                "not-applicable",
            }:
                _schema_error(errors, logical, "capability-index", "invalid capability_status")
                continue
            capability_id = index["capability_id"]
            parts = logical.split("/")
            expected_id = f"{parts[2]}.{parts[4]}" if len(parts) >= 6 else ""
            if not isinstance(capability_id, str) or capability_id != expected_id:
                _schema_error(errors, logical, "capability-index", "capability_id must match its tool/topic directory")
            scope = _validate_applicability(index["applicability"], logical, "applicability", errors, status=status)
            record_ids = index["record_ids"]
            status_evidence = index["status_evidence"]
            if not _is_string_list(record_ids):
                _schema_error(errors, logical, "capability-index", "record_ids must be a unique list")
            if not _is_string_list(status_evidence):
                _schema_error(errors, logical, "capability-index", "status_evidence must be a unique list")
            if status in {"officially-supported", "officially-not-supported"} and not status_evidence:
                _schema_error(errors, logical, "capability-status-evidence", "official status requires status_evidence")
            if status == "not-applicable":
                if not isinstance(index.get("reason"), str) or not index["reason"]:
                    _schema_error(errors, logical, "capability-index", "not-applicable requires reason")
            elif "reason" in index and (not isinstance(index["reason"], str) or not index["reason"]):
                _schema_error(errors, logical, "capability-index", "reason must be a non-empty string when present")
            lifecycle = index["lifecycle"]
            if not isinstance(lifecycle, dict) or set(lifecycle) != set(record_ids if isinstance(record_ids, list) else []):
                _schema_error(errors, logical, "record-lifecycle", "lifecycle must map exactly the listed record IDs")
            for record_id in record_ids if isinstance(record_ids, list) else []:
                if isinstance(record_id, str):
                    indexed_record_ids.add(record_id)
                record = records.get(record_id)
                if record is None:
                    _schema_error(errors, logical, "capability-record", f"record {record_id} does not exist")
                    continue
                if record["tool"] != parts[2] or record["topic"] != parts[4]:
                    _schema_error(errors, logical, "capability-record", f"record {record_id} has a different tool or topic")
                if scope is not None and not _scope_overlaps(scope, record["scope"]):
                    _schema_error(errors, logical, "capability-record", f"record {record_id} has incompatible applicability")
                state = lifecycle.get(record_id) if isinstance(lifecycle, dict) else None
                if not isinstance(state, dict) or set(state) != {"status", "superseded_by"}:
                    _schema_error(errors, logical, "record-lifecycle", f"invalid lifecycle for {record_id}")
                elif state["status"] not in {"current", "superseded", "deprecated"}:
                    _schema_error(errors, logical, "record-lifecycle", f"invalid lifecycle status for {record_id}")
                elif state["superseded_by"] is not None and state["superseded_by"] not in records:
                    _schema_error(errors, logical, "record-lifecycle", f"unknown replacement record for {record_id}")
            for fact_id in status_evidence if isinstance(status_evidence, list) else []:
                fact = facts.get(fact_id)
                if fact is None:
                    _schema_error(errors, logical, "capability-status-evidence", f"FACT {fact_id} does not exist")
                elif scope is not None and not _scope_overlaps(scope, fact["scope"]):
                    _schema_error(errors, logical, "capability-status-evidence", f"FACT {fact_id} has incompatible applicability")
            if scope is not None:
                indexes.append({"id": capability_id, "status": status, "scope": scope, "logical": logical})
    for record_id, record in records.items():
        if record_id not in indexed_record_ids:
            _schema_error(errors, record["logical"], "capability-record", "record is not reachable from a capability index")
    for position, first in enumerate(indexes):
        for second in indexes[position + 1 :]:
            if first["id"] != second["id"]:
                continue
            opposite = {first["status"], second["status"]} == {
                "officially-supported",
                "officially-not-supported",
            }
            if opposite and _scope_overlaps(first["scope"], second["scope"]):
                _schema_error(
                    errors,
                    second["logical"],
                    "capability-status-overlap",
                    f"{first['id']} has overlapping opposite official states",
                )
    return records


def _validate_candidate_manifest(root: Path, candidate_id: str, errors: list[ValidationError]) -> tuple[dict[str, Any] | None, ContentView]:
    candidate_root = root / "updates" / "candidates" / candidate_id
    view = ContentView(root, "candidate", errors)
    manifest_path = candidate_root / "manifest.json"
    manifest: dict[str, Any] | None = None
    if not manifest_path.exists():
        _schema_error(errors, _relative(root, manifest_path), "candidate-manifest", "manifest.json is required")
        return None, view
    try:
        parsed = _read_json(manifest_path)
    except (OSError, ValueError, _DuplicateJsonKey) as exc:
        _schema_error(errors, _relative(root, manifest_path), "candidate-manifest", str(exc))
        return None, view
    if not isinstance(parsed, dict) or set(parsed) != {"manifest_version", "candidate_id", "files", "manifest_hash"}:
        _schema_error(errors, _relative(root, manifest_path), "candidate-manifest", "manifest uses an unsupported schema")
        return None, view
    if parsed["manifest_version"] != 1 or parsed["candidate_id"] != candidate_id or not _is_sha256(parsed["manifest_hash"]):
        _schema_error(errors, _relative(root, manifest_path), "candidate-manifest", "invalid version, candidate ID, or manifest hash")
        return None, view
    candidate_copy = dict(parsed)
    candidate_copy.pop("manifest_hash")
    if sha256_bytes(canonical_json(candidate_copy)) != parsed["manifest_hash"]:
        _schema_error(errors, _relative(root, manifest_path), "manifest-hash", "manifest_hash does not match canonical JSON")
    files = parsed["files"]
    if not isinstance(files, list) or not files:
        _schema_error(errors, _relative(root, manifest_path), "candidate-manifest", "files must be a non-empty list")
        return None, view
    candidate_paths: list[str] = []
    target_paths: set[str] = set()
    report_entries = 0
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {"candidate_path", "target_path", "sha256"}:
            _schema_error(errors, _relative(root, manifest_path), "candidate-manifest", "each file needs candidate_path, target_path, and sha256")
            continue
        candidate_path, target_path, digest = entry["candidate_path"], entry["target_path"], entry["sha256"]
        if not _safe_posix_path(candidate_path):
            _schema_error(errors, _relative(root, manifest_path), "candidate-path", "candidate_path must be safe and relative")
            continue
        if candidate_path in candidate_paths:
            _schema_error(errors, _relative(root, manifest_path), "candidate-path", f"duplicate candidate path {candidate_path}")
        candidate_paths.append(candidate_path)
        if not _is_sha256(digest):
            _schema_error(errors, _relative(root, manifest_path), "candidate-manifest", f"invalid SHA-256 for {candidate_path}")
        is_report = candidate_path == "candidate.md"
        if is_report != (target_path is None):
            _schema_error(errors, _relative(root, manifest_path), "candidate-path", "only candidate.md may use a null target")
        if is_report:
            report_entries += 1
        if not is_report and not (candidate_path.startswith("evidence/") or candidate_path.startswith("publish/")):
            _schema_error(errors, _relative(root, manifest_path), "candidate-path", "candidate files must be evidence/ or publish/")
        if target_path is not None:
            if not _safe_posix_path(target_path):
                _schema_error(errors, _relative(root, manifest_path), "target-path", "target_path must be safe and relative")
            elif not target_path.startswith(("references/", "sources/", "evals/")):
                _schema_error(errors, _relative(root, manifest_path), "target-path", "target must be under references/, sources/, or evals/")
            elif target_path == "sources/integrity/published-records.sha256":
                _schema_error(errors, _relative(root, manifest_path), "target-path", "integrity ledger is generated only by the publisher")
            elif target_path in target_paths:
                _schema_error(errors, _relative(root, manifest_path), "target-path", f"duplicate target path {target_path}")
            else:
                target_paths.add(target_path)
        actual = candidate_root / PurePosixPath(candidate_path)
        if actual.is_symlink() or not _is_within(actual, candidate_root) or _has_symlink_component(actual, candidate_root):
            _schema_error(errors, _relative(root, manifest_path), "candidate-path", f"path escapes or is a symbolic link: {candidate_path}")
        elif not actual.is_file():
            _schema_error(errors, _relative(root, manifest_path), "candidate-path", f"listed file is missing: {candidate_path}")
        else:
            if sha256_file(actual) != digest:
                _schema_error(errors, _relative(root, manifest_path), "manifest-file-hash", f"hash mismatch for {candidate_path}")
            if target_path is not None:
                view.add(target_path, actual, "candidate-path")
    if candidate_paths != sorted(candidate_paths):
        _schema_error(errors, _relative(root, manifest_path), "candidate-manifest", "files must be sorted by candidate_path")
    if report_entries != 1:
        _schema_error(errors, _relative(root, manifest_path), "candidate-manifest", "candidate.md must appear exactly once with a null target")
    actual_paths = {
        _relative(candidate_root, path)
        for path in _walk_files(candidate_root, errors, _relative(root, candidate_root))
        if path.name != "manifest.json"
    }
    if set(candidate_paths) != actual_paths:
        _schema_error(errors, _relative(root, manifest_path), "candidate-manifest", "manifest must list every candidate file exactly once")
    return parsed, view


def _candidate_view_without_manifest(
    root: Path,
    candidate_id: str,
    errors: list[ValidationError],
    *,
    allow_published_sources: bool = False,
) -> ContentView:
    candidate_root = root / "updates" / "candidates" / candidate_id
    view = ContentView(root, "candidate", errors)
    report = candidate_root / "candidate.md"
    if not report.is_file() or report.is_symlink():
        _schema_error(errors, _relative(root, report), "candidate-stage-scope", "candidate.md is required")
    elif not report.read_text(encoding="utf-8").strip():
        _schema_error(errors, _relative(root, report), "candidate-stage-scope", "candidate.md cannot be empty")
    source_registry = candidate_root / "publish" / "sources" / "source-registry.md"
    if source_registry.is_file():
        view.add("sources/source-registry.md", source_registry, "candidate-path")
    elif not allow_published_sources or not (root / "sources" / "source-registry.md").is_file():
        _schema_error(errors, _relative(root, source_registry), "candidate-stage-scope", "candidate source registry is required")
    evidence_root = candidate_root / "evidence"
    evidence_files = _walk_files(evidence_root, errors, _relative(root, evidence_root))
    published_evidence = _walk_files(root / "sources" / "evidence", errors, "sources/evidence")
    if not evidence_files and (not allow_published_sources or not published_evidence):
        _schema_error(errors, _relative(root, evidence_root), "candidate-stage-scope", "candidate evidence is required")
    for path in evidence_files:
        relative = _relative(evidence_root, path)
        view.add(f"sources/evidence/{relative}", path, "candidate-path")
    for path in _walk_files(candidate_root / "publish", errors, _relative(root, candidate_root / "publish")):
        relative = _relative(candidate_root / "publish", path)
        if relative.startswith("sources/evidence/"):
            view.add(relative, path, "candidate-path")
        elif relative.startswith("references/") or relative.startswith("evals/") or relative.startswith("sources/"):
            view.add(relative, path, "candidate-path")
        else:
            _schema_error(errors, _relative(root, path), "candidate-stage-scope", "publish content is outside formal target roots")
    return view


def _effective_candidate_view(root: Path, candidate_view: ContentView, errors: list[ValidationError]) -> ContentView:
    """Project a candidate onto the currently published formal tree."""
    effective = _published_view(root, errors)
    effective.files.update(candidate_view.files)
    return effective


def _validate_approval(root: Path, candidate_id: str, manifest: dict[str, Any], errors: list[ValidationError], *, required: bool) -> None:
    path = root / "updates" / "approvals" / f"{candidate_id}.md"
    logical = _relative(root, path)
    if not path.exists():
        if required:
            _schema_error(errors, logical, "approval-manifest-hash", "approved record is required")
        return
    parsed = _parse_markdown_frontmatter(path, logical, errors, "approval-schema")
    if parsed is None:
        return
    approval, _ = parsed
    if not _validate_exact_fields(approval, APPROVAL_FIELDS, logical, "approval-schema", errors):
        return
    if approval["candidate_id"] != candidate_id:
        _schema_error(errors, logical, "approval-manifest-hash", "candidate_id does not match approval path")
    if approval["manifest_hash"] != manifest.get("manifest_hash"):
        _schema_error(errors, logical, "approval-manifest-hash", "approval does not match manifest hash")
    if approval["decision"] not in {"approved", "rejected"}:
        _schema_error(errors, logical, "approval-schema", "decision must be approved or rejected")
    if not isinstance(approval["approver"], str) or not approval["approver"]:
        _schema_error(errors, logical, "approval-schema", "approver must be non-empty")
    if not _is_rfc3339(approval["approved_at"]):
        _schema_error(errors, logical, "approval-schema", "approved_at must be UTC RFC 3339")
    for field in ("approved_scope", "reason", "limitations"):
        if not isinstance(approval[field], str):
            _schema_error(errors, logical, "approval-schema", f"{field} must be a string")


def _validate_manifest_shape(manifest: Any, logical: str, errors: list[ValidationError]) -> dict[str, Any] | None:
    if not isinstance(manifest, dict) or set(manifest) != {"manifest_version", "candidate_id", "files", "manifest_hash"}:
        _schema_error(errors, logical, "release-manifest", "manifest uses an unsupported schema")
        return None
    if manifest["manifest_version"] != 1 or not isinstance(manifest["candidate_id"], str) or not _is_sha256(manifest["manifest_hash"]):
        _schema_error(errors, logical, "release-manifest", "invalid manifest version, candidate ID, or hash")
        return None
    copy = dict(manifest)
    copy.pop("manifest_hash")
    if sha256_bytes(canonical_json(copy)) != manifest["manifest_hash"]:
        _schema_error(errors, logical, "manifest-hash", "manifest_hash does not match canonical JSON")
    return manifest


def _validate_releases(root: Path, view: ContentView, errors: list[ValidationError]) -> None:
    releases = root / "updates" / "releases"
    release_files = sorted(releases.glob("*/manifest.json")) if releases.exists() else []
    if not release_files:
        _schema_error(errors, "updates/releases", "release-manifest", "at least one release manifest is required")
    released_hashes: dict[str, set[str]] = {}
    for path in release_files:
        logical = _relative(root, path)
        candidate_id = path.parent.name
        try:
            manifest = _read_json(path)
        except (OSError, ValueError, _DuplicateJsonKey) as exc:
            _schema_error(errors, logical, "release-manifest", str(exc))
            continue
        manifest = _validate_manifest_shape(manifest, logical, errors)
        if manifest is None:
            continue
        if manifest["candidate_id"] != candidate_id:
            _schema_error(errors, logical, "release-manifest", "candidate ID must match release directory")
        _validate_approval(root, candidate_id, manifest, errors, required=True)
        files = manifest["files"]
        if not isinstance(files, list):
            _schema_error(errors, logical, "release-manifest", "files must be a list")
            continue
        for entry in files:
            if not isinstance(entry, dict):
                _schema_error(errors, logical, "release-manifest", "invalid file entry")
                continue
            target = entry.get("target_path")
            if target is None:
                continue
            if not _safe_posix_path(target) or not _is_sha256(entry.get("sha256")):
                _schema_error(errors, logical, "release-manifest", "invalid target path or SHA-256")
                continue
            actual = view.get(target)
            if actual is None:
                _schema_error(errors, logical, "release-manifest", f"published target is missing: {target}")
            released_hashes.setdefault(target, set()).add(entry["sha256"])
    # Source registries and indexes are intentionally updated by later
    # candidates.  A formal file must therefore match some release manifest,
    # rather than every historical release that previously owned its path.
    for target, actual in view.files.items():
        if target == "sources/integrity/published-records.sha256" or target.startswith("evals/reports/"):
            continue
        known_hashes = released_hashes.get(target)
        if not known_hashes:
            _schema_error(errors, target, "release-manifest", "formal file is absent from all release manifests")
        elif sha256_file(actual) not in known_hashes:
            _schema_error(errors, target, "release-manifest", "formal file differs from all release manifests")


def _validate_ledger(view: ContentView, records: dict[str, dict[str, Any]], errors: list[ValidationError]) -> None:
    logical = "sources/integrity/published-records.sha256"
    path = view.get(logical)
    if path is None:
        _schema_error(errors, logical, "record-integrity", "integrity ledger is required")
        return
    entries: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        _schema_error(errors, logical, "record-integrity", str(exc))
        return
    for number, line in enumerate(lines, start=1):
        match = re.fullmatch(r"([0-9a-f]{64})  (references/tools/.+/records/.+\.md)", line)
        if not match:
            _schema_error(errors, logical, "record-integrity", f"line {number} must be '<sha256>  <record path>'")
            continue
        digest, record_path = match.groups()
        if record_path in entries:
            _schema_error(errors, logical, "record-integrity", f"duplicate ledger path {record_path}")
        entries[record_path] = digest
    discovered_paths = {record["logical"] for record in records.values()}
    if set(entries) != discovered_paths:
        _schema_error(errors, logical, "record-integrity", "ledger paths must exactly match published records")
    for record_path, digest in entries.items():
        actual = view.get(record_path)
        if actual is None or sha256_file(actual) != digest:
            _schema_error(errors, record_path, "record-integrity", "record bytes differ from integrity ledger")


def _validate_eval_data(view: ContentView, errors: list[ValidationError], *, require_reports: bool) -> None:
    logical = "evals/evals.json"
    path = view.get(logical)
    if path is None:
        _schema_error(errors, logical, "eval-metadata", "evals.json is required")
        return
    try:
        evals = _read_json(path)
    except (OSError, ValueError, _DuplicateJsonKey) as exc:
        _schema_error(errors, logical, "eval-metadata", str(exc))
        return
    if not isinstance(evals, list) or not evals:
        _schema_error(errors, logical, "eval-metadata", "evals.json must be a non-empty array")
        return
    ids: set[str] = set()
    for entry in evals:
        if not isinstance(entry, dict) or set(entry) != EVAL_FIELDS:
            _schema_error(errors, logical, "eval-metadata", "each eval must use the fixed metadata fields")
            continue
        eval_id = entry["id"]
        if not isinstance(eval_id, str):
            _schema_error(errors, logical, "eval-metadata", "eval id must be unique lowercase kebab-case")
            continue
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", eval_id) or eval_id in ids:
            _schema_error(errors, logical, "eval-metadata", "eval id must be unique lowercase kebab-case")
        ids.add(eval_id)
        if not isinstance(entry["prompt"], str) or not entry["prompt"]:
            _schema_error(errors, logical, "eval-metadata", "prompt must be non-empty")
        for field in ("expected_records", "required_answer_fields", "forbidden_claims"):
            if not _is_string_list(entry[field]):
                _schema_error(errors, logical, "eval-metadata", f"{field} must be a unique string list")
        if not isinstance(entry["manual_review"], str) or not entry["manual_review"]:
            _schema_error(errors, logical, "eval-metadata", "manual_review must be non-empty")
    reports = {logical_path: actual for logical_path, actual in view.matching("evals/reports/", ".md")}
    report_ids: set[str] = set()
    for report_logical, report_path in reports.items():
        parsed = _parse_markdown_frontmatter(report_path, report_logical, errors, "eval-report")
        if parsed is None:
            continue
        report, body = parsed
        if not _validate_exact_fields(report, REPORT_FIELDS, report_logical, "eval-report", errors):
            continue
        eval_id = report["eval_id"]
        report_ids.add(eval_id if isinstance(eval_id, str) else "")
        if report_path.stem != eval_id or eval_id not in ids:
            _schema_error(errors, report_logical, "eval-report", "report eval_id must match a metadata ID and file name")
        for field in ("actual_records", "required_fields_present", "forbidden_claims_found"):
            if not _is_string_list(report[field]):
                _schema_error(errors, report_logical, "eval-report", f"{field} must be a unique string list")
        if not isinstance(report["manual_reviewer"], str) or not report["manual_reviewer"]:
            _schema_error(errors, report_logical, "eval-report", "manual_reviewer must be non-empty")
        if not _is_rfc3339(report["manual_reviewed_at"]):
            _schema_error(errors, report_logical, "eval-report", "manual_reviewed_at must be UTC RFC 3339")
        if not isinstance(report["manual_review_passed"], bool):
            _schema_error(errors, report_logical, "eval-report", "manual_review_passed must be boolean")
        if not body.strip():
            _schema_error(errors, report_logical, "eval-report", "report body must contain answer and review rationale")
    if require_reports and report_ids != ids:
        _schema_error(errors, "evals/reports", "eval-report", "every eval requires exactly one report")


def _validate_candidate(root: Path, candidate_id: str, stage: str, errors: list[ValidationError]) -> None:
    if not _safe_posix_path(candidate_id) or "/" in candidate_id:
        _schema_error(errors, "updates/candidates", "candidate-stage-scope", "candidate ID must be one path component")
        return
    candidate_root = root / "updates" / "candidates" / candidate_id
    if not candidate_root.is_dir() or candidate_root.is_symlink():
        _schema_error(errors, _relative(root, candidate_root), "candidate-stage-scope", "candidate directory is required")
        return
    if stage == "complete":
        manifest, candidate_view = _validate_candidate_manifest(root, candidate_id, errors)
        if manifest is None:
            return
        _validate_approval(root, candidate_id, manifest, errors, required=False)
    else:
        candidate_view = _candidate_view_without_manifest(
            root,
            candidate_id,
            errors,
            allow_published_sources=stage == "tool-subtree",
        )
    if stage in {"tool-subtree", "complete"}:
        has_tool_subtree = any(
            "/capabilities/" in logical and "/records/" in logical for logical in candidate_view.files
        )
        if not has_tool_subtree:
            _schema_error(errors, _relative(root, candidate_root), "candidate-stage-scope", "tool-subtree requires a record and capability index")
    view = _effective_candidate_view(root, candidate_view, errors) if stage in {"tool-subtree", "complete"} else candidate_view
    if stage in {"tool-subtree", "complete"}:
        _validate_no_candidate_leaks(view, errors)
    _validate_records_and_indexes(view, errors)
    if stage == "complete":
        _validate_eval_data(view, errors, require_reports=False)


def _published_view(root: Path, errors: list[ValidationError]) -> ContentView:
    view = ContentView(root, "published", errors)
    for top in ("references", "sources", "evals"):
        base = root / top
        for path in _walk_files(base, errors, top):
            view.add(_relative(root, path), path)
    return view


def _validate_no_candidate_leaks(view: ContentView, errors: list[ValidationError]) -> None:
    for logical, path in view.files.items():
        if b"updates/candidates/" in path.read_bytes():
            _schema_error(errors, logical, "candidate-leak", "formal content cannot reference a candidate path")


def _validate_published(root: Path, errors: list[ValidationError], *, require_reports: bool) -> None:
    view = _published_view(root, errors)
    _validate_no_candidate_leaks(view, errors)
    records = _validate_records_and_indexes(view, errors)
    _validate_ledger(view, records, errors)
    _validate_releases(root, view, errors)
    _validate_eval_data(view, errors, require_reports=require_reports)


def validate(root: Path | str, candidate: str | None = None, stage: str | None = None) -> list[ValidationError]:
    """Return all deterministic handbook validation errors for one supported mode."""
    root_path = Path(root)
    errors: list[ValidationError] = []
    if not root_path.is_dir():
        return [ValidationError(str(root_path), "root", "skill root directory does not exist")]
    _check_pending_transactions(root_path, errors)
    if candidate is not None:
        if stage not in {"source-only", "tool-subtree", "complete"}:
            return errors + [ValidationError("<command>", "usage", "candidate requires source-only, tool-subtree, or complete stage")]
        _validate_candidate(root_path, candidate, stage, errors)
    elif stage == "published-pending-reports":
        _validate_published(root_path, errors, require_reports=False)
    elif stage is None:
        _validate_published(root_path, errors, require_reports=True)
    else:
        return errors + [ValidationError("<command>", "usage", "only published-pending-reports is valid without --candidate")]
    return errors


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--candidate")
    parser.add_argument("--stage")
    args = parser.parse_args(argv)
    if args.candidate is not None and args.stage not in {"source-only", "tool-subtree", "complete"}:
        parser.error("--candidate requires --stage source-only, tool-subtree, or complete")
    if args.candidate is None and args.stage not in {None, "published-pending-reports"}:
        parser.error("--stage without --candidate must be published-pending-reports")
    return args


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    errors = validate(args.root, args.candidate, args.stage)
    if errors:
        for error in errors:
            print(error.render(), file=sys.stderr)
        if any(error.rule == "publication-transaction-pending" for error in errors):
            return EXIT_TRANSACTION_PENDING
        return EXIT_VALIDATION
    mode = f"candidate {args.candidate} {args.stage}" if args.candidate else (args.stage or "final published")
    print(f"validated {mode}: {args.root}")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
