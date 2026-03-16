---
description: 安装 skills 到当前项目（支持 SkillHub 下载、Git repo、本地 local-skills 三种来源）
---

# 安装 Skills 到当前项目

你的任务是帮用户安装 skill，以软链接方式挂载到**当前项目**的 `.opencode/skills/` 目录。支持三种来源：

| 来源 | 说明 | 文件位置 |
|------|------|---------|
| SkillHub | 从腾讯 SkillHub 在线下载 | 下载到 `skill-hub/<slug>/`，再软链接 |
| local-skills | 用户手动放入 `local-skills/` 的自建 skills | 直接从 `local-skills/<name>/` 软链接 |
| git-repo-skills | `git-repo-skills/` 下的 Git 仓库（支持 clone 新增） | 直接从 `git-repo-skills/<repo>/` 软链接 |

**路径约定**（贯穿全流程）：
- `AGENT_SKILLS_DIR="$HOME/.agent-skills"` — skills 中央仓库，存放源文件
- `PROJECT_SKILLS_DIR="$(pwd)/.opencode/skills"` — 当前项目，软链接安装目标

---

## 执行步骤

### 1. 选择安装来源

使用 question 工具询问用户：

```
请选择安装来源：
```
- 选项1（默认）：SkillHub（在线下载，国内高速，收录 1.3 万个 AI Skills）
- 选项2：git-repo-skills（Git 仓库，支持输入 clone 地址新增）
- 选项3：local-skills（本地自建，手动放入 local-skills/ 目录）

---

## 分支 A：从 SkillHub 安装

### A1. 先运行下载流程

**完整执行 `/download-skills` 命令的分支 A 流程**（SkillHub 下载），将 skills 下载到 `~/.agent-skills/skill-hub/`。

具体步骤见 `download-skills.md` 的「分支 A：从 SkillHub 下载」，包括：
- A1：检查 skillhub CLI 是否已安装
- A2：获取用户意图（浏览榜单/输入名称/搜索/描述需求）
- A3：执行下载到 `$HOME/.agent-skills/skill-hub/`

下载完成后，记录本次成功下载的 slug 列表，进入 A2。

### A2. 创建软链接到当前项目

对每个成功下载的 slug：

```bash
SKILLS_DIR="$(pwd)/.opencode/skills"
mkdir -p "$SKILLS_DIR"
SKILL_SLUG="<slug>"
LINK_PATH="$SKILLS_DIR/$SKILL_SLUG"
[ -L "$LINK_PATH" ] && rm "$LINK_PATH"
ln -s "$HOME/.agent-skills/skill-hub/$SKILL_SLUG" "$LINK_PATH"
```

### A3. 汇报并提醒

列出成功安装/更新、跳过、失败的 skills，提醒用户**重启 OpenCode** 生效。

> 补充：Skills 文件在 `skill-hub/<slug>/`，软链接在 `.opencode/skills/<slug>`，可用 `uninstall-skills` 卸载。

---

## 分支 B：从 local-skills 安装

### B1. 扫描 local-skills/

```bash
LOCAL_SKILLS_DIR="$HOME/.agent-skills/local-skills"
if [ -d "$LOCAL_SKILLS_DIR" ]; then
    find "$LOCAL_SKILLS_DIR" -maxdepth 2 -name "SKILL.md" | while read f; do
        skill_dir=$(dirname "$f")
        echo "$(basename "$skill_dir")|$(realpath "$skill_dir")"
    done
else
    echo "NOT_FOUND"
fi
```

如果 `local-skills/` 不存在或为空，告知用户：将 skill 目录（含 `SKILL.md`）手动放入 `~/.agent-skills/local-skills/` 后重试，终止流程。

### B2. 展示并选择

检查当前项目 `$(pwd)/.opencode/skills/` 已安装情况，用 question 工具展示：

```
local-skills/ 中可用的 skills（输入编号，多个用空格分隔，all=全选，exit=取消）：

  [1] github [已安装]
  [2] nano-pdf
  [3] skill-vetter
```

### B3. 创建软链接

```bash
SKILLS_DIR="$(pwd)/.opencode/skills"
mkdir -p "$SKILLS_DIR"
# 对每个选中的 skill
SKILL_DIR="<skill的绝对路径>"
LINK_PATH="$SKILLS_DIR/<skillname>"
if [ ! -L "$LINK_PATH" ]; then
    ln -s "$SKILL_DIR" "$LINK_PATH"
    echo "LINKED: <skillname>"
else
    echo "SKIP: <skillname>（已安装）"
fi
```

### B4. 汇报并提醒

列出安装结果，提醒用户**重启 OpenCode** 生效。

---

## 分支 C：从 git-repo-skills 安装

### C1. 先运行下载/clone 流程

**完整执行 `/download-skills` 命令的分支 B 流程**（Git 仓库 Clone），将仓库克隆到 `~/.agent-skills/git-repo-skills/`。

具体步骤见 `download-skills.md` 的「分支 B：从 Git 仓库 Clone」，包括：
- B1：获取仓库地址（或展示已有仓库，让用户选择）
- B2：clone 新仓库或 pull 更新已有仓库

完成后记录目标仓库路径，进入 C2。

### C2. 选择要安装的 skills

对用户选中的仓库目录，递归扫描 `SKILL.md`：

```bash
GIT_REPO_DIR="$HOME/.agent-skills/git-repo-skills"
REPO_DIR="$GIT_REPO_DIR/<repo>"
find "$REPO_DIR" -name "SKILL.md" | while read skill_md; do
    skill_dir=$(dirname "$skill_md")
    skill_name=$(basename "$skill_dir")
    rel_path="${skill_dir#$REPO_DIR/}"
    depth=$(echo "$rel_path" | tr -cd '/' | wc -c)
    if [ "$depth" -eq 0 ]; then
        echo "standalone|$skill_name|$(realpath "$skill_dir")"
    else
        group_skills_dir=$(dirname "$skill_dir")
        echo "grouped|$skill_name|$(realpath "$skill_dir")|$(realpath "$group_skills_dir")"
    fi
done
```

检查当前项目 `$(pwd)/.opencode/skills/` 已安装情况，用 question 工具展示供选择：

```
请选择要安装的 skills（输入编号，多个用空格分隔，all=全选，exit=取消）：

[1] anthropics-skills 整组（17 个 skills）[部分已安装]
    [1a] frontend-design [已安装]
    [1b] skill-creator [已安装]
    [1c] github
    ...
[2] superpowers 整组（12 个 skills）
    [2a] brainstorming
    [2b] systematic-debugging
    ...
```

- 输入组号 = 整组安装（软链接指向该组 skills 的公共父目录）
- 输入子编号 = 单独安装（软链接指向具体 skill 目录）

### C3. 创建软链接

```bash
SKILLS_DIR="$(pwd)/.opencode/skills"
mkdir -p "$SKILLS_DIR"
LINK_PATH="$SKILLS_DIR/<skillname>"
[ -L "$LINK_PATH" ] && rm "$LINK_PATH"
ln -s "<skill目录绝对路径>" "$LINK_PATH"
```

整组安装后做去重检查（移除已被整组包含的单独软链接）。

### C4. 汇报并提醒

列出安装结果，提醒用户**重启 OpenCode** 生效。
