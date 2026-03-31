# self-improving-agent

> 一个让 AI coding agent 具备“持续自我改进”能力的 skill。
>
> **一句话概括**：它把 agent 在工作中遇到的错误、纠正、知识盲区、最佳实践和功能缺口，沉淀为结构化的外部记忆，并把高价值经验逐步提升为长期规则，甚至提炼成新的 skill。

---

## 先说明一件事

这个目录里真正会被 agent 加载和执行的是 `SKILL.md`，而不是本 README。

- `SKILL.md`：给 agent 看的运行说明
- `README.md`：给人看的原理说明

也就是说，**这个 skill 的运行入口是 `SKILL.md`，本文件的作用是解释它“为什么这样设计、怎么工作、解决什么问题、适合什么场景”**。

---

## 1. Skill 身份与定位

| 项目 | 内容 |
|---|---|
| 目录名 | `self-improving-agent` |
| skill 名称 | `self-improvement` |
| 当前元数据版本 | `3.0.8` |
| 核心定位 | 为 AI agent 建立一个“发现问题 → 记录经验 → 回顾经验 → 晋升规则 → 提炼技能”的学习闭环 |
| 推荐平台 | OpenClaw |
| 兼容方式 | OpenClaw、Claude Code、Codex、GitHub Copilot（手动） |

这里有一个很重要的区分：

- **`self-improving-agent`** 更像是这个 skill 在仓库/分发层面的名字。
- **`self-improvement`** 才是 agent 运行时识别的 skill 名。

---

## 2. 这个 skill 本质上是什么

这个 skill 本质上不是“自动修 bug 的脚本”，也不是“训练模型的系统”。

它真正做的是：

1. **在 agent 工作过程中发现值得记住的经验**
2. **把经验写入结构化日志文件**
3. **在后续任务中重新利用这些经验**
4. **把反复验证过的经验升级为长期规则**
5. **把通用解决方案提炼成独立 skill**

所以它不是直接替你完成开发任务，而是：

> **降低 agent 重复犯错的概率，增强 agent 对项目规律、工具坑点、有效工作流的长期保留能力。**

---

## 3. 它主要解决什么问题

AI coding agent 在真实开发里有几个常见问题：

### 3.1 它会重复犯同样的错误

比如：

- 总是误用错误的包管理器
- 总是忽略某个项目约定
- 遇到相同错误时再次从头排查
- 被用户纠正后，下次又犯同样的问题

这个 skill 通过 `.learnings/` 把这些问题沉淀下来，避免“每次都重新吃亏”。

### 3.2 它容易遗忘项目特定知识

很多知识不是通用知识，而是“这个仓库特有的事实”：

- 这个项目必须用 `pnpm`
- API 改完必须重新生成 client
- 某类测试必须用 module-scoped fixture
- 某个外部 API 需要特殊 header

这些东西如果不外化，session 一结束就很容易丢失。

### 3.3 它很难把零散经验变成长期规则

一次错误可能只是一次事故；
三次同类错误就说明这是一个模式。

这个 skill 设计了“记录 → 回顾 → 晋升 → 提炼”的链路，让经验从一次性笔记，变成长期工作规则。

### 3.4 它缺少跨会话的外部记忆

模型本身不会因为这次会话就真的“永久学会”一件事。

这个 skill 的解法不是改模型，而是：

> **把经验保存到 markdown 文件里，作为可复用、可检索、可晋升的外部记忆层。**

### 3.5 团队知识很容易散落在聊天记录里

很多高价值经验只存在于：

- 某次排障聊天
- 某次失败命令输出
- 某次用户纠正
- 某次“终于找到正确做法”的过程里

如果不提炼出来，这些知识对下次工作几乎没有价值。

这个 skill 就是在做这件事：**把瞬时经验转成可持续复用的知识资产。**

---

## 4. 它的核心设计思想

这个 skill 的设计思想可以概括为 5 句话。

### 4.1 学习不发生在模型内部，而发生在工作流外部

它不假设模型会自动长期记住任何事。

所以它选择把学习结果写入文件：

- `.learnings/LEARNINGS.md`
- `.learnings/ERRORS.md`
- `.learnings/FEATURE_REQUESTS.md`

这是一种**外部化记忆**策略。

### 4.2 不是“记录所有事”，而是“记录高价值信号”

skill 关注的不是普通工作日志，而是这类高价值信号：

- 被用户纠正
- 命令失败
- 外部工具异常
- 发现知识过时
- 找到更好的方法
- 用户提出系统当前没有的能力

也就是说，它记录的是：

> **会影响未来决策质量的信息。**

### 4.3 不是只记笔记，而是形成闭环

它不是单纯要求“写日志”。

它真正的目标是建立闭环：

```text
触发信号
  ↓
结构化记录
  ↓
定期回顾
  ↓
识别模式
  ↓
晋升为长期规则
  ↓
必要时提炼成独立 skill
```

### 4.4 提醒机制要轻量，不能过度打断主流程

例如：

- `activator.sh` 的输出控制在约 50~100 token
- hook 默认只做提醒，不直接改文件
- 错误检测脚本只在检测到疑似错误时才输出提示

这说明它的设计哲学不是“强制介入”，而是：

> **低干扰地把学习意识注入 agent 的工作流。**

### 4.5 真正有价值的经验，应该升级

这个 skill 认为，高价值经验不应该永远停留在 `.learnings/`。

当经验被多次验证、跨任务复现、具备通用性后，应该：

- 晋升到 `CLAUDE.md`
- 晋升到 `AGENTS.md`
- 晋升到 `.github/copilot-instructions.md`
- 在 OpenClaw 环境中晋升到 `SOUL.md` 或 `TOOLS.md`
- 最终必要时提炼成新的 skill

这一步非常关键，因为它把“局部经验”变成“长期上下文”。

---

## 5. 它的整体工作原理

从系统角度看，这个 skill 可以分成 5 层。

### 5.1 第 1 层：触发层（Trigger Layer）

这一层负责回答：**什么时候应该启动“学习判断”？**

触发来源主要有两种：

#### A. 显式事件触发

例如：

- 用户提交 prompt
- Bash 工具执行后返回错误
- OpenClaw session bootstrap 开始

这类触发通常由 hook 完成。

#### B. 语义信号触发

例如用户说：

- “No, that's wrong...”
- “Actually...”
- “Can you also...”
- “Why can't you...”

或者 agent 自己发现：

- 自己之前理解错了
- 文档已经过时
- API 行为与预期不一致
- 当前解决方案明显优于原方案

这类触发不是依赖程序报错，而是依赖 agent 的语义判断。

---

### 5.2 第 2 层：分类层（Classification Layer）

当触发发生后，这个 skill 要决定：**这条信息应该记录到哪里？**

它把可记录内容分成 3 类。

#### A. Learning

记录到 `.learnings/LEARNINGS.md`

适用于：

- 用户纠正
- 发现知识盲区
- 找到最佳实践
- 发现更优工作方式

这是“经验类知识”的主容器。

#### B. Error

记录到 `.learnings/ERRORS.md`

适用于：

- 命令失败
- 工具异常
- 外部 API 超时
- 异常堆栈
- 非预期行为

这是“失败案例与排障线索”的容器。

#### C. Feature Request

记录到 `.learnings/FEATURE_REQUESTS.md`

适用于：

- 用户希望 agent 具备当前没有的能力
- 用户反复请求缺失功能
- 某类能力缺口被明确暴露

这是“需求缺口与潜在扩展方向”的容器。

---

### 5.3 第 3 层：结构化记录层（Structured Logging Layer）

skill 不鼓励写随意笔记，而是要求使用固定结构。

这样做的原因是：

- 便于后续搜索
- 便于过滤高优先级问题
- 便于关联相似案例
- 便于 future agent 快速理解
- 便于把条目升级为规则或 skill

每条记录都有清晰字段，例如：

- `ID`
- `Logged`
- `Priority`
- `Status`
- `Area`
- `Summary`
- `Details`
- `Suggested Action`
- `Metadata`

这说明它不是在做“自由文本日志”，而是在做一个**轻量级知识数据库的 markdown 版本**。

---

### 5.4 第 4 层：回顾与晋升层（Review & Promotion Layer）

有记录还不够，还要回顾。

这个 skill 要求在自然断点回顾 `.learnings/`，例如：

- 开始新的 major task 前
- 完成一个 feature 后
- 进入一个以前出过问题的区域时
- 周期性复盘时

然后判断：

#### 如果只是局部经验

那就留在 `.learnings/`。

#### 如果是项目长期规则

那就提升到：

- `CLAUDE.md`
- `AGENTS.md`
- `.github/copilot-instructions.md`

#### 如果是 OpenClaw 工作空间级经验

那就提升到：

- `SOUL.md`：行为/风格/原则
- `AGENTS.md`：工作流/协作模式
- `TOOLS.md`：工具能力、限制、踩坑点

所以 `.learnings/` 更像“候选池”，不是最终归宿。

---

### 5.5 第 5 层：技能提炼层（Skill Extraction Layer）

当某个 learning 已经足够成熟，它就不应该只是一条记录，而应该被提炼为新的 skill。

这个 skill 为此提供了：

- `scripts/extract-skill.sh`
- `assets/SKILL-TEMPLATE.md`

目标是把“某次排障中学到的方法”升级成“以后可直接复用的标准技能”。

这一步非常像把经验知识产品化。

---

## 6. 它的完整工作过程

下面按时间顺序，完整解释这个 skill 是怎么工作的。

---

### 阶段 1：session 启动或 prompt 提交时，skill 尝试把“学习意识”注入上下文

不同环境下做法不同：

#### 在 OpenClaw 中

- `hooks/openclaw/HOOK.md` 声明它监听 `agent:bootstrap`
- `hooks/openclaw/handler.ts` 在 bootstrap 时向 `bootstrapFiles` 注入一个虚拟文件
- 这个虚拟文件内容是一个 reminder，告诉 agent：
  - 什么时候该记录 learnings
  - 记录到哪个文件
  - 哪些内容值得晋升

换句话说，OpenClaw 下它是通过**上下文注入**工作的。

#### 在 Claude Code / Codex 中

- `scripts/activator.sh` 可以绑定到 `UserPromptSubmit`
- 每次用户提交 prompt 后，这个脚本输出一个 `<self-improvement-reminder>` 块
- 这个块提醒 agent：任务完成后检查是否产生了可提炼知识

换句话说，Claude/Codex 下它是通过**轻量 hook 输出提醒文本**工作的。

---

### 阶段 2：当 agent 工作时，持续观察是否出现高价值信号

在工作过程中，agent 要有一个持续判断：

> 这件事值得被记录下来吗？

这个判断主要关注几类事件：

1. **被用户纠正**
2. **命令或工具失败**
3. **发现自己原先理解是错的**
4. **找到更好的方法**
5. **发现了未文档化的项目规律**
6. **用户请求了当前不支持的能力**

这个阶段的核心不是“立刻解决”，而是：

> 在解决问题的同时识别“未来是否还会再遇到”。

---

### 阶段 3：一旦信号成立，决定记录类型

此时会进入一个分流判断：

```text
这是一个失败吗？
  ├─ 是 → ERRORS.md
  └─ 否
       这是一个能力缺口吗？
         ├─ 是 → FEATURE_REQUESTS.md
         └─ 否 → LEARNINGS.md
```

这是这个 skill 的核心判断之一。

因为只有分流明确，后续的搜索、回顾、晋升才会有秩序。

---

### 阶段 4：写入结构化条目

每条记录不是一句“记住这个”，而是一条完整条目。

例如 learning 条目要说明：

- 学到了什么
- 为什么之前错了
- 正确做法是什么
- 后续建议动作是什么
- 跟哪些文件相关

error 条目则更强调：

- 失败内容
- 错误输出
- 发生上下文
- 可疑根因
- 建议修复方式

feature request 条目则强调：

- 用户具体想要什么
- 为什么想要
- 复杂度如何
- 可以如何实现

这一步实际上是在把临时经验“标准化”。

---

### 阶段 5：在合适时机回顾 `.learnings/`

这个 skill 明确建议不要等日志堆很多才看。

它推荐在自然断点做 review：

- major task 开始前
- feature 完成后
- 某个领域再次开工前
- 周期性维护时

review 时要做几件事：

1. 看是否有 `pending` 的高优先级项
2. 看某类错误是否反复出现
3. 看是否有项目规则值得晋升
4. 看是否有 learning 其实已经具备 skill 提炼条件

也就是说，回顾不是浏览，而是第二次加工。

---

### 阶段 6：识别“这不是偶发，而是模式”

这个 skill 非常重视 recurring pattern。

它通过这些方式识别模式：

- `See Also`
- `Pattern-Key`
- `Recurrence-Count`
- `First-Seen`
- `Last-Seen`

也就是说，它不是只记录一次事件，而是希望回答：

> **这类问题是不是已经形成稳定模式？**

一旦答案是“是”，就应该考虑更强的治理方式：

- 加到长期规则文件里
- 形成自动化流程
- 提炼为新 skill

---

### 阶段 7：把模式晋升为规则或 skill

如果某条经验满足这些条件，就应该升级：

- 反复出现
- 已经验证有效
- 不是某个单一文件的偶发问题
- 对很多未来任务都适用

升级路径通常有两种：

#### 路径 A：晋升为长期上下文规则

例如：

- 项目约定 → `CLAUDE.md`
- 工作流规则 → `AGENTS.md`
- Copilot 指导 → `.github/copilot-instructions.md`
- OpenClaw 行为规则 → `SOUL.md`
- OpenClaw 工具知识 → `TOOLS.md`

#### 路径 B：提炼为独立 skill

如果一个解决方案已经足够完整、通用、可复用，就用 `extract-skill.sh` 生成 skill 脚手架。

---

## 7. 什么场景下会触发它

下面是最关键的一部分：触发场景。

### 7.1 用户纠正 agent

典型信号：

- “No, that's wrong...”
- “Actually...”
- “你这个理解不对”
- “这个项目不是这么做的”

这类情况通常应该记录到：

- `.learnings/LEARNINGS.md`

常见分类：

- `correction`
- `knowledge_gap`

这类触发的重要性很高，因为它直接说明：

> agent 当前知识或判断存在偏差。

---

### 7.2 命令失败或工具报错

典型信号：

- 命令非零退出
- 输出里有 `error:`、`fatal:`、`Traceback`
- 依赖安装失败
- 构建失败
- API 请求失败

这类情况通常应该记录到：

- `.learnings/ERRORS.md`

这也是 `scripts/error-detector.sh` 重点辅助的场景。

---

### 7.3 用户提出当前 skill / agent 不具备的能力

典型信号：

- “Can you also...”
- “Is there a way to...”
- “Why can't you...”
- “我希望你能自动做这个”

这类情况通常应该记录到：

- `.learnings/FEATURE_REQUESTS.md`

这能帮助你识别：

- 真正缺的功能是什么
- 哪些需求反复出现
- 哪些方向值得做成新 skill 或新自动化工具

---

### 7.4 发现知识过时或理解错误

例如：

- 文档写法过时
- API 行为和印象中不一样
- 原本以为是 npm 项目，其实是 pnpm workspace
- 原本以为 hook 会在所有 session 生效，实际上 sub-agent 被跳过

这类情况通常记录到：

- `.learnings/LEARNINGS.md`

常见分类：

- `knowledge_gap`

---

### 7.5 找到更好的做法

例如：

- 发现比当前实现更稳健的命令
- 发现更符合项目风格的模式
- 发现更适合长期维护的工作流

这类情况通常记录到：

- `.learnings/LEARNINGS.md`

常见分类：

- `best_practice`

---

### 7.6 反复出现的同类问题

如果你发现某类问题已经不是第一次出现，就不该只记一次，而应该：

- 链接 `See Also`
- 增加优先级
- 补充 `Pattern-Key`
- 递增 `Recurrence-Count`
- 考虑晋升为规则或 skill

这类触发其实意味着：

> 系统正在从“事件管理”进入“模式治理”。

---

## 8. 它到底能帮助我们做什么

这是最实际的问题。

### 8.1 帮助 agent 少犯重复错误

尤其适合：

- 容易踩工具坑的项目
- 有强项目约定的仓库
- 接口/生成代码/CI 流程复杂的系统

### 8.2 帮助团队沉淀项目知识

如果 `.learnings/` 被纳入仓库管理，它就不再只是某个 agent 的私人笔记，而会变成：

- 团队共享知识库
- 项目演化记录
- 高价值故障案例库

### 8.3 帮助把“聊天里的经验”变成“下次可直接用的规则”

这是它最大的价值之一。

很多时候，最有价值的信息并不在文档里，而在一次真实排障过程中。

这个 skill 可以把这种经验固化下来。

### 8.4 帮助把 recurring issue 变成系统级优化

如果某类问题反复出现，它往往说明：

- 文档不够
- 工作流缺少自动化
- 工具使用方式有坑
- 架构本身存在高频脆弱点

这个 skill 可以推动你从“修一次”走向“系统性避免再发生”。

### 8.5 帮助把通用解法提炼成可复用 skill

这意味着它不仅能帮助“记住经验”，还能帮助你：

> **把经验变成产品化的能力模块。**

---

## 9. 目录与关键文件说明

下面按目录解释每个部分的职责。

### 9.1 `SKILL.md`

这是核心文件，也是 agent 真正读取的主说明。

它里面定义了：

- 何时使用这个 skill
- 三类日志文件的用途
- 日志格式规范
- 状态与优先级规则
- 晋升逻辑
- recurring pattern 处理方式
- skill extraction 规则
- 多 agent 场景适配方式

你可以把它理解为：**运行说明书 + 方法论总纲**。

### 9.2 `.learnings/`

这是实际的持久化知识层。

包含：

- `LEARNINGS.md`
- `ERRORS.md`
- `FEATURE_REQUESTS.md`

当前仓库中的这三个文件基本是空模板，说明这里是 skill 分发版，真正使用时需要由具体项目不断累积内容。

### 9.3 `scripts/activator.sh`

这是轻量提醒脚本。

作用：

- 绑定到 `UserPromptSubmit`
- 在每次用户提交 prompt 后输出提醒
- 提醒 agent 在任务结束后检查是否出现可提炼学习

它不会改文件，也不会强制记录，只是注入提醒。

### 9.4 `scripts/error-detector.sh`

这是错误提醒脚本。

作用：

- 绑定到 `PostToolUse`（通常是 Bash）
- 读取 `CLAUDE_TOOL_OUTPUT`
- 用关键词匹配方式判断是否出现错误
- 若出现，则输出 `<error-detected>` 提示

它的定位不是准确诊断错误，而是：

> 在“出错了”这一刻提醒 agent：这可能值得被记录。

### 9.5 `scripts/extract-skill.sh`

这是技能提取脚手架。

作用：

- 根据 skill 名创建新目录
- 生成标准 `SKILL.md`
- 支持 dry-run
- 限制输出路径，避免写出工作区

注意：它只生成骨架，不自动帮你总结内容。

### 9.6 `hooks/openclaw/`

这是 OpenClaw 集成目录。

包含：

- `HOOK.md`：hook 声明
- `handler.ts`：TypeScript 实现
- `handler.js`：JavaScript 兼容版本

主要职责是在 OpenClaw bootstrap 阶段注入提醒内容。

### 9.7 `references/`

这是详细文档目录。

包含：

- `openclaw-integration.md`
- `hooks-setup.md`
- `examples.md`

它们分别负责：

- OpenClaw 深度集成说明
- Claude/Codex/Copilot hook 配置说明
- 各类日志条目的完整示例

### 9.8 `assets/`

这是模板资源目录。

包含：

- `LEARNINGS.md`
- `SKILL-TEMPLATE.md`

主要作用是初始化 `.learnings/` 或生成新 skill 时复用模板。

---

## 10. 在不同平台里它是怎么工作的

---

### 10.1 OpenClaw：工作最完整、集成最深

这是这个 skill 的主战场。

#### 工作链路

```text
session 启动
  ↓
触发 agent:bootstrap
  ↓
handler 注入虚拟提醒文件
  ↓
agent 在上下文中读到自我改进提醒
  ↓
工作中记录 .learnings/
  ↓
必要时晋升到 SOUL.md / AGENTS.md / TOOLS.md
```

#### 它的优势

- 提醒能在 session 一开始就进入上下文
- 可以和 workspace 注入体系协同工作
- 可以结合 `sessions_list/history/send/spawn` 做跨 session 协作
- 更适合形成“长期工作空间知识”

#### 关键实现点

- `handler.ts` 会检查事件是否合法
- 只处理 `agent:bootstrap`
- 会向 `bootstrapFiles` push 一个 `virtual: true` 的文件
- TypeScript 版本额外包含 sub-agent 跳过逻辑，避免对子代理 bootstrap 产生问题

#### 一个值得注意的细节

当前仓库里：

- `handler.ts` 包含 **跳过 sub-agent session** 的逻辑
- `handler.js` 没有完整体现这一分支

这意味着：

> 如果运行时实际使用的是 `.js`，需要留意源码与产物是否完全同步。

这也是一个很典型的“应被记录为 learnings 的实现细节”。

---

### 10.2 Claude Code / Codex：通过 hook 轻量提醒驱动

#### 工作链路

```text
用户提交 prompt
  ↓
UserPromptSubmit 触发 activator.sh
  ↓
输出 <self-improvement-reminder>
  ↓
agent 完成任务后评估是否记入 .learnings/

如果 Bash 工具失败：
  ↓
PostToolUse 触发 error-detector.sh
  ↓
输出 <error-detected>
  ↓
提醒 agent 记录到 ERRORS.md
```

#### 它的优势

- 配置简单
- 侵入性低
- 能覆盖最关键的两个时点：prompt 提交、命令失败

#### 它的限制

- hook 是 opt-in，不配置就不会生效
- 仍然只是提醒，不是自动写日志
- `error-detector.sh` 依赖运行时注入 `CLAUDE_TOOL_OUTPUT`

#### overhead 控制

文档明确把 activator 的预算控制在约 50~100 token。

这说明它很在意：

- 不要让提醒淹没主任务
- 不要让每次 prompt 的成本过高

如果你觉得过于频繁，还可以通过 `matcher` 只在某些 prompt 上触发。

---

### 10.3 GitHub Copilot：没有 hook，只能依赖静态指导

Copilot 不支持像 Claude/OpenClaw 那样的 hook 注入，因此它的工作方式最弱。

#### 工作方式

- 在 `.github/copilot-instructions.md` 中加入自我改进指导
- 让 Copilot 在合适场景下提醒记录 learnings
- 依赖用户在聊天中显式要求：“把这个记到 learnings”

#### 这意味着什么

在 Copilot 场景下，这个 skill 更像：

> 一套规范和提醒模板，而不是可自动触发的行为系统。

---

## 11. 日志结构为什么这样设计

这是这个 skill 的一个核心优势：**结构化而不是随意化。**

### 11.1 ID 机制

格式：`TYPE-YYYYMMDD-XXX`

例如：

- `LRN-20250115-001`
- `ERR-20250115-A3F`
- `FEAT-20250115-002`

作用：

- 唯一标识条目
- 便于交叉引用
- 便于 `See Also` 建立关系
- 便于未来晋升或提炼 skill 时追溯来源

### 11.2 Status 机制

典型状态包括：

- `pending`
- `in_progress`
- `resolved`
- `wont_fix`
- `promoted`
- `promoted_to_skill`

这意味着条目不是“写完就完了”，而是有生命周期。

### 11.3 Metadata 机制

Metadata 允许你给一条经验附加更多上下文，例如：

- 来源
- 相关文件
- 标签
- 关联条目
- Pattern-Key
- Recurrence-Count
- 首次出现时间 / 最近出现时间

这让它可以支持“模式治理”而不是只是“错误存档”。

---

## 12. recurring pattern 是这个 skill 的灵魂之一

很多团队会记日志，但并不会形成真正的改进闭环。

这个 skill 特别强调 recurring pattern，原因是：

> 一次错误是偶发，两三次同类错误就是系统信号。

它对 recurring issue 的处理方式包括：

1. 先搜索是否已有相似条目
2. 用 `See Also` 建立关联
3. 必要时提高 priority
4. 使用 `Pattern-Key` 作为稳定去重键
5. 维护 `Recurrence-Count`
6. 达到阈值后晋升为长期规则

在 `simplify-and-harden` 集成逻辑里，还定义了一个更明确的提升条件：

- `Recurrence-Count >= 3`
- 覆盖至少 2 个不同任务
- 发生在 30 天窗口内

这说明它的目标不是写很多日志，而是识别真正值得改变系统行为的模式。

---

## 13. skill extraction 为什么重要

如果说 `.learnings/` 是经验池，那么 skill extraction 就是在做“经验产品化”。

提取条件大致包括：

- 已验证有效
- 有复用价值
- 不是某个仓库独有的小问题
- 解决方案足够完整
- 用户明确说“把这个保存成 skill”

提取后，原本的一条 learning 会变成：

- 一个有 frontmatter 的 `SKILL.md`
- 一个可被单独安装/调用/阅读的能力包

这意味着这个 skill 不只是帮助“记住”，它还帮助“扩展 skill 生态”。

---

## 14. 它最适合哪些场景

这个 skill 特别适合以下场景：

### 14.1 项目约定很多、容易踩坑的仓库

例如：

- monorepo
- 代码生成较多
- CI / 部署链路复杂
- 有大量隐式规则的老项目

### 14.2 需要长期与 AI 协作的项目

如果 agent 只是偶尔用一次，这个 skill 的价值有限。

如果 agent 会持续参与：

- 写代码
- 修 bug
- 跑命令
- 调文档
- 跟用户反复交互

那这个 skill 的价值会非常明显。

### 14.3 团队希望积累“AI 工作经验”

不是只想让 agent 完成任务，而是希望 agent 越来越理解项目、越来越少犯错、越来越符合团队习惯。

### 14.4 经常出现 recurring issue 的环境

例如：

- 相同命令反复失败
- 相同依赖问题反复出现
- 相同 API 陷阱反复踩中
- 相同沟通误解反复发生

这类场景下，它非常有价值。

---

## 15. 它不做什么

理解边界很重要。

这个 skill **不直接做**这些事：

- 不自动修复代码
- 不自动写入最终规则文件
- 不自动解决错误根因
- 不自动分析所有失败输出
- 不自动保证条目唯一性
- 不自动防止并发写入冲突
- 不自动把 learning 变成完整 skill 内容

它更像一个：

> **学习闭环框架 + 提醒系统 + 结构化知识载体 + 技能提炼脚手架**

而不是一个“全自动知识管理平台”。

---

## 16. 现实中的限制与注意事项

### 16.1 hook 只是提醒，不是强制执行

无论是 OpenClaw bootstrap、Claude UserPromptSubmit 还是 Bash PostToolUse，当前实现本质上都只是提醒 agent。

最终是否真的记录，仍然依赖 agent 是否执行这一工作流。

### 16.2 `error-detector.sh` 是关键词匹配，不是智能诊断

它主要通过字符串匹配判断错误，例如：

- `error:`
- `fatal:`
- `Traceback`
- `TypeError`
- `Permission denied`

这带来两个现实限制：

- 可能漏报
- 可能误报

它的价值在提醒，不在精确分类。

### 16.3 并发写同一日志文件时没有锁

如果多个 agent 同时往 `.learnings/*.md` 里写，可能会：

- ID 冲突
- 结构混乱
- 覆盖彼此内容

所以团队级使用时，最好配合更严格的写入规范。

### 16.4 `.learnings/` 放哪里，需要你自己定策略

这个 skill 支持两种思路：

- **项目级**：放在仓库里，适合团队共享
- **工作空间级**：放在 OpenClaw workspace，适合个人长期记忆

这两种选择会影响：

- 是否进 git
- 是否能跟项目一起迁移
- 是否适合跨项目复用

### 16.5 `extract-skill.sh` 只生成骨架，不生成完整知识

它创建的是 scaffold，不是最终内容。

生成后仍然需要：

- 回填说明
- 补充示例
- 检查命名
- 验证是否自包含

---

## 17. 如果把它总结成一句方法论

这个 skill 的方法论可以概括成一句话：

> **把 AI agent 每次“吃亏、纠正、摸索、优化”的过程，结构化沉淀为下次不必重新摸索的知识。**

再展开一点，就是：

> **让经验从一次会话中的临时发现，变成项目中的长期规则，再变成可移植、可复用的能力模块。**

---

## 18. 最后的结论

`self-improving-agent` 不是一个“炫技型” skill，它非常务实。

它解决的不是模型推理本身，而是 AI 协作开发里最真实的问题：

- 重复犯错
- 容易遗忘
- 经验无法复用
- 规则无法沉淀
- 好的解决方案不会自动升级为长期资产

它的真正价值不在于一次使用，而在于长期使用之后形成的复利：

- agent 会越来越贴近项目现实
- 反复踩过的坑会越来越少
- 高价值经验会越来越容易被团队共享
- 解决方案会从“聊天记录”升级成“技能资产”

如果你希望 AI agent 不只是“会做事”，而是“能从做事中持续变好”，那么这个 skill 的意义就非常大。
