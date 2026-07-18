---
name: executing-plans
description: 已有获批执行计划并准备实现时使用。按任务耦合度选择主 agent、单 worker 或安全并行，采用计划指定的测试或验证策略，实现、验收并按用户确认的策略提交。
---

# 执行已批准计划

目标是用最少的协调成本落实计划并证明验收通过。计划是实现和验收依据，不是运行时数据库；不要为了恢复理论上的任意中断，把正常任务变成分布式事务。

## 入口检查

1. 定位用户指定或当前对话明确批准的计划；多个候选时询问，不按修改时间猜测。
2. 读取 `Plan Revision` 和 `Plan Approval Revision`，要求二者相等。兼容旧计划中的 `Plan Approval Status`：若存在且不是 `approved`，同样停止。
3. 有来源 spec 时，从计划记录的精确路径读取当前 `Spec Revision` 和 `Spec Approval Revision`，要求二者相等，并确认计划记录的来源 revision 仍是当前版本。不要比较计划中遗留的整套 spec 状态副本。
4. 没有 spec 时，要求计划包含足以执行的“实现依据”。
5. 检查 Task、依赖、验证策略和最终验收。发现产品、范围或公共接口缺口时返回 `brainstorming`；发现任务或验证缺口时返回 `writing-plans`。
6. 读取计划中的 `Review Mode`：`review` 执行最终 implementation review，`no-review` 跳过所有 subagent review；两种模式都保留主 agent 自检和用户批准门禁。

不要把多份计划自动解释成一个计划集、跨计划 DAG 或跨计划 Wave。存在多个候选时必须让用户明确指定；一次只执行当前明确指定且已批准的一份计划。用户要求统一编排相互依赖的多份计划时，返回 `writing-plans` 将它们合并为一份计划内的 Task、DAG 和 Wave；若它们应成为独立交付目标，则先返回 `brainstorming` 拆成各自的设计和验收。

旧计划中的 `Workflow Review Mode`、`Execution State`、`Resume Point`、`Execution Blocker`、`Source Document Baseline`、evidence 和 boundary 字段均视为废弃元数据，不作为恢复或批准依据，也不要求迁移后才能执行。

## 提交策略

执行前确定一次 `Commit Policy`：当前用户明确指令优先于计划记录；用户未表态且计划没有可信选择时询问，默认 `wave-commits`。只有针对提交问题的回复才算确认。

- `wave-commits`：由主 agent 在验证通过的 Wave 边界创建连贯 commit。通常每 Wave 一个；同一 Wave 有明显独立成果时可以拆成多个逻辑 commit
- `no-commits`：不提交，也不创建 patch、evidence 或 boundary 替代工件

不创建强制文档基线 commit，也不创建只包含复选框或完成状态的 finalization commit。Worker 不得进行任何 Git 写操作；只有主 agent 可以暂存和提交。

在第一个实现 commit 前，用户可以改变策略。已有实现 commit 后不改写历史；如果用户改变后续提交意图，说明当前历史并确认后续处理方式。

## 协调执行

多 Task、跨模块或包含 Wave 的计划默认由主 agent 协调，业务 Task 优先委派给 `general` worker。主 agent 负责调度、回收结果、更新 plan/TodoList/run state、Wave 验收和提交，不直接实现业务 Task；修复优先委派 repair worker。

Worker 的 Task DoD 必须包括：自查完整 diff 和 OWNED_SCOPE、逐项通过 Task 验收、运行计划中的验证命令并回传精确结果。主 agent 不重复执行 Task 级测试或逐行审 diff，只确认回传完整、changed paths 未越界，并执行必要的 Wave 级验证。

单 Task、`no-review`、无共享契约或外部副作用的 Wave，主 agent 可直接采信 worker DoD，不重跑测试或完整审 diff。`wave-commits` 仍须在提交前检查提交边界；`review` 仍按模式执行最终 implementation review。

Wave DoD：所有 Task worker 均完成且无 `blocked|unknown`，范围和依赖正确，跨 Task 验证通过。失败或异常时暂停并分类，不自动重复派发。

TodoList 只按 Wave 建项；Task 进度由 plan checkbox 和 run state 记录。Wave 完成后再更新 TodoList 和计划状态。

单一低风险 Task 可由主 agent 直接执行；有清晰边界的 Task 使用单 worker；至少两个真正独立的 Task 才并行。并行前确认写入范围、共享契约和运行资源隔离；无法证明隔离时串行或使用独立 worktree/sandbox。

## 最小运行状态

普通直接执行和单 worker 任务使用按 Wave 的会话 Todo 与计划 Task 复选框即可，不创建额外状态目录。

只有并行 worker、长时间任务或非幂等外部副作用确实需要中断对账时，才在当前仓库解析出的 Git 元数据路径下创建一个临时 run 目录，例如：

```text
git rev-parse --git-path agent-plan-state/<plan-id>/<run-id>
```

运行记录只保存：`run_id`、计划路径与 revision、`running|blocked|completed`、当前 Wave，以及每个 active dispatch 的 Task ID、宿主 task handle（如有）和 `planned|dispatched|completed|blocked|unknown` 状态。不要复制完整计划、文件内容、完整 task manifest 或每文件 hash。

中断恢复规则：

- 宿主能确认 worker 已完成：读取结果，确认 Task DoD 和范围后继续；按 Wave 规则执行必要验证
- 宿主能确认 worker 未启动或已终止：检查当前改动和外部副作用，再决定重派
- worker 结果未知：不得依靠超时猜测或重复派发；保持 blocked，并要求宿主状态或人工确认
- 文件内容与预期不一致：不要用旧 snapshot 自动覆盖，先区分 worker、用户和其他进程的改动；无法证明时阻塞
- 外部操作无法可靠幂等或清理：不自动重试

运行完成后删除当前 `run_id` 子目录；不得删除其他 run 或根据计划中保存的旧绝对路径清理目录。

## 执行流程

1. **读取项目规则和计划**：检查相关 `AGENTS.md`、贡献说明、现有架构、测试风格和可用命令。
2. **建立当前基线**：记录 `HEAD`、Git status 和本次相关 changed paths。发现 Task 涉及的路径已有无法区分的修改时询问用户，不尝试复杂的自动回滚。
3. **选择执行方式**：按上节决定主 agent、单 worker 或有界并行；需要委派时提供完整 Task 内容和项目约束。
4. **执行 Task**：只修改当前 Task 范围，采用计划指定的验证策略，不添加无关重构、抽象或依赖。
5. **回收 Task**：检查 worker DoD、回传结果和范围；单 Task `no-review` Wave 不重复 Task 验证，异常时阻塞。
6. **验证 Wave**：多 Task 或有共享契约时运行跨 Task、构建或集成检查。失败时先分类根因，不自动生成 synthetic Remediation Waves。
7. **提交边界**：`wave-commits` 下由主 agent 提交已验证的连贯改动；`no-commits` 保留工作树修改。提交失败时不进入下一 Wave。
8. **审核实现**：`review` 模式在全部 Task 完成后运行一轮 implementation reviewer；主 agent 分类，implementation findings 委派 repair worker 修复并重跑受影响验证，plan/design findings 返回上游，不自动复审。`no-review` 模式跳过该步骤。
9. **最终验收**：运行计划中的完整最终检查，记录精确命令和结果。
10. **报告结果**：列出变更、验证、审核、提交和偏离；清理当前 run 临时状态。

## 测试与验证纪律

严格执行每个 Task 选择的验证策略，但不要把 TDD 扩大到不适合的任务：

- `测试驱动`：先写或更新能因目标行为而失败的测试，确认失败原因正确，再实现并运行相关回归
- `验证驱动`：先确定可判定的目标状态，再修改并运行 schema、lint、build、dry-run、smoke、浏览器或人工检查；不要求人为制造 red
- `混合验证`：对可隔离逻辑使用测试，对视觉、真实集成或系统状态使用对应验证
- `探索验证`：遵守时间盒和决策门；结论改变后续实现时先更新计划，不把实验直接当生产实现

计划中的通用旧 TDD 样板明显不适合配置、文档、视觉、迁移或机械重构时，可以改用等强度的场景验证，并在最终报告中说明。任何会降低验收强度、删除回归保障或改变行为的调整都必须返回 `writing-plans` 或询问用户。

缺失测试不自动等于必须新增测试：只有改动确定性行为、存在合理测试设施且回归价值明确时才补。每个 Task 后运行最小相关检查，完成前运行计划要求的更广检查。

## 失败和偏离处理

先分类，再决定动作：

- **当前 Task 内的实现问题**：在原范围内做定向修复并重跑验证；无需创建新的 synthetic Task 或 Wave
- **flaky、环境或既有失败**：确认来源，能安全处理则处理；否则阻塞并报告，不把它伪装成代码修复
- **需要新增文件、依赖、行为、验收或任务**：返回 `writing-plans`
- **产品意图、范围、数据或安全决策变化**：返回 `brainstorming`，批准后再更新计划

机械调整可以直接继续，例如现有代码要求等价命名或路径变化。无法保持设计与验收不变时停止，不自行猜测。

## Git 安全

- 不修改或清理用户及其他 agent 的无关改动
- Worker 只能运行只读 Git 命令，禁止 `add`、`restore`、`checkout`、`reset`、`stash`、`clean`、`switch`、`commit` 等 Git 写操作
- 主 agent 只暂存当前连贯改动；同一文件混有无法隔离的既有修改时暂停询问
- 提交前确认实际 staged diff、当前 `HEAD` 和预期一致
- Git hook 修改文件后重新检查范围并重跑受影响验证
- 禁止使用 `--no-verify`

## 实现审核

`Review Mode=review` 时，在全部 Task 完成后使用 `implementation-reviewer-prompt.md`：

- 对当前实现做一轮独立审核
- 主 agent 委派 repair worker 修复 findings，并重跑受影响验证
- 修复后不自动派发复审

`Review Mode=no-review` 时只做主 agent 的 Wave 范围和验收确认；单 Task Wave 不重跑测试或完整审 diff。Reviewer 发现 plan 或 design 问题时返回对应上游，不让实现 worker 自行改变依据。

## 进度与最终回复

只在 Task 实现和验证通过后勾选 Task；多步骤内部过程不要求逐命令实时勾选。最终验收在所有修复和必要验证通过后勾选。

最终报告包括：

```markdown
实现结果：[完成 | 部分完成 | 阻塞]

变更：
- `path`：对应 Task 和结果

验证：
- `command / 人工步骤`：PASS/FAIL 和关键结果

审核：
- [no-review：主 agent 协调验收 | review：一轮独立审核、主 agent 委派修复并重跑受影响验证，不复审]

提交：
- [commit 列表 | 未提交]

偏离：
- [无，或验证策略/机械调整及理由]
```

任何必需验收失败或未运行时，不要声称完成。
