---
description: 安装 skills 的旧入口，已拆分为 OpenCode / Claude Code / Codex 三个独立命令
---

# 安装 Skills（已拆分）

`install-skills` 已拆分为三个更小的独立命令。

## 执行步骤

### 1. 使用 question 工具让用户选择目标平台

不要让用户自由回复平台名称；必须使用 question 工具给出固定选项：

```
请选择要安装到哪个平台：
```
- 选项1（默认）：OpenCode → `install-skills-opencode`
- 选项2：Claude Code → `install-skills-claude`
- 选项3：Codex → `install-skills-codex`

### 2. 根据选择，引导用户改用对应命令

告知用户当前旧入口已拆分，请改用：

- OpenCode：`install-skills-opencode`
- Claude Code：`install-skills-claude`
- Codex：`install-skills-codex`

如果运行环境支持直接跳转或重试对应命令，则优先进入对应命令；否则清楚提示用户下一步该运行哪个命令。
