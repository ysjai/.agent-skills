---
record_id: codex-subagents-2026-07-29-r2
tool: codex
topic: subagents
content_type: reference
learning_level: team
evidence_class: official-fact
publication_status: published
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

> **FACT-codex-subagents-2026-07-29-r2-01**
> - 断言：核对的配置 schema 在 `[agents]` 中声明 `default_subagent_model` 和 `default_subagent_reasoning_effort` 字段。
> - 适用范围（JSON）：`{"deployment":"local","platforms":["macos","linux","windows"],"product_form":"cli","release_channel":"stable","verified_versions":["rust-v0.145.0"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-CODEX-SUBAGENT-001`，https://raw.githubusercontent.com/openai/codex/rust-v0.145.0/codex-rs/core/config.schema.json
> - 证据快照：`sources/evidence/SRC-CODEX-SUBAGENT-001/2026-07-29.md`，SHA-256 `6bc18dcfddb05a2aafa6b9d0b3925fbc44a27dc7f25d9b795d4b3bfd9733c58f`

> **FACT-codex-subagents-2026-07-29-r2-02**
> - 断言：核对的配置 schema 声明 `max_concurrent_threads_per_session` 为最小值 1 的整数，用于每个会话可同时打开的 spawned agent threads 数量上限。
> - 适用范围（JSON）：`{"deployment":"local","platforms":["macos","linux","windows"],"product_form":"cli","release_channel":"stable","verified_versions":["rust-v0.145.0"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-CODEX-SUBAGENT-001`，https://raw.githubusercontent.com/openai/codex/rust-v0.145.0/codex-rs/core/config.schema.json
> - 证据快照：`sources/evidence/SRC-CODEX-SUBAGENT-001/2026-07-29.md`，SHA-256 `6bc18dcfddb05a2aafa6b9d0b3925fbc44a27dc7f25d9b795d4b3bfd9733c58f`

## 可用性与版本边界

这些事实只描述 `rust-v0.145.0` 的 tagged schema。schema 中存在字段不证明本机已启用相应功能，也不证明所选后端、模型、默认值、线程后端或其他版本具有相同行为。使用前应先确认本机版本和本机可用的配置校验方式。

## 工程建议（非产品事实）

将互不写入同一文件的任务分配给不同工作单元，并把并发上限从较小值开始调整。收益是减少共享工作树冲突；代价是协调、审查和失败排查成本会上升。对共享配置、迁移、生成文件或外部副作用，优先串行处理并保留人工审查点。

## 手工配置练习（未实测运行时）

在隔离、无凭证、非生产目录中创建一个不被实际加载的 TOML 草稿，只检查结构而不调用 Codex：

```toml
[agents]
default_subagent_model = "<已在本机核对的模型标识>"
default_subagent_reasoning_effort = "<已在本机 schema 核对的值>"
max_concurrent_threads_per_session = 1
```

记录本机版本和每个占位符的核对来源。不要把草稿写入共享或真实配置，也不要从本示例推断可用的模型或 reasoning 值。若后续以本机运行时手工验证，观察并记录实际接受或拒绝的配置结果；本 record 没有该运行时测试结果。

## 来源与边界

最后核对：2026-07-29。来源是 `SRC-CODEX-SUBAGENT-001`。本 record 不建立自动启用、默认后端、模型可用性、实际线程调度或支持生命周期结论。
