# 实现审核提示词

仅在 `Review Mode=review` 且全部执行 Task 完成后使用。Reviewer 只读审核当前实现；主 agent 委派 repair worker 修复 findings 后重跑受影响验证，不自动复审。

```text
Task tool（优先使用宿主或项目配置的审核 subagent，未指定时使用 `explore`）：
  description: "Review implementation"
  prompt: |
    你是实现 reviewer。请只读审核当前实现，不要修改文件。

    仓库根目录：[REPO_ROOT]
    设计依据：[SPEC_CONTEXT]
    执行计划：[PLAN_FILE_PATH]
    实现基线：[BASELINE_HEAD_OR_DESCRIPTION]
    本次 changed paths：[CHANGED_PATHS]
    验证结果：[VERIFICATION_RESULTS]
    审核范围：[FULL 或用户明确指定的 FOCUSED_SCOPE]

    使用只读工具自行检查相关 diff 和文件，不只依赖主 agent 摘要。忽略明确标注且可验证为本次范围外的既有改动。

    检查：
    - 实现是否满足设计、Task 和验收，且没有未批准范围
    - bug、回归、边界处理、错误处理和数据/安全风险
    - 测试或验证方式是否适合场景，证据是否足够
    - 是否有不必要的抽象、依赖、兼容层或重构
    - 并行结果是否正确接线，最终 tree 是否经过完整验证
    - 若指定 FOCUSED_SCOPE，只检查该范围及其相关回归

    为每个问题标记：
    - implementation：原计划范围内的代码、测试或验证修复
    - plan：任务、依赖或验收计划有缺口
    - design：产品、范围、公共接口、数据或安全决策需要改变

    输出：
    ## 实现审核
    **状态：** 通过 | 需要修改
    **问题：**
    - [implementation | plan | design] [path:line 或 Task] [问题、影响和最小修正方向]
    **建议：**
    - [非阻塞建议]
```

只要列出“问题”，状态必须是“需要修改”。审核结果只代表 reviewer 看过的实现 revision；主 agent 修复后记录修复和验证结果，不把它描述为复审通过。
