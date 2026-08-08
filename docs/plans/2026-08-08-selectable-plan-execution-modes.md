# 可选择的计划执行模式执行计划

**目标：** 为三阶段 skill 工作流增加 `direct | orchestrated` 两档执行模式，使简单连续任务无需 DAG/Wave 和 worker 协调，同时保留复杂任务的安全编排协议。
**来源设计：** `docs/specs/2026-08-08-selectable-plan-execution-modes-design.md`，revision 2
**计划版本（Plan Revision）：** `2`
**计划批准版本（Plan Approval Revision）：** `2`
**审核模式（Review Mode）：** `review`
**审核复杂度（Review Complexity）：** `simple`
**审核轮次（Review Rounds）：** `1 / 1`
**独立审核（Independent Review）：** `skipped-by-user revision 2`
**计划详细度（Plan Detail Level）：** `standard`，理由：默认；目标均为 Markdown 协议调整，精确章节、字段和行为规则足以实现，无需代码骨架。
**执行模式（Execution Mode）：** `direct`
**模式依据：** 沿用来源设计的 `agent-recommended` 建议；目标文件共享同一模式选择协议和术语，需要连续校准，且不存在两个同时满足独立成果、稳定契约、文件与资源隔离、协调净收益四项条件的执行成果。
**提交策略（Commit Policy）：** `wave-commits`，来源：用户明确选择；整份 direct Task 作为一个隐式提交边界，提交延迟到实现审核、修复和最终验收之后。

**最终验收：**
- [x] 三项 SKILL.md 和相关 reviewer/worker prompt 使用一致的模式字段、选择门槛、兼容规则与执行责任。
- [x] `direct` 不要求 DAG、Wave、业务/repair worker 或 Task Packet，但不降低关键决策和最终验收的充分性。
- [x] `orchestrated` 保留现有安全并行和委派协议；旧文档缺少新字段时有明确、保守的兼容行为。

## 实现依据

来源设计确定：

- spec 保存非绑定的 `Recommended Execution Mode`、理由和 `Recommendation Source`；`agent-recommended` 可由计划复核后改选，`user-preferred` 不得静默覆盖。
- 只有至少两个独立连贯成果、共享契约稳定或可先稳定、写入和运行资源可隔离、协调存在净收益四项同时成立，才推荐或选择 `orchestrated`；证据不足默认 `direct`。
- plan 保存最终 `Execution Mode` 和模式依据；模式变化属于实质计划修订。
- `direct` 由主 agent 连续执行，不建立 DAG/Wave、业务 Task Packet、worker ownership 或临时 run state；`orchestrated` 保留现有协议。
- `Review Mode`、`Plan Detail Level` 和 `Execution Mode` 相互独立。

## 实现策略

按协议流向顺序进行一次连续修改：先让 `brainstorming` 产生可靠的非绑定推荐，再让 `writing-plans` 复核并固化最终模式，最后让 `executing-plans` 按模式执行。随后同步 reviewer 和 worker prompt，避免主文档与委派提示词冲突。

现有锚点：

- `personal-skills/brainstorming/SKILL.md` 的“确认范围”“设计文档”“自检与独立审核”“下一步”。
- `personal-skills/brainstorming/spec-document-reviewer-prompt.md` 的设计完整性和范围检查。
- `personal-skills/writing-plans/SKILL.md` 的“输入与门禁”“计划边界”“Task 拆分与并行”“实现充分性门禁”“并行与 Wave”“计划头部”“必备章节”“Task 模板”“自检与可选审核”。
- `personal-skills/writing-plans/plan-document-reviewer-prompt.md` 的 Task/DAG/Wave、上下文和并行检查。
- `personal-skills/executing-plans/SKILL.md` 的“入口检查”“提交策略”“协调执行”“最小运行状态”“执行流程”“失败和偏离处理”“实现审核”“进度与最终回复”。
- `personal-skills/executing-plans/implementation-reviewer-prompt.md` 的 repair worker 输出要求。
- `personal-skills/executing-plans/general-worker-prompt.md` 的适用边界。

本次不重命名 `wave-commits`，不改变审核轮次、批准门禁、最终验收强度或 Git 安全规则，不新增第三种执行模式或 direct 专用 worker prompt。

## 关键实现契约

### C1：设计推荐字段与选择门槛

**现有锚点或新建依据：** `personal-skills/brainstorming/SKILL.md:设计文档`，基于来源设计新增字段。

**必须保持的数据形态：**

```markdown
**推荐执行模式（Recommended Execution Mode）：** `direct | orchestrated`
**推荐理由：** [成果独立性、共享契约、隔离条件和协调净收益]
**推荐来源（Recommendation Source）：** `agent-recommended | user-preferred`
```

**行为规则：**

| 条件 | 结果 |
|------|------|
| 四项 orchestrated 条件全部成立 | 可推荐 `orchestrated` |
| 条件不全或证据不足 | 推荐 `direct` |
| 仅设计复杂、风险高、模块多或 review 复杂 | 不得据此推荐 `orchestrated` |
| `Recommendation Source=agent-recommended` | 计划可基于核实证据直接改选并记录理由 |
| `Recommendation Source=user-preferred` | 计划不得静默覆盖；不安全、不可执行或显著可靠性风险时请求重新确认 |
| 旧 spec 缺少推荐或来源字段 | 视为未提供推荐；计划按完整四项门槛自行判断，不迁移旧 spec |

推荐模式、推荐理由或推荐来源的新增、移除或变化属于 spec 实质修订，必须递增 `Spec Revision`、清空批准版本并重置审核状态；现有来源 revision 门禁会使绑定旧 revision 的计划失效并要求重新核验。

**禁止偏离：** 快速路径不为了保存推荐而强制创建 spec；设计阶段不为模式推荐提前完成计划级调查；“非绑定推荐”不表示其变化可以绕过 spec revision 规则。

### C2：计划模式复核与充分性

**现有锚点或新建依据：** `personal-skills/writing-plans/SKILL.md:输入与门禁/Task 拆分与并行/实现充分性门禁`。

**必须保持的数据形态：**

```markdown
**执行模式（Execution Mode）：** `direct | orchestrated`
**模式依据：** [来源推荐及来源；沿用或改选的核实证据]
```

**行为规则：**

| 模式 | 计划结构与充分性 |
|------|------------------|
| `direct` | 一个连贯 Task 加有序步骤；无 DAG/Wave、并行边界、worker ownership、Task Packet 或 Wave 验证责任；仍固定范围、关键行为、调用与接线、边界案例、验证和禁止偏离项 |
| `orchestrated` | 保留连贯 Task、DAG、必要 Wave、跨 Task 契约、文件所有权、资源隔离、独立 DoD 和 Task Packet 充分性 |

只有从已核实锚点唯一推导、私有且局部、不会改变行为、范围或验收的 helper 名称、文件内控制流、样板实现和测试组织可留到 direct 执行。调用方、注册、导出、依赖注入、路由、迁移和跨模块接线必须在计划中固定。

没有来源 spec 推荐时，`writing-plans` 根据明确需求和定向代码调查使用同一四项合取条件选择模式，证据不足默认 `direct`；不得把新增 spec 字段变成旧 spec 的入口门禁。

**禁止偏离：** 不先生成完整 DAG/Wave 再判断模式；reviewer 对 direct 只能在完整四项条件同时成立且模式错误会实质影响执行时要求改为 orchestrated。

### C3：执行模式分支与兼容

**现有锚点或新建依据：** `personal-skills/executing-plans/SKILL.md:入口检查/协调执行/执行流程`。

**行为规则：**

| 输入 | 执行行为 |
|------|----------|
| 新计划 `Execution Mode=direct` | 主 agent 直接实现；无业务/repair worker、Task Packet、Wave Todo 或临时 run state |
| 新计划 `Execution Mode=orchestrated` | 使用现有协调、Task Packet、worker、Wave 验证和必要 run state 协议 |
| 旧计划无字段，存在多个独立执行 Task、明确 DAG/Wave 调度表或独立 worker 指令 | 兼容视为 `orchestrated` |
| 旧计划无字段且为单 Task | 兼容视为 `direct` |
| 只有 `wave-commits`、普通 Wave 文字或“隐式 Wave 1” | 不作为 `orchestrated` 证据 |
| 新字段与计划结构冲突 | 停止并返回 `writing-plans` |

`direct + review` 仍执行一轮完整 implementation review；reviewer 输出供主 agent 定向修复的信息，主 agent 修复并重跑受影响验证。`orchestrated + review` 才使用 repair worker。

**禁止偏离：** 兼容推断不回写旧计划、不触发 revision 迁移；direct 仍必须完成最终验收。

## 执行任务

### [x] Task 1：落实执行模式推荐、计划和执行协议

**目标与范围：** 修改三项 skill 及四个相关 prompt，使设计推荐、计划确认、执行分支和审核行为完整贯通；不修改辅助脚本、可视化伴侣或无关 personal skill。

**涉及文件与符号：**

- `personal-skills/brainstorming/SKILL.md`：风险分流后的模式推荐、正式设计流程、设计模板、自检和交接。
- `personal-skills/brainstorming/spec-document-reviewer-prompt.md`：推荐字段和门槛检查。
- `personal-skills/writing-plans/SKILL.md`：模式复核、两种计划结构、计划头部、模板和自检。
- `personal-skills/writing-plans/plan-document-reviewer-prompt.md`：按模式分支审核。
- `personal-skills/executing-plans/SKILL.md`：入口兼容、direct/orchestrated 执行、提交、状态、审核和报告。
- `personal-skills/executing-plans/implementation-reviewer-prompt.md`：按模式指定 finding 接收方。
- `personal-skills/executing-plans/general-worker-prompt.md`：限定为 orchestrated dispatch。

**必读上下文：** 上述文件的对应章节及本计划 C1-C3；每次编辑前核对同一术语在上游和下游的实际含义。

**建议执行方式：** 主 agent 直接执行。

**实施要点：**

1. 在 `brainstorming` 增加特征门槛、推荐来源、设计字段和自检；将“同一计划内用 Task/DAG/Wave”改为由计划阶段选择模式；明确推荐模式、理由或来源变化属于 spec 实质修订并触发现有下游 revision 门禁。
2. 在 `writing-plans` 把执行模式选择放在深入 Task/DAG/Wave 调研之前，增加计划字段与 revision 规则，并将现有 Task、Wave、Packet 要求限定到 `orchestrated`；旧 spec 缺少推荐字段时按未提供推荐处理，不要求迁移。
3. 为 `direct` 增加单 Task 有序步骤模板和充分性边界，避免把关键调用或接线推迟到执行。
4. 让 plan reviewer 使用完整四项门槛并按模式分支，既不因 direct 无 Wave 而阻塞，也不放松关键决策核实。
5. 在 `executing-plans` 先解析模式及旧计划兼容，再进入对应执行分支；更新 Todo、run state、提交、review/repair 和最终验收规则。
6. 同步 implementation reviewer 和 general worker prompt，消除 direct 仍要求 repair worker 的冲突。
7. 全局检查新增字段和术语，确认没有残留“所有多 Task/跨模块默认委派”或“direct 需要 Wave”的无条件规则。

**行为与检查案例：**

| 场景 | 输入/准备 | 预期结果或断言 |
|------|-----------|----------------|
| 集中但高风险的单一迁移 | `review + guided`，共享同一文件与验证闭环 | 可推荐并计划为 `direct`；风险不会自动触发 orchestrated，关键迁移和恢复规则仍提前固定 |
| 三个隔离平台适配 | 独立成果、稳定接口、文件和资源隔离、并行有净收益 | 推荐并计划为 `orchestrated`，保留 Task/DAG/Wave 和 Packet |
| agent 推荐 direct，计划发现四项条件齐备 | `Recommendation Source=agent-recommended` | 计划可改选 orchestrated，记录证据，不回改 spec |
| 用户偏好 direct，但计划发现显著可靠性风险 | `Recommendation Source=user-preferred` | 停止并请求重新确认，不静默改选 |
| 旧 spec 缺少推荐模式或推荐来源 | 已批准旧 spec，需求和验收明确 | `writing-plans` 按完整四项门槛自行选择，不阻塞、不迁移旧 spec |
| 已批准 spec 的推荐或来源发生变化 | 新增、移除或改变任一推荐元数据 | 作为实质修订递增 Spec Revision，并使绑定旧 revision 的计划需要重新核验 |
| 旧单 Task 计划含 `wave-commits` 和“隐式 Wave 1”文字 | 无 `Execution Mode` | 执行器兼容视为 direct |
| direct 实现审核发现 implementation finding | `Execution Mode=direct` | reviewer 输出给主 agent 的修复范围和验证；不派 repair worker |

**禁止偏离：**

- 不增加评分制或按 simple/medium/complex 直接映射模式。
- 不增加 `delegated-serial` 等第三模式。
- 不重命名提交策略或改动审核轮次、批准门禁、Git 安全规则。
- 不让 direct 绕过 implementation review 或最终验收。

**验收标准：**

- C1-C3 在所有相关文件中的字段名、选择条件和责任一致。
- 所有无条件 Wave/worker 规则都被正确限定或保留为旧计划兼容说明。
- direct 与 orchestrated 的正反场景均能从文档得到唯一执行结果。

**验证策略：** 验证驱动；这是 Markdown 工作流协议修改，没有运行时代码或合适的 red-green 测试设施，使用精确搜索、结构审查、场景对照和独立 implementation review。

**验证：**

- `git diff --check`，预期无空白错误。
- 搜索 `Recommended Execution Mode|Recommendation Source|Execution Mode|direct|orchestrated`，逐项确认字段只出现在适用文档且语义一致。
- 搜索 `DAG|Wave|Task Packet|repair worker|主 agent`，确认所有调度规则均按执行模式限定，没有残留冲突。
- 检查 brainstorming 的 revision 规则明确覆盖推荐模式、理由和来源的新增、移除与变化，并确认 writing-plans 不把新增推荐字段作为旧 spec 入口门禁。
- 对照全部行为与检查案例逐项只读检查，预期每个案例能得到唯一、符合 C1-C3 的结果。

**完成版本：** `Plan Revision 2`

## 最终验收

1. 运行 `git diff --check`，必须 PASS。
2. 检查本次 changed paths 仅包含获批设计、计划和 Task 1 声明的七个目标 skill/prompt 文件，以及实施过程必要的批准元数据更新。
3. 对照 `docs/specs/2026-08-08-selectable-plan-execution-modes-design.md:180-192` 的全部验收标准，确认每项均映射到实际规则。
4. 运行一轮 FULL implementation review；`direct` 模式的 implementation finding 由主 agent 修复并重跑受影响检查，plan/design finding 返回上游。
5. 再次检查关键词和最终 diff，确认 `Review Mode`、`Plan Detail Level`、`Execution Mode` 正交，旧计划兼容不会被 `wave-commits` 或普通 Wave 文字误触发。
