---
description: 安装 skills（交互式从 skills 目录选择要安装的 skill 到当前项目）
---

# 安装 Skills

交互式从 skills 目录中选择 skills 安装到当前项目的 `.opencode/skills/` 目录。

## 执行步骤

1. 检查默认 skills 目录 `~/.agent-skills/` 是否存在：

   ```bash
   if [ -d ~/.agent-skills ]; then echo "FOUND"; else echo "NOT_FOUND"; fi
   ```

   如果目录不存在，调用 question 工具询问用户：
   - 选项 1（默认）：终止安装（提示用户先创建 `~/.agent-skills/` 目录并将 skills 放入其中）
   - 选项 2：指定其他 skills 目录路径

   选择 1 → 终止流程，告知用户：`请先创建 ~/.agent-skills/ 目录，将 skill 或包含 skills 的仓库放入其中，然后重新运行此命令。`
   选择 2 → 再次调用 question 工具让用户输入路径，验证该路径存在后继续

2. 使用 bash 一次性递归扫描所有包含 `SKILL.md` 的目录：

   ```bash
   SKILLS_DIR="<用户选择的目录>"
   find "$SKILLS_DIR" -name "SKILL.md" | while read skill_md; do
       skill_dir=$(dirname "$skill_md")
       skill_name=$(basename "$skill_dir")
       rel_path="${skill_dir#$SKILLS_DIR/}"
       depth=$(echo "$rel_path" | tr -cd '/' | wc -c)
       if [ "$depth" -eq 0 ]; then
           echo "standalone|$skill_name|$skill_dir"
       else
           group=$(echo "$rel_path" | cut -d'/' -f1)
           # 取该 skill 目录的父目录作为分组的 skills 存放目录
           group_skills_dir=$(dirname "$skill_dir")
           echo "grouped|$group|$skill_name|$skill_dir|$group_skills_dir"
       fi
   done
   ```

   输出中 `group_skills_dir` 即为该分组内所有 skill 的公共父目录（如 `~/.agent-skills/anthropics-skills/skills/`），
   整组安装时应链接此目录，而非仓库根目录。

3. 使用 bash 检查当前项目已安装的 skills：

   ```bash
   if [ -d .opencode/skills ]; then ls -1 .opencode/skills/; fi
   ```

4. 根据扫描结果构建带编号的选项列表，**分两个阶段**用 question 工具询问：

   **阶段一：总览选择**

   将扫描结果按以下方式组织并展示，每个分组下列出其包含的所有 skills：
   - 分组编号选项（如 `[1]`）表示**整组安装**
   - 分组内每个 skill 也有独立编号（如 `[1a]`、`[1b]`）表示**单独安装**
   - 独立 skill 各自有编号
   - 已完整安装的标注 `[已安装]`，部分安装的标注 `[部分已安装]`

   使用 question 工具展示，例如：

   ```
   请选择要安装的内容（输入编号，多个用空格分隔，all=全选，exit=取消）：

   分组（输入组号=整组安装，输入子编号=单独安装）：
   [1] anthropics-skills（17 个 skills）[部分已安装]
       [1a] frontend-design [已安装]
       [1b] github
       [1c] git
       [1d] skill-creator [已安装]
       ...
   [2] superpowers（12 个 skills）
       [2a] weather
       [2b] browser
       ...

   独立 skills：
   [3] my-custom-skill [已安装]
   [4] another-skill
   ```

   - 用户输入编号，支持混合选择，如 `1 2b 4`（整组安装 anthropics-skills + 单独安装 superpowers 的 browser + 安装 another-skill）
   - 输入 `all` 全选所有
   - 输入 `exit` 取消

5. 使用 bash 创建软链接：

   ```bash
   mkdir -p .opencode/skills

   # 整组安装：链接到该组内存放各 skill 的公共父目录，而非仓库根目录
   # 例如链接 ~/.agent-skills/anthropics-skills/skills/ 而非 ~/.agent-skills/anthropics-skills/
   # 该公共父目录在步骤 2 扫描时可通过分组内任意 skill 的路径取其 dirname 得到
   ln -s <分组内skills的公共父目录> .opencode/skills/<group>

   # 单个 skill 安装，软链接指向具体 skill 目录
   ln -s <skill_dir的绝对路径> .opencode/skills/<skillname>
   ```

   - 如果目标软链接已存在则跳过，不要覆盖

6. **去重检查**：整组安装后，检查 `.opencode/skills/` 下是否存在之前单独安装的、属于该组的 skill 软链接，如果有则移除。

   判断依据：遍历 `.opencode/skills/` 下所有软链接，如果某个软链接的目标路径（`readlink`）是刚安装的分组目录下的子路径，则说明已被整组包含，移除该单独的软链接。

   ```bash
   # 对每个刚整组安装的 group
   GROUP_TARGET=$(readlink .opencode/skills/<group>)
   for link in .opencode/skills/*; do
       if [ -L "$link" ] && [ "$(basename "$link")" != "<group>" ]; then
           link_target=$(readlink "$link")
           # 检查该软链接目标是否在 group 目录内
           case "$link_target" in
               "$GROUP_TARGET"/*|"<SKILLS_DIR>/<group>"/*)
                   rm "$link"
                   echo "移除重复链接: $(basename "$link")（已包含在 <group> 中）"
                   ;;
           esac
       fi
   done
   ```

7. 列出本次安装结果，告知用户共安装了哪些 skills。

8. 提醒用户：**请重启 OpenCode 以使新配置的 skills 生效。**
