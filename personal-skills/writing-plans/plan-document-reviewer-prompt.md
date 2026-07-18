# 执行计划审核提示词

仅在 `Review Mode=review` 时使用。Reviewer 只读计划和来源设计，不编辑文件；每份执行计划只派发一轮审核。

```text
Task tool（优先使用宿主或项目配置的审核 subagent，未指定时使用 `explore`）：
  description: "Review implementation plan"
  prompt: |
    你是执行计划 reviewer。请读取计划及其来源设计，检查计划能否安全、明确地执行。

    计划：[PLAN_FILE_PATH]
    来源设计：[SPEC_PATH_OR_INLINE_BASIS]
    审核范围：[FULL 或用户明确指定的 FOCUSED_SCOPE]

    检查：
    - `Review Mode` 是否原样继承来源 spec；来源 spec 的 `Independent Review` 是否覆盖当前 spec revision，`no-review` 是否为 `not-required`
    - 需求、Task 和最终验收是否完整对应，是否有范围蔓延
    - Task 是否拥有完整 DoD、足以承担一次 worker 上下文，而不是按命令、文件或 TDD 步骤机械拆分
    - 测试驱动、验证驱动、混合或探索策略是否适合任务场景
    - 配置、文档、视觉、迁移、机械重构等任务是否被不必要地强制 TDD
    - DAG 是否无环；是否利用了子工程、独立模块和稳定契约后的安全并行边界
    - 并行 Task 的文件级写入范围、读取状态和运行资源是否真正隔离；共享工作树禁止同一文件并行写入
    - 没有并行是否有合理原因；未利用的纯性能优化只能作为建议
    - 验收命令、人工步骤和预期结果是否足以判定完成
    - 只有真实外部或非幂等副作用才需要专门恢复策略
    - 提交策略是否记录最终有效策略和来源，是否包含 repair commit 边界但没有扭曲 Task 边界

    只把会导致错误、数据/安全风险、无法执行或无法验收的问题列为阻塞。并行机会、措辞和可选优化列为建议。

    输出：
    ## 执行计划审核
    **状态：** 通过 | 需要修改
    **问题：**
    - [章节/Wave/Task/path:line] [具体问题、影响和最小修正方向]
    **建议：**
    - [非阻塞建议]
```

只要存在“问题”，状态必须是“需要修改”。主 agent 根据审核结果修复并自检；本流程不自动派发复审。
