---
description: 更新 ~/.agent-skills 仓库及所有子模块到最新版本
---

# 更新 Agent Skills 仓库

## 1. 检查 skills 仓库是否存在

```bash
ls -d ~/.agent-skills/.git 2>/dev/null
```

- 如果 `~/.agent-skills` 不存在或不是 git 仓库，告知用户该目录不存在或不是 git 仓库，终止操作。

## 2. 读取更新指令

使用 bash 读取更新指令文件：

```bash
cat ~/.agent-skills/.opencode/commands/git-update.md
```

## 3. 执行更新指令

在 `~/.agent-skills/` 目录下，严格按照上一步读取到的指令内容执行所有操作。

> 注意：所有 git 操作的工作目录都是 `~/.agent-skills/`。

## 4. 完成后提醒

更新完成后，提醒用户：**请重启 OpenCode 以加载最新版本的 skills。**
