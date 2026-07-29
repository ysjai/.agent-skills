---
record_id: qoder-mcp-and-security-2026-07-29-r1
tool: qoder
topic: mcp-and-security
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
本 record 的 `unversioned-docs-2026-07-29` 只表示官方在线文档快照，不是 Qoder 产品版本。它没有绑定公开生命周期，因此不确认版本级支持状态。

> **FACT-qoder-mcp-and-security-2026-07-29-r1-01**
> - 断言：Qoder Plugins 文档将 MCP Servers 列为插件可包含的组件，并说明 MCP 配置文件为 `mcp.json`（或 `.mcp.json`），顶层字段为 `mcpServers`。
> - 适用范围（JSON）：`{"deployment":"cloud","platforms":["web"],"product_form":"web","release_channel":"stable","verified_versions":["unversioned-docs-2026-07-29"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-QODER-PLUGINS-001`，https://docs.qoder.com/qoder-plugins
> - 证据快照：`sources/evidence/SRC-QODER-PLUGINS-001/2026-07-29.md`，SHA-256 `f4260ed69b86c072831e1593ae34ae01f8db0c97889b521dd7a0944bb98b2bb7`

> **FACT-qoder-mcp-and-security-2026-07-29-r1-02**
> - 断言：Qoder Plugins 文档将 `mcpServers` 列为 `plugin.json` 可声明的组件路径字段，用于指向 MCP server 配置 JSON 文件。
> - 适用范围（JSON）：`{"deployment":"cloud","platforms":["web"],"product_form":"web","release_channel":"stable","verified_versions":["unversioned-docs-2026-07-29"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-QODER-PLUGINS-001`，https://docs.qoder.com/qoder-plugins
> - 证据快照：`sources/evidence/SRC-QODER-PLUGINS-001/2026-07-29.md`，SHA-256 `f4260ed69b86c072831e1593ae34ae01f8db0c97889b521dd7a0944bb98b2bb7`

## 安全手工练习

这不是已实测 Lab。仅在隔离仓库副本中以只读方式检查候选 MCP 配置和关联文档：先确认每个外部连接的目的、最小权限、数据范围和所有者，再决定是否允许安装或启用。不得在示例、配置或日志中写入真实凭证、令牌、内部地址或生产资源；不得通过 MCP 或配置绕过审批、权限提示、沙箱或既有安全控制。

当前客户端、实际连接权限和配置加载方式均须由学习者针对本机版本重新核对。本 record 不提供凭证示例，也不声称未验证的客户端能力不可用。
