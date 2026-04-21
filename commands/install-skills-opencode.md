---
description: 安装 skills 到 OpenCode（项目级或全局，来源支持 SkillHub、Git repo、本地 personal-skills）
---

# 安装 Skills 到 OpenCode

你的任务是帮用户安装 skill，以软链接方式挂载到 OpenCode 的指定目录。支持三种来源：

| 来源 | 说明 | 文件位置 |
|------|------|---------|
| SkillHub | 从腾讯 SkillHub 在线下载 | 下载到 `skill-hub/<slug>/`，再软链接 |
| personal-skills | 用户手动放入 `personal-skills/` 的自建 skills | 直接从 `personal-skills/<name>/` 软链接 |
| git-repo-skills | `git-repo-skills/` 下的 Git 仓库（支持 clone 新增） | 直接从 `git-repo-skills/<repo>/` 软链接 |

**路径约定**：
- `AGENT_SKILLS_DIR="$HOME/.agent-skills"`
- `PLATFORM="OpenCode"`
- `SKILLS_DIR` = `$(pwd)/.opencode/skills` 或 `$HOME/.config/opencode/skills`

## 执行步骤

### 0. 选择安装目标

使用 question 工具询问用户：

```
请选择安装目标：
```
- 选项1（默认）：当前项目（`$(pwd)/.opencode/skills/`，仅当前项目生效）
- 选项2：全局（`~/.config/opencode/skills/`，所有项目均生效）

### 1. 选择安装来源

使用 question 工具询问用户：

```
请选择安装来源：
```
- 选项1（默认）：SkillHub（在线下载，国内高速，收录 1.3 万个 AI Skills）
- 选项2：git-repo-skills（Git 仓库，支持输入 clone 地址新增）
- 选项3：personal-skills（本地自建，手动放入 personal-skills/ 目录）

## 冲突检测与软链接创建（统一模板）

### 检测

```bash
LINK_PATH="$SKILLS_DIR/<skillname>"
if [ ! -e "$LINK_PATH" ] && [ ! -L "$LINK_PATH" ]; then
    echo "OK"
elif [ -L "$LINK_PATH" ]; then
    TARGET=$(readlink "$LINK_PATH")
    case "$TARGET" in
        $HOME/.agent-skills/*) echo "MANAGED" ;;
        *) echo "CONFLICT_SYMLINK|$TARGET" ;;
    esac
else
    echo "CONFLICT_REAL"
fi
```

### 处理

| 检测结果 | 处理方式 |
|----------|----------|
| `OK` | 直接创建软链接 |
| `MANAGED` | 删除旧链接，重新创建 |
| `CONFLICT_SYMLINK` | 提示用户目标已存在并指向 `<target>`，询问：覆盖 / 跳过 |
| `CONFLICT_REAL` | 提示用户目标是真实目录/文件，询问：覆盖 / 跳过 |

### 创建

```bash
mkdir -p "$SKILLS_DIR"
LINK_PATH="$SKILLS_DIR/<skillname>"
SOURCE_PATH="<源目录绝对路径>"
ln -s "$SOURCE_PATH" "$LINK_PATH"
```

> 以下各分支中，凡“执行冲突检测并创建软链接”均指此统一模板。

## 分支 A：从 SkillHub 安装

### A1. 扫描本地已有的 SkillHub skills

```bash
SKILL_HUB_DIR="$HOME/.agent-skills/skill-hub"
if [ -d "$SKILL_HUB_DIR" ]; then
    for d in "$SKILL_HUB_DIR"/*/; do
        [ -d "$d" ] || continue
        slug=$(basename "$d")
        skill_md="$d/SKILL.md"
        name=$(grep -m1 '^# ' "$skill_md" 2>/dev/null | sed 's/^# //' || echo "$slug")
        link="$SKILLS_DIR/$slug"
        if [ -L "$link" ]; then
            echo "INSTALLED|$slug|$name"
        elif [ -e "$link" ]; then
            echo "CONFLICT|$slug|$name"
        else
            echo "AVAILABLE|$slug|$name"
        fi
    done
else
    echo "EMPTY"
fi
```

如果本地有已下载的 SkillHub skills，用 question 工具展示列表并询问：
- 选项1（默认）：直接安装
- 选项2：更新后安装
- 选项3：下载新技能

如果本地没有任何 SkillHub skills（EMPTY），跳过此询问，直接执行 A3。

### A2. 直接安装

让用户从列表中选择要安装的 skills（输入编号，多个空格分隔，`all`=全选，`exit`=取消）。

对每个选中的 slug，执行冲突检测并创建软链接，源路径为 `$HOME/.agent-skills/skill-hub/$SKILL_SLUG`。

### A3. 检查 skillhub CLI

```bash
which skillhub 2>/dev/null && skillhub -v 2>&1 || echo "NOT_INSTALLED"
```

如果未安装，询问：
- 选项1（默认）：立即安装 skillhub CLI
- 选项2：取消

若用户取消，提示：

```bash
curl -fsSL https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/install.sh | bash -s -- --cli-only
```

### A4. 选择要下载/更新的 skills

如果是“更新后安装”：让用户从已有列表中选择要更新的 skills。

如果是“下载新技能”或首次下载：询问用户意图：
- 选项1（默认）：浏览精选榜单
- 选项2：直接输入技能名称标识
- 选项3：搜索关键词
- 选项4：描述我的需求，帮我找合适的技能

**浏览精选榜单**：

```bash
curl -fsSL "https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/skills.json" 2>/dev/null | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
skills = data.get('skills', [])
for s in skills[:10]:
    slug = s.get('slug', '')
    name = s.get('name', slug)
    desc = s.get('description', '')[:60]
    version = s.get('version', '')
    stars = s.get('stars', 0)
    rank = s.get('rank', '')
    print(f'{rank:>2}. [{slug}] {name} v{version} ★{stars}')
    print(f'    {desc}')
"
```

允许用户输入编号选择；`more` 继续加载更多；`exit` 取消。

**直接输入技能名称**：让用户输入 slug（支持多个，空格分隔）。

**搜索关键词**：

```bash
skillhub search "<关键词>" 2>&1 | head -80
```

**描述需求**：让用户用自然语言描述需求，提取 1-3 个关键词依次搜索，去重合并后展示。

### A5. 执行下载

```bash
TARGET_DIR="$HOME/.agent-skills/skill-hub"
mkdir -p "$TARGET_DIR"

TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"
skillhub install "$SKILL_SLUG" --force 2>&1
cd - > /dev/null

INSTALLED_DIR="$TMP_DIR/skills/$SKILL_SLUG"
if [ -d "$INSTALLED_DIR" ]; then
    rm -rf "$TARGET_DIR/$SKILL_SLUG"
    mv "$INSTALLED_DIR" "$TARGET_DIR/$SKILL_SLUG"
else
    FOUND=$(ls "$TMP_DIR/skills/" 2>/dev/null | head -1)
    [ -n "$FOUND" ] && rm -rf "$TARGET_DIR/$SKILL_SLUG" && mv "$TMP_DIR/skills/$FOUND" "$TARGET_DIR/$SKILL_SLUG"
fi
rm -rf "$TMP_DIR"
```

### A6. 创建软链接

对每个成功下载（或直接安装）的 slug，执行冲突检测并创建软链接，源路径为 `$HOME/.agent-skills/skill-hub/$SKILL_SLUG`。

### A7. 汇报并提醒

列出成功安装/更新、跳过、失败的 skills，提醒用户**重启 OpenCode**生效。

- 当前项目：提示软链接位置，可用 `uninstall-skills` 卸载
- 全局：提示在任何项目中均可使用

## 分支 B：从 personal-skills 安装

### B1. 扫描 personal-skills/

```bash
LOCAL_SKILLS_DIR="$HOME/.agent-skills/personal-skills"
if [ -d "$LOCAL_SKILLS_DIR" ]; then
    find "$LOCAL_SKILLS_DIR" -maxdepth 2 -name "SKILL.md" | while read f; do
        skill_dir=$(dirname "$f")
        echo "$(basename "$skill_dir")|$(realpath "$skill_dir")"
    done
else
    echo "NOT_FOUND"
fi
```

如果 `personal-skills/` 不存在或为空，提示用户先把 skill 目录（含 `SKILL.md`）放入 `~/.agent-skills/personal-skills/`。

### B2. 展示并选择

检查 `$SKILLS_DIR` 已安装情况，用 question 工具展示列表并让用户选择（多个空格分隔，`all`=全选，`exit`=取消）。

### B3. 创建软链接

对每个选中的 skill，执行冲突检测并创建软链接，源路径为 skill 的绝对路径。

### B4. 汇报并提醒

列出安装结果，提醒用户**重启 OpenCode**生效。

## 分支 C：从 git-repo-skills 安装

### C1. 扫描本地已有的 Git repo

```bash
GIT_REPO_DIR="$HOME/.agent-skills/git-repo-skills"
if [ -d "$GIT_REPO_DIR" ] && [ -n "$(ls -A "$GIT_REPO_DIR" 2>/dev/null)" ]; then
    ls -1 "$GIT_REPO_DIR"
else
    echo "EMPTY"
fi
```

如果本地有已有仓库，展示列表并询问：
- 选项1（默认）：直接使用已有仓库安装
- 选项2：`git pull` 更新后再安装
- 选项3：clone 新仓库

如果为空，直接执行 C2c。

### C2a. 直接使用已有仓库

让用户选择要使用的仓库（可多选），进入 C3。

### C2b. 更新后安装

对每个选中的仓库执行：

```bash
git -C "$HOME/.agent-skills/git-repo-skills/<repo>" pull 2>&1
```

### C2c. Clone 新仓库

让用户输入 Git 仓库地址，执行：

```bash
GIT_REPO_DIR="$HOME/.agent-skills/git-repo-skills"
mkdir -p "$GIT_REPO_DIR"
REPO_URL="<用户输入的地址>"
REPO_NAME=$(basename "$REPO_URL" .git)
git clone "$REPO_URL" "$GIT_REPO_DIR/$REPO_NAME" 2>&1
```

clone 完成后进入 C3。

### C3. 选择要安装的 skills

递归扫描 `SKILL.md`：

```bash
GIT_REPO_DIR="$HOME/.agent-skills/git-repo-skills"
REPO_DIR="$GIT_REPO_DIR/<repo>"
find "$REPO_DIR" -name "SKILL.md" | while read skill_md; do
    skill_dir=$(dirname "$skill_md")
    skill_name=$(basename "$skill_dir")
    if [ "$skill_dir" = "$REPO_DIR" ]; then
        echo "standalone|$skill_name|$(realpath "$skill_dir")"
    else
        rel_path="${skill_dir#$REPO_DIR/}"
        depth=$(echo "$rel_path" | tr -cd '/' | wc -c)
        if [ "$depth" -eq 0 ]; then
            echo "standalone|$skill_name|$(realpath "$skill_dir")"
        else
            group_skills_dir=$(dirname "$skill_dir")
            echo "grouped|$skill_name|$(realpath "$skill_dir")|$(realpath "$group_skills_dir")"
        fi
    fi
done
```

OpenCode 支持整组选择。展示时允许：
- 输入组号 = 安装该组下所有 skills
- 输入子编号 = 单独安装某个 skill

### C4. 创建软链接

#### OpenCode 平台策略

- **整组安装**：将该组 skills 的公共父目录作为软链接目标。
  - 组名推导规则：`<group-name>` = `basename $REPO_DIR`。若同一仓库有多个不同的 `group_skills_dir`，则组名格式为 `<repo>-<subdir>`。
  ```bash
  GROUP_NAME="$(basename "$REPO_DIR")"
  ln -s "<组 skills 的公共父目录>" "$SKILLS_DIR/$GROUP_NAME"
  ```
- **单独安装**：
  ```bash
  ln -s "<skill目录绝对路径>" "$SKILLS_DIR/<skillname>"
  ```

对每个待创建的软链接，都执行冲突检测并创建。

### C5. 汇报并提醒

列出安装结果，提醒用户**重启 OpenCode**生效。
