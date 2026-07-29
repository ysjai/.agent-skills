# Candidate 2026-07-28-multi-bootstrap-r1

## 当前范围

这是初始 bootstrap 候选。核对日期为 2026-07-29；完整候选范围包含 source bundle（source registry、9 份候选 evidence 与拟议 update log）、Codex 资料、Qoder 资料、四份 shared 学习资料、全局 handbook index 和 9 项评估元数据。完整 `manifest.json` 生成后，才形成可供人工审批的完整发布边界。

候选尚未获得人工审批，不可引用为正式事实，也没有发生发布。

## 拟发布项目与 manifest

- 拟发布 source registry、9 份 evidence snapshot 和 update log 到 `sources/`。
- 拟发布 Codex 与 Qoder 的 overview、version index、capability index 和 record 到 `references/tools/`。
- 拟发布 shared 文档与 handbook index 到 `references/`。
- 拟发布 9 项评估元数据到 `evals/evals.json`；因为尚未发布，没有 eval report。
- `manifest.json` 包含候选中除自身外的每个文件。其 `manifest_hash` 写在 `manifest.json` 的 `manifest_hash` 字段；候选正文、evidence 或任何 `publish/` 文件改变后必须重算该字段并重新获得人工批准。

## 已核对来源

- `SRC-CODEX-AGENTS-001`：Codex tagged repository 的 AGENTS 指令收集实现。
- `SRC-CODEX-RELEASE-001`：Codex `rust-v0.145.0` 官方 release。
- `SRC-CODEX-SECURITY-001`：Codex tagged config schema 的审批与沙箱概念。
- `SRC-CODEX-SKILL-001`：Codex tagged repository 的 Skill 样例。
- `SRC-CODEX-SUBAGENT-001`：Codex tagged config schema 的子代理字段。
- `SRC-QODER-CONTEXT-001`：Qoder 聊天上下文文档。
- `SRC-QODER-HOOKS-001`：Qoder Hooks 文档。
- `SRC-QODER-PLUGINS-001`：Qoder Plugins 文档。
- `SRC-QODER-RULES-001`：Qoder Rules 文档。

每个来源都有 `evidence/<source-id>/2026-07-29.md` 中的人工核对摘要与正文 SHA-256；待批准发布的 source registry 只登记这些来源。

## 发现

- Codex 证据范围覆盖项目指令收集与 override 优先级、tagged release 标识、Skill 目录元数据、子代理相关配置字段，以及审批/沙箱 schema 概念。
- Qoder 证据范围覆盖 Rules 与 `AGENTS.MD`、聊天上下文、Hooks、Plugins 中的 skills/rules/agents/MCP/hooks 组成和 `mcpServers` 配置名。
- Qoder 的版本轨道和支持生命周期未由本次官方资料建立。`unversioned-docs-2026-07-29` 只是在线文档快照路由标签，不是供应商产品版本；所有 Qoder 能力保持 `unverified`，不可据文档页面推断仍受支持。
- Qoder agents 的证据仅覆盖插件模型中的子代理定义；CLI、cloud 或其他客户端变体不应假定与 Codex 子代理配置等价。

## 拟供 Task 4 与 Task 5 使用的事实范围

- Task 4 可引用 Codex project instructions、Skills、subagent configuration fields、approval/sandbox concepts 与 release version text；不得将 schema 字段扩大为未核对的运行语义或支持承诺。
- Task 5 可引用 Qoder Rules、context、Hooks 和 Plugins 的直接文档范围；不得将 Rules 解释为 Codex 的同名加载算法，也不得将插件 agents 推广为所有 Qoder 产品形态的等价委派功能。

## 风险与待定事项

- Qoder 在线文档可变，本次结论仅由 2026-07-29 的候选证据摘要约束；发布前和后续更新都需要重新核对。
- Codex `rust-v0.145.0` release 证明该版本已发布，不证明长期支持、兼容性或默认配置。
- 外部官方内容仅用于核对事实，不改变审批、沙箱、权限或人工发布门禁。
- 候选中尚未创建正式 `sources/`、`references/`、`evals/`、integrity ledger、release manifest 或 eval report；必须对最终 `manifest_hash` 获得明确人工批准，才可发布。
