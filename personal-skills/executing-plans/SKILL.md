---
name: executing-plans
description: 在 brainstorming 和 writing-plans 之后使用。按获批计划的 Wave 委派 `general` workers，实现、验证并建立每 Wave 边界；全部完成后统一进行一次 explore 实现审核和修复。
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
2. 同一 Wave 的全部 Task 在一次并行 dispatch 中启动。全部回收后，主 agent 检查范围和冲突、运行 Wave 验证，并按 `Commit Policy` 建立边界。
3. 全部 Wave 和最终验收完成后，主 agent 使用 canonical `implementation-reviewer-prompt.md` 统一派发一次 explore 实现审核。
4. reviewer 的“问题”进入 Review-Fix 流程；“建议”默认只报告，不实施。默认不运行第二轮审核，除非用户明确要求。

每次派发 `general` worker 都必须使用 canonical `general-worker-prompt.md`，填入文档路径、Wave/Task、依赖产物、完整文件所有权、验收标准、验证命令和项目指令。完整 worker 边界只在该文件维护。

当前环境缺少 `general` 或 `explore` 能力时，以阻塞报告结束；禁止主 agent 自行实现或跳过最终审核。用户明确禁止所有 subagent 时，说明与本 skill 冲突，并询问是否改用其他执行方式。

## 必需输入

实现前先定位设计依据和执行计划：

- **设计依据：** 优先使用 `docs/specs/YYYY-MM-DD-<topic>-design.md`；用户明确跳过 spec 时，使用计划中的“实现依据（无 spec）”章节作为 `SPEC_CONTEXT`
- **执行计划：** 通常是 `docs/plans/YYYY-MM-DD-<feature-name>.md`

如果用户没有提供路径，搜索常见的 `docs/specs/` 和 `docs/plans/` 位置。只有能明确匹配时，才使用最相关的近期文件。如果有多个可能的设计文档或计划，问一个澄清问题。

同时读取 `Workflow Review Mode`、`Spec Review Status`、`Plan Review Status`、`Commit Policy`、`Source Document Baseline` 和 `Wave Evidence Directory`。提交策略优先级为：当前用户明确指令 > 计划记录 > 默认 `wave-commits`。如果当前指令改变策略，必须在派发前重新物化并自检所有派生字段和每 Wave 边界：`wave-commits` 需要 baseline、每 Wave commit message、Evidence Directory=`not-applicable`；`no-commits` 需要 Baseline=`not-applicable`、可写 evidence 目录和每 Wave evidence 路径。旧策略值不得保留；`wave-commits` 的 `pending` baseline 必须在步骤 2 解析为 commit hash 后才能派发 worker。

分别校验状态值：`Spec Review Status` 只允许 `lightweight|explore-pending|explore-reviewed|review-blocked|needs-review-after-changes|not recorded`；`Plan Review Status` 只允许前五项，不允许 `not recorded`。字段缺失或值未知一律阻塞。

状态处理：

- `Spec Review Status: not recorded`：仅在计划包含完整“实现依据（无 spec）”章节时可继续；否则阻塞。它不适用于 Plan Review Status
- `explore-pending`、`review-blocked`：停止，先完成或解决上游审核
- `needs-review-after-changes`：表示上游文档在 explore 审核后又有实质改动、但尚未复审。不要静默当作已审核；先向用户简短提示“上游 <设计文档/计划> 有未复审的实质改动，是否需要回上游补审”，再按用户答复继续

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

1. **加载并验证输入** — 读取源文档、状态字段、Wave、验收标准和边界策略；按入口状态规则决定继续或阻塞。
2. **建立基线** — 记录当前 `HEAD`、status、staged/unstaged diff。`wave-commits` 且 Baseline=`pending` 时，只暂存获批 spec（如有）和 plan 的精确路径并创建独立文档基线 commit；提交前后确认无关 staged diff 不变、实际 commit 只含源文档、`HEAD` 按预期变化。hook 修改文档时重新运行对应文档自检；实质修改必须迁移审核状态并重新取得用户批准后才能重试。禁止 `--no-verify`。成功后把 commit hash 写回计划；这项元数据更新不改变 Plan Review Status，并归入 Wave 1 commit。若无法安全隔离，询问切换 `no-commits`。`no-commits` 下确认 evidence 目录可写。
3. **验证 Wave 计划** — 检查每个 Task 恰属一个 Wave、依赖均在更早 Wave、同波文件所有权不重叠，且没有遗漏明显可并行任务。只有不改变 DAG、Wave、Task、文件所有权、验证或验收的机械修正可直接应用。其他修改必须把 `Plan Review Status` 改为 `needs-review-after-changes`，停止并返回 writing-plans，由用户批准后再执行；不得在执行阶段静默串行化或重写计划。用户明确切换 Commit Policy 后的派生字段重物化属于已授权机械更新。
4. **派发当前 Wave** — 为每个 Task 启动一个 `general` worker；同波多 Task 必须在一次并行工具调用中派发。
5. **回收并验证** — 等待全波返回，检查范围、冲突和 worker 证据，再由主 agent 运行 Wave 验证。需要集成代码时必须由计划中的后续 Task 完成，主 agent 不临时编码。
6. **处理 Wave 失败** — 验证失败时生成 synthetic `Remediation-<Wave>-<N>` Tasks，并按依赖组织成一个或多个 Remediation Waves。每 Task 一个 `general` worker；同一 Remediation Wave 在一次 dispatch 中派发，单 Task Wave 也必须委派。修复后重跑完整原 Wave 验证；未通过前不建立边界、不进入下一 Wave。
7. **建立 Wave 边界** — 验证通过后更新计划复选框。`wave-commits` 创建恰好一个 Wave commit；`no-commits` 从临时 pre-Wave 文件快照计算增量，写入计划指定的 `Wave-N.patch` 和 `Wave-N.md`，记录 Task、snapshot ID/SHA-256、路径、patch SHA-256、验证结果和结束状态。生成 patch 和后续 diff 时排除 evidence 目录本身。
8. **最终验收与审核** — 所有 Wave 完成后运行最终验收，再向 explore reviewer 提供本次相关 diff、每 Wave commit/evidence 和验证证据。
9. **Review-Fix 流程** — 将 reviewer 的每个阻塞问题转成 synthetic `Review-Fix-R<N>-T<M>` Task，按依赖组成 `Review-Fix Wave R<N>`。每 Task 一个 `general` worker；同一 Review-Fix Wave 在一次 dispatch 中派发，单 Task Wave 也必须委派。全部修复后重跑受影响检查和最终验收。
10. **建立最终修复边界并报告** — 有实际修复时，`wave-commits` 创建一个独立最终修复 commit；`no-commits` 从临时 pre-Review-Fix snapshot 生成 `Review-Fix.patch` 和 `Review-Fix.md`，记录 snapshot/patch SHA-256、路径、修复 Task、验证结果和结束状态，并排除 evidence 目录。无修复时不创建空边界。汇总 commits/evidence、验收、审核和偏离。

## Wave 提交与异常处理

- **用户明确要求不提交：** 当前用户指令优先，切换为 `no-commits`，并使用计划的 evidence 目录；跳过 commit，不跳过 Wave evidence、验证或最终审核
- **已有无关修改：** 实现开始前保存既有未暂存和已暂存基线。只暂存当前 Wave 产生的文件或可精确隔离的 hunk；存在预先 staged 改动时，使用显式 Wave 路径限定提交，并在提交前后确认无关 staged diff 保持不变、实际 commit 只包含当前 Wave。若本 Wave 与既有改动涉及同一文件、或无法证明安全隔离，暂停并询问；不得把无关改动带入 commit
- **Git hook 失败：** 如果需要改代码，把修复委派给 `general` worker；如果 hook 自己修改了文件，也要重新检查范围。任何文件变化后都必须重新运行当前 Wave 的完整验证，再重试 commit。如果明确是无关既有问题导致，暂停并报告。禁止使用 `--no-verify`
- **提交失败：** 不进入下一 Wave。先解决失败；无法安全解决时以阻塞报告结束
- **Evidence 不可变性：** evidence 目录不属于实现 diff。普通 Wave 与 Review-Fix 的 `.patch`/`.md` 创建后均不得覆盖；同一文件跨 Wave 再修改时，后续 evidence 以自身 pre-Wave snapshot 记录增量

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
- 如果 explore 审核提出修复，修复和复验通过后，再勾选相关审核/修复/验收项
- 两种模式下，最终验收清单的最终勾选必须以统一实现审核及其修复后的复验结果为准；如果审核修复打破了之前的通过状态，撤回或保持未勾选，直到重新验证通过
- 只允许记录不改变 DAG、Wave、Task、文件所有权、验证或验收的机械修正；其他变化按步骤 3 返回 writing-plans

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
- 已由主 agent 在全部 Wave 与最终验收后统一执行一轮 explore 实现审核

Wave 边界：
- [wave-commits：Wave commit 列表；no-commits：evidence 路径和 patch SHA-256]
- 最终修复：[commit / evidence 路径 / 无修复]

与计划的偏离：
- 无
```

如果全部通过，就明确说明。如果有任何阻塞或部分完成，把它作为首要结论，不要把工作描述为完成。
