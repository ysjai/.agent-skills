# Coding Agent Handbook 索引

## 已发布状态与使用边界

本索引定位已发布 handbook 的正式 `references/` 路径。回答前仍须读取版本索引、能力索引和适用的 current record；索引不复制产品行为事实。

Qoder 条目受 `unversioned-docs-2026-07-29` 限制：它是 2026-07-29 官方在线文档快照的路由标签，不是产品版本、支持生命周期或对本机功能的确认。Qoder 能力索引为 `unverified` 时，只能说明本地 handbook 没有版本或客户端绑定，不能说“不支持”。

## 检索顺序

1. 确认工具、能力域、学习层级与用户提供的版本、平台和部署形态。
2. 阅读对应工具版本索引，声明实际使用的覆盖范围或请求用户补充版本。
3. 阅读能力索引以确认状态和 current record。
4. 只读与适用范围相交的 current record；将官方事实与建议分开回答。
5. 仅在需要通用工作方式、协作、组织治理或资料追溯时读取相应 shared 文档。

## 工具与能力域

| 工具 | 覆盖范围与状态入口 | 能力域 | 当前 record |
| --- | --- | --- | --- |
| Codex | [版本索引](tools/codex/version-index.md)，`rust-v0.145.0`，支持生命周期未公开确认 | 项目指令 | [codex-project-instructions-2026-07-29-r2](tools/codex/capabilities/project-instructions/records/codex-project-instructions-2026-07-29-r2.md) |
| Codex | 同上 | Skills | [codex-skills-2026-07-29-r2](tools/codex/capabilities/skills/records/codex-skills-2026-07-29-r2.md) |
| Codex | 同上 | 子代理 | [codex-subagents-2026-07-29-r2](tools/codex/capabilities/subagents/records/codex-subagents-2026-07-29-r2.md) |
| Codex | 同上 | MCP 与安全 | [codex-mcp-and-security-2026-07-29-r2](tools/codex/capabilities/mcp-and-security/records/codex-mcp-and-security-2026-07-29-r2.md) |
| Codex | `unverified`，不代表不存在 | 执行与审查 | [codex-execution-and-review-2026-07-29-r2](tools/codex/capabilities/execution-and-review/records/codex-execution-and-review-2026-07-29-r2.md) |
| Qoder | [版本索引](tools/qoder/version-index.md)，`unversioned-docs-2026-07-29` 文档快照，`unverified` | Rules 与上下文 | [qoder-rules-and-context-2026-07-29-r2](tools/qoder/capabilities/rules-and-context/records/qoder-rules-and-context-2026-07-29-r2.md) |
| Qoder | 同上 | Skills | [qoder-skills-2026-07-29-r2](tools/qoder/capabilities/skills/records/qoder-skills-2026-07-29-r2.md) |
| Qoder | 同上 | Hooks | [qoder-hooks-2026-07-29-r2](tools/qoder/capabilities/hooks/records/qoder-hooks-2026-07-29-r2.md) |
| Qoder | 同上 | Agents 与委派 | [qoder-agents-and-delegation-2026-07-29-r2](tools/qoder/capabilities/agents-and-delegation/records/qoder-agents-and-delegation-2026-07-29-r2.md) |
| Qoder | 同上 | MCP 与安全 | [qoder-mcp-and-security-2026-07-29-r2](tools/qoder/capabilities/mcp-and-security/records/qoder-mcp-and-security-2026-07-29-r2.md) |
| Qoder | 同上 | 执行与审查 | [qoder-execution-and-review-2026-07-29-r2](tools/qoder/capabilities/execution-and-review/records/qoder-execution-and-review-2026-07-29-r2.md) |

## 学习层级

| 学习层级 | 资料类型 | 资料路径 | 使用方式 |
| --- | --- | --- | --- |
| 个人 | `experimental-guidance` | [个人工作流](shared/personal-workflows.md) | 澄清目标、选择最小上下文、分阶段执行、验证与复盘；不替代工具 record。 |
| 团队 | `experimental-guidance` | [团队协作](shared/team-collaboration.md) | 共享说明、PR/Git 边界、skills/MCP 所有权和变更审查。 |
| 组织 | `experimental-guidance` | [组织效能](shared/organization-effectiveness.md) | 受限试点、最小权限、质量/效率指标、培训与治理。 |
| 所有层级 | 资料模型 | [证据与版本](shared/evidence-and-versioning.md) | 解释 FACT、source、evidence、record、index、manifest、approval 与 release。 |

## 资料类型与状态

- 工具 `record`：工具专属事实或已显式分类的建议；由能力 index 管理生命周期。
- 能力 `index`：状态和范围路由，不是行为事实来源。
- 共享资料：跨工具 `experimental-guidance`，需要按文中假设与验证方法在本地检验。
- `unverified` 与 `not-covered`：本地资料缺少确认，均不等于不支持。
- 候选资料：尚未批准，不能作为正式 handbook 或 release 结论引用。
