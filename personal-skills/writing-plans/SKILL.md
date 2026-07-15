---
name: writing-plans
description: 已有获批设计文档或 spec、尚未进入实现时使用。生成按依赖 DAG 和最大安全并行度组织的 Wave 执行计划，并确定提交策略、验证边界和验收证据。
---

# 编写执行计划

## 概览

编写无需执行者猜测核心决策的计划：明确设计依据、文件所有权、接口形态、任务依赖、测试命令和验收证据。把任务 DAG 组织成尽可能宽且安全的 Wave，并为每个 Wave 定义可恢复边界。

假设执行者是熟练开发者，但几乎不了解我们的工具链和业务领域。也假设他们不一定擅长测试设计。

**开始时说明：** “我正在使用 writing-plans skill 创建执行计划。”

**计划保存到：** `docs/plans/YYYY-MM-DD-<feature-name>.md`

- 如果用户指定其他计划路径，以用户偏好为准

## 必需输入

执行计划应基于已批准的设计文档或 spec。开始前定位来源设计文档，通常是 `docs/specs/YYYY-MM-DD-<topic>-design.md`，并读取 `Workflow Review Mode` 和 `Spec Review Status`。

如果用户只有需求描述、没有设计文档，默认建议先使用 `brainstorming`。只有用户明确要求跳过 spec 时才继续：计划头部写 `来源设计文档：无（用户明确跳过）`，并增加 `实现依据（无 spec）` 章节，记录已确认需求、假设、设计决策、范围和验收标准。该章节是后续 worker 与实现 reviewer 的 `SPEC_CONTEXT`，不得留空。

入口状态处理：

- `lightweight`、`explore-reviewed`、`not recorded`：可继续；`not recorded` 仅适用于用户明确跳过 spec
- `explore-pending`、`review-blocked`：停止，先完成或解决上游审核
- `needs-review-after-changes`：提示用户选择返回补审，或明确接受未复审风险继续；继续时原样保留该状态，不得伪装成已审核

## 工作流审核模式

有效审核模式优先级为：**当前用户明确指定 > 设计文档记录 > 默认 `lightweight`**。计划头部写入该 effective mode；`Spec Review Status` 原样复制，二者不得混淆。模式只控制当前计划文档是否增加 explore 审核，不改变 executing-plans 的固定实现协议。

- `lightweight`：计划只做主 agent 自检，写 `Plan Review Status: lightweight`
- `explore-review`：计划初始写 `explore-pending`；自检后按 canonical `plan-document-reviewer-prompt.md` 派发一次 explore 审核。缺少 explore 能力时写 `review-blocked` 并停止，不得降级
- reviewer 的“问题”由主 agent 在不改变设计时修复并自检；需改变设计、范围或验收时写 `review-blocked` 并询问用户。“建议”默认只报告，不自动实施
- 阻塞发现处理完并通过自检后写 `explore-reviewed`，含义与 spec 阶段一致：一轮审核完成、发现已修复并由主 agent 自检，不表示 reviewer 再看过修复版本
- 本轮结束后发生实质修改时写 `needs-review-after-changes`；默认不追加第二轮，除非用户明确要求

`Plan Review Status` 可用值：`lightweight`、`explore-pending`、`explore-reviewed`、`review-blocked`、`needs-review-after-changes`。完整 reviewer 指令和输出格式只在 `plan-document-reviewer-prompt.md` 维护。

## 提交策略与源文档基线

`Commit Policy` 优先级为：**当前用户明确指定 > 项目明确流程 > 默认 `wave-commits`**。

- `wave-commits`：每个 Wave 验证通过后由主 agent 创建恰好一个 commit。计划生成时 `Source Document Baseline` 写 `pending`；执行前，获批 spec（如有）和 plan 必须先形成独立、干净的文档基线。执行器随后把实际 baseline commit hash 写回计划，该元数据与计划勾选更新归入 Wave 1 commit。若不能安全建立基线，询问用户切换为 `no-commits`
- `no-commits`：不创建任何实现或修复 commit。每个 Wave 必须从临时 pre-Wave 文件快照计算增量 patch，并将 patch 与验证记录写入 `docs/plans/<plan-name>-wave-evidence/Wave-N.{patch,md}`；记录 snapshot ID 和 SHA-256，后续 Wave 不得覆盖已有 evidence

## 范围检查

如果设计文档覆盖多个独立子系统，头脑风暴阶段本应拆成多个子项目规格。如果没有拆，建议拆成多份计划，每个子系统一份。每份计划都应该独立产出可运行、可测试的软件。

## 文件结构

在定义任务前，先梳理要创建或修改哪些文件，以及每个文件负责什么。这一步锁定拆分决策。

- 设计边界清晰、接口明确的单元。每个文件应该只有一个明确职责
- 你更擅长处理能放进上下文的小段代码；文件职责集中时，编辑更可靠。优先使用小而聚焦的文件，避免一个大文件承担太多职责
- 会一起变化的文件应该放在一起。按职责拆分，而不是机械地按技术层拆分
- 在现有代码库中，遵循既有模式。如果代码库本来就是大文件风格，不要单方面重构；但如果你要修改的文件已经明显臃肿，把拆分纳入计划是合理的

这个结构会影响任务拆分。每个任务都应该产生自洽、可独立理解的变更。

## 并行任务拆分与 Wave

先根据代码库的实际工程特征建立任务依赖 DAG，再把任务组织成**最大安全并行**的拓扑 Wave。探测：是否 monorepo、前后端是否分离、模块边界是否清晰、哪些文件会一起变化。不要默认串行，也不要为了并行而硬拆。

**Wave 定义：**

1. 每个 Task 必须且只能属于一个 `Wave N`；即使整个计划只有一个 Task，也必须有 `Wave 1`。
2. `Wave 1` 包含所有无依赖且可安全并行的 Task；后续 Wave 包含其全部依赖均已位于更早 Wave 的 Task。
3. 同一 Wave 的 Task 必须一次性并行派发给独立的 `general` workers；单 Task Wave 也按同一委派协议执行。
4. 共享契约、接线和端到端集成也必须是明确 Task，并放入符合依赖关系的 Wave；不要保留由主 agent 直接编码的隐式“串行阶段”。
5. 每个 Wave 完成后形成事务边界：主 agent 回收结果、检查范围和冲突、运行 Wave 验证并更新计划。`wave-commits` 时为该 Wave 创建恰好一个 commit；`no-commits` 时持久化该 Wave 的 patch 和验证证据。`general` worker 永远不提交。

**最大安全并行不是可选优化：** 在满足安全前提时，必须把 Task 放入最早可执行的 Wave。不得因为书写方便或习惯而把互不依赖的 Task 排进连续的单任务 Wave。如果本次只能串行，必须写明阻止并行的具体文件冲突或数据依赖。

**同一 Wave 的安全前提，全部满足才可并行：**

- **契约先行**：共享类型/接口/schema 已由更早 Wave 的 Task 定死，同波 Task 只依赖契约、不依赖彼此实现
- **文件所有权隔离**：同波 Task 的新建、修改和测试文件集合不重叠；无法隔离时必须拆到不同 Wave
- **无数据依赖**：一个 Task 不需要另一个 Task 的运行结果或产出

**必须有显式汇合点**：需要接线、跨边界联调或端到端代码修改时，把它写成后续集成 Task，并委派给 `general`；纯验证性质的 Wave 级集成检查由主 agent 执行。不要让主 agent 临时补写计划外集成代码。

**常见可并行场景（结合工程结构判断，不要生搬）：**

- 文档 vs 代码；配置/基础设施（CI、Dockerfile、IaC）vs 应用代码；i18n/翻译、种子/mock 数据 vs 功能代码
- 前端 vs 后端；monorepo 里多个独立 package；多个微服务；SDK 多语言实现、多端实现，共享同一 spec
- 多个互不依赖的功能模块；多个独立 endpoint/handler（只共享路由注册）；组件库里多个独立组件；无交叉外键的多个数据模型；共享同一接口的多个插件/适配器
- 一个计划里打包的多个独立 bug 修复；对多文件做同一机械改动（rename、import 迁移）可分片

**不可并行，必须串行：**

- TDD 单元内的“写测试 → 确认失败 → 写实现 → 确认通过”是顺序的，不要拆到不同并行 Task
- 依赖尚未确定的共享契约定义与其消费者不能同波
- 最终集成代码与其所集成的实现 Task 不能同波
- 有明确顺序或数据依赖的任务链

如果工程结构决定这次改动本质是串行的（例如全部集中在一个文件或存在强顺序依赖），就使用连续的单 Task Wave，并在实现摘要里逐项说明为什么不能合并到同一 Wave。不要为了并行而制造人为拆分。

## 设计与决策映射

写任务前，先从设计文档中提取与实现相关的决策。好的计划能追溯到设计：每个重要需求或决策都应该指向一个或多个具体任务。

在计划中包含这个映射：

```markdown
## 设计决策到任务的映射

| 设计需求/决策 | 实现任务 | 验证方式 |
|---------------|----------|----------|
| [设计文档中的决策] | 任务 N | [测试、命令、UI 检查或人工验收步骤] |
```

如果设计文档中存在阻塞计划的缺失或矛盾决策，停下来询问澄清，不要自行编造细节。

## 小步任务粒度

每一步只做一个可独立验证的动作；不要用机械的分钟目标拆出大量无意义步骤：

- “写失败测试”是一步
- “运行测试确认它失败”是一步
- “写最小实现让测试通过”是一步
- “运行测试确认通过”是一步
- Task 内不包含 commit；是否提交由主 agent 在整个 Wave 验证通过后按 `Commit Policy` 处理

## 计划文档头部

**每份计划都必须以这个头部开始：**

状态字段必须写入单个实际值，不要在最终计划中保留多个候选值或条件说明。

`Workflow Review Mode` 写按优先级计算出的 effective mode；`Spec Review Status` 原样复制来源事实。

```markdown
# [功能名称] 执行计划

> 步骤使用复选框（`- [ ]`）语法，便于跟踪进度。

**目标：** [一句话说明要构建什么]

**架构：** [2-3 句话说明实现思路]

**技术栈：** [关键技术/库]

**来源设计文档：** [`docs/specs/YYYY-MM-DD-topic-design.md`]

**工作流审核模式（Workflow Review Mode）：** `<effective mode：当前用户明确指定 > 设计文档记录 > lightweight>`

**规格审核状态（Spec Review Status）：** `<从来源设计文档复制实际值；无来源设计文档时写 not recorded>`

**计划审核状态（Plan Review Status）：** `<lightweight 模式写 lightweight；explore-review 模式初始写 explore-pending>`

**提交策略（Commit Policy）：** `<wave-commits 或 no-commits；记录决定来源>`

**源文档基线（Source Document Baseline）：** `<wave-commits：pending，执行时写回 commit hash；no-commits：not-applicable>`

**Wave 证据目录（Wave Evidence Directory）：** `<no-commits：docs/plans/<plan-name>-wave-evidence/；wave-commits：不适用>`

**实现 Worker：** 所有 Task 均由独立的 `general` worker（`subagent_type=general`）执行

**主要验收标准：**
- [ ] [必须成立的具体用户可见行为或系统行为]
- [ ] [具体集成或回归要求]
- [ ] [具体测试/构建/lint 期望]

---
```

## 必备计划章节

每份计划在任务列表前都必须包含这些章节：

```markdown
## 实现摘要
[简要说明实现策略、依赖 DAG 和 Wave 顺序。列出每个 Wave 的 Task、可并行理由和汇合点；如果全部是单 Task Wave，说明阻止并行的具体原因。]

## 实现依据（无 spec 时必需）
[用户明确跳过 spec 时，记录已确认需求、假设、设计决策、范围和验收标准；有 spec 时删除本章节。]

## Wave 执行总览
[用表格列出 Wave、Task、前置依赖、同波文件所有权、验证命令，以及 `wave-commits` 下的 commit message 或 `no-commits` 下的 evidence 文件路径。]

## 设计决策到任务的映射
[用表格把设计决策/需求映射到任务和验证方式。]

## 文件结构
[要创建/修改的文件、职责和重要接口。]

## 关键接口与代码形态
[核心类型、函数签名、组件 props、API 合约、数据模型，以及后续任务必须遵循的代表性代码片段。]

## 执行任务
[按 Wave 组织详细复选框 Task。同一 Wave 的所有 Task 必须可在一次并行 dispatch 中启动；每个 Task 都由独立的 `general` worker 执行。]

## 最终验收清单
[严格、可执行的检查，用于证明整个计划完成。]
```

## 关键代码片段

计划不应该用大段伪代码替代实现，但必须包含足够的代码形态，让实现者不需要猜核心结构。

包括这些片段：

- 核心类型、schema、接口、组件 props、API 合约或数据模型
- 主要控制流或编排函数
- 一个代表性的 happy-path 测试，以及一个重要失败/边界场景测试
- 容易写错的迁移、配置、路由、命令或集成点

共享接口和代表性代码在本章节定义一次，作为后续 Task 的 canonical 来源。每个 Task 可引用这里的精确小节，并只补任务特有代码；不要复制同一接口到多个 Task。避免使用 `// ...` 这类占位，除非省略的是已有且不变的代码，并明确说明。

## 任务结构

````markdown
### 任务 N：[组件名称]

**执行波次：** Wave W

**可并行对象：** [同一 Wave 内可同时派发的其他 Task；没有则写“无（单 Task Wave：具体原因）”]

**依赖：** [必须位于更早 Wave 的任务编号，例如“任务 1（契约）”；无依赖写“无”]

**文件：**
- 新建：`exact/path/to/file.py`
- 修改：`exact/path/to/existing.py:123-145`
- 测试：`tests/exact/path/to/test.py`

**设计关联：** [此任务实现的需求/决策]

**验收标准：**
- [ ] [此任务的可执行或可直接观察标准]
- [ ] [回归/边界场景标准]

- [ ] **步骤 1：编写失败测试**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **步骤 2：运行测试，确认它失败**

运行：`pytest tests/path/test.py::test_name -v`
期望：失败，错误信息包含 "function not defined"

- [ ] **步骤 3：编写最小实现**

```python
def function(input):
    return expected
```

- [ ] **步骤 4：运行测试，确认通过**

运行：`pytest tests/path/test.py::test_name -v`
期望：通过

- [ ] **步骤 5：验证任务验收标准**

运行：`[精确命令或人工检查]`
期望：`[严格的预期结果，包括输出/状态/UI 状态]`

- [ ] **步骤 6：向主 agent 回传结果**

回传：修改文件、验收标准状态、运行命令及结果、遗留风险。禁止 worker 创建 commit。
````

## 禁止占位

每一步都必须包含工程师需要的实际内容。下面这些都是**计划失败**，不要写：

- “TBD”、“TODO”、“后续实现”、“补充细节”
- “添加适当错误处理” / “添加校验” / “处理边界情况”
- “为上面内容写测试”，但没有实际测试代码
- “类似任务 N”这类含糊引用；可以引用“关键接口与代码形态”的精确小节，但必须补齐当前 Task 特有内容
- 只描述要做什么但不展示怎么做的步骤。涉及代码的步骤必须有足够明确的代码块，至少覆盖关键接口、签名、控制流或代表性测试
- 引用了任何任务中都没有定义的类型、函数或方法
- 验收标准写“正常工作”“处理错误”“测试通过”，但没有具体行为、命令和预期结果
- 关键实现决策只隐含在设计文档中，没有映射到任务

## 自检

写完整份计划后，换个视角重新看设计文档，并对照检查计划。这是主 agent 自检，不是 subagent 审核。

**1. 设计覆盖：** 快速浏览设计文档的每个章节/需求。每个需求能否指向一个实现任务？列出缺口。

**2. 占位符扫描：** 搜索计划中的红旗，例如“禁止占位”章节中的所有模式。修复它们。

**3. 类型一致性：** 后续任务中使用的类型、方法签名、属性名是否和前面定义一致？任务 3 叫 `clearLayers()`，任务 7 叫 `clearFullLayers()`，这就是 bug。

**4. 决策可追溯：** 每个重要设计决策是否出现在“设计决策到任务的映射”里，并且都有验证方式？补齐缺口。

**5. 代码充分性：** 实现者能否依靠包含的片段、签名和示例写出预期方案，而不用发明核心接口？补上缺失片段。

**6. 验收严格性：** 验收标准是否可执行、可判定真假？把含糊检查替换成精确命令、预期输出、UI 状态、API 响应或文件 diff。

**7. DAG 合法性：** 每个 Task 是否恰好属于一个 Wave？所有依赖是否位于更早 Wave？是否存在循环依赖、同波依赖或遗漏依赖？发现后调整 DAG 和 Wave。

**8. 最大安全并行：** 对每个 Task 判断它是否已经位于依赖允许的最早 Wave。逐条核对同波共享契约、完整文件所有权和隐藏数据依赖。若两个 Task 安全且互不依赖，却被无理由拆成连续 Wave，计划自检失败，必须合并。

**9. 汇合完整性：** 并行实现后需要的接线和集成代码是否成为后续 `general` Task？Wave 级验证是否覆盖跨边界和端到端行为？不要把代码集成隐式留给主 agent。

**10. 边界策略：** 计划头部是否记录实际 `Commit Policy`、决定来源、Source Document Baseline 和 Wave Evidence Directory？`wave-commits` 下每个 Wave 是否有唯一 commit message，且 Task 内没有 commit？`no-commits` 下是否为每个 Wave 指定不可覆盖的 `.patch` 和 `.md` evidence 路径？

发现问题时直接修复并重新自检；设计需求没有任务时补充任务。若计划已是 `explore-reviewed`，本轮结束后的实质修改必须改为 `needs-review-after-changes`；默认不再派第二轮审核。

## 完成

保存计划后，告诉用户：

**“计划已完成并保存到 `docs/plans/<filename>.md`。请审核。准备实现时，使用 executing-plans skill；它会按 Wave 委派 `general` workers、验证并建立 commit/evidence 边界，最后统一运行一次 explore 实现审核。”**

计划阶段到此结束。建议 `executing-plans` 作为自然下一步，但不要自动调用它；由用户决定什么时候开始实现。
