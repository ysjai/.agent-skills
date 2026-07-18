# 可视化伴侣

只在“看到内容”明显比文字说明更容易理解时使用，例如 UI mockup、布局对比、架构图和空间关系。需求澄清、技术取舍、范围和纯文字选项继续在终端讨论。可视化伴侣只支持本地 HTTP，不支持 HTTPS 页面、WSS 或 TLS 反向代理。

## 选择最轻模式

### 静态模式，默认

一次展示或不需要结构化点击时：

1. 在系统临时目录创建唯一 HTML 文件。
2. 使用可用的浏览器或本地打开工具展示文件。
3. 让用户直接在终端反馈。
4. 不启动服务器，不创建项目目录，不维护事件状态。

使用内联 CSS 或项目本地资源。不要默认加载 Unsplash、CDN 或其他外部资源；确实需要外部素材时先征得用户同意。

### 交互模式，按需

只有多轮实时刷新或结构化点击能显著改善讨论时，才启动 bundled server：

```bash
scripts/start-server.sh
```

默认会话位于 `/tmp`，停止后清理。启动结果包含：

```json
{"type":"server-started","url":"http://localhost:52341","session_dir":"/tmp/brainstorm-...","screen_dir":".../content","state_dir":".../state"}
```

保存 `session_dir`、`screen_dir` 和 `state_dir`，只在首次启动或服务重启时告诉用户 URL。

如果用户明确要求保留 mockup，可以使用：

```bash
scripts/start-server.sh --project-dir /path/to/project
```

持久模式只用于用户要保留的内容。确认 `.brainstorm/` 已被忽略，结束时清理运行状态。不要因为“以后可能有用”默认污染项目。

服务器只允许 loopback。远程或容器环境使用受控端口转发，不绑定 `0.0.0.0`。

## 交互循环

1. 向 `screen_dir/current.html` 写内容片段或完整 HTML；可以反复覆盖同一文件。
2. 服务器检测到更新后清空旧事件并刷新页面。
3. 告诉用户当前展示的问题；终端消息始终是主要反馈。
4. 用户回复后，如 `$STATE_DIR/events` 存在，读取 JSON lines 并与终端反馈一起理解。
5. 不需要视觉内容时保持上一个页面即可，不生成 waiting 页面。

服务异常或 `server-info` 消失时重新启动，不依赖多个标记文件推断复杂生命周期。

## 内容格式

HTML 以 `<!DOCTYPE` 或 `<html` 开头时原样提供并注入 helper；其他内容会自动套用 frame template。默认写内容片段。

最小选项示例：

```html
<h2>哪种布局更合适？</h2>
<p class="subtitle">重点比较可读性和视觉层级</p>

<div class="options">
  <div class="option" data-choice="single" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>单列布局</h3>
      <p>聚焦阅读</p>
    </div>
  </div>
  <div class="option" data-choice="split" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content">
      <h3>双列布局</h3>
      <p>导航和内容并列</p>
    </div>
  </div>
</div>
```

常用类见 `scripts/frame-template.html`：

- `.options`、`.option`：文字选项
- `.cards`、`.card`：视觉卡片
- `.mockup`、`.mockup-header`、`.mockup-body`：界面预览
- `.split`：并排布局
- `.mock-nav`、`.mock-sidebar`、`.mock-content`：线框元素

容器添加 `data-multiselect` 可启用多选。每屏保持 2-4 个真正有区别的选项，保真度与问题匹配，不追求无关的像素细节。

## 事件

点击事件写入 `$STATE_DIR/events`，每行一个 JSON 对象：

```jsonl
{"type":"click","choice":"single","text":"单列布局","timestamp":1706000101000}
```

浏览器点击只表示探索或倾向，不自动替代用户在终端中的最终决定。没有 events 文件时直接使用终端反馈。

## 清理

```bash
scripts/stop-server.sh "$SESSION_DIR"
```

临时会话只删除经过严格校验的单层 `/tmp/brainstorm-*` 目录。持久会话保留 content，删除 server 状态和事件。

参考：

- `scripts/frame-template.html`：样式和内容容器
- `scripts/helper.js`：刷新和点击交互
