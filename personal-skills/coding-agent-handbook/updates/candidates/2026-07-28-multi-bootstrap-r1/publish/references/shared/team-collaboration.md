# 团队协作

## 定位与事实边界

本文件为中文工程团队提供跨工具协作建议，不声明供应商要求，也不把 Codex 与 Qoder 的概念视为等价。

**事实分类：** 全文为 `experimental-guidance`。本候选尚未登记可复现的第三方团队实践来源，因此所有收益均是待验证假设，不能表述为已证实的成熟实践。

## 共享规范与仓库说明

- **假设：** 团队可以维护一个可访问、可审查的仓库级说明位置。
- **做法：** 将目标、目录职责、测试入口、敏感区域、生成物和升级规则放在短而可检索的共享说明中；工具专属规则只链接对应 record。Codex 项目指令应从 [项目指令 record](../tools/codex/capabilities/project-instructions/records/codex-project-instructions-2026-07-29-r1.md) 核对，Qoder Rules 与上下文应从 [Qoder record](../tools/qoder/capabilities/rules-and-context/records/qoder-rules-and-context-2026-07-29-r1.md) 核对，不能互相替代。
- **预期收益：** 降低重复澄清和新人定位成本。
- **代价：** 说明会过时，需要维护责任和变更审查。
- **验证方法：** 让不参与原任务的成员按说明定位测试、边界和负责人；记录无法定位或与实际不符的项。

## PR 与 Git 边界

- **假设：** 团队使用可审查的变更记录，并能区分本任务改动与并发改动。
- **做法：** 为每项变更声明拥有的文件边界、依赖、验证证据和回滚方式；在 PR 或等价审查入口中区分产品事实、工程建议和待确认风险。未经明确授权，不把工具生成内容直接视为已审查或已发布。
- **预期收益：** 减少冲突、误合并和不可追溯的安全影响。
- **代价：** 小变更也需要填写最少的上下文和验证记录。
- **验证方法：** 审查者仅依赖变更说明、diff 和验证输出判断范围是否清楚；无法识别副作用或回滚点时退回补充。

## Skills、MCP 与自动化资产的所有权

- **假设：** 复用资产会影响多名成员或多个仓库，且团队能够指定维护者。
- **做法：** 为每个共享 skill、MCP 定义或自动化配置记录所有者、适用仓库、权限与数据边界、变更评审人、版本/来源依据和停用方式。工具机制分别以 [Codex Skills](../tools/codex/capabilities/skills/records/codex-skills-2026-07-29-r1.md)、[Qoder Skills](../tools/qoder/capabilities/skills/records/qoder-skills-2026-07-29-r1.md)、[Codex MCP 与安全](../tools/codex/capabilities/mcp-and-security/records/codex-mcp-and-security-2026-07-29-r1.md)、[Qoder MCP 与安全](../tools/qoder/capabilities/mcp-and-security/records/qoder-mcp-and-security-2026-07-29-r1.md) 为准。
- **预期收益：** 减少无人维护、权限不明和跨仓库意外影响。
- **代价：** 增加所有权登记、审查排期和定期复核成本。
- **验证方法：** 随机抽取一个资产，确认维护者能说明其权限、依赖、审批路径和停用步骤；不能确认时暂停扩大复用范围。

## 变更审查与交接

- **假设：** 团队允许独立成员核对高风险变更。
- **做法：** 将范围正确性、测试结果、事实引用、权限变化与可维护性分别检查；交接时保留目标、已做内容、未做内容、验证输出和已知风险。子代理或委派问题必须分别查阅 [Codex 子代理 record](../tools/codex/capabilities/subagents/records/codex-subagents-2026-07-29-r1.md) 与 [Qoder Agents 与委派 record](../tools/qoder/capabilities/agents-and-delegation/records/qoder-agents-and-delegation-2026-07-29-r1.md)，不得宣称完全等价。
- **预期收益：** 降低单人知识集中和遗漏风险。
- **代价：** 需要审查时间，且审查不能替代实际测试。
- **验证方法：** 交接接收者复现一个关键验证或明确标记无法复现的原因；下一次审查统计交接后发现的范围/环境缺口。

## 安全边界

本建议不提供绕过 Git 审查、审批、沙箱、权限提示或凭证管理的方法。任何仓库可执行规则、Hook 或外部连接均需先确认副作用与所有者；Qoder Hooks 的已覆盖资料只限 [Qoder Hooks record](../tools/qoder/capabilities/hooks/records/qoder-hooks-2026-07-29-r1.md) 的适用范围。
