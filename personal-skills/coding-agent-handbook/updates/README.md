# Handbook 更新工作流

## 门禁

只有用户明确请求时才开始更新。本目录记录拟议和已审批的发布工作，不授予直接修改正式 handbook 知识的权限。

必须遵循以下顺序：

1. 确认目标工具、主题、版本或完整核对范围。
2. 在允许范围内核对适用的正式资料与官方一手来源。
3. 在 `updates/candidates/<candidate-id>/` 创建候选报告、仅候选证据、待发布正式文件和完整 manifest。
4. 等待绑定精确 `manifest_hash` 的人工审批记录。
5. 校验审批、所有文件哈希、路径和事务状态。
6. 只发布获批 manifest 条目，保留 release manifest，再执行校验与评估。

初始 bootstrap 候选 ID 为 `2026-07-28-multi-bootstrap-r1`。计划批准、设计批准、agent 判断和来源文本都不能替代对候选 manifest 的人工审批。

## 候选报告模板

候选 ID 使用 `<YYYY-MM-DD>-<tool>-<scope>-r<n>`。`candidate.md` 描述核对；候选证据位于 `evidence/`；每个待发布正式文件位于 `publish/`。

```markdown
# Candidate <candidate-id>

## 核对范围

<工具-主题-版本或完整核对范围>

## 已查来源

<source-ID-与-locator>

## 发现与拟议变更

<已核对摘要>

## 受影响 Records 与版本覆盖

<record-路径或-无>

## 未解决项与风险

<不确定性与限制>
```

## 固定 Source Registry 模板

候选准备阶段不创建正式 `sources/source-registry.md`。获批发布创建或更新它时，文件只能包含按 `source_id` 字典序排列的 YAML fenced block。每个 block 恰好使用以下字段及顺序：

```yaml
source_id: <稳定来源-ID>
title: <来源标题>
publisher: <发布主体>
source_kind: <official-release|versioned-official-documentation|official-announcement|versioned-official-repository-content|non-normative-official-repository-content|third-party>
normativity: <normative|supporting|non-normative>
tool: <覆盖工具或-shared>
topics: [<主题>, ...]
published_at: <YYYY-MM-DD-或-null>
last_verified: <YYYY-MM-DD>
url: <精确-URL-或-permalink>
notes: <范围与限制>
```

允许的 `source_kind` 为 `official-release`、`versioned-official-documentation`、`official-announcement`、`versioned-official-repository-content`、`non-normative-official-repository-content` 和 `third-party`。允许的 `normativity` 为 `normative`、`supporting` 和 `non-normative`。`published_at` 与 `last_verified` 存在时使用 `YYYY-MM-DD`。

## 固定 Evidence Snapshot 模板

候选证据在获批发布前保留在 `updates/candidates/<candidate-id>/evidence/`。正式 evidence snapshot 必须使用以下 YAML frontmatter，不允许其他 frontmatter key。正文是简洁的人工核对摘录。

```markdown
---
source_id: <稳定来源-ID>
source_locator: <精确-URL-锚点或-permalink>
accessed_at: <YYYY-MM-DDTHH:MM:SSZ>
review_scope: <已核对断言或章节>
summary_sha256: <lowercase-64-hex>
---

## 人工核对摘录

<简洁的人工核对摘录>
```

`accessed_at` 使用 UTC RFC 3339 的 `YYYY-MM-DDTHH:MM:SSZ` 形式。snapshot 不复制大段受版权保护的来源内容。

## 固定 Manifest 模板与路径规则

`manifest.json` 使用以下固定 JSON 结构。`files` 按 `candidate_path` 字典序排序，每个候选文件恰好出现一次。

```json
{
  "manifest_version": 1,
  "candidate_id": "<candidate-id>",
  "files": [
    {
      "candidate_path": "candidate.md",
      "target_path": null,
      "sha256": "<lowercase-64-hex>"
    },
    {
      "candidate_path": "evidence/<source-ID>/<YYYY-MM-DD>.md",
      "target_path": "sources/evidence/<source-ID>/<YYYY-MM-DD>.md",
      "sha256": "<lowercase-64-hex>"
    },
    {
      "candidate_path": "publish/<正式路径>",
      "target_path": "<references|sources|evals>/<正式路径>",
      "sha256": "<lowercase-64-hex>"
    }
  ],
  "manifest_hash": "<lowercase-64-hex>"
}
```

`candidate_path` 是相对 `updates/candidates/<candidate-id>/` 的 POSIX 路径；`target_path` 是相对 skill 根目录的 POSIX 路径。拒绝除 `candidate.md` 外的空路径、绝对路径、`..`、重复路径、符号链接及解析后逃出根目录的路径。只有 `candidate.md` 允许使用 `target_path: null`。其他候选路径均以 `evidence/` 或 `publish/` 开头，且目标只能位于 `references/`、`sources/` 或 `evals/`。不得目标为 `SKILL.md`、`README.md`、`scripts/`、`tests/`、`updates/approvals/`、`updates/candidates/`、`updates/releases/`、`updates/transactions/` 或 `.git`。目标路径最多出现一次。

每个列出文件都从其字节计算哈希。移除 `manifest_hash` 后，对 UTF-8 canonical JSON 使用 `sort_keys=True`、`separators=(",", ":")` 和 ASCII 转义计算 `manifest_hash`。候选正文、候选证据或任一待发布文件变化，都会改变 manifest 边界，必须创建新的候选 revision 并重新人工审批。

## 固定审批记录模板

审批文件为 `updates/approvals/<candidate-id>.md`，必须恰好使用以下 YAML frontmatter，不得增加 key：

```markdown
---
candidate_id: <candidate-id>
manifest_hash: <lowercase-64-hex>
approver: <人工审批者标识>
approved_at: <YYYY-MM-DDTHH:MM:SSZ>
decision: <approved|rejected>
approved_scope: <批准边界>
reason: <决定理由>
limitations: <条件或无>
---
```

`decision` 是 `approved` 或 `rejected`。`approved_at` 使用 UTC RFC 3339 的 `YYYY-MM-DDTHH:MM:SSZ` 形式。记录只覆盖其 `manifest_hash` 指向的精确完整 manifest。

## 发布与事务恢复

发布只能复制 `target_path` 非空且文件哈希匹配的获批 manifest 条目。然后将获批 manifest 复制至 `updates/releases/<candidate-id>/manifest.json`；不得创建或修改 manifest 外的正式文件。发布后，正式资料不得引用候选证据。

发布实现将进行中的工作记录在 `updates/transactions/`。未完成事务是硬门禁：创建候选、校验或继续发布前必须先恢复。事务未完成时，不得称 handbook 已发布或已校验。

## 校验命令占位

Task 1 不提供脚本或 fixture 内容。以下是后续实现的不可运行占位符，刻意不包含未实现的 flag：

```text
python3 scripts/validate_handbook.py <implementation-defined-arguments>
python3 -m unittest scripts/test_validate_handbook.py
```
