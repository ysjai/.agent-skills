# Coding Agent Handbook

## 加载与范围

用户在当前宿主安装或以其他方式加载 `personal-skills/coding-agent-handbook/SKILL.md` 后，才能使用本 skill。本地目录与 frontmatter 名称只用于统一手动安装和定位，不声明 Codex、Qoder 或其他宿主会自动发现此 skill。

Task 1 只建立维护结构，不发布 Codex 或 Qoder 的行为、版本覆盖、record、source registry 条目、evidence snapshot、完整性清单或候选内容。在存在获批资料之前，handbook 不能确认产品行为。

## 目录职责

| 路径 | 职责 |
| --- | --- |
| `SKILL.md` | 加载范围、问题路由、回答边界与人工更新门禁。 |
| `references/handbook-index.md` | 未来路由至版本 index、能力 index、record 和 shared 资料的主题入口。 |
| `references/shared/` | 个人、团队、组织以及证据/版本的共享写作框架。 |
| `references/tools/` | 未来工具总览、version-index、capability-index 和不可变 record 的位置；本任务不在此创建产品资料。 |
| `sources/` | 未来正式 source registry、evidence snapshot、完整性清单和 update log；未经获批发布不得创建。 |
| `updates/` | 候选、审批、发布与事务生命周期。参见 `updates/README.md`。 |
| `scripts/` 和 `tests/fixtures/` | 预留给后续校验、发布与 fixture 工作；本任务不创建可执行或 fixture 内容。 |
| `evals/reports/` | 预留给后续人工复核的回答评估报告。 |

## 证据等级

未来 record 必须且只能使用以下一种内容分类。等级描述内容的证据边界，不能替代产品事实块。

| 证据等级 | 必须的写作边界 |
| --- | --- |
| `official-fact` | 每个事实块只写一个可直接核对的断言，带兼容的适用范围、source ID、精确 locator、evidence snapshot、snapshot 哈希和最后核对日期。 |
| `established-practice` | 写明适用条件、收益、代价以及实践证据或可复现范围。 |
| `local-practice` | 明确组织或仓库适用范围。MVP 不预先创建此类内容。 |
| `experimental-guidance` | 写明验证范围与风险；不是默认推荐，也不是供应商事实。 |

## 人工更新门禁

1. 用户明确发起更新，并说明目标工具、主题、版本或核对范围。
2. 正式资料存在时，维护者查阅既有 version index、能力条目、source registry 和更新历史。
3. 拟议产品行为只可由官方一手资料支撑；第三方资料最多记为延伸阅读候选。
4. 在 `updates/candidates/<candidate-id>/` 创建 `candidate.md`、仅候选使用的 `evidence/`、`publish/` 下的待发布正式文件和 `manifest.json`。此阶段不得修改正式路径。
5. 人工核对完整 manifest 边界并写入匹配的审批记录。
6. 发布前校验审批哈希、每个列出文件的哈希、候选路径与目标路径规则，以及事务状态。
7. 只发布获批 manifest 条目，保留 release manifest，再运行后续实现定义的校验与评估步骤。

审批只覆盖精确且完整的 manifest。候选正文、证据或 `publish/` 文件的变更会使审批失效，必须创建新的候选 revision。计划批准、设计批准和 agent 判断都不是发布审批。

## 固定来源与证据模板

正式 `sources/source-registry.md` 只能由获批发布创建。它存在时，只能包含按 `source_id` 字典序排列的 YAML fenced block。每个 block 使用以下固定字段顺序，且不得增加字段：

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

`source_kind` 只能取 `official-release`、`versioned-official-documentation`、`official-announcement`、`versioned-official-repository-content`、`non-normative-official-repository-content` 或 `third-party`。`normativity` 只能取 `normative`、`supporting` 或 `non-normative`。`published_at` 与 `last_verified` 存在时使用 `YYYY-MM-DD`。

evidence snapshot 必须使用以下 YAML frontmatter。`accessed_at` 使用 UTC RFC 3339 时间戳 `YYYY-MM-DDTHH:MM:SSZ`。正文只包含人工核对摘录，不复制大段来源内容。

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

## 候选、Manifest 与审批模板

候选 ID 使用 `<YYYY-MM-DD>-<tool>-<scope>-r<n>`。后续任务执行初始 bootstrap 时，固定候选 ID 为 `2026-07-28-multi-bootstrap-r1`。

`candidate.md` 是核对报告，必须标明核对范围、已查来源、发现、受影响 records、版本变化、未解决项和风险。候选证据位于 `evidence/`；所有待发布正式文件位于 `publish/`。

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

`manifest.json` 使用以下固定结构。`files` 按 `candidate_path` 字典序排序，每个候选文件恰好出现一次。

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

`candidate_path` 相对 `updates/candidates/<candidate-id>/` 使用 POSIX 路径；`target_path` 相对 skill 根目录使用 POSIX 路径。拒绝绝对路径、`..`、符号链接、除 `candidate.md` 外的空路径、重复路径和解析后逃出根目录的路径。只有 `candidate.md` 可以使用 `target_path: null`。其他候选路径必须以 `evidence/` 或 `publish/` 开头，目标路径只能位于 `references/`、`sources/` 或 `evals/`。候选不得目标为 `SKILL.md`、`README.md`、`scripts/`、`tests/`、任一 `updates/` 生命周期目录或 `.git`。同一目标路径最多出现一次。

每个 `sha256` 对文件字节计算。`manifest_hash` 对移除 `manifest_hash` 后的 UTF-8 canonical JSON 计算 SHA-256，使用 `sort_keys=True`、`separators=(",", ":")` 和 ASCII 转义。哈希后不得重排 `files`。

审批记录必须使用以下 YAML frontmatter。`decision` 只能是 `approved` 或 `rejected`；`approved_at` 使用 UTC RFC 3339 时间戳 `YYYY-MM-DDTHH:MM:SSZ`。

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

## 发布与恢复规则

发布顺序为：创建候选和 manifest，等待人工审批，校验匹配的哈希及所有文件哈希，只发布获批且目标路径非空的条目，将获批 manifest 复制到 `updates/releases/<candidate-id>/manifest.json`，追加允许的完整性信息，最后校验和评估。

事务实现将进行中的发布工作记录在 `updates/transactions/`。存在未完成事务时，必须先恢复，才能创建候选、校验或发布。恢复未完成时，不得称 handbook 已发布或已校验。

## 校验命令占位

Task 1 有意不创建校验脚本或 fixture 内容。以下是供后续实现使用的不可运行占位符，在实现存在前不指定 flag。

```text
python3 scripts/validate_handbook.py <implementation-defined-arguments>
python3 -m unittest scripts/test_validate_handbook.py
```
