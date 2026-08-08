# 可选择的计划执行模式设计

**规格版本（Spec Revision）：** `2`
**规格批准版本（Spec Approval Revision）：** `2`
**审核模式（Review Mode）：** `review`
**审核复杂度（Review Complexity）：** `simple`
**审核轮次（Review Rounds）：** `1 / 1`
**独立审核（Independent Review）：** `skipped-by-user revision 2`
**推荐执行模式（Recommended Execution Mode）：** `direct`
**推荐理由：** 本次修改跨三个 skill，但文件少、共享上下文强、规则需要连续校准，拆成并行 worker 的协调收益不足。
**推荐来源（Recommendation Source）：** `agent-recommended`

## 目标与范围

扩展 `brainstorming`、`writing-plans` 和 `executing-plans`，让计划根据任务特征选择两种执行模式：

- `direct`：主 agent 在连续上下文中按有序步骤直接实施，不建立 DAG、Wave 或业务 Task Packet。
- `orchestrated`：按连贯成果拆 Task，建立必要 DAG 和 Wave，并在委派时生成自包含 Task Packet。

设计阶段只给出非绑定推荐；计划阶段结合已核实的代码锚点、依赖和真实并行收益确定最终模式。此次不增加第三种串行 worker 模式，不改变现有 `Review Mode` 或 `Plan Detail Level` 的含义。

## 已确认决策

### 模式与其他维度独立

新增 `Execution Mode`，不把它合并到审核模式或计划详细度：

- `Review Mode` 决定是否派发独立 reviewer。
- `Plan Detail Level` 决定计划需要展开多少高熵实现信息。
- `Execution Mode` 决定是否需要 Task/DAG/Wave、业务 worker 和相应协调协议。

允许任意合理组合，例如高风险但集中修改可以使用 `direct + review + guided`，多个低风险且隔离的平台适配可以使用 `orchestrated + no-review + standard`。

### 设计阶段按特征推荐，默认 direct

`brainstorming` 在正式设计中根据已知设计复杂度和结构给出 `Recommended Execution Mode` 及理由，但不为了推荐模式提前完成计划级代码调研。

只有已知信息同时支持以下特征时，才推荐 `orchestrated`：

- 至少两个值得分别占用完整 worker 上下文的连贯成果；
- 成果之间的共享契约已经稳定或可先稳定；
- 预计写入范围和运行资源能够隔离；
- 并行、隔离、专业上下文或独立验收收益可能高于 Task Packet、重复加载和集成成本。

证据不足、步骤共享大量上下文、集中修改同一批文件或共享同一验证闭环时推荐 `direct`。设计风险高、模块数量多或审核复杂度高，本身都不构成 `orchestrated` 的充分条件。

快速路径不强制生成正式设计，也不为了保存推荐而创建 spec。若快速路径后来确实需要书面计划，由 `writing-plans` 直接选择模式。

设计文档同时记录 `Recommendation Source`：

- `agent-recommended`：agent 根据设计特征给出的非绑定推荐，计划可基于核实证据直接改选并记录理由。
- `user-preferred`：用户明确指定的执行偏好。计划不得静默覆盖；若代码调查显示该模式不安全、不可执行或有显著可靠性风险，必须说明证据并请求用户重新确认。

用户偏好仍不是产品或工程设计契约，但其新增、移除或变化会改变执行选择依据，因此按设计文档实质修订处理。

### 计划阶段复核并最终确定

`writing-plans` 在深入研究 Task DAG 和 Wave 之前选择模式：

1. 读取 spec 中的推荐与理由，或在无 spec 时根据明确需求形成初始推荐。
2. 只做足以判断执行拓扑的定向调查，核实成果边界、共享上下文、写入范围、依赖和隔离条件。
3. 使用相同特征门槛确定最终 `Execution Mode`，默认 `direct`。
4. 若 `Recommendation Source=agent-recommended`，最终模式可以不同于 spec 推荐；计划记录计划层证据和改选理由，这不是设计语义变化，不要求修改或重新批准 spec。
5. 若 `Recommendation Source=user-preferred`，沿用该模式；只有发现不安全、不可执行或显著可靠性风险时才暂停并请求用户重新确认，不得自行改选。
6. 若调查暴露产品、公共接口、数据或安全决策缺口，仍返回 `brainstorming`。

不先完成足以生成完整 DAG/Wave 的全面调查，再决定是否需要 `orchestrated`。模式选定后才按对应充分性标准继续调研和编写计划。

## 设计

### brainstorming

正式设计文档增加：

```markdown
**推荐执行模式（Recommended Execution Mode）：** `direct | orchestrated`
**推荐理由：** [基于成果独立性、共享契约、隔离条件和协调净收益；不得只写“任务复杂”]
**推荐来源（Recommendation Source）：** `agent-recommended | user-preferred`
```

调整范围确认和下一步说明：同一 spec 下的多步骤工作由 `writing-plans` 选择执行模式；只有 `orchestrated` 使用 Task、DAG 和必要 Wave。设计自检增加一项，检查推荐是否基于执行特征，而非把设计复杂度、审核模式或模块数量直接映射成并行。

该推荐只适用于正式设计文档，不成为计划入口门禁；`agent-recommended` 不需要由计划原样继承，`user-preferred` 则按前述重新确认规则处理。旧 spec 缺少推荐或来源字段时视为“未提供推荐”，由 `writing-plans` 自行判断，不要求迁移。

### writing-plans

计划头部增加：

```markdown
**执行模式（Execution Mode）：** `direct | orchestrated`
**模式依据：** [设计推荐及来源；沿用理由，或允许改选时基于已核实依赖、隔离与协调净收益给出的理由]
```

计划依据中记录来源 spec 的推荐，但 `Execution Mode` 是计划自身的最终决定。模式及模式依据变化会改变任务结构和执行协议，属于实质计划修订。

#### direct 计划

- 适用于一个主 agent 连续完成、共享上下文和验证闭环强、委派净收益不足的工作。
- 使用一个连贯执行 Task，内部列出有序实施步骤；步骤不是独立 Task，不要求分别具备 worker 级 DoD。
- 不创建依赖 DAG、Wave 表、并行边界、文件级 worker ownership、Task Packet 或 Wave 验证责任。
- 仍需列出精确影响范围、已知锚点、影响正确性的契约与行为、重要边界案例、禁止偏离项、验证策略和最终验收。
- 公共或跨模块接口、schema、错误语义、状态转换、安全、迁移、幂等及不可逆副作用必须在计划前固定。
- 只有可从计划已核实的锚点唯一推导、私有且局部、不会改变行为、范围或验收的 helper 名称、文件内控制流、样板实现和测试组织，才可以由主 agent 在执行中确定。调用方以及注册、导出、依赖注入、路由、迁移和跨模块接线仍须在计划中固定。

#### orchestrated 计划

保留现有完整协议：按连贯成果拆 Task，建立 DAG，安排有净收益且安全的 Wave，固定跨 Task 契约、文件级写入范围、运行资源隔离、独立 DoD 和 Task Packet 所需信息。选择 `orchestrated` 不等于强制最大并行；无法安全并行的相邻 Task 可以串行或复用 worker 会话。

计划 reviewer 按 `Execution Mode` 分支检查。对 `direct` 不要求 DAG、Wave 或证明已经榨取所有并行机会；除用户明确偏好外，只有“至少两个独立连贯成果、共享契约稳定或可先稳定、写入及运行资源可隔离、协调存在净收益”四项同时成立，且模式错误足以影响执行可靠性或成本时，才把应改为 `orchestrated` 列为阻塞问题。对 `orchestrated` 保留现有 DAG、Wave、ownership、隔离和 Task Packet 充分性检查。

### executing-plans

入口读取 `Execution Mode`：

- 旧计划缺失时根据调度结构兼容读取：存在多个独立执行 Task、明确的依赖 DAG/Wave 调度表或独立 worker 指令时视为 `orchestrated`；旧单 Task 计划视为 `direct`。`wave-commits` 字段、普通叙述中的 Wave 字样以及“单 Task 等同隐式 Wave 1”都不构成 `orchestrated` 证据。该兼容推断不回写计划，也不要求仅为元数据迁移而提高 revision。
- 新计划字段与内容冲突时停止并返回 `writing-plans`，不在执行阶段静默改选。

`direct` 执行协议：

- 主 agent 直接执行，不派发业务 worker，不生成 Task Packet，不建立按 Wave 的 Todo 或临时 run state。
- 使用一个实现 Todo 和必要的验证 Todo 即可；计划内部步骤可以顺序完成，不按步骤创建提交或独立状态。
- 执行中可以继续核实计划明确允许延后的私有实现细节，但不得改变公共契约、行为、范围或验收。
- `review` 模式仍派发一轮完整 implementation reviewer；dispatch 时传入 `Execution Mode`。Reviewer 在 `direct` 下输出供主 agent 定向修复的文件范围、验收和验证信息，在 `orchestrated` 下才输出 repair worker Packet 所需约束。`direct` 的 implementation finding 由主 agent 在原范围内修复并重跑受影响验证。
- 最终执行计划级验收；只有所有必需验证通过后才能报告完成。

`orchestrated` 执行协议继续使用当前主 agent 协调、Task Packet、业务 worker、Wave 验证、必要 run state 和 repair worker 规则。

同步修改 `implementation-reviewer-prompt.md`，使其按 `Execution Mode` 分支描述修复接收方；`general-worker-prompt.md` 明确只适用于 `orchestrated` 的业务或 repair dispatch。无需为 `direct` 新建 worker prompt。

### 提交策略

本次不重命名 `wave-commits`，避免把执行模式改造扩大为持久化提交策略迁移。补充模式相关语义：

- `direct + wave-commits`：将整份 direct Task 视为一个隐式提交边界，通常在实现审核、修复和最终验收后创建一个连贯 commit。
- `orchestrated + wave-commits`：保持当前按已验证 Wave 边界提交的规则。
- `no-commits`：两种模式都不提交。

后续若需要更中性的命名，可单独设计 `checkpoint-commits` 及旧字段兼容，不纳入本次范围。

## 工程契约

### 字段所有权

| 字段 | 所属文档 | 约束 |
|------|----------|------|
| `Recommended Execution Mode` | spec | 非绑定推荐；旧 spec 可缺失 |
| `推荐理由` | spec | 设计层特征，不包含计划级虚构证据 |
| `Recommendation Source` | spec | 区分 agent 推荐与用户明确偏好，决定计划能否直接改选 |
| `Execution Mode` | plan | 执行器必须遵守的最终模式 |
| `模式依据` | plan | 说明沿用或改选设计推荐的代码与依赖证据 |

spec 的推荐或来源变化属于设计文档实质修订。按照现有来源 revision 门禁，任何 spec 实质修订都会使绑定旧 spec revision 的计划失效并要求重新核验；“非绑定”只表示计划可以按规则改选模式，不表示 spec revision 变化不会影响下游门禁。已批准 plan 的 `Execution Mode` 变化属于计划实质修订，必须递增 `Plan Revision`、清空批准状态并重新经过计划审核与批准门禁。

### 模式选择判定

推荐和最终选择都使用同一原则：

```text
Recommendation Source=user-preferred 且可安全执行
  -> 使用用户偏好
否则，至少两个独立连贯成果
  AND 共享契约稳定或可先稳定
  AND 写入与运行资源可隔离
  AND 委派、并行、专业上下文或独立验收存在净收益
  -> orchestrated
否则
  -> direct
```

用户明确要求 `orchestrated` 但隔离条件不成立时，不应伪造并行边界；说明冲突并请求改用 `direct` 或先调整设计。用户明确要求 `direct` 但单主 agent 执行会造成明显上下文、隔离或可靠性风险时，说明风险并在写计划前请求确认。没有 `user-preferred` 约束时，agent 只能按完整四项合取条件推荐或选择 `orchestrated`。

## 风险与约束

- 如果 `direct` 充分性规则放宽过度，执行阶段可能重新发明关键行为。通过只允许延后私有、局部、不会改变范围和验收的实现细节控制。
- 如果推荐规则把“多个模块”直接视为并行，会恢复当前过度调研问题。规则必须要求独立成果、稳定契约、隔离和净收益同时成立。
- 如果计划执行器仍看到“多步骤”就默认委派，新字段不会生效。`executing-plans` 必须先按字段分支，再应用 worker 选择规则。
- 旧计划没有新字段。兼容推断只用于执行入口，不能反向制造迁移工作或改变已批准计划内容。
- 本次不改变 review revision、批准门禁、最终验收强度或 Git 安全规则。

## 验收标准

- 正式设计会给出 `direct` 或 `orchestrated` 的非绑定推荐及基于特征的理由，且证据不足时默认为 `direct`。
- 计划在建立 DAG/Wave 前复核推荐，并持久化最终 `Execution Mode` 和模式依据。
- `direct` 计划不要求 DAG、Wave、Task Packet 或 worker 文件所有权，但仍固定影响行为和验收的关键决策。
- `direct` 计划由主 agent 连续执行，不派发业务或 repair worker；`review` 和最终验收仍按计划执行。
- `orchestrated` 保留现有安全并行、Task Packet、Wave 验证和运行状态协议。
- 计划 reviewer 根据模式使用对应检查项，不因 `direct` 缺少 Wave 而提出问题。
- `Recommendation Source` 能区分 agent 推荐与用户明确偏好；计划只能直接改选前者，后者需要用户重新确认。
- `direct` 只能延后可从已核实锚点唯一推导且不改变行为、范围或验收的私有局部细节；关键调用与接线位置仍在计划中固定。
- implementation reviewer 按执行模式提供修复信息；`direct` 交给主 agent，`orchestrated` 才交给 repair worker。
- 旧 spec 和旧 plan 在缺少新增字段时仍可按明确兼容规则使用。
- `Review Mode`、`Plan Detail Level` 与 `Execution Mode` 保持正交，不根据设计复杂度自动绑定。
