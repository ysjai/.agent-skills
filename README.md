# Agent Skills 管理仓库

本仓库用于集中管理你的 AI Agent Skills，支持 **OpenCode**、**Claude Code** 和 **Codex** 三个平台，方便你在不同设备间同步和更新。

> **平台说明**：目前仅支持 macOS。

## 这是什么？

这是一个技能仓库管理器：

- **存放位置**：`~/.agent-skills/` - 集中存放所有 skills（SkillHub 下载、本地自建、Git 仓库）
- **管理命令**：安装几个快捷命令，方便你通过 `/install-skills-opencode`、`/install-skills-claude`、`/install-skills-codex`、`/uninstall-skills` 等命令管理 skills
- **多平台**：同一份源文件，可分别安装到 OpenCode、Claude Code 和 Codex

## 前置要求

在开始之前，请确保已安装以下工具：

| 工具                                           | 说明                           | 安装方式                      |
| -------------------------------------------- | ---------------------------- | ------------------------- |
| [OpenCode](https://opencode.ai) / [Claude Code](https://docs.anthropic.com/en/docs/claude-code) / [Codex](https://developers.openai.com/codex/cli) | AI 编程助手（至少安装其中一个） | 参见各自官网文档 |
| [git](https://git-scm.com)                   | 版本控制，用于克隆仓库和管理子模块            | `brew install git`（macOS） |
| [skillhub CLI](https://skillhub.tencent.com) | SkillHub 官方命令行工具，用于搜索和下载在线技能 | `curl -fsSL https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/install.sh \| bash -s -- --cli-only` |

> **注意**：skillhub CLI 仅在使用 SkillHub 在线来源时才需要。如果你只使用本地或 Git 仓库来源，可以跳过安装。

## 快速设置

### 第一步：克隆仓库到 \~/.agent-skills/

方式1：使用 HTTPS

```bash
git clone --recurse-submodules https://github.com/ysjai/.agent-skills.git ~/.agent-skills
```

方式2：使用 SSH（推荐，已配置 SSH key 的用户）

```bash
git clone --recurse-submodules git@github.com:ysjai/.agent-skills.git ~/.agent-skills
```

### 第二步：安装管理命令

根据你使用的平台，将管理命令通过软链接安装到对应的全局配置目录：

#### OpenCode

```bash
# 创建命令目录（如果不存在）
mkdir -p ~/.config/opencode/commands

# 创建软链接
ln -s ~/.agent-skills/commands/download-skills.md ~/.config/opencode/commands/
ln -s ~/.agent-skills/commands/install-skills-opencode.md ~/.config/opencode/commands/
ln -s ~/.agent-skills/commands/install-skills-claude.md ~/.config/opencode/commands/
ln -s ~/.agent-skills/commands/install-skills-codex.md ~/.config/opencode/commands/
ln -s ~/.agent-skills/commands/uninstall-skills.md ~/.config/opencode/commands/
ln -s ~/.agent-skills/commands/update-skills.md ~/.config/opencode/commands/
```

#### Claude Code

```bash
# 创建命令目录（如果不存在）
mkdir -p ~/.claude/commands

# 创建软链接（在 Claude Code 中以 /user:xxx 调用）
ln -s ~/.agent-skills/commands/download-skills.md ~/.claude/commands/
ln -s ~/.agent-skills/commands/install-skills-opencode.md ~/.claude/commands/
ln -s ~/.agent-skills/commands/install-skills-claude.md ~/.claude/commands/
ln -s ~/.agent-skills/commands/install-skills-codex.md ~/.claude/commands/
ln -s ~/.agent-skills/commands/uninstall-skills.md ~/.claude/commands/
ln -s ~/.agent-skills/commands/update-skills.md ~/.claude/commands/
```

> **两个平台都安装？** 完全可以！同一份命令文件通过软链接同时服务两个平台。

#### Codex

Codex 官方当前推荐通过原生 skill 发现目录 `.agents/skills/`（项目级）和 `~/.agents/skills/`（全局）来加载 skills，而不是通过本仓库这种自定义 commands 目录来管理。因此：

- 你可以继续在 OpenCode / Claude Code 中运行本仓库的管理命令，然后把 skill 安装到 Codex 的目录
- 或者直接按本文后面的手动软链接方式，把 skill 挂到 Codex 的 `.agents/skills/` / `~/.agents/skills/`
- 若参考过旧资料，请注意：`~/.codex/skills/` 已不是 Codex 官方当前推荐的主路径

### 第三步：验证

#### OpenCode

启动 OpenCode，输入 `/` 查看可用命令，你应该看到：

- `/download-skills` - 只下载 skills 到 `~/.agent-skills/`，**不创建软链接**
- `/install-skills-opencode` - 安装 skills 到 OpenCode
- `/install-skills-claude` - 安装 skills 到 Claude Code
- `/install-skills-codex` - 安装 skills 到 Codex
- `/uninstall-skills` - 卸载已安装的 skills（移除软链接）
- `/update-skills` - 更新已有 skills

#### Claude Code

启动 Claude Code，输入 `/` 查看可用命令，你应该看到：

- `/user:download-skills` - 只下载 skills 到 `~/.agent-skills/`
- `/user:install-skills-opencode` - 安装 skills 到 OpenCode
- `/user:install-skills-claude` - 安装 skills 到 Claude Code
- `/user:install-skills-codex` - 安装 skills 到 Codex
- `/user:uninstall-skills` - 卸载已安装的 skills
- `/user:update-skills` - 更新已有 skills

#### Codex

启动 Codex 后，可通过以下方式确认 skills 已被发现：

- 输入 `/skills` 查看可用 skills
- 在对话中输入 `$` 查看可显式调用的 skill 列表
- 直接输入 `$<skill-name>` 显式调用某个 skill

Codex 一般会自动发现新安装的 skills；若没有出现，重启 Codex 即可。

## 平台路径对照表

| 用途 | OpenCode | Claude Code | Codex |
|------|----------|-------------|-------|
| Skills 全局目录 | `~/.config/opencode/skills/` | `~/.claude/skills/` | `~/.agents/skills/` |
| Skills 项目级目录 | `<项目>/.opencode/skills/` | `<项目>/.claude/skills/` | `<项目>/.agents/skills/` |
| Commands 全局目录 | `~/.config/opencode/commands/` | `~/.claude/commands/` | 官方文档未提供等价的用户自定义 commands 目录 |
| Commands 项目级目录 | `<项目>/.opencode/commands/` | `<项目>/.claude/commands/` | - |
| 命令调用方式 | `/install-skills-opencode` 等 | `/user:install-skills-opencode` 等 | 通过已有平台命令安装，或手动创建软链接 |
| Skill 显式调用 | 自动发现 / 命令触发 | 自动发现 / 命令触发 | `$<skill-name>` 或 `/skills` |
| 整组安装 | ✅ 支持 | ✅ 支持（自动展开为独立 skill 链接） | ✅ 支持 |

## 日常使用

### 安装 skills

**只下载不安装**（仅下载到 `~/.agent-skills/`，不创建软链接）：

```
/download-skills          # OpenCode
/user:download-skills     # Claude Code
```

**安装 skills**（选择平台、项目级或全局，按提示选择）：

```
/install-skills-opencode  # 安装到 OpenCode
/install-skills-claude    # 安装到 Claude Code
/install-skills-codex     # 安装到 Codex

/user:install-skills-opencode  # Claude Code 中调用，安装到 OpenCode
/user:install-skills-claude    # Claude Code 中调用，安装到 Claude Code
/user:install-skills-codex     # Claude Code 中调用，安装到 Codex
```

> **Codex 说明**：Codex 当前不以本仓库这类自定义 command 文件作为主要集成方式。你可以在 OpenCode / Claude Code 中运行 `install-skills-codex`；也可以直接手动把 skill 软链接到 `.agents/skills/` 或 `~/.agents/skills/`。

两个命令说明：

- `download-skills`：支持 SkillHub 在线下载和 Git 仓库 clone，只下载源文件不安装
- `install-skills-opencode` / `install-skills-claude` / `install-skills-codex`：各自只处理一个目标平台，再按来源决定是否先下载再创建软链接

### 添加 Git 仓库 skill

通过对应平台的 `install-skills-*` 命令 → 选择 `git-repo-skills` 来源，按提示输入 clone 地址即可。

也可以手动添加子模块：

```bash
cd ~/.agent-skills
git submodule add https://github.com/user/repo.git git-repo-skills/my-repo
git submodule update --init git-repo-skills/my-repo
```

### 添加本地自建 skill

在 `personal-skills/` 下创建目录，放入 skill 文件：

```bash
mkdir ~/.agent-skills/personal-skills/my-skill
# 创建 SKILL.md 等文件...
```

然后通过对应平台的 `install-skills-*` 命令 → 选择 `personal-skills` 来源安装。

### 手动创建软链接

如果你不想通过命令方式安装，也可以手动创建软链接。以下列出三种 skill 类型分别链接到两个平台的命令。

> 以下示例均为**全局安装**（用户级目录），如需项目级安装，将目标路径替换为项目内的 `.opencode/skills/` 或 `.claude/skills/`。

#### SkillHub 类型（`skill-hub/`）

SkillHub 下载的 skill 存放在 `~/.agent-skills/skill-hub/<slug>/`：

```bash
# OpenCode（全局）
mkdir -p ~/.config/opencode/skills
ln -s ~/.agent-skills/skill-hub/<slug> ~/.config/opencode/skills/<slug>

# Claude Code（全局）
mkdir -p ~/.claude/skills
ln -s ~/.agent-skills/skill-hub/<slug> ~/.claude/skills/<slug>

# Codex（全局）
mkdir -p ~/.agents/skills
ln -s ~/.agent-skills/skill-hub/<slug> ~/.agents/skills/<slug>
```

#### Git 仓库类型（`git-repo-skills/`）

Git 仓库中的 skill 存放在 `~/.agent-skills/git-repo-skills/<repo>/` 下的某个子目录：

```bash
# OpenCode（全局）
mkdir -p ~/.config/opencode/skills
ln -s ~/.agent-skills/git-repo-skills/<repo>/<skill-dir> ~/.config/opencode/skills/<skill-name>

# Claude Code（全局）
mkdir -p ~/.claude/skills
ln -s ~/.agent-skills/git-repo-skills/<repo>/<skill-dir> ~/.claude/skills/<skill-name>

# Codex（全局）
mkdir -p ~/.agents/skills
ln -s ~/.agent-skills/git-repo-skills/<repo>/<skill-dir> ~/.agents/skills/<skill-name>
```

示例（链接 Anthropic 官方 skill 中的 `frontend-design`）：

```bash
# OpenCode
ln -s ~/.agent-skills/git-repo-skills/anthropics-skills/skills/frontend-design ~/.config/opencode/skills/frontend-design

# Claude Code
ln -s ~/.agent-skills/git-repo-skills/anthropics-skills/skills/frontend-design ~/.claude/skills/frontend-design

# Codex
ln -s ~/.agent-skills/git-repo-skills/anthropics-skills/skills/frontend-design ~/.agents/skills/frontend-design
```

#### 本地自建类型（`personal-skills/`）

个人自建 skill 存放在 `~/.agent-skills/personal-skills/<skill-name>/`：

```bash
# OpenCode（全局）
mkdir -p ~/.config/opencode/skills
ln -s ~/.agent-skills/personal-skills/<skill-name> ~/.config/opencode/skills/<skill-name>

# Claude Code（全局）
mkdir -p ~/.claude/skills
ln -s ~/.agent-skills/personal-skills/<skill-name> ~/.claude/skills/<skill-name>

# Codex（全局）
mkdir -p ~/.agents/skills
ln -s ~/.agent-skills/personal-skills/<skill-name> ~/.agents/skills/<skill-name>
```

> **提示**：链接创建后，可用 `ls -la ~/.config/opencode/skills/`（OpenCode）、`ls -la ~/.claude/skills/`（Claude Code）或 `ls -la ~/.agents/skills/`（Codex）验证软链接是否正确指向源目录。

---

### 卸载 skills

```
/uninstall-skills         # OpenCode
/user:uninstall-skills    # Claude Code
```

选择平台和安装范围后，会列出已安装的 skills（包括软链接和非托管的真实目录/文件）。选择要卸载的 skill，确认后移除软链接。非托管项会标记 ⚠️，需额外确认。

### 更新已有 skills

```
/update-skills            # OpenCode
/user:update-skills       # Claude Code
```

或手动更新：

```bash
cd ~/.agent-skills
git submodule update --remote git-repo-skills/
git add .
git commit -m "Update git-repo-skills submodules"
git push
```

### 同步仓库到最新（换设备 / 拉取他人更新）

一键拉取主仓库最新内容，并同步所有子模块：

```bash
git -C ~/.agent-skills pull && git -C ~/.agent-skills submodule update --init --recursive --remote
```

## 目录结构

```
~/.agent-skills/                    # 本仓库位置（中央仓库，平台无关）
├── commands/                       # 管理命令（可软链接到 OpenCode 和/或 Claude Code）
│   ├── download-skills.md
│   ├── install-skills.md
│   ├── install-skills-opencode.md
│   ├── install-skills-claude.md
│   ├── install-skills-codex.md
│   ├── uninstall-skills.md
│   └── update-skills.md
│
├── skill-hub/                      # SkillHub 下载的 skills（由 /install-skills-* 自动管理）
│   └── <slug>/
│
├── personal-skills/                # 个人自建 skills
│   ├── brainstorming/
│   ├── writing-plans/
│   └── ...
│
├── git-repo-skills/                # Git 仓库 skills（子模块或手动 clone）
│   ├── anthropics-skills/          # 子模块：Anthropic 官方 skills
│   └── superpowers/                # 子模块：Superpowers skills（或手动 clone 的仓库）
│
├── .gitmodules                     # Git 子模块配置
└── README.md                       # 本文件
```

软链接安装在各平台对应的目录下：

```
# OpenCode（当前项目）
<你的项目>/
└── .opencode/
    └── skills/
        ├── brave-search -> ~/.agent-skills/skill-hub/brave-search/
        └── frontend-design -> ~/.agent-skills/git-repo-skills/anthropics-skills/skills/frontend-design/

# Claude Code（当前项目）
<你的项目>/
└── .claude/
    └── skills/
        ├── brave-search -> ~/.agent-skills/skill-hub/brave-search/
        └── frontend-design -> ~/.agent-skills/git-repo-skills/anthropics-skills/skills/frontend-design/

# Codex（当前项目）
<你的项目>/
└── .agents/
    └── skills/
        ├── brave-search -> ~/.agent-skills/skill-hub/brave-search/
        └── frontend-design -> ~/.agent-skills/git-repo-skills/anthropics-skills/skills/frontend-design/
```

## 工作原理

1. **`~/.agent-skills/`**：作为中央仓库，集中存放三类 skills 的源文件（平台无关）
2. **安装目标目录**：通过软链接将源文件挂载到对应平台的 skills 目录
3. **命令目录**：同一份命令文件可同时软链接到 OpenCode 和 Claude Code；Codex 则通过 `.agents/skills` / `~/.agents/skills` 原生发现 skills

当你运行 `download-skills` 时：

- SkillHub 来源：下载源文件到 `~/.agent-skills/skill-hub/<slug>/`，不创建软链接
- Git 仓库来源：clone 到 `~/.agent-skills/git-repo-skills/<repo>/`，不创建软链接

当你运行 `install-skills-opencode` / `install-skills-claude` / `install-skills-codex` 时：

- 直接对应一个固定目标平台，再选择安装范围（项目级 / 全局）
- 再选择来源：SkillHub 先下载再链接，personal-skills / git-repo-skills 直接链接
- Claude Code 支持整组选择，但安装时会自动展开为多个独立 skill 软链接

## 常见问题

**Q: 为什么要把仓库放在 \~/.agent-skills/？**
A: 这是约定的位置，方便管理命令用绝对路径找到所有 skills。

**Q: SkillHub、git-repo-skills、personal-skills 有什么区别？**
A: SkillHub 是从 [skillhub.tencent.com](https://skillhub.tencent.com) 在线下载的第三方 skills；git-repo-skills 是通过 git submodule 跟踪的外部仓库，可以统一执行 `git submodule update --remote` 更新；personal-skills 是你自己创建和维护的技能。

**Q: 同一个仓库可以同时服务 OpenCode、Claude Code 和 Codex 吗？**
A: 可以。中央仓库 `~/.agent-skills/` 存放源文件，通过软链接分别安装到不同平台的 skills 目录。同一个 skill 可以同时安装到多个平台。

**Q: Codex 应该装到 `~/.codex/skills/` 还是 `~/.agents/skills/`？**
A: 按 Codex 官方当前文档，应优先使用 `~/.agents/skills/`（全局）和 `<项目>/.agents/skills/`（项目级）做原生发现。`~/.codex/skills/` 属于旧资料中常见的历史路径，不应再作为默认方案。

**Q: Claude Code 为什么要把整组安装展开成多个独立 skill？**
A: Claude Code 要求 `skills/<name>/SKILL.md` 的扁平目录结构，因此即使用户选择了整组，安装时也必须展开为多个独立 skill 目录；不能像 OpenCode / Codex 那样把一个包含多个 skill 的父目录直接作为单个入口挂载。

**Q: Codex 怎么调用已安装的 skill？**
A: 可以在对话里输入 `$<skill-name>` 显式调用，也可以用 `/skills` 查看当前已发现的 skills。符合 `description` 的任务也可能被 Codex 自动匹配到对应 skill。

**Q: 在 Claude Code 中命令为什么是 /user:xxx 格式？**
A: Claude Code 区分用户级命令（`/user:xxx`，来自 `~/.claude/commands/`）和项目级命令（`/project:xxx`，来自 `.claude/commands/`）。本仓库的管理命令安装到用户级目录，因此以 `/user:` 前缀调用。
