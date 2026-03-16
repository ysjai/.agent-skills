---
description: 安装 skills（支持 SkillHub 下载、Git repo、本地 local-skills 三种来源）
---

# 安装 Skills

你的任务是帮用户安装Skill。支持三种来源，统一以软链接方式挂载到**当前项目**的 `.opencode/skills/` 目录：

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

## 分支 A：从 SkillHub 下载

### A1. 检查 skillhub CLI 是否已安装

```bash
which skillhub 2>/dev/null && skillhub -v 2>&1 || echo "NOT_INSTALLED"
```

如果未安装（输出 `NOT_INSTALLED`），使用 question 工具询问：
- 选项1（默认）：立即安装 skillhub CLI
- 选项2：取消

选择"取消"则终止流程，提示用户手动安装：
```
curl -fsSL https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/install.sh | bash -s -- --cli-only
```

选择"安装"则执行上述命令，安装完成后重新验证，若仍失败则终止并告知用户。

### A2. 获取用户意图

使用 question 工具询问：
- 选项1（默认）：浏览精选榜单（默认展示前 10 条）
- 选项2：直接输入技能名称标识安装（如 `brave-search`、`github`，可在 https://skillhub.tencent.com 查看）
- 选项3：搜索关键词
- 选项4：描述我的需求，帮我找合适的技能

### A3a. 浏览精选榜单

默认展示前 10 个精选技能：

```bash
curl -fsSL "https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/skills.json" 2>/dev/null | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
featured = data.get('featured', [])
skills_map = {s['slug']: s for s in data.get('skills', [])}
for i, slug in enumerate(featured[:10], 1):
    s = skills_map.get(slug, {})
    name = s.get('name', slug)
    desc_zh = s.get('description_zh', s.get('description', ''))[:60]
    version = s.get('version', '')
    stars = s.get('stars', 0)
    print(f'{i:2d}. [{slug}] {name} v{version} ★{stars}')
    print(f'    {desc_zh}')
"
```

用 question 工具展示，让用户输入编号选择（多个用空格分隔，`more` 加载更多，`exit` 取消）。

若用户输入 `more`，将上限改为 50 重新获取并展示。

### A3b. 直接输入技能名称

用 question 工具提示用户输入技能的名称标识（即 slug，技能在 SkillHub 上的唯一 ID）：

```
请输入要安装的技能名称标识（支持同时输入多个，用空格分隔）：

示例：
  brave-search          → Brave 网页搜索技能
  github                → GitHub 操作技能
  brave-search github   → 同时安装以上两个

可在 https://skillhub.tencent.com 查看所有技能名称
```

### A3c. 搜索关键词

用 question 工具让用户输入关键词，执行：

```bash
skillhub search "<关键词>" 2>&1 | head -80
```

解析结果，用 question 工具展示供用户选择。

### A3d. 描述需求，智能匹配技能

用 question 工具让用户用自然语言描述想解决的问题，例如：

> "我想让 AI 能搜索网络"
> "帮我处理 PDF 文件"
> "我需要查看 GitHub 上的 issue 和 PR"

根据用户描述，理解其核心意图，提取 1-3 个最相关的搜索关键词，然后依次执行搜索：

```bash
skillhub search "<关键词1>" 2>&1 | head -80
skillhub search "<关键词2>" 2>&1 | head -80  # 如有多个关键词
```

对搜索结果去重合并，按相关度排序，用 question 工具展示给用户，并在列表上方用一句话说明"根据您的描述，为您找到以下相关技能"。若搜索结果为空，直接告知用户未找到相关技能，询问是否换个关键词重试。

### A4. 检查已有，确认覆盖

```bash
TARGET_DIR="$HOME/.agent-skills/skill-hub"
mkdir -p "$TARGET_DIR"
for SLUG in <选中的slugs>; do
    if [ -d "$TARGET_DIR/$SLUG" ]; then echo "EXISTS: $SLUG"; else echo "NEW: $SLUG"; fi
done
```

如果有已存在的 skill，用 question 工具**一次性**展示所有冲突，询问：
- 选项1（默认）：全部覆盖更新
- 选项2：跳过已存在，只安装新的
- 选项3：取消

### A5. 下载并创建软链接

对每个需要安装（或覆盖）的 slug：

```bash
TARGET_DIR="$HOME/.agent-skills/skill-hub"
mkdir -p "$TARGET_DIR"

# skillhub install 默认安装到当前目录的 skills/ 下，因此切换到临时目录执行
TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"
skillhub install "$SKILL_SLUG" --force 2>&1
cd - > /dev/null

# 将安装结果移到 skill-hub/
INSTALLED_DIR="$TMP_DIR/skills/$SKILL_SLUG"
if [ -d "$INSTALLED_DIR" ]; then
    rm -rf "$TARGET_DIR/$SKILL_SLUG"
    mv "$INSTALLED_DIR" "$TARGET_DIR/$SKILL_SLUG"
else
    # 兜底：找 skills/ 下第一个目录
    FOUND=$(ls "$TMP_DIR/skills/" 2>/dev/null | head -1)
    [ -n "$FOUND" ] && rm -rf "$TARGET_DIR/$SKILL_SLUG" && mv "$TMP_DIR/skills/$FOUND" "$TARGET_DIR/$SKILL_SLUG"
fi
rm -rf "$TMP_DIR"

# 软链接到当前项目的 .opencode/skills/
mkdir -p "$(pwd)/.opencode/skills"
LINK_PATH="$(pwd)/.opencode/skills/$SKILL_SLUG"
[ -L "$LINK_PATH" ] && rm "$LINK_PATH"
ln -s "$HOME/.agent-skills/skill-hub/$SKILL_SLUG" "$LINK_PATH"
```

### A6. 汇报并提醒

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

### C1. 列出当前已有的 Git repo

```bash
GIT_REPO_DIR="$HOME/.agent-skills/git-repo-skills"
if [ -d "$GIT_REPO_DIR" ]; then
    ls -1 "$GIT_REPO_DIR"
else
    echo "NOT_FOUND"
fi
```

用 question 工具展示已有 repo 列表，并询问操作：

```
git-repo-skills/ 中已有以下仓库：

  [1] anthropics-skills
  [2] superpowers

请选择操作：
```
- 选项1（默认）：从已有仓库中安装 skills
- 选项2：clone 新的 Git 仓库到 git-repo-skills/

若目录不存在或为空，跳过选项1，直接进入 C2b clone 流程。

### C2a. 从已有仓库安装

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

创建软链接：

```bash
SKILLS_DIR="$(pwd)/.opencode/skills"
mkdir -p "$SKILLS_DIR"
LINK_PATH="$SKILLS_DIR/<skillname>"
[ -L "$LINK_PATH" ] && rm "$LINK_PATH"
ln -s "<skill目录绝对路径>" "$LINK_PATH"
```

整组安装后做去重检查（移除已被整组包含的单独软链接）。

### C2b. Clone 新仓库

用 question 工具让用户输入 Git 仓库地址（如 `https://github.com/xxx/skills.git`），然后执行：

```bash
GIT_REPO_DIR="$HOME/.agent-skills/git-repo-skills"
mkdir -p "$GIT_REPO_DIR"
REPO_URL="<用户输入的地址>"
REPO_NAME=$(basename "$REPO_URL" .git)

# 检查是否已存在
if [ -d "$GIT_REPO_DIR/$REPO_NAME" ]; then
    echo "EXISTS: git-repo-skills/$REPO_NAME"
else
    git clone "$REPO_URL" "$GIT_REPO_DIR/$REPO_NAME"
fi
```

Clone 完成后，自动进入 C2a 流程，扫描该仓库中的 skills 供用户选择安装。

> 提示：若需持久化管理，建议手动将该仓库注册为 git submodule：
> `git submodule add <url> git-repo-skills/<name>`

### C3. 汇报并提醒

列出安装结果，提醒用户**重启 OpenCode** 生效。
