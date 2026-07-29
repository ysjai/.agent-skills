---
record_id: codex-skills-2026-07-29-r1
tool: codex
topic: skills
content_type: reference
learning_level: personal
evidence_class: official-fact
publication_status: unverified
applicability:
  release_channel: stable
  product_form: cli
  platforms: [macos, linux, windows]
  deployment: local
  verified_versions: [rust-v0.145.0]
support_status: support-not-publicly-confirmed
support_evidence: null
last_verified: 2026-07-29
---

## 官方事实

> **FACT-codex-skills-2026-07-29-r1-01**
> - 断言：核对的 Skill 示例使用带有 `name` 和 `description` 的 `SKILL.md` YAML frontmatter。
> - 适用范围（JSON）：`{"deployment":"local","platforms":["macos","linux","windows"],"product_form":"cli","release_channel":"stable","verified_versions":["rust-v0.145.0"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-CODEX-SKILL-001`，https://raw.githubusercontent.com/openai/codex/rust-v0.145.0/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md
> - 证据快照：`sources/evidence/SRC-CODEX-SKILL-001/2026-07-29.md`，SHA-256 `cf9a2be1362422c1bb17c87db7b5fe6455f6ff1a12579e7c9a0a0ca6614afd8c`

> **FACT-codex-skills-2026-07-29-r1-02**
> - 断言：核对的 Skill 示例可包含 `scripts`、`references` 和 `assets` 目录作为可选资源。
> - 适用范围（JSON）：`{"deployment":"local","platforms":["macos","linux","windows"],"product_form":"cli","release_channel":"stable","verified_versions":["rust-v0.145.0"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-CODEX-SKILL-001`，https://raw.githubusercontent.com/openai/codex/rust-v0.145.0/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md
> - 证据快照：`sources/evidence/SRC-CODEX-SKILL-001/2026-07-29.md`，SHA-256 `cf9a2be1362422c1bb17c87db7b5fe6455f6ff1a12579e7c9a0a0ca6614afd8c`

## 手工布局练习（未实测自动发现）

本 record 是 reference，不是 Lab。于临时目录创建最小布局，并只检查文件内容和目录边界：

```text
minimal-skill/
  SKILL.md
  scripts/
  references/
  assets/
```

`SKILL.md` 可以使用非敏感的占位 `name` 和 `description`。手工检查 frontmatter 中两个键均存在、文件位于 skill 根目录，且可选目录不含可执行或凭证内容。这个练习只验证资料布局；它不验证、也不得声称 Codex 自动发现、加载或触发该目录。

## 推荐实践与边界

把能产生副作用的脚本留在隔离目录，并在人工审查后再执行。将说明材料与资源分开可降低维护成本，但这是一项工程建议，不是产品保证。完成练习后删除临时目录。

## 来源与边界

最后核对：2026-07-29。来源是 `SRC-CODEX-SKILL-001`。本 record 不覆盖发现路径、触发规则、安装方式、运行权限或跨版本兼容性。
