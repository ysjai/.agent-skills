#!/usr/bin/env python3
"""Publish an approved handbook candidate with a recoverable local transaction.

Set CODING_AGENT_HANDBOOK_PUBLISH_FAIL_AT to ``fail-after-copy-N`` to exercise
normal rollback, or ``interrupt-after-copy-N`` to leave a recoverable pending
transaction.  The ``publish`` function accepts the same value as an explicit
failure_point argument for unit tests.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path, PurePosixPath
from typing import Any

import validate_handbook


EXIT_OK = 0
EXIT_USAGE = 2
EXIT_VALIDATION = 3
EXIT_TRANSACTION_PENDING = 4
EXIT_PUBLISH_FAILURE = 5


class PublishFailure(RuntimeError):
    pass


class SimulatedInterruption(RuntimeError):
    pass


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _safe_relative(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts)


def _within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _atomic_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(validate_handbook.canonical_json(data) + b"\n")
    os.replace(temporary, path)


def _atomic_copy(source: Path, destination: Path, root: Path) -> None:
    if not _within(destination, root):
        raise PublishFailure(f"destination escapes skill root: {destination}")
    current = root
    for part in destination.relative_to(root).parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise PublishFailure(f"destination contains symbolic link: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".publish-tmp")
    shutil.copyfile(source, temporary)
    os.replace(temporary, destination)


def _pending_transactions(root: Path) -> list[Path]:
    transactions = root / "updates" / "transactions"
    pending: list[Path] = []
    for path in sorted(transactions.glob("*.json")) if transactions.exists() else []:
        try:
            value = validate_handbook.strict_json_loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict) or value.get("state") not in {"completed", "rolled-back", "recovered"}:
                pending.append(path)
        except (OSError, ValueError):
            pending.append(path)
    return pending


def _render_errors(errors: list[validate_handbook.ValidationError]) -> None:
    for error in errors:
        print(error.render(), file=sys.stderr)


def _load_manifest(root: Path, candidate_id: str) -> dict[str, Any]:
    path = root / "updates" / "candidates" / candidate_id / "manifest.json"
    value = validate_handbook.strict_json_loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PublishFailure("manifest is not an object")
    return value


def _load_approval(root: Path, candidate_id: str) -> dict[str, Any]:
    path = root / "updates" / "approvals" / f"{candidate_id}.md"
    try:
        approval, _ = validate_handbook.parse_frontmatter(path)
    except (OSError, validate_handbook.RestrictedYamlError) as exc:
        raise PublishFailure(f"approval cannot be read: {exc}") from exc
    if set(approval) != validate_handbook.APPROVAL_FIELDS:
        raise PublishFailure("approval schema is invalid")
    return approval


def _failure_point(point: str, failure_point: str | None) -> None:
    requested = (
        failure_point
        or os.environ.get("HANDBOOK_PUBLISH_FAILURE_POINT")
        or os.environ.get("CODING_AGENT_HANDBOOK_PUBLISH_FAIL_AT")
    )
    if requested != point:
        return
    if point.startswith("interrupt-"):
        raise SimulatedInterruption(point)
    raise PublishFailure(point)


def _transaction_targets(root: Path, candidate_id: str, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    candidate_root = root / "updates" / "candidates" / candidate_id
    targets: list[dict[str, Any]] = []
    for entry in manifest["files"]:
        target = entry["target_path"]
        if target is None:
            continue
        if not _safe_relative(target) or not _safe_relative(entry["candidate_path"]):
            raise PublishFailure("manifest path is not safe")
        source = candidate_root / PurePosixPath(entry["candidate_path"])
        destination = root / PurePosixPath(target)
        if not source.is_file() or source.is_symlink() or not _within(source, candidate_root):
            raise PublishFailure(f"candidate source is unsafe: {entry['candidate_path']}")
        if destination.exists() and destination.is_symlink():
            raise PublishFailure(f"target is symbolic link: {target}")
        if target.startswith("references/") and "/records/" in target and destination.exists():
            raise PublishFailure(f"immutable record already exists: {target}")
        targets.append(
            {
                "target_path": target,
                "source_path": entry["candidate_path"],
                "had_file": destination.is_file(),
            }
        )
    release_target = f"updates/releases/{candidate_id}/manifest.json"
    targets.append({"target_path": release_target, "source_path": "manifest.json", "had_file": (root / release_target).is_file()})
    targets.append(
        {
            "target_path": "sources/integrity/published-records.sha256",
            "source_path": None,
            "had_file": (root / "sources/integrity/published-records.sha256").is_file(),
        }
    )
    return targets


def _backup_targets(root: Path, transaction_path: Path, transaction: dict[str, Any]) -> None:
    backup_root = transaction_path.with_suffix(".backups")
    backup_root.mkdir(parents=True, exist_ok=True)
    for index, target in enumerate(transaction["targets"]):
        destination = root / PurePosixPath(target["target_path"])
        backup_relative = f"{transaction_path.stem}.backups/{index}"
        target["backup_path"] = f"updates/transactions/{backup_relative}"
        if destination.is_file():
            backup = root / PurePosixPath(target["backup_path"])
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(destination, backup)
            target["had_file"] = True
        else:
            target["had_file"] = False


def _restore(root: Path, transaction: dict[str, Any]) -> None:
    targets = transaction.get("targets")
    if not isinstance(targets, list):
        raise PublishFailure("transaction targets are invalid")
    for target in reversed(targets):
        target_path = target.get("target_path")
        backup_path = target.get("backup_path")
        if not _safe_relative(target_path) or not _safe_relative(backup_path):
            raise PublishFailure("transaction contains unsafe path")
        destination = root / PurePosixPath(target_path)
        backup = root / PurePosixPath(backup_path)
        if target.get("had_file"):
            if not backup.is_file() or backup.is_symlink() or not _within(backup, root):
                raise PublishFailure(f"transaction backup is unavailable: {backup_path}")
            _atomic_copy(backup, destination, root)
        elif destination.exists():
            if destination.is_dir() or destination.is_symlink() or not _within(destination, root):
                raise PublishFailure(f"cannot remove unsafe transaction target: {target_path}")
            destination.unlink()


def _cleanup_transaction(transaction_path: Path) -> None:
    backup_root = transaction_path.with_suffix(".backups")
    if backup_root.exists():
        shutil.rmtree(backup_root)
    if transaction_path.exists():
        transaction_path.unlink()


def _new_ledger(root: Path, manifest: dict[str, Any]) -> bytes:
    ledger = root / "sources" / "integrity" / "published-records.sha256"
    existing = ledger.read_bytes() if ledger.exists() else b""
    if existing and not existing.endswith(b"\n"):
        raise PublishFailure("existing integrity ledger lacks trailing newline")
    seen_paths: set[str] = set()
    additions: list[tuple[str, str]] = []
    for entry in manifest["files"]:
        target = entry["target_path"]
        if isinstance(target, str) and target.startswith("references/") and "/records/" in target:
            if target in seen_paths:
                raise PublishFailure(f"duplicate record ledger target: {target}")
            seen_paths.add(target)
            additions.append((target, entry["sha256"]))
    existing_paths = {
        line.split("  ", 1)[1]
        for line in existing.decode("utf-8").splitlines()
        if "  " in line
    }
    if existing_paths.intersection(seen_paths):
        raise PublishFailure("integrity ledger already lists a candidate record")
    additions.sort()
    return existing + b"".join(f"{digest}  {target}\n".encode("ascii") for target, digest in additions)


def publish(root: Path | str, candidate_id: str, failure_point: str | None = None) -> int:
    """Publish one approved candidate, returning a stable process-style exit code."""
    root_path = Path(root)
    pending = _pending_transactions(root_path)
    if pending:
        _render_errors(
            [
                validate_handbook.ValidationError(
                    _relative(root_path, path), "publication-transaction-pending", "recover this transaction first"
                )
                for path in pending
            ]
        )
        return EXIT_TRANSACTION_PENDING
    validation_errors = validate_handbook.validate(root_path, candidate_id, "complete")
    if validation_errors:
        _render_errors(validation_errors)
        return EXIT_VALIDATION
    try:
        manifest = _load_manifest(root_path, candidate_id)
        approval = _load_approval(root_path, candidate_id)
        if approval["candidate_id"] != candidate_id or approval["decision"] != "approved":
            raise PublishFailure("approval is not an approval for this candidate")
        if approval["manifest_hash"] != manifest["manifest_hash"]:
            raise PublishFailure("approval manifest hash does not match")
        transaction_path = root_path / "updates" / "transactions" / f"{candidate_id}.json"
        transaction = {
            "transaction_version": 1,
            "candidate_id": candidate_id,
            "manifest_hash": manifest["manifest_hash"],
            "state": "prepared",
            "targets": _transaction_targets(root_path, candidate_id, manifest),
        }
        _backup_targets(root_path, transaction_path, transaction)
        _atomic_json(transaction_path, transaction)
        _failure_point("fail-after-transaction", failure_point)
        _failure_point("interrupt-after-transaction", failure_point)
        transaction["state"] = "writing"
        _atomic_json(transaction_path, transaction)
        candidate_root = root_path / "updates" / "candidates" / candidate_id
        copied = 0
        for target in transaction["targets"]:
            if target["source_path"] is None:
                continue
            source = candidate_root / PurePosixPath(target["source_path"])
            if target["source_path"] == "manifest.json":
                source = candidate_root / "manifest.json"
            _atomic_copy(source, root_path / PurePosixPath(target["target_path"]), root_path)
            copied += 1
            _failure_point(f"fail-after-copy-{copied}", failure_point)
            _failure_point(f"interrupt-after-copy-{copied}", failure_point)
        _failure_point("fail-before-ledger", failure_point)
        _failure_point("interrupt-before-ledger", failure_point)
        ledger_target = root_path / "sources" / "integrity" / "published-records.sha256"
        ledger_target.parent.mkdir(parents=True, exist_ok=True)
        temporary = ledger_target.with_name(ledger_target.name + ".publish-tmp")
        temporary.write_bytes(_new_ledger(root_path, manifest))
        os.replace(temporary, ledger_target)
        transaction["state"] = "completed"
        _atomic_json(transaction_path, transaction)
        _cleanup_transaction(transaction_path)
        print(f"published candidate {candidate_id}")
        return EXIT_OK
    except SimulatedInterruption as exc:
        # A process loss cannot roll back.  The durable transaction makes the
        # interrupted state visible to every validator and later publisher.
        transaction_path = root_path / "updates" / "transactions" / f"{candidate_id}.json"
        if transaction_path.exists():
            transaction = validate_handbook.strict_json_loads(transaction_path.read_text(encoding="utf-8"))
            transaction["state"] = "interrupted"
            _atomic_json(transaction_path, transaction)
        print(f"updates/transactions/{candidate_id}.json: publication-interrupted: {exc}", file=sys.stderr)
        return EXIT_PUBLISH_FAILURE
    except (OSError, ValueError, PublishFailure) as exc:
        transaction_path = root_path / "updates" / "transactions" / f"{candidate_id}.json"
        try:
            if transaction_path.exists():
                transaction = validate_handbook.strict_json_loads(transaction_path.read_text(encoding="utf-8"))
                _restore(root_path, transaction)
                transaction["state"] = "rolled-back"
                _atomic_json(transaction_path, transaction)
                _cleanup_transaction(transaction_path)
        except (OSError, ValueError, PublishFailure) as rollback_exc:
            print(
                f"updates/transactions/{candidate_id}.json: publication-transaction-pending: rollback failed: {rollback_exc}",
                file=sys.stderr,
            )
            return EXIT_TRANSACTION_PENDING
        print(f"updates/candidates/{candidate_id}: publication-failed: {exc}", file=sys.stderr)
        return EXIT_PUBLISH_FAILURE


def recover(root: Path | str, candidate_id: str) -> int:
    root_path = Path(root)
    transaction_path = root_path / "updates" / "transactions" / f"{candidate_id}.json"
    if not transaction_path.exists():
        print(f"updates/transactions/{candidate_id}.json: publication-transaction-missing: no transaction to recover", file=sys.stderr)
        return EXIT_VALIDATION
    try:
        transaction = validate_handbook.strict_json_loads(transaction_path.read_text(encoding="utf-8"))
        if not isinstance(transaction, dict) or transaction.get("candidate_id") != candidate_id:
            raise PublishFailure("transaction candidate ID is invalid")
        _restore(root_path, transaction)
        transaction["state"] = "recovered"
        _atomic_json(transaction_path, transaction)
        _cleanup_transaction(transaction_path)
    except (OSError, ValueError, PublishFailure) as exc:
        print(f"updates/transactions/{candidate_id}.json: publication-recovery: {exc}", file=sys.stderr)
        return EXIT_TRANSACTION_PENDING
    print(f"recovered candidate {candidate_id}")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--candidate")
    group.add_argument("--recover")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    if args.candidate:
        return publish(args.root, args.candidate)
    return recover(args.root, args.recover)


if __name__ == "__main__":
    raise SystemExit(main())
