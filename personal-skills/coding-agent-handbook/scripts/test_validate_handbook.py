"""Fixture coverage for handbook validation and controlled candidate publishing."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import publish_candidate
import validate_handbook


FIXTURES = SCRIPTS.parent / "tests" / "fixtures"
VALID_FIXTURE = FIXTURES / "valid-minimal"
VALIDATE = SCRIPTS / "validate_handbook.py"
PUBLISH = SCRIPTS / "publish_candidate.py"
RECORD = "references/tools/codex/capabilities/demo/records/codex-demo-2026-07-28-r1.md"


class HandbookFixtureTests(unittest.TestCase):
    maxDiff = None

    def _copy_valid_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name) / "handbook"
        shutil.copytree(VALID_FIXTURE, root)
        return temporary, root

    def _run(self, script: Path, root: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(script), "--root", str(root), *args]
        command_env = os.environ.copy()
        if env:
            command_env.update(env)
        return subprocess.run(command, capture_output=True, encoding="utf-8", env=command_env, check=False)

    def _initial_publish_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary, root = self._copy_valid_fixture()
        for relative in ("references", "sources", "evals", "updates/releases", "updates/transactions"):
            path = root / relative
            if path.exists():
                shutil.rmtree(path)
        return temporary, root

    def _sync_release_manifest(self, root: Path) -> None:
        manifest_path = root / "updates" / "releases" / "fixture-r1" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in manifest["files"]:
            target = entry["target_path"]
            if target is not None:
                entry["sha256"] = validate_handbook.sha256_file(root / target)
        unsigned = dict(manifest)
        unsigned.pop("manifest_hash")
        manifest["manifest_hash"] = validate_handbook.sha256_bytes(validate_handbook.canonical_json(unsigned))
        manifest_path.write_bytes(validate_handbook.canonical_json(manifest) + b"\n")

        approval_path = root / "updates" / "approvals" / "fixture-r1.md"
        approval = approval_path.read_text(encoding="utf-8")
        approval = re.sub(
            r"^manifest_hash: .*?$",
            f"manifest_hash: {manifest['manifest_hash']}",
            approval,
            flags=re.MULTILINE,
        )
        approval_path.write_text(approval, encoding="utf-8")

    def _set_ledger_digest(self, root: Path) -> None:
        digest = validate_handbook.sha256_file(root / RECORD)
        (root / "sources" / "integrity" / "published-records.sha256").write_text(
            f"{digest}  {RECORD}\n", encoding="utf-8"
        )

    def _write_candidate(self, root: Path, candidate_id: str, files: dict[str, tuple[str | None, str]]) -> dict[str, object]:
        candidate_root = root / "updates" / "candidates" / candidate_id
        for candidate_path, (_, content) in files.items():
            path = candidate_root / candidate_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        manifest = {
            "manifest_version": 1,
            "candidate_id": candidate_id,
            "files": [
                {
                    "candidate_path": candidate_path,
                    "target_path": files[candidate_path][0],
                    "sha256": validate_handbook.sha256_file(candidate_root / candidate_path),
                }
                for candidate_path in sorted(files)
            ],
        }
        manifest["manifest_hash"] = validate_handbook.sha256_bytes(
            validate_handbook.canonical_json(manifest)
        )
        (candidate_root / "manifest.json").write_bytes(validate_handbook.canonical_json(manifest) + b"\n")
        return manifest

    def _write_approval(self, root: Path, candidate_id: str, manifest_hash: str) -> None:
        approval = root / "updates" / "approvals" / f"{candidate_id}.md"
        approval.parent.mkdir(parents=True, exist_ok=True)
        approval.write_text(
            "---\n"
            f"candidate_id: {candidate_id}\n"
            f"manifest_hash: {manifest_hash}\n"
            "approver: fixture-approver\n"
            "approved_at: 2026-07-29T00:00:00Z\n"
            "decision: approved\n"
            "approved_scope: Fixture correction candidate.\n"
            "reason: Fixture correction approval.\n"
            "limitations: Fictional test data only.\n"
            "---\n"
            "Fixture correction approval record.\n",
            encoding="utf-8",
        )

    def _write_codex_correction_candidate(self, root: Path) -> tuple[str, dict[str, object], str]:
        candidate_id = "fixture-r2"
        record_id = "codex-demo-2026-07-29-r2"
        record_target = f"references/tools/codex/capabilities/demo/records/{record_id}.md"
        evidence_hash = validate_handbook.sha256_file(root / "sources" / "evidence" / "SRC-FIXTURE-001" / "2026-07-28.md")
        record = (
            "---\n"
            f"record_id: {record_id}\n"
            "tool: codex\n"
            "topic: demo\n"
            "content_type: reference\n"
            "learning_level: personal\n"
            "evidence_class: official-fact\n"
            "publication_status: published\n"
            "applicability:\n"
            "  release_channel: stable\n"
            "  product_form: cli\n"
            "  platforms: [linux]\n"
            "  deployment: local\n"
            "  verified_versions: [fixture-v1]\n"
            "support_status: officially-supported\n"
            f"support_evidence: FACT-{record_id}-01\n"
            "last_verified: 2026-07-29\n"
            "---\n"
            f"> **FACT-{record_id}-01**\n"
            "> - 断言：Fixture behavior remains available.\n"
            "> - 适用范围（JSON）：`{\"deployment\":\"local\",\"platforms\":[\"linux\"],\"product_form\":\"cli\",\"release_channel\":\"stable\",\"verified_versions\":[\"fixture-v1\"]}`\n"
            "> - 最后核对：2026-07-29\n"
            "> - 证据：`SRC-FIXTURE-001`，https://example.invalid/docs/fixture-v1#demo\n"
            f"> - 证据快照：`sources/evidence/SRC-FIXTURE-001/2026-07-28.md`，SHA-256 `{evidence_hash}`\n"
        )
        index = (
            "```yaml\n"
            "capability_id: codex.demo\n"
            "applicability:\n"
            "  release_channel: stable\n"
            "  product_form: cli\n"
            "  platforms: [linux]\n"
            "  deployment: local\n"
            "  verified_versions: [fixture-v1]\n"
            "capability_status: officially-supported\n"
            f"record_ids: [codex-demo-2026-07-28-r1, {record_id}]\n"
            f"status_evidence: [FACT-{record_id}-01]\n"
            "lifecycle:\n"
            f"  codex-demo-2026-07-28-r1: {{status: superseded, superseded_by: {record_id}}}\n"
            f"  {record_id}: {{status: current, superseded_by: null}}\n"
            "```\n"
        )
        manifest = self._write_candidate(
            root,
            candidate_id,
            {
                "candidate.md": (None, "# Fixture correction\n\nSupersede the fixture record without rewriting it.\n"),
                "publish/references/tools/codex/capabilities/demo/index.md": (
                    "references/tools/codex/capabilities/demo/index.md",
                    index,
                ),
                f"publish/{record_target}": (record_target, record),
            },
        )
        return candidate_id, manifest, record_target

    def _write_unconfirmed_qoder_candidate(self, root: Path) -> str:
        candidate_id = "fixture-qoder-r1"
        record_id = "qoder-demo-2026-07-29-r1"
        record_target = f"references/tools/qoder/capabilities/demo/records/{record_id}.md"
        evidence_hash = validate_handbook.sha256_file(root / "sources" / "evidence" / "SRC-FIXTURE-001" / "2026-07-28.md")
        scope_json = (
            '{"deployment":"unspecified","platforms":"unspecified","product_form":"unspecified",'
            '"release_channel":"unspecified","verified_versions":["unversioned-docs-2026-07-29"]}'
        )
        record = (
            "---\n"
            f"record_id: {record_id}\n"
            "tool: qoder\n"
            "topic: demo\n"
            "content_type: reference\n"
            "learning_level: personal\n"
            "evidence_class: official-fact\n"
            "publication_status: published\n"
            "applicability:\n"
            "  release_channel: unspecified\n"
            "  product_form: unspecified\n"
            "  platforms: unspecified\n"
            "  deployment: unspecified\n"
            "  verified_versions: [unversioned-docs-2026-07-29]\n"
            "support_status: support-not-publicly-confirmed\n"
            "support_evidence: null\n"
            "last_verified: 2026-07-29\n"
            "---\n"
            f"> **FACT-{record_id}-01**\n"
            "> - 断言：Fixture documentation describes a Qoder behavior.\n"
            f"> - 适用范围（JSON）：`{scope_json}`\n"
            "> - 最后核对：2026-07-29\n"
            "> - 证据：`SRC-FIXTURE-001`，https://example.invalid/docs/fixture-v1#demo\n"
            f"> - 证据快照：`sources/evidence/SRC-FIXTURE-001/2026-07-28.md`，SHA-256 `{evidence_hash}`\n"
        )
        index = (
            "```yaml\n"
            "capability_id: qoder.demo\n"
            "applicability:\n"
            "  release_channel: unspecified\n"
            "  product_form: unspecified\n"
            "  platforms: unspecified\n"
            "  deployment: unspecified\n"
            "  verified_versions: [unversioned-docs-2026-07-29]\n"
            "capability_status: unverified\n"
            f"record_ids: [{record_id}]\n"
            "status_evidence: []\n"
            "lifecycle:\n"
            f"  {record_id}: {{status: current, superseded_by: null}}\n"
            "```\n"
        )
        self._write_candidate(
            root,
            candidate_id,
            {
                "candidate.md": (None, "# Fixture Qoder document snapshot\n\nNo product support status is asserted.\n"),
                "publish/references/tools/qoder/capabilities/demo/index.md": (
                    "references/tools/qoder/capabilities/demo/index.md",
                    index,
                ),
                f"publish/{record_target}": (record_target, record),
            },
        )
        return candidate_id

    def _apply_invalid_mutation(self, root: Path, mutation: str) -> None:
        record = root / RECORD
        if mutation == "ledger-digest":
            (root / "sources" / "integrity" / "published-records.sha256").write_text(
                f"{'0' * 64}  {RECORD}\n", encoding="utf-8"
            )
        elif mutation == "fact-snapshot-hash":
            text = record.read_text(encoding="utf-8")
            record.write_text(re.sub(r"SHA-256 `[0-9a-f]{64}`", f"SHA-256 `{'0' * 64}`", text), encoding="utf-8")
            self._set_ledger_digest(root)
            self._sync_release_manifest(root)
        elif mutation == "overlapping-opposite-status":
            index = root / "references" / "tools" / "codex" / "capabilities" / "demo" / "index.md"
            index.write_text(
                index.read_text(encoding="utf-8")
                + "\n```yaml\n"
                "capability_id: codex.demo\n"
                "applicability:\n"
                "  release_channel: stable\n"
                "  product_form: cli\n"
                "  platforms: [linux]\n"
                "  deployment: local\n"
                "  verified_versions: [fixture-v1]\n"
                "capability_status: officially-not-supported\n"
                "record_ids: [codex-demo-2026-07-28-r1]\n"
                "status_evidence: [FACT-codex-demo-2026-07-28-r1-01]\n"
                "lifecycle:\n"
                "  codex-demo-2026-07-28-r1: {status: current, superseded_by: null}\n"
                "```\n",
                encoding="utf-8",
            )
            self._sync_release_manifest(root)
        elif mutation == "lab-missing-network-safety":
            text = record.read_text(encoding="utf-8").replace("content_type: reference", "content_type: lab")
            record.write_text(
                text
                + "\n## 目标\n验证 fixture。\n"
                "## 已实测适用范围与前置条件\n版本 fixture-v1，平台 linux。\n"
                "## 隔离环境、权限与网络要求\n隔离环境、权限限制、真实凭证与生产环境均不可用。\n"
                "## 官方机制\n仅使用虚构 fixture。\n"
                "## 最小示例\n执行本地验证。\n"
                "## 练习任务\n检查输出。\n"
                "## 预期可观察结果与验收方式\n通过验收。\n"
                "## 清理与恢复\n完成清理和恢复。\n"
                "## 常见失败与排查\n检查哈希。\n"
                "## 推荐实践与适用边界\n仅限 fixture。\n"
                "## 来源与最后确认日期\nFixture source，2026-07-28。\n",
                encoding="utf-8",
            )
            self._set_ledger_digest(root)
            self._sync_release_manifest(root)
        elif mutation == "formal-candidate-reference":
            update_log = root / "sources" / "update-log.md"
            update_log.write_text("Fixture update log: updates/candidates/fixture-r1.\n", encoding="utf-8")
            self._sync_release_manifest(root)
        elif mutation == "approval-hash":
            approval = root / "updates" / "approvals" / "fixture-r1.md"
            approval.write_text(
                re.sub(r"^manifest_hash: .*?$", f"manifest_hash: {'0' * 64}", approval.read_text(encoding="utf-8"), flags=re.MULTILINE),
                encoding="utf-8",
            )
        elif mutation == "report-boolean":
            report = root / "evals" / "reports" / "fixture-eval.md"
            report.write_text(
                report.read_text(encoding="utf-8").replace("manual_review_passed: true", "manual_review_passed: invalid"),
                encoding="utf-8",
            )
        elif mutation == "pending-transaction":
            transaction = root / "updates" / "transactions" / "fixture-r1.json"
            transaction.parent.mkdir(parents=True, exist_ok=True)
            transaction.write_text('{"candidate_id":"fixture-r1","state":"writing"}\n', encoding="utf-8")
        else:
            self.fail(f"unknown fixture mutation: {mutation}")

    def test_valid_fixture_supports_all_five_cli_modes(self) -> None:
        cases = (
            (),
            ("--stage", "published-pending-reports"),
            ("--candidate", "fixture-r1", "--stage", "tool-subtree"),
            ("--candidate", "fixture-r1", "--stage", "complete"),
            ("--candidate", "fixture-source-only", "--stage", "source-only"),
        )
        for args in cases:
            with self.subTest(args=args):
                result = self._run(VALIDATE, VALID_FIXTURE, *args)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_unversioned_document_snapshot_allows_unconfirmed_scope_only(self) -> None:
        scope = {
            "release_channel": "unspecified",
            "product_form": "unspecified",
            "platforms": "unspecified",
            "deployment": "unspecified",
            "verified_versions": ["unversioned-docs-2026-07-29"],
        }
        unconfirmed_errors: list[validate_handbook.ValidationError] = []
        validate_handbook._validate_applicability(
            scope,
            "fixture",
            "applicability",
            unconfirmed_errors,
            status="support-not-publicly-confirmed",
        )
        self.assertEqual(unconfirmed_errors, [])

        supported_errors: list[validate_handbook.ValidationError] = []
        validate_handbook._validate_applicability(
            scope,
            "fixture",
            "applicability",
            supported_errors,
            status="officially-supported",
        )
        self.assertEqual([error.rule for error in supported_errors], ["applicability-unspecified"])

    def test_unconfirmed_qoder_fact_scope_allows_unspecified_fields(self) -> None:
        temporary, root = self._copy_valid_fixture()
        with temporary:
            candidate_id = self._write_unconfirmed_qoder_candidate(root)
            result = self._run(VALIDATE, root, "--candidate", candidate_id, "--stage", "complete")
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_correction_candidate_overlays_published_records_and_publishes_r2(self) -> None:
        temporary, root = self._copy_valid_fixture()
        with temporary:
            original_record = (root / RECORD).read_bytes()
            candidate_id, manifest, record_target = self._write_codex_correction_candidate(root)
            for stage in ("tool-subtree", "complete"):
                result = self._run(VALIDATE, root, "--candidate", candidate_id, "--stage", stage)
                self.assertEqual(result.returncode, 0, result.stderr)

            self._write_approval(root, candidate_id, str(manifest["manifest_hash"]))
            result = self._run(PUBLISH, root, "--candidate", candidate_id)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((root / RECORD).read_bytes(), original_record)
            self.assertTrue((root / record_target).is_file())

            ledger = (root / "sources" / "integrity" / "published-records.sha256").read_text(encoding="utf-8")
            self.assertIn(RECORD, ledger)
            self.assertIn(record_target, ledger)
            result = self._run(VALIDATE, root, "--stage", "published-pending-reports")
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_each_invalid_fixture_breaks_only_its_declared_rule(self) -> None:
        scenarios = sorted(FIXTURES.glob("invalid-*/scenario.json"))
        self.assertEqual(len(scenarios), 8)
        for scenario_path in scenarios:
            scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
            with self.subTest(fixture=scenario_path.parent.name):
                temporary, root = self._copy_valid_fixture()
                with temporary:
                    self._apply_invalid_mutation(root, scenario["mutation"])
                    result = self._run(VALIDATE, root)
                    self.assertNotEqual(result.returncode, 0)
                    rules = [line.split(": ", 2)[1] for line in result.stderr.splitlines() if line.count(": ") >= 2]
                    self.assertEqual(rules, [scenario["rule"]], result.stderr)

    def test_publish_refuses_unapproved_or_mismatched_approval_without_writes(self) -> None:
        temporary, root = self._initial_publish_root()
        with temporary:
            record = root / RECORD
            release = root / "updates" / "releases" / "fixture-r1" / "manifest.json"
            approval = root / "updates" / "approvals" / "fixture-r1.md"
            approval.unlink()
            result = self._run(PUBLISH, root, "--candidate", "fixture-r1")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(record.exists())
            self.assertFalse(release.exists())
            self.assertFalse((root / "sources" / "integrity" / "published-records.sha256").exists())

            shutil.copyfile(VALID_FIXTURE / "updates" / "approvals" / "fixture-r1.md", approval)
            approval.write_text(
                re.sub(r"^manifest_hash: .*?$", f"manifest_hash: {'0' * 64}", approval.read_text(encoding="utf-8"), flags=re.MULTILINE),
                encoding="utf-8",
            )
            result = self._run(PUBLISH, root, "--candidate", "fixture-r1")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("approval-manifest-hash", result.stderr)
            self.assertFalse(record.exists())
            self.assertFalse(release.exists())

    def test_approved_publish_reaches_pending_reports(self) -> None:
        temporary, root = self._initial_publish_root()
        with temporary:
            result = self._run(PUBLISH, root, "--candidate", "fixture-r1")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root / RECORD).is_file())
            self.assertTrue((root / "sources" / "integrity" / "published-records.sha256").is_file())
            self.assertTrue((root / "updates" / "releases" / "fixture-r1" / "manifest.json").is_file())
            result = self._run(VALIDATE, root, "--stage", "published-pending-reports")
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_interrupted_publish_blocks_operations_until_recovered(self) -> None:
        temporary, root = self._initial_publish_root()
        with temporary:
            result = self._run(
                PUBLISH,
                root,
                "--candidate",
                "fixture-r1",
                env={"HANDBOOK_PUBLISH_FAILURE_POINT": "interrupt-after-copy-1"},
            )
            self.assertNotEqual(result.returncode, 0)
            transaction = root / "updates" / "transactions" / "fixture-r1.json"
            self.assertTrue(transaction.is_file())
            self.assertEqual(json.loads(transaction.read_text(encoding="utf-8"))["state"], "interrupted")

            result = self._run(VALIDATE, root)
            self.assertEqual(result.returncode, validate_handbook.EXIT_TRANSACTION_PENDING)
            self.assertIn("publication-transaction-pending", result.stderr)
            result = self._run(PUBLISH, root, "--candidate", "fixture-r1")
            self.assertEqual(result.returncode, publish_candidate.EXIT_TRANSACTION_PENDING)
            self.assertIn("publication-transaction-pending", result.stderr)

            result = self._run(PUBLISH, root, "--recover", "fixture-r1")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(transaction.exists())
            self.assertFalse(transaction.with_suffix(".backups").exists())
            self.assertFalse((root / RECORD).exists())
            self.assertFalse((root / "sources" / "evidence" / "SRC-FIXTURE-001" / "2026-07-28.md").exists())


if __name__ == "__main__":
    unittest.main()
