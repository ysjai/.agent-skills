---
description: 卸载 skills（交互式从当前项目移除已安装的 skills）
---

# 卸载 Skills

交互式从当前项目的 `.opencode/skills/` 目录中移除已安装的 skills。

## 执行步骤

1. 使用 bash 扫描当前项目已安装的 skills：

   ```bash
   if [ -d .opencode/skills ]; then
       for item in .opencode/skills/*; do
           if [ -L "$item" ]; then
               name=$(basename "$item")
               target=$(readlink "$item")
               # 检查是否是分组（软链接目标目录内含多个 skill）
               if [ -d "$item" ] && ls "$item"/*/SKILL.md >/dev/null 2>&1; then
                   count=$(ls -d "$item"/*/SKILL.md 2>/dev/null | wc -l)
                   echo "group|$name|$target|$count"
               else
                   echo "single|$name|$target"
               fi
           fi
       done
   else
       echo "NO_SKILLS_DIR"
   fi
   ```

   如果 `.opencode/skills/` 不存在或为空，告知用户当前项目没有已安装的 skills，终止流程。

2. 根据扫描结果构建带编号的选项列表，向用户展示：

   - 分组编号（如 `[1]`）表示**整组卸载**
   - 分组内每个 skill 也有独立编号（如 `[1a]`、`[1b]`）表示**单独卸载**
   - 独立 skill 各自有编号

   使用 question 工具展示，例如：

   ```
   请选择要卸载的内容（输入编号，多个用空格分隔，all=全选，exit=取消）：

   分组（输入组号=整组卸载，输入子编号=单独卸载）：
   [1] anthropics-skills（17 个 skills）
       [1a] frontend-design
       [1b] github
       [1c] skill-creator
       ...
   [2] superpowers（12 个 skills）
       [2a] weather
       [2b] browser
       ...

   独立 skills：
   [3] my-custom-skill
   [4] another-skill
   ```

   - 用户输入编号，支持混合选择，如 `1 3`（整组卸载 anthropics-skills + 卸载 my-custom-skill）
   - 输入 `all` 全选所有
   - 输入 `exit` 取消

3. 使用 bash 移除用户选择的软链接：

   ```bash
   # 整组卸载，移除分组软链接
   rm .opencode/skills/<group>

   # 单个 skill 卸载，移除该 skill 的软链接
   rm .opencode/skills/<skillname>
   ```

   - 只移除软链接，**不删除** `~/.agent-skills/` 中的源文件

4. 列出本次卸载结果，告知用户共卸载了哪些 skills。

5. 提醒用户：**请重启 OpenCode 以使变更生效。**
