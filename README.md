# Agent Skills 管理仓库

本仓库用于集中管理你的 AI Agent Skills，支持 **OpenCode**、**Claude Code** 和 **Codex** 三个平台，方便在不同设备间同步、安装和更新同一份 skill 源文件。

> **平台说明**：目前仅支持 macOS。

## 这是什么？

- **中央仓库**：默认放在 `~/.agent-skills/`，平台无关。
- **多来源管理**：支持 SkillHub 下载、本地自建、Git 仓库三类 skill 来源。
- **多平台安装**：通过软链接把同一份源文件安装到 OpenCode、Claude Code 或 Codex。
- **管理命令**：通过 `/download-skills`、`/install-skills-*`、`/update-skills`、`/uninstall-skills` 管理下载、安装、更新和卸载。

三类 skill 来源的细节放在各自目录中维护，根 README 只保留总览和入口：

| 目录 | 用途 | 详细说明 |
|------|------|----------|
| `skill-hub/` | SkillHub 下载的第三方 skills | [`skill-hub/README.md`](skill-hub/README.md) |
| `personal-skills/` | 个人自建和维护的 skills | [`personal-skills/README.md`](personal-skills/README.md) |
| `git-repo-skills/` | Git 仓库或子模块引入的 skills | [`git-repo-skills/README.md`](git-repo-skills/README.md) |

## 前置要求

| 工具 | 说明 | 安装方式 |
|------|------|----------|
| [OpenCode](https://opencode.ai) / [Claude Code](https://docs.anthropic.com/en/docs/claude-code) / [Codex](https://developers.openai.com/codex/cli) | AI 编程助手，至少安装其中一个 | 参见各自官网文档 |
| [git](https://git-scm.com) | 克隆仓库和管理子模块 | `brew install git` |
| [skillhub CLI](https://skillhub.tencent.com) | 仅在下载或更新 SkillHub skills 时需要 | 见 [`skill-hub/README.md`](skill-hub/README.md) |

## 快速设置

### 1. 克隆仓库

```bash
git clone --recurse-submodules https://github.com/ysjai/.agent-skills.git ~/.agent-skills
```

或使用 SSH：

```bash
git clone --recurse-submodules git@github.com:ysjai/.agent-skills.git ~/.agent-skills
```

### 2. 安装管理命令

#### OpenCode

```bash
mkdir -p ~/.config/opencode/commands
ln -s ~/.agent-skills/commands/download-skills.md ~/.config/opencode/commands/
ln -s ~/.agent-skills/commands/install-skills-opencode.md ~/.config/opencode/commands/
ln -s ~/.agent-skills/commands/install-skills-claude.md ~/.config/opencode/commands/
ln -s ~/.agent-skills/commands/install-skills-codex.md ~/.config/opencode/commands/
ln -s ~/.agent-skills/commands/uninstall-skills.md ~/.config/opencode/commands/
ln -s ~/.agent-skills/commands/update-skills.md ~/.config/opencode/commands/
```

#### Claude Code

```bash
mkdir -p ~/.claude/commands
ln -s ~/.agent-skills/commands/download-skills.md ~/.claude/commands/
ln -s ~/.agent-skills/commands/install-skills-opencode.md ~/.claude/commands/
ln -s ~/.agent-skills/commands/install-skills-claude.md ~/.claude/commands/
ln -s ~/.agent-skills/commands/install-skills-codex.md ~/.claude/commands/
ln -s ~/.agent-skills/commands/uninstall-skills.md ~/.claude/commands/
ln -s ~/.agent-skills/commands/update-skills.md ~/.claude/commands/
```

> Claude Code 中用户级命令以 `/user:<command>` 调用。

#### Codex

Codex 当前推荐通过 `.agents/skills/`（项目级）和 `~/.agents/skills/`（用户级）发现 skills，不依赖本仓库的 command 目录。你可以：

- 在 OpenCode / Claude Code 中运行本仓库的安装命令，并选择安装到 Codex。
- 手动把需要的 skill 软链接到 `.agents/skills/` 或 `~/.agents/skills/`。

### 3. 验证

- OpenCode：启动后输入 `/`，应能看到 `/download-skills`、`/install-skills-opencode` 等命令。
- Claude Code：启动后输入 `/`，应能看到 `/user:download-skills`、`/user:install-skills-claude` 等命令。
- Codex：启动后输入 `/skills`，或在对话中输入 `$` 查看可用 skills。

## 平台路径

| 用途 | OpenCode | Claude Code | Codex |
|------|----------|-------------|-------|
| Skills 全局目录 | `~/.config/opencode/skills/` | `~/.claude/skills/` | `~/.agents/skills/` |
| Skills 项目级目录 | `<项目>/.opencode/skills/` | `<项目>/.claude/skills/` | `<项目>/.agents/skills/` |
| Commands 全局目录 | `~/.config/opencode/commands/` | `~/.claude/commands/` | 无等价通用目录 |
| Commands 项目级目录 | `<项目>/.opencode/commands/` | `<项目>/.claude/commands/` | - |
| Skill 显式调用 | 自动发现 / skill 触发 | 自动发现 / skill 触发 | `$<skill-name>` 或 `/skills` |

## 常用命令

### 下载 skills

只下载到 `~/.agent-skills/`，不安装到具体平台：

```text
/download-skills          # OpenCode
/user:download-skills     # Claude Code
```

### 安装 skills

```text
/install-skills-opencode  # 安装到 OpenCode
/install-skills-claude    # 安装到 Claude Code
/install-skills-codex     # 安装到 Codex

/user:install-skills-opencode
/user:install-skills-claude
/user:install-skills-codex
```

安装命令会让你选择目标范围（项目级 / 全局）和来源目录。各来源目录的具体规则见上方子目录 README。

### 更新 skills

```text
/update-skills
/user:update-skills
```

### 卸载 skills

```text
/uninstall-skills
/user:uninstall-skills
```

卸载只移除平台目录中的链接或条目，不删除 `~/.agent-skills/` 中的源文件。

## 三阶段工作流

`personal-skills/` 里的核心工作流分成三个阶段，按顺序衔接：

1. `brainstorming`：按风险把需求整理成设计文档（spec），低风险单一任务可走快速路径。
2. `writing-plans`：基于已批准的 spec，或基于明确且获用户确认的无 spec 实现依据，生成执行计划。
3. `executing-plans`：按 spec 和 plan 实现，并验证验收标准。

开始时根据需求复杂度推荐 `review` 或 `no-review`，由用户选择并贯穿三个阶段。`review` 会分别审核设计文档、执行计划和最终实现；`no-review` 跳过 subagent 审核，只保留主 agent 自检和用户批准门禁。

## 目录结构

```text
~/.agent-skills/
├── commands/             # 管理命令
├── skill-hub/            # SkillHub 来源，见 skill-hub/README.md
├── personal-skills/      # 本地自建来源，见 personal-skills/README.md
├── git-repo-skills/      # Git 仓库来源，见 git-repo-skills/README.md
├── .gitmodules           # Git 子模块配置
└── README.md             # 总览入口
```

## 工作原理

1. `~/.agent-skills/` 保存 skill 源文件。
2. 安装命令根据目标平台创建软链接。
3. 平台从自己的 skills 目录发现并加载 skill。

链接创建后，源文件更新会通过软链接反映到已安装 skill；OpenCode / Claude Code 通常需要重启后生效，Codex 通常会自动发现，若未出现则重启。

## 同步仓库

换设备或拉取更新时：

```bash
git -C ~/.agent-skills pull && git -C ~/.agent-skills submodule update --init --recursive --remote
```

## 常见问题

**Q: 为什么仓库放在 `~/.agent-skills/`？**
A: 这是管理命令约定的中央路径，方便跨平台复用同一份源文件。

**Q: 三类来源有什么区别？**
A: 见三个子目录 README：[`skill-hub/`](skill-hub/README.md)、[`personal-skills/`](personal-skills/README.md)、[`git-repo-skills/`](git-repo-skills/README.md)。

**Q: 同一个 skill 能同时安装到多个平台吗？**
A: 可以。各平台目录只保存软链接，源文件仍在 `~/.agent-skills/`。

**Q: Claude Code 为什么整组安装时要展开？**
A: Claude Code 更适合 `skills/<name>/SKILL.md` 的扁平结构。Git 仓库整组选择时，安装命令会展开成多个独立 skill 链接。
