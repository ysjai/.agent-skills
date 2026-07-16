# 可视化伴侣指南

这是一个基于浏览器的头脑风暴辅助工具，用来展示 mockup、图表和选项。

## 什么时候使用

按“每个问题”判断，而不是按“整个会话”判断。判断标准是：**用户看见它会不会比只读文字更容易理解？**

**内容本身是视觉内容时，使用浏览器：**

- **UI mockup** — 线框图、布局、导航结构、组件设计
- **架构图** — 系统组件、数据流、关系图
- **并排视觉对比** — 比较两种布局、两套配色、两个设计方向
- **视觉细节打磨** — 问题涉及观感、间距、视觉层级时
- **空间关系** — 状态机、流程图、实体关系图

**内容是文本或表格时，使用终端：**

- **需求和范围问题** — “X 是什么意思？”、“哪些功能在范围内？”
- **概念性的 A/B/C 选择** — 在文字描述的方案之间选择
- **取舍列表** — 优缺点、对比表
- **技术决策** — API 设计、数据建模、架构方案选择
- **澄清问题** — 任何答案主要是文字，而不是视觉偏好的问题

关于 UI 的问题不一定就是视觉问题。“你想要哪种向导？”是概念问题，走终端。“哪种向导布局感觉更合适？”是视觉问题，走浏览器。

## 工作方式

服务器会监听一个目录中的 HTML 文件，并把最新文件展示到浏览器里。你向 `screen_dir` 写入 HTML，用户在浏览器中看到并点击选择。选择结果会记录到 `state_dir/events`，下一轮你读取即可。

**内容片段 vs 完整文档：** 如果 HTML 文件以 `<!DOCTYPE` 或 `<html` 开头，服务器会原样提供它，只注入 helper 脚本。否则服务器会自动用 frame template 包裹内容，添加页头、CSS 主题、选择指示器和交互基础设施。**默认写内容片段。** 只有需要完全控制页面时，才写完整文档。

## 启动会话

```bash
# 使用持久化模式启动服务器（mockup 保存到项目里）
scripts/start-server.sh --project-dir /path/to/project

# 返回：{"type":"server-started","port":52341,"url":"http://localhost:52341",
#        "screen_dir":"/path/to/project/.brainstorm/12345-1706000000/content",
#        "state_dir":"/path/to/project/.brainstorm/12345-1706000000/state"}
```

保存返回结果中的 `screen_dir` 和 `state_dir`。告诉用户打开 URL。

**查找连接信息：** 服务器会把启动 JSON 写入 `$STATE_DIR/server-info`。如果你在后台启动服务器但没有捕获 stdout，读取该文件即可获取 URL 和端口。使用 `--project-dir` 时，在 `<project>/.brainstorm/` 下查找会话目录。

**注意：** 传入项目根目录作为 `--project-dir`，这样 mockup 会持久化到 `.brainstorm/`，重启服务器也不会丢。否则文件会写到 `/tmp`，停止后会清理。如果项目还没有忽略 `.brainstorm/`，提醒用户把它加入 `.gitignore`。

**按平台启动服务器：**

**Claude Code（macOS / Linux）：**
```bash
# 默认模式可用，脚本会自己把服务器放到后台
scripts/start-server.sh --project-dir /path/to/project
```

**Claude Code（Windows）：**
```bash
# Windows 会自动检测并使用前台模式，这会阻塞工具调用。
# 使用 Bash 工具调用时设置 run_in_background: true，让服务器跨会话轮次保持运行。
scripts/start-server.sh --project-dir /path/to/project
```
通过 Bash 工具调用时，设置 `run_in_background: true`。下一轮读取 `$STATE_DIR/server-info` 获取 URL 和端口。

**Codex：**
```bash
# Codex 会回收后台进程。脚本会自动检测 CODEX_CI，切换到前台模式。
# 正常运行即可，不需要额外参数。
scripts/start-server.sh --project-dir /path/to/project
```

**Gemini CLI：**
```bash
# 使用 --foreground，并在 shell 工具调用中设置 is_background: true，
# 让进程跨会话轮次保持运行。
scripts/start-server.sh --project-dir /path/to/project --foreground
```

**其他环境：** 服务器必须能在多轮对话间保持后台运行。如果环境会回收 detached 进程，使用 `--foreground`，并用该平台支持的后台执行机制启动。

如果浏览器无法访问 URL（远程/容器环境常见），绑定非 loopback host：

```bash
scripts/start-server.sh \
  --project-dir /path/to/project \
  --host 0.0.0.0 \
  --url-host localhost
```

使用 `--url-host` 控制返回 URL 中显示的 hostname。

## 循环流程

1. **检查服务器仍在运行**，然后向 `screen_dir` 写一个新的 HTML 文件：
   - 每次写入前，检查 `$STATE_DIR/server-info` 是否存在。如果不存在，或者 `$STATE_DIR/server-stopped` 存在，说明服务器已停止，需要用 `start-server.sh` 重启。服务器在 30 分钟无活动后会自动退出
   - 使用语义化文件名，例如 `platform.html`、`visual-style.html`、`layout.html`
   - **不要复用文件名**，每个 screen 都要用新文件
   - 使用 Write 工具，不要用 cat/heredoc，避免把噪音输出到终端
   - 服务器会自动展示最新文件

2. **告诉用户该看什么，然后结束本轮：**
   - 提醒他们 URL（每一步都提醒，不只第一次）
   - 简短说明屏幕内容，例如“正在展示首页的 3 个布局选项”
   - 请他们在终端回复：“看一下，告诉我你的想法。如果愿意，也可以点击选择一个选项。”

3. **下一轮用户回复后：**
   - 如果 `$STATE_DIR/events` 存在，读取它。这里包含用户在浏览器中的交互（点击、选择），格式为 JSON lines
   - 把浏览器事件和用户终端文本合并理解
   - 终端消息是主要反馈；`state_dir/events` 提供结构化交互数据

4. **迭代或前进：** 如果反馈改变当前 screen，写一个新文件，例如 `layout-v2.html`。只有当前步骤确认后，才进入下一个问题

5. **回到终端时清除视觉内容：** 当下一步不再需要浏览器，例如澄清问题或取舍讨论，推送一个等待页面，清掉旧内容：

   ```html
   <!-- 文件名：waiting.html（或 waiting-2.html 等） -->
   <div style="display:flex;align-items:center;justify-content:center;min-height:60vh">
     <p class="subtitle">继续在终端中讨论...</p>
   </div>
   ```

   这样可以避免用户在对话已经前进后，仍然盯着一个已经解决的选择。下一个视觉问题出现时，再推送新内容文件。

6. 重复直到完成。

## 编写内容片段

只写页面内部内容。服务器会自动用 frame template 包裹它，加入页头、主题 CSS、选择指示器和全部交互基础设施。

**最小示例：**

```html
<h2>哪种布局更合适？</h2>
<p class="subtitle">请重点考虑可读性和视觉层级</p>

<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>单列布局</h3>
      <p>干净、聚焦的阅读体验</p>
    </div>
  </div>
  <div class="option" data-choice="b" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content">
      <h3>双列布局</h3>
      <p>侧边栏导航 + 主内容区</p>
    </div>
  </div>
</div>
```

就这样。不需要 `<html>`，不需要 CSS，也不需要 `<script>` 标签。服务器会提供这些。

## 可用 CSS 类

frame template 为你的内容提供这些 CSS 类：

### 选项（A/B/C 选择）

```html
<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>标题</h3>
      <p>描述</p>
    </div>
  </div>
</div>
```

**多选：** 在容器上添加 `data-multiselect`，允许用户选择多个选项。每次点击都会切换选中状态。指示条会显示选中数量。

```html
<div class="options" data-multiselect>
  <!-- 选项标记同上，用户可多选/取消选择 -->
</div>
```

### 卡片（视觉设计）

```html
<div class="cards">
  <div class="card" data-choice="design1" onclick="toggleSelect(this)">
    <div class="card-image"><!-- mockup 内容 --></div>
    <div class="card-body">
      <h3>名称</h3>
      <p>描述</p>
    </div>
  </div>
</div>
```

### Mockup 容器

```html
<div class="mockup">
  <div class="mockup-header">预览：Dashboard 布局</div>
  <div class="mockup-body"><!-- mockup HTML --></div>
</div>
```

### 分屏视图（并排）

```html
<div class="split">
  <div class="mockup"><!-- 左侧 --></div>
  <div class="mockup"><!-- 右侧 --></div>
</div>
```

### 优缺点

```html
<div class="pros-cons">
  <div class="pros"><h4>优点</h4><ul><li>收益</li></ul></div>
  <div class="cons"><h4>缺点</h4><ul><li>代价</li></ul></div>
</div>
```

### Mock 元素（线框构建块）

```html
<div class="mock-nav">Logo | 首页 | 关于 | 联系</div>
<div style="display: flex;">
  <div class="mock-sidebar">导航</div>
  <div class="mock-content">主内容区</div>
</div>
<button class="mock-button">操作按钮</button>
<input class="mock-input" placeholder="输入框">
<div class="placeholder">占位区域</div>
```

### 排版和章节

- `h2` — 页面标题
- `h3` — 章节标题
- `.subtitle` — 标题下方的次级文本
- `.section` — 带底部间距的内容块
- `.label` — 小号大写标签文字

## 浏览器事件格式

当用户在浏览器中点击选项时，交互会记录到 `$STATE_DIR/events`，一行一个 JSON 对象。你推送新 screen 时，该文件会自动清空。

```jsonl
{"type":"click","choice":"a","text":"选项 A - 简洁布局","timestamp":1706000101}
{"type":"click","choice":"c","text":"选项 C - 复杂网格","timestamp":1706000108}
{"type":"click","choice":"b","text":"选项 B - 混合布局","timestamp":1706000115}
```

完整事件流能显示用户探索路径。他们可能先后点击多个选项再做决定。最后一个包含 `choice` 字段的事件通常是最终选择，但点击模式也可能暴露犹豫或偏好，值得进一步询问。

如果 `$STATE_DIR/events` 不存在，说明用户没有在浏览器中交互；只使用他们在终端中的文本反馈。

## 设计建议

- **按问题调整保真度** — 布局问题用线框图，视觉细节打磨问题再做更精细的效果
- **每页都解释问题** — 写“哪种布局更专业？”而不是只写“选一个”
- **先迭代再前进** — 如果反馈改变当前 screen，写一个新版本
- **每屏最多 2-4 个选项**
- **重要时使用真实内容** — 例如摄影作品集，用真实图片（Unsplash）。占位内容会掩盖设计问题
- **保持 mockup 简洁** — 聚焦布局和结构，不追求像素级完美

## 文件命名

- 使用语义化名称：`platform.html`、`visual-style.html`、`layout.html`
- 不要复用文件名；每个 screen 都必须是新文件
- 迭代时追加版本后缀，例如 `layout-v2.html`、`layout-v3.html`
- 服务器按修改时间展示最新文件

## 清理

```bash
scripts/stop-server.sh $SESSION_DIR
```

如果会话使用了 `--project-dir`，mockup 文件会保留在 `.brainstorm/` 中，方便后续参考。只有 `/tmp` 会话会在停止时删除。

## 参考

- Frame template（CSS 参考）：`scripts/frame-template.html`
- Helper script（客户端逻辑）：`scripts/helper.js`
