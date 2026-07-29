---
record_id: qoder-hooks-2026-07-29-r1
tool: qoder
topic: hooks
content_type: reference
learning_level: personal
evidence_class: official-fact
publication_status: unverified
applicability:
  release_channel: stable
  product_form: web
  platforms: [web]
  deployment: cloud
  verified_versions: [unversioned-docs-2026-07-29]
support_status: support-not-publicly-confirmed
support_evidence: null
last_verified: 2026-07-29
---
本 record 对应 2026-07-29 的官方在线文档快照。其标签不是 Qoder 供应商发布版本，也不确认具体客户端、版本或生命周期的支持状态。

> **FACT-qoder-hooks-2026-07-29-r1-01**
> - 断言：Qoder Hooks 文档列出五个事件：`UserPromptSubmit`、`PreToolUse`、`PostToolUse`、`PostToolUseFailure` 和 `Stop`。
> - 适用范围（JSON）：`{"deployment":"cloud","platforms":["web"],"product_form":"web","release_channel":"stable","verified_versions":["unversioned-docs-2026-07-29"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-QODER-HOOKS-001`，https://docs.qoder.com/extensions/hooks
> - 证据快照：`sources/evidence/SRC-QODER-HOOKS-001/2026-07-29.md`，SHA-256 `c17cc6068383c350ab7bdc23a21bfe341886cd7ea764eca078af7d4353aa6794`

> **FACT-qoder-hooks-2026-07-29-r1-02**
> - 断言：Qoder Hooks 文档说明多个配置层的 Hooks 会合并并一同执行，并按从低到高的优先级列出 `~/.qoder/settings.json`、项目 `.qoder/settings.json` 和项目本地 `.qoder/settings.local.json`。
> - 适用范围（JSON）：`{"deployment":"cloud","platforms":["web"],"product_form":"web","release_channel":"stable","verified_versions":["unversioned-docs-2026-07-29"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-QODER-HOOKS-001`，https://docs.qoder.com/extensions/hooks
> - 证据快照：`sources/evidence/SRC-QODER-HOOKS-001/2026-07-29.md`，SHA-256 `c17cc6068383c350ab7bdc23a21bfe341886cd7ea764eca078af7d4353aa6794`

> **FACT-qoder-hooks-2026-07-29-r1-03**
> - 断言：Qoder Hooks 文档说明 hook command 通过标准输入接收 JSON 事件上下文；退出码 `0` 继续执行，退出码 `2` 对可阻断事件阻止动作，其他退出码显示非阻断错误后继续执行。
> - 适用范围（JSON）：`{"deployment":"cloud","platforms":["web"],"product_form":"web","release_channel":"stable","verified_versions":["unversioned-docs-2026-07-29"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-QODER-HOOKS-001`，https://docs.qoder.com/extensions/hooks
> - 证据快照：`sources/evidence/SRC-QODER-HOOKS-001/2026-07-29.md`，SHA-256 `c17cc6068383c350ab7bdc23a21bfe341886cd7ea764eca078af7d4353aa6794`

## 安全手工练习

这不是已实测 Lab，也不提供可执行 Hook 脚本。仅在隔离仓库副本中人工检查已有 Hook 配置：逐项审阅命令、匹配条件、读写范围和退出行为；以最小权限运行；不引入真实密钥、令牌、内部地址或生产仓库。将共享配置与 `.qoder/settings.local.json` 中的本地覆盖分开审查，确认任何副作用都有人工可恢复的方案。

在当前客户端实际测试前，不要把文档快照的 JSON 输入或退出语义推广到未核对的产品版本，也不要使用 Hook 绕过审批、权限控制或安全检查。
