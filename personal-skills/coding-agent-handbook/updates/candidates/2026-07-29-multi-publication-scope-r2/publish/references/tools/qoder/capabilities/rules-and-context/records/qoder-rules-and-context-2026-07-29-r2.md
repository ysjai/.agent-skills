---
record_id: qoder-rules-and-context-2026-07-29-r2
tool: qoder
topic: rules-and-context
content_type: reference
learning_level: personal
evidence_class: official-fact
publication_status: published
applicability:
  release_channel: unspecified
  product_form: unspecified
  platforms: unspecified
  deployment: unspecified
  verified_versions: [unversioned-docs-2026-07-29]
support_status: support-not-publicly-confirmed
support_evidence: null
last_verified: 2026-07-29
---

本 record 只覆盖 2026-07-29 核对的 Qoder 官方在线文档快照。`unversioned-docs-2026-07-29` 是路由标签，不是 Qoder 供应商发布的产品版本；官方快照没有为本 record 建立发行通道、客户端、平台、部署或生命周期的可绑定范围。

> **FACT-qoder-rules-and-context-2026-07-29-r2-01**
> - 断言：Qoder Rules 文档说明项目规则位于 `.qoder/rules`，并可随项目通过 Git 共享。
> - 适用范围（JSON）：`{"deployment":"unspecified","platforms":"unspecified","product_form":"unspecified","release_channel":"unspecified","verified_versions":["unversioned-docs-2026-07-29"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-QODER-RULES-001`，https://docs.qoder.com/user-guide/rules
> - 证据快照：`sources/evidence/SRC-QODER-RULES-001/2026-07-29.md`，SHA-256 `dba5c0467284c85a2d17e041ec7ccde59bc19148861a907e5d2a6896367e3740`

> **FACT-qoder-rules-and-context-2026-07-29-r2-02**
> - 断言：Qoder Rules 文档列出 Apply Manually、Model Decision、Always Apply 和 Specific Files 四种规则类型，并将全部活动规则文件的总字符数限制为 100,000，超出内容会被截断。
> - 适用范围（JSON）：`{"deployment":"unspecified","platforms":"unspecified","product_form":"unspecified","release_channel":"unspecified","verified_versions":["unversioned-docs-2026-07-29"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-QODER-RULES-001`，https://docs.qoder.com/user-guide/rules
> - 证据快照：`sources/evidence/SRC-QODER-RULES-001/2026-07-29.md`，SHA-256 `dba5c0467284c85a2d17e041ec7ccde59bc19148861a907e5d2a6896367e3740`

> **FACT-qoder-rules-and-context-2026-07-29-r2-03**
> - 断言：Qoder Rules 文档说明 `AGENTS.MD` 可被识别；当其内容与 Rules 内容冲突时，Rules 内容优先。
> - 适用范围（JSON）：`{"deployment":"unspecified","platforms":"unspecified","product_form":"unspecified","release_channel":"unspecified","verified_versions":["unversioned-docs-2026-07-29"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-QODER-RULES-001`，https://docs.qoder.com/user-guide/rules
> - 证据快照：`sources/evidence/SRC-QODER-RULES-001/2026-07-29.md`，SHA-256 `dba5c0467284c85a2d17e041ec7ccde59bc19148861a907e5d2a6896367e3740`

> **FACT-qoder-rules-and-context-2026-07-29-r2-04**
> - 断言：Qoder 聊天上下文文档列出 `@file`、`@folder`、`@attachments` 和 `@rule`；其中 `@rule` 用于引用项目规则作为持久上下文。
> - 适用范围（JSON）：`{"deployment":"unspecified","platforms":"unspecified","product_form":"unspecified","release_channel":"unspecified","verified_versions":["unversioned-docs-2026-07-29"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-QODER-CONTEXT-001`，https://docs.qoder.com/user-guide/chat/context
> - 证据快照：`sources/evidence/SRC-QODER-CONTEXT-001/2026-07-29.md`，SHA-256 `9e640f76a1578d3df9797b6c41d74a911ad6171eca86482eea6192bc34f927be`

## 手工练习

这不是已实测 Lab。请在不含机密和生产配置的隔离仓库副本中，先确认实际客户端和版本与对应的官方资料，再分别准备简短的 `.qoder/rules` 与 `AGENTS.MD` 文本，且只使用可识别的无害标记。通过一次人工发起的聊天请求观察实际客户端是否呈现预期的冲突优先级；完成后删除练习文件或恢复副本。

该练习不验证也不暗示 Codex 的加载算法、目录递归或优先级与 Qoder 等价。若本机版本或客户端与文档快照不一致，应停止并以该版本的官方资料为准。
