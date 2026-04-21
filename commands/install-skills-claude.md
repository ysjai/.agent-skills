---
description: 安装 skills 到 Claude Code（项目级或全局，来源支持 SkillHub、Git repo、本地 personal-skills）
---

# 安装 Skills 到 Claude Code

你的任务是帮用户安装 skill，以软链接方式挂载到 Claude Code 的指定目录。支持三种来源：SkillHub、personal-skills、git-repo-skills。

**路径约定**：
- `AGENT_SKILLS_DIR="$HOME/.agent-skills"`
- `PLATFORM="Claude Code"`
- `SKILLS_DIR` = `$(pwd)/.claude/skills` 或 `$HOME/.claude/skills`

## 执行步骤

### 0. 选择安装目标

使用 question 工具询问用户：

```
请选择安装目标：
```
- 选项1（默认）：当前项目（`$(pwd)/.claude/skills/`，仅当前项目生效）
- 选项2：全局（`~/.claude/skills/`，所有项目均生效）

### 1. 选择安装来源

使用 question 工具询问用户：

```
请选择安装来源：
```
- 选项1（默认）：SkillHub
- 选项2：git-repo-skills
- 选项3：personal-skills

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

如果本地有已下载的 SkillHub skills，询问：
- 选项1（默认）：直接安装
- 选项2：更新后安装
- 选项3：下载新技能

如果为空，直接执行 A3。

### A2. 直接安装

让用户从列表中选择要安装的 skills（`all`=全选，`exit`=取消），然后逐个执行冲突检测并创建软链接。

### A3. 检查 skillhub CLI

```bash
which skillhub 2>/dev/null && skillhub -v 2>&1 || echo "NOT_INSTALLED"
```

如果未安装，询问：立即安装 / 取消。

取消时提示：

```bash
curl -fsSL https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/install.sh | bash -s -- --cli-only
```

### A4. 选择要下载/更新的 skills

更新后安装：从已有列表中选择要更新的 skills。

下载新技能或首次下载：询问用户意图：
- 选项1（默认）：浏览精选榜单
- 选项2：直接输入技能名称标识
- 选项3：搜索关键词
- 选项4：描述我的需求，帮我找合适的技能

浏览精选榜单：

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

搜索关键词：

```bash
skillhub search "<关键词>" 2>&1 | head -80
```

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

列出成功安装/更新、跳过、失败的 skills，提醒用户**重启 Claude Code**生效。

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

### B2. 展示并选择

检查 `$SKILLS_DIR` 已安装情况，用 question 工具展示列表并让用户选择。

### B3. 创建软链接

对每个选中的 skill，执行冲突检测并创建软链接。

### B4. 汇报并提醒

列出安装结果，提醒用户**重启 Claude Code**生效。

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

如果本地有已有仓库，询问：直接使用已有仓库安装 / `git pull` 更新后再安装 / clone 新仓库。

### C2a. 直接使用已有仓库

让用户选择要使用的仓库（可多选），进入 C3。

### C2b. 更新后安装

```bash
git -C "$HOME/.agent-skills/git-repo-skills/<repo>" pull 2>&1
```

### C2c. Clone 新仓库

```bash
GIT_REPO_DIR="$HOME/.agent-skills/git-repo-skills"
mkdir -p "$GIT_REPO_DIR"
REPO_URL="<用户输入的地址>"
REPO_NAME=$(basename "$REPO_URL" .git)
git clone "$REPO_URL" "$GIT_REPO_DIR/$REPO_NAME" 2>&1
```

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

Claude Code 也支持“整组选择”，但**实际创建时一律展开为多个独立软链接**。

### C4. 创建软链接

无论用户选择“整组”还是“单独”，最终都创建扁平的独立软链接：

```bash
ln -s "<skill目录绝对路径>" "$SKILLS_DIR/<skillname>"
```

对每个待创建的软链接，都执行冲突检测并创建。

### C5. 汇报并提醒

列出安装结果，提醒用户**重启 Claude Code**生效。

> Claude Code 要求 `skills/<name>/SKILL.md` 的扁平结构，因此即使用户选择整组，实际安装也必须展开为多个独立 skill 目录。
