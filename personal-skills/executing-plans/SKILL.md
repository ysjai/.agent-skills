---
name: executing-plans
description: 已有经 brainstorming/writing-plans 生成的获批计划，或获批的无 spec 计划并准备实现时使用。按 Wave 委派 `general` workers，实现、验证并建立边界；全部完成后统一进行独立实现审核和修复。
---

# 执行计划落地

实现已经批准的设计文档和执行计划。这是完整工作流的第三步：

1. `brainstorming` 产出设计文档。
2. `writing-plans` 产出执行计划。
3. `executing-plans` 实现计划，并证明验收标准通过。

## 概览

把书面计划变成可工作的软件，同时不能偏离已批准设计。把设计文档视为产品意图和设计意图的来源，把执行计划视为执行步骤和验收标准的来源。

目标不是宽泛地“让它能跑”。目标是落实文档中的决策，遵守代码库的工程约束，并拿出证据证明计划中的验收标准已经满足。

**开始时说明：** “我正在使用 executing-plans skill 执行已批准的计划。”

## 固定实现协议

`Workflow Review Mode` 只记录上游文档审核强度；`lightweight` 和 `explore-review` 的实现行为完全相同：

1. 每个计划 Task 都交给独立的 `general` worker（`subagent_type=general`），包括契约、接线和集成 Task；单 Task Wave 也必须委派。
2. 同一 Wave 的全部 Task 先在一次并行 dispatch 中启动；只有宿主明确拒绝调用并由主 agent 把对应 lease 标记为 `not-started` 时，这些 Task 才能作为同一逻辑 Wave 的 transport retry batches 继续派发。`dispatching` lease 表示 worker 可能已启动，未确认终止前禁止重派。全部回收后，主 agent 检查范围和冲突、运行 Wave 验证，并按 `Commit Policy` 建立边界。
3. 全部 Wave 和最终验收完成后，主 agent 使用 canonical `implementation-reviewer-prompt.md` 统一派发一次独立实现审核。
4. reviewer 的“问题”先由主 agent 分类：代码问题进入 Review-Fix，计划或设计问题返回对应上游阶段；“建议”默认只报告，不实施。默认不运行第二轮审核，除非用户明确要求。

每次派发 `general` worker 都必须使用 canonical `general-worker-prompt.md`，填入文档路径、Wave/Task、依赖产物、完整文件所有权、验收标准、验证命令、共享运行资源/隔离约束和项目指令。完整 worker 边界只在该文件维护。

当前环境缺少 `general` 或可用审核 subagent 能力时，以阻塞报告结束；禁止主 agent 自行实现或跳过最终审核。审核 subagent 优先使用当前宿主或项目指令指定的类型，未指定时使用 `explore`。用户明确禁止所有 subagent 时，说明与本 skill 冲突，并询问是否改用其他执行方式。

## 必需输入

实现前先定位执行计划，再从计划定位设计依据：

- **执行计划：** 优先使用用户本轮提供的精确路径，其次使用当前对话已明确生成/批准的路径，最后才搜索 `docs/plans/`。如果自定义路径不在常见目录且当前上下文没有精确路径，询问用户，不得猜测
- **设计依据：** 读取计划头部 `来源设计文档` 的精确路径并使用它；只有该字段明确记录“无（用户明确跳过）”时，才使用计划中的“实现依据（无 spec）”作为 `SPEC_CONTEXT`。不得先搜索默认 spec 目录再覆盖计划记录

如果有多个可能的计划，问一个澄清问题。来源设计文档路径不存在、与计划记录不一致或无法读取时阻塞。

同时读取 `Workflow Review Mode`、`Spec Revision`、`Spec Review Status`、`Spec Approval Status`、`Spec Approval Revision`、`Spec Review Exception`、`Plan Revision`、`Plan Review Status`、`Plan Approval Status`、`Plan Approval Revision`、`Plan Review Exception`、`Commit Policy`、`Source Document Baseline`、`Wave Evidence Directory`、`Execution State Directory`、`Execution State`、`Execution Blocker`、`Resume Point` 和 `Last Completed Boundary`。有 spec 时，从来源文件重新读取当前 Spec Revision、Review Status、Review Exception、Approval Status 和 Approval Revision，并要求与计划副本逐项一致；不一致时把计划批准状态/版本清为 `pending`/`none`，写 `Execution State: blocked` 和具体 Execution Blocker，返回 writing-plans 同步来源并重新批准，禁止按旧计划执行。提交策略优先级为：当前用户明确指令 > 计划中有明确用户授权来源的记录 > 默认 `no-commits`；旧计划仅记录“默认 wave-commits”不构成授权，必须切换为 `no-commits`。如果当前指令改变策略，必须在派发前重新物化并自检所有派生字段和每 Wave 边界：`wave-commits` 需要 baseline、每 Wave commit message、Evidence Directory=`not-applicable`；`no-commits` 需要 Baseline=`not-applicable`、可写 evidence 目录和每 Wave evidence 路径。旧策略值不得保留；`wave-commits` 的 `pending` baseline 必须在建立基线步骤解析为 commit hash 后才能派发 worker。`Execution State Directory` 必须是计划生成时通过 `git rev-parse --git-path` 解析的实际路径，不得假设 `.git` 是目录。

分别校验状态值：`Spec Review Status` 只允许 `lightweight|explore-pending|explore-reviewed|review-blocked|needs-review-after-changes|not recorded`；`Plan Review Status` 只允许前五项，不允许 `not recorded`；有 spec 时 `Spec Approval Status` 必须为 `approved` 且 `Spec Approval Revision` 必须等于当前 `Spec Revision`，无 spec 时 Spec Revision、Spec Approval Status、Spec Approval Revision 必须为 `not-applicable` 且 Spec Review Exception 必须为 `none`；`Plan Approval Status` 必须为 `approved` 且 `Plan Approval Revision` 必须等于当前 `Plan Revision`；`Execution State` 只允许 `not-started`、`ready: Wave N`、`in-progress: Wave N`、`final-validation`、`review-fix`、`blocked`、`completed`；Resume Point 只允许 `Wave N|final-validation|review-fix|completed`；Execution Blocker 在非 blocked 状态必须为 `none`，blocked 时必须是具体原因。批准字段缺失、`pending`、版本不匹配或未知值一律阻塞，不能从 reviewer 状态或用户启动本 skill 的动作推断批准。执行状态、Execution Blocker、Resume Point 或 Last Completed Boundary 缺失/未知时同样阻塞，不得猜测恢复点。

状态处理：

- `Spec Review Status: not recorded`：仅在计划包含完整“实现依据（无 spec）”章节且 `Spec Approval Status: not-applicable` 时可继续；否则阻塞。它不适用于 Plan Review Status
- `explore-pending`、`review-blocked`：停止，先完成或解决上游审核
- `needs-review-after-changes`：表示上游文档在审核后又有实质改动、但尚未复审。先检查对应 `Spec Review Exception` 或 `Plan Review Exception`；存在 `user-accepted` 且记录的 revision 等于当前 Spec/Plan Revision 时继续且不得重复询问。没有匹配记录时，提示用户选择回上游补审或接受风险；接受时把当前 revision、日期和范围持久化到对应 exception 字段，并确认对应 Approval Status/Revision 仍匹配

执行状态恢复分支：

- `not-started` 或 `ready: Wave N`：从 Resume Point 指向的 Wave 开始，派发前再建立 snapshot
- `in-progress: Wave N`：按 durable snapshot 和 worker evidence/lease 状态恢复；`completed` 跳过，`not-started` 可重派，`started`/`blocked` 必须先执行 Task 的中断恢复策略，`dispatching` 必须等待原 worker 更新状态或确认其已终止，缺失/损坏 evidence 一律阻塞
- `final-validation`：重跑最终验收后重新派发只读实现审核；审核调用中断时允许重跑，因为它不修改文件
- `review-fix`：按 Review-Fix snapshot、Task evidence 和中断恢复策略对账，再补齐未完成修复
- `blocked`：保留 Execution Blocker；只有 blocker 已解决且批准 revision 重新匹配时，清空 blocker，并按 Resume Point 转成对应 `ready: Wave N`、`final-validation` 或 `review-fix`
- `completed`：验证最终边界和验收记录后直接报告，不重新派发 worker 或 reviewer

## 硬门槛

- 没有读完设计依据（spec 或 `SPEC_CONTEXT`）和执行计划前，不要开始编辑代码
- 不要静默改变、重新解释或丢弃设计文档中的决策
- 不要因为验收标准麻烦，就削弱、跳过或替换它们
- 不要添加无关重构、清理、抽象、依赖或行为
- 实现和验证未通过前，不要把计划复选框标记为完成
- 主 agent 不直接编写计划中的实现代码；所有代码修改 Task 都交给 `general` worker。主 agent 只负责编排、上下文准备、范围与冲突检查、Wave/最终验证、进度更新、提交和最终审核
- `general` worker 禁止创建 commit；主 agent 必须在每个 Wave 验证通过后按 `Commit Policy` 创建恰好一个 Wave commit 或持久化 no-commits evidence
- 任一 Wave 未完整返回、存在文件冲突或验证失败时，不提交，也不进入下一 Wave

如果设计文档和执行计划冲突，停下来说明冲突。推荐最小修正，但除非用户已经明确优先级，不要自行判断哪份文档优先。

## 执行流程

每次都按这个顺序执行：

1. **加载并验证输入** — 先定位计划，再按计划记录定位设计依据；读取 revision、批准/审核状态、例外、Wave、验收标准、执行状态和边界策略；按入口状态规则决定继续或阻塞。
2. **恢复对账并验证 Wave 计划** — 检查每个 Task 恰属一个 Wave、依赖均在更早 Wave、同波文件所有权不重叠、共享运行资源可隔离，且没有遗漏明显可并行任务。读取 `Execution State`、`Resume Point` 和 `Last Completed Boundary`：已完成边界必须用 commit hash 或 evidence SHA-256 验证后跳过。恢复 in-progress/review-fix 时，evidence=`completed` 且 owned-file hash 有效的 Task 视为已返回；`not-started` Task 可作为 transport retry；`started|blocked` Task 可能已有部分文件或外部副作用，先从 snapshot 恢复该 Task 独占文件，并执行计划记录的中断恢复策略，只有恢复证据通过后才创建 `Recovery-<Wave>-<Task>`；`dispatching` 表示旧 worker 可能仍在运行，必须等待它写 `started|completed|blocked`，或从宿主获得已终止/未启动的确定证据后才能转成 `not-started`，不得基于超时猜测；缺失或损坏 evidence、snapshot 缺失或无法证明状态时一律写 `Execution State: blocked`、把具体原因写入 Execution Blocker、保留 Resume Point 并询问用户。只有不改变 DAG、Wave、Task、文件所有权、资源隔离、验证或验收的机械修正可直接应用。其他修改先写 `Execution State: blocked` 和具体 Execution Blocker、保留当前 Resume Point，再把 Plan Approval Status/Revision 写为 `pending`/`none`；原 Plan Review Status 为 `explore-reviewed` 时写 `needs-review-after-changes`，为 `lightweight` 时保持 `lightweight`，然后停止并返回 writing-plans；Plan Revision 只在 writing-plans 实际修改计划内容时递增。用户明确切换 Commit Policy 后的派生字段重物化属于已授权机械更新。
3. **建立基线** — 计划合法且批准门禁通过后，记录当前 `HEAD`、status、staged/unstaged diff。`wave-commits` 且 Baseline=`pending` 时，只暂存获批 spec（如有）和 plan 的精确路径并创建独立文档基线 commit；提交前后确认无关 staged diff 不变、实际 commit 只含源文档、`HEAD` 按预期变化。hook 修改文档时重新运行对应文档自检；实质修改必须迁移审核和批准状态并重新取得用户批准后才能重试。禁止 `--no-verify`。成功后把 commit hash 写回计划；这项元数据更新不改变 Plan Review Status 或 Plan Approval Status，并归入 Wave 1 commit。若无法安全隔离，询问切换 `no-commits`。`no-commits` 下确认 evidence 目录可写。
4. **派发当前 Wave** — 派发前在 `Execution State Directory` 为当前 Wave 持久化 pre-Wave snapshot：记录 `HEAD`、staged/unstaged 状态与 SHA-256、完整 owned-files 与计划文件清单、每个文件内容或不存在标记及 SHA-256，并把计划的 `Execution State`/`Execution Blocker`/`Resume Point` 更新为 `in-progress: Wave N`/`none`/`Wave N`。预先创建 worker evidence 父目录，为每个 Task 生成唯一 Dispatch ID 和 Worker Evidence Path，并由主 agent 在调用 Task tool 之前原子写入 `{status: dispatching, dispatch_id, task, wave, timestamp}` lease。worker 启动后必须在任何文件修改、外部副作用或验证命令之前把同一 lease 原子更新为 `started`，完成或阻塞时再替换为完整报告。然后先在一次并行工具调用中启动全波 workers；宿主明确返回“未启动”的 Task 由主 agent 把 lease 更新为 `not-started`，只有这些 Task 可作为同一逻辑 Wave 的 transport retry batches；调用结果不确定或会话中断时保留 `dispatching`，禁止重复派发。
5. **回收并验证** — 等待全波返回，逐个读取 durable worker evidence，检查范围、owned-file hash、冲突和验证结果，再由主 agent 运行 Wave 验证。需要集成代码时必须由计划中的后续 Task 完成，主 agent 不临时编码。
6. **处理 Wave 失败** — 验证失败时生成 synthetic `Remediation-<Wave>-<N>` Tasks，并按依赖组织成一个或多个 Remediation Waves。每个 synthetic Task 都必须重新声明完整文件所有权、共享运行资源/隔离约束、中断恢复策略和 Worker Evidence Path，并满足与普通 Wave 相同的文件隔离、资源安全、durable snapshot 和 dispatch 规则；修复后重跑完整原 Wave 验证，未通过前不建立边界、不进入下一 Wave。
7. **建立 Wave 边界** — 验证通过后更新计划复选框。`wave-commits` 创建恰好一个 Wave commit；`no-commits` 从 durable pre-Wave snapshot 计算增量，写入计划指定的 `Wave-N.patch` 和 `Wave-N.md`，记录 Task、snapshot ID/SHA-256、路径、patch SHA-256、验证结果和结束状态。生成 patch 和后续 diff 时排除 evidence 和 execution-state 目录。边界建立后把 `Last Completed Boundary` 更新为 Wave、commit/evidence 标识及 SHA-256；还有后续 Wave 时把 `Execution State`/`Resume Point` 写为 `ready: Wave N+1`/`Wave N+1`，此状态不要求下一 Wave snapshot；否则写为 `final-validation`/`final-validation`。
8. **最终验收与审核** — 所有 Wave 完成后运行最终验收，再向配置的审核 subagent 提供本次相关 diff、每 Wave commit/evidence 和验证证据。
9. **分类并处理审核问题** — 主 agent 先分类每个阻塞发现。实现偏离、bug 或缺失测试属于代码修复：持久化 pre-Review-Fix snapshot，把 `Execution State`/`Execution Blocker`/`Resume Point` 写为 `review-fix`/`none`/`review-fix`，再创建 synthetic Tasks；每个 Task 必须声明文件所有权、资源隔离、中断恢复策略和 Worker Evidence Path，并遵循普通 Wave 的安全/dispatch 规则。计划遗漏 Task、验证或边界时，把 `Execution State`/`Execution Blocker`/`Resume Point` 写为 `blocked`/具体计划缺陷/`final-validation`，按步骤 2 的 revision/approval/review 状态迁移返回 writing-plans；writing-plans 修订后应把 Resume Point 改为最早新增或未完成 Wave。设计、范围或验收依据需要改变时，同样写 `blocked`/具体设计缺陷/`final-validation`，把 Spec Approval Status/Revision 清为 `pending`/`none` 并返回 brainstorming，之后必须经过 writing-plans 同步计划和恢复点。不得把上游文档缺陷派给禁止改设计的 worker。代码修复全部完成后重跑受影响检查和最终验收。
10. **建立最终修复边界并报告** — 有实际修复时，`wave-commits` 创建一个独立最终修复 commit；`no-commits` 从 durable pre-Review-Fix snapshot 生成 `Review-Fix.patch` 和 `Review-Fix.md`，记录 snapshot/patch SHA-256、路径、修复 Task、验证结果和结束状态，并排除 evidence 和 execution-state 目录。无修复时不创建空边界。全部验收和审核流程结束后把 `Execution State`/`Execution Blocker`/`Resume Point` 写为 `completed`/`none`/`completed`；阻塞退出时写精确值 `Execution State: blocked`，把原因写入 `Execution Blocker` 并保留恢复点。汇总 commits/evidence、验收、审核和偏离。

## Wave 提交与异常处理

- **没有明确提交授权或用户明确要求不提交：** 使用 `no-commits` 和计划的 evidence 目录；跳过 commit，不跳过 Wave evidence、验证或最终审核
- **已有无关修改：** 实现开始前保存既有未暂存和已暂存基线。只暂存当前 Wave 产生的文件或可精确隔离的 hunk；存在预先 staged 改动时，使用显式 Wave 路径限定提交，并在提交前后确认无关 staged diff 保持不变、实际 commit 只包含当前 Wave。若本 Wave 与既有改动涉及同一文件、或无法证明安全隔离，暂停并询问；不得把无关改动带入 commit
- **Git hook 失败：** 如果需要改代码，把修复委派给 `general` worker；如果 hook 自己修改了文件，也要重新检查范围。任何文件变化后都必须重新运行当前 Wave 的完整验证，再重试 commit。如果明确是无关既有问题导致，暂停并报告。禁止使用 `--no-verify`
- **提交失败：** 不进入下一 Wave。先解决失败；无法安全解决时以阻塞报告结束
- **Evidence 不可变性：** evidence 目录不属于实现 diff。普通 Wave 与 Review-Fix 的 `.patch`/`.md` 创建后均不得覆盖；同一文件跨 Wave 再修改时，后续 evidence 以自身 pre-Wave snapshot 记录增量
- **中断恢复：** 恢复保证以已完成 Wave 边界为单位。已验证边界直接跳过；中断 Wave 必须先用 durable snapshot 对账。不得因会话重启重新执行已经有有效 commit/evidence 的 Wave，也不得在 snapshot 缺失时声称可以无损恢复

## 工程约束与规范

编辑前，检查并遵守项目本地规则和约定：

- Agent 或贡献者指令，例如 `AGENTS.md`、`CLAUDE.md`、`.cursorrules`、`CONTRIBUTING.md` 或等价文件
- 现有架构、命名、文件组织、错误处理、日志、测试风格和依赖模式
- 来自 `package.json`、`Makefile`、`pyproject.toml`、`Cargo.toml`、`go.mod`、CI 配置或项目文档的构建/测试/lint/typecheck 命令
- 代码库已经采用的框架约定

如果计划和现有代码风格不一致，保留计划要求的行为和设计决策，但在不违反设计的前提下，把实现细节调整为符合仓库既有风格。

优先使用最小正确改动：

- 先复用现有工具函数和模式，再引入新东西
- 只有计划要求，或代码库明显没有合理现有方案时，才添加依赖
- 保持文件聚焦，接口明确
- 只删除因你本次改动而变得无用的代码
- 除非计划明确包含，否则避免大范围重构

## 忠实于设计和计划

实现必须能追溯到前两份文档。

对每个实质性改动，都要能回答：

- 它实现了哪个设计需求或设计决策？
- 哪个计划任务和步骤要求这个改动？
- 哪条验收标准证明它有效？

如果发现某个计划步骤无法按原文实现，先暂停，不要即兴发挥。说明：

- 被阻塞的确切步骤或验收标准
- 哪个代码库事实造成阻塞
- 最小可行调整是什么
- 这个调整是否改变已批准设计

只有当调整完全是机械性的，并且保持设计决策和验收标准不变时，才可以不询问用户直接继续。

## 实现纪律

采用测试驱动或验证驱动的执行方式：

- 计划含测试步骤时，严格按 TDD 先写或更新测试再实现；如果计划漏掉了本应有的测试，用仓库原生方式补上最小验证，不要因为“计划没写”就跳过测试
- 可行时，在写实现前先确认失败测试因预期原因失败
- 只写满足当前任务所需的最小代码
- 每个任务后运行最小相关检查
- 完成前运行更广泛检查

编辑代码时：

- 匹配现有风格和命名
- 保持公共接口与计划中的关键代码片段一致，除非代码库事实证明必须采用不同形态
- 只有设计文档、计划、现有持久化数据或外部消费者要求时，才做向后兼容
- 类型错误、lint 失败、测试失败和构建失败都视为阻塞，除非能明确证明是无关的既有失败

## 验收标准

验收标准必须严格执行。必须有证据才能算完成。

有效证据包括：

- 测试命令通过，并记录精确命令
- 构建、lint、typecheck 或格式化命令通过，并记录精确命令
- API 响应、CLI 输出、文件 diff、数据库迁移结果、UI 状态或人工验证结果符合预期
- 如果某项检查无法运行，记录原因，并提供最接近的替代证据，明确标为部分完成

以下情况不要声称完全完成：

- 必需命令没有运行
- 命令失败
- 人工验收项没有检查
- 实现只部分满足设计决策
- 你改变了验收标准，而不是满足它

如果最终验收无法通过，以阻塞报告结束，不要写成功报告。

## 更新计划文档

凡执行计划包含 `- [ ]` 复选框，就必须用它跟踪进度，并保持及时和诚实：

- 完成一个步骤或任务并通过对应验证后，立即把计划中的对应复选框从 `- [ ]` 更新为 `- [x]`
- 不要等到所有实现结束后才批量更新计划；计划文件应该实时反映当前执行状态
- 只有实现完成且验证通过后，才标记任务或步骤完成
- 阻塞、失败或未验证的项目保持未勾选，并在该项附近或最终报告中说明原因
- 如果实现审核提出修复，修复和复验通过后，再勾选相关审核/修复/验收项
- 两种模式下，最终验收清单的最终勾选必须以统一实现审核及其修复后的复验结果为准；如果审核修复打破了之前的通过状态，撤回或保持未勾选，直到重新验证通过
- `Source Document Baseline`、`Execution State`、`Resume Point`、`Last Completed Boundary`、复选框和 evidence 标识等运行时元数据更新不递增 Plan Revision，也不改变 `Plan Review Status` 或 `Plan Approval Status`
- 只允许记录不改变 DAG、Wave、Task、文件所有权、资源隔离、验证或验收的机械修正；其他变化按步骤 2 返回 writing-plans

## 最终回复

最后输出简洁实现报告：

```markdown
已按批准计划完成实现。

变更文件：
- `path/to/file`：改了什么，对应哪个计划任务

验收状态：
- PASS `criterion`：证据 / 命令
- FAIL 或 BLOCKED `criterion`：原因和下一步

已运行验证：
- `command`：PASS/FAIL

实现审核：
- 已由主 agent 在全部 Wave 与最终验收后统一执行一轮独立实现审核

Wave 边界：
- [wave-commits：Wave commit 列表；no-commits：evidence 路径和 patch SHA-256]
- 最终修复：[commit / evidence 路径 / 无修复]

与计划的偏离：
- 无
```

如果全部通过，就明确说明。如果有任何阻塞或部分完成，把它作为首要结论，不要把工作描述为完成。
