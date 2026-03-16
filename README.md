# Agent Skills 管理仓库

本仓库用于集中管理你的 OpenCode Agent Skills，方便你在不同设备间同步和更新。

## 这是什么？

这是一个技能仓库管理器：
- **存放位置**：`~/.agent-skills/` - 集中存放所有 skills（SkillHub 下载、本地自建、Git 仓库）
- **管理命令**：安装几个快捷命令到 OpenCode，方便你通过 `/install-skills` 安装 skills

## 快速设置

### 第一步：克隆仓库到 ~/.agent-skills/

```bash
# 方式1：使用 HTTPS
git clone --recurse-submodules https://github.com/mac-home-config-ysj/.agent-skills.git ~/.agent-skills

# 方式2：使用 SSH（推荐，已配置 SSH key 的用户）
git clone --recurse-submodules git@github.com:mac-home-config-ysj/.agent-skills.git ~/.agent-skills
```

### 第二步：安装管理命令

将这些命令通过软链接安装到 OpenCode 全局配置，方便在任何项目使用：

```bash
# 创建命令目录（如果不存在）
mkdir -p ~/.config/opencode/commands

# 创建软链接
ln -s ~/.agent-skills/.opencode/commands/install-skills.md ~/.config/opencode/commands/
ln -s ~/.agent-skills/.opencode/commands/uninstall-skills.md ~/.config/opencode/commands/
ln -s ~/.agent-skills/.opencode/commands/update-skills.md ~/.config/opencode/commands/
```

### 第三步：验证

启动 OpenCode，输入 `/` 查看可用命令，你应该看到：
- `/install-skills` - 安装 skills（支持 SkillHub、local-skills、git-repo-skills 三种来源）
- `/uninstall-skills` - 卸载已安装的 skills
- `/update-skills` - 更新 git-repo-skills 中的所有子模块

## 日常使用

### 安装 skills

在任何项目目录下启动 OpenCode，运行：

```
/install-skills
```

支持三种来源：
1. **SkillHub**（默认）：从腾讯 SkillHub 在线下载，存储在 `skill-hub/`，收录 1.3 万个 AI Skills
2. **git-repo-skills**：`git-repo-skills/` 下的 Git 仓库，支持输入 clone 地址新增
3. **local-skills**：手动放入 `local-skills/` 的自建 skills

### 添加本地自建 skill

在 `local-skills/` 下创建目录，放入 skill 文件：

```bash
mkdir ~/.agent-skills/local-skills/my-skill
# 创建 SKILL.md 等文件...
```

然后通过 `/install-skills` → 选择 local-skills 来源安装。

### 添加 Git 仓库 skill

通过 `/install-skills` → 选择 git-repo-skills 来源，按提示输入 clone 地址即可。

也可以手动添加子模块：

```bash
cd ~/.agent-skills
git submodule add https://github.com/user/repo.git git-repo-skills/my-repo
git submodule update --init git-repo-skills/my-repo
```

### 更新 git-repo-skills 中的所有子模块

```
/update-skills
```

或手动更新：

```bash
cd ~/.agent-skills
git submodule update --remote git-repo-skills/
git add .
git commit -m "更新 git-repo-skills 子模块"
git push
```

## 目录结构

```
~/.agent-skills/                    # 本仓库位置
├── .opencode/
│   └── commands/                   # 管理命令（软链接到 ~/.config/opencode/commands/）
│       ├── install-skills.md
│       ├── uninstall-skills.md
│       ├── update-skills.md
│       └── git-update.md           # 仓库内部命令，不需全局安装
│
├── skill-hub/                      # SkillHub 下载的 skills（由 /install-skills 自动管理）
│   └── <slug>/
│
├── local-skills/                   # 本地自建 skills
│   ├── github/
│   ├── nano-pdf/
│   └── skill-vetter/
│
├── git-repo-skills/                # Git 仓库 skills（子模块）
│   ├── anthropics-skills/          # 子模块：Anthropic 官方 skills
│   └── superpowers/                # 子模块：Superpowers skills
│
├── .gitmodules                     # Git 子模块配置
└── README.md                       # 本文件
```

软链接安装在**当前项目**目录下：

```
<你的项目>/
└── .opencode/
    └── skills/                     # 软链接由 /install-skills 自动创建，指向 ~/.agent-skills/ 中的源文件
        ├── brave-search -> ~/.agent-skills/skill-hub/brave-search/
        ├── github -> ~/.agent-skills/local-skills/github/
        └── frontend-design -> ~/.agent-skills/git-repo-skills/anthropics-skills/skills/frontend-design/
```

## 工作原理

1. **`~/.agent-skills/`**：作为中央仓库，集中存放三类 skills 的源文件
2. **`<当前项目>/.opencode/skills/`**：软链接安装目标，指向 `~/.agent-skills/` 中的源文件
3. **`~/.config/opencode/commands/`**：存放全局可用的管理命令软链接

当你运行 `/install-skills` 时：
- SkillHub 来源：下载源文件到 `~/.agent-skills/skill-hub/<slug>/`，再在当前项目的 `.opencode/skills/` 创建软链接
- local-skills / git-repo-skills 来源：直接在当前项目的 `.opencode/skills/` 创建指向源目录的软链接

## 常见问题

**Q: 为什么要把仓库放在 ~/.agent-skills/？**
A: 这是约定的位置，方便管理命令用绝对路径找到所有 skills。

**Q: SkillHub、local-skills、git-repo-skills 有什么区别？**
A: SkillHub 是在线下载的第三方 skills；local-skills 是你自己创建的；git-repo-skills 是通过 git submodule 跟踪的外部仓库，可以统一更新。

**Q: git-update.md 为什么不全局安装？**
A: 它是用于更新本仓库自身的命令，只在 `~/.agent-skills/` 内使用。
