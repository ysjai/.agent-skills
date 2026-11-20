# deck-kit · 演示片制作

把内容做成一份**单文件 HTML 演示片**：双击能开、离线能放、Ctrl+P 直接导 PDF。
自带一套固定的视觉系统（藏青蓝 + 酒红强调）；品牌按需注入，不提供就不带 logo。

---

## 解决什么问题

| 做 PPT 的常见麻烦 | 这个技能的做法 |
|---|---|
| 每页手工排版，风格飘 | 11 个固化的版式片段，页面只写语义结构，样式全在 `deck.css` |
| 做完发现文字溢出、卡片拉空 | 交付前跑 `verify.mjs`，自动截图 + 查越界 / 页码 / 占位残留 |
| 换公司、加合作方 logo 要重做 | `brand.json` 里配 `logos` 数组，单 logo / 双 logo 自动排 |
| 发给别人打不开、字体丢失 | 单文件 HTML，CSS/JS/logo 全部内联，无外部依赖 |
| 想换公司色要逐页改 | 改 `:root` 一个 `--accent`，浅色强调与深底高亮自动派生 |

---

## 30 秒上手

在**项目目录**下执行（`KIT` 指向技能自己）：

```bash
KIT=~/.workbuddy/skills/deck-kit

# 1. 生成外壳（自带封面 + 1 页示例 + 全部导航逻辑）
node $KIT/scripts/new-deck.mjs --out outputs/my-deck.html --title "分享标题"

# 2. 按 $KIT/references/layouts.md 把页面插到 <!-- SLIDES --> 锚点之前
#    示例页用完删掉，页脚页码改成实际位置

# 3. 交付前自检（0 越界、0 报错、页码连续、无占位残留才算过）
node $KIT/scripts/verify.mjs outputs/my-deck.html
```

打开 `outputs/my-deck.html` 就能讲。截图落在 `/tmp/deck-shot/`，逐页看一遍密度和对齐再交付。

> 外壳刚生成时校验**必然不通过**——它本身就是占位内容。这不是坏了。

---

## 一份片子怎么长出来

1. **收料**：受众、时长、必讲点、手上的材料、品牌（可选）
2. **定类型 + 出大纲**：先定这是方案讲解 / 方案评审 / 总结汇报 / 经验分享，再按该类骨架排页
3. **生成外壳** → **填页面**：从 `references/layouts.md` 挑版式，替换文案
4. **校验** → 看截图 → 修
5. **交付**：单文件 HTML + 一句使用说明

页数经验值：10 分钟 ≈ 6–8 页，30 分钟 ≈ 12–16 页。

四类片子的骨架、自检清单、页面配比与版式偏好都在 `references/deck-types.md`。

---

## 品牌（可选）

**不传就是无品牌**：封面没有品牌行，内页右上没有 logo，标题区也不留 logo 位。要牌子就写一份 `brand.json`：

```json
{
  "name": "某某公司",
  "tagline": "内部技术分享",
  "accent": "#8E3B45",
  "logos": [
    { "src": "logo-a.png", "alt": "A 公司" },
    { "src": "logo-b.png", "alt": "B 公司" }
  ]
}
```

```bash
node $KIT/scripts/new-deck.mjs --out outputs/x.html --title "标题" --brand brand.json
```

注意：`logos[].src` 的路径相对 `brand.json` 自己所在目录，不是项目根；`~` 不会被展开。

- `name` + `tagline` 上封面左上角，填一个显示一个，两个都空则整行不占位
- `logos` 放几个就并排几个，自动加分隔线；内页标题区会按 logo 实际宽度留白，不会压字
- 新 logo 先处理成透明底、统一高度：`node $KIT/scripts/brand.mjs logo.png --out-dir <目标目录>`
  （`brand.mjs` 只适合白底图；深色底的 logo 会被抠坏，请人工处理）
- 只换强调色不动版式：加 `--accent "#7A5C3E"`

---

## 目录里都是什么

```
SKILL.md                 agent 的执行指令：五步流程、选版式、硬规则
README.md                本文件：给人看的速览
assets/deck.css          设计系统：色/字/间距令牌 + 组件 + 导航 + 打印
assets/deck.js           运行时：logo 注入、缩放自适应、翻页、缩略图目录、全屏
assets/template.html     骨架与占位符
assets/logos/            品牌 logo 库（备用素材，默认不使用）
scripts/new-deck.mjs     生成外壳
scripts/brand.mjs        处理 logo（去白底、等比缩放）
scripts/verify.mjs       交付前自检
references/deck-types.md 四类片子（方案讲解 / 方案评审 / 总结汇报 / 经验分享）的骨架与自检
references/layouts.md    11 个版式片段，可直接拷贝
references/style-guide.md 色板、字号、间距、密度、对齐铁律
references/content-rules.md 文案口径：结论先行、数字带来源、讲代价
examples/sample-ai-dlc.html 14 页样例（只参考内容写法，不要抄它的 style/script）
examples/README.md      样例怎么看
```

---

## 讲的时候

`←` `→` 翻页 · `Home` / `End` 首末页 · `T` 目录 · `F` 全屏 · `ESC` 退出 · `Ctrl+P` 导 PDF

导 PDF 时选「另存为 PDF」，纸张 1280×720，勾选「背景图形」。

全屏即放映模式：底部导航和左侧目录按钮会自动隐藏，动鼠标唤出、静止 2.2 秒淡出。

---

## 边界

- **不做 `.pptx` 导出**：要可回编的 Word/PPT 源文件，走 `workbuddy-pptx` 那条路；本技能产物是 HTML + PDF
- **不做多比例**：锁定 16:9（1280×720）
- **不做主题市场**：可换的是 logo、封面文案、强调色（`accent`）；藏青与主蓝是这套风格的骨架，要换主色得连浅底色一起成组调整
- **不替代内容思考**：版式解决「怎么摆」，标题写什么、数据从哪来仍然要人定
