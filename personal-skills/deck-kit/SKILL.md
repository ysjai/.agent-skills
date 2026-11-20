---
name: "deck-kit"
version: "2.1.1"
display_name: "演示片制作"
display_name_en: "Deck Kit"
description: "把内容做成单文件 HTML 演示片（1280×720，16:9），带翻页、缩略图目录、全屏放映、导出 PDF。用于技术分享、方案汇报、项目复盘、内部培训、路演。视觉风格已固化，可按需注入企业 logo（单枚或多枚并排），不提供则不带品牌。用户提到做片子、做 PPT、出幻灯片、做汇报页、deck、讲稿配图时使用。"
description_zh: "把内容做成单文件 HTML 演示片（1280×720，16:9），带翻页、缩略图目录、全屏放映、导出 PDF。用于技术分享、方案汇报、项目复盘、内部培训、路演。视觉风格已固化，可按需注入企业 logo（单枚或多枚并排），不提供则不带品牌。"
description_en: "Build single-file HTML slide decks (1280x720) with navigation, thumbnail rail, fullscreen presenting and PDF export. Fixed visual system, optional corporate logos (single or co-branded), unbranded by default."
---

# 演示片制作

做一份**单文件 HTML** 的演示片：双击能开、离线能放、Ctrl+P 直接导 PDF。视觉风格已固化为设计系统，页面只写语义结构。

## 什么时候用

用户要「做几页 PPT」「出个分享稿」「把这堆材料变成片子」，且满足：现场讲 / 内部汇报 / 方案评审 / 复盘。
需要可编辑 `.pptx` 源文件时另走 PPT 技能——本技能的产物是 HTML，导出的 PDF 不可回编。

## 五步流程

**1. 收料**（缺一项就问，不要猜）
先问一句：这份片子讲完，**听众要做什么决定**——批预算 / 拍板 / 认可进展 / 带走方法。这一句定类型，类型定骨架。
另外还要问：受众与场合、时长与页数、必讲的 3–5 个点、手上的材料（数据、报表、截图、旧文档都算；没有就说没有）、品牌（要不要放 logo、封面品牌行写什么；用户说空着就空着，不追问）。

**2. 定类型，出大纲，先确认**
从 `references/deck-types.md` 落一类（A 方案讲解 / B 方案评审 / C 总结汇报 / D 经验分享；D 再按主角是项目还是方法，选 D1 案例复盘或 D2 方法论讲解），取该类骨架。必需页不能省，可选页按内容取舍，「不要出现」的页直接不列。
每页一行：`页码 | 结论式标题 | 一句话主张 | 版式名`。用户点头再写代码。
页数经验值：10 分钟 ≈ 6–8 页，30 分钟 ≈ 12–16 页；与该类型的默认区间冲突时以内容为准，先砍可选页。

**3. 生成外壳**（命令在**项目目录**下执行，脚本用技能的绝对路径）

先确认依赖，别写完十几页才发现跑不起来：`node -v` 要有；校验阶段要 playwright（缺就 `npm i -D playwright`）；只有处理新 logo 才需要 `python3` + Pillow。校验优先用本机 Chrome，没装会退回自带的 chromium。

```bash
KIT=~/.workbuddy/skills/deck-kit
node $KIT/scripts/new-deck.mjs --out outputs/<name>.html --title "<标题>"
# 要品牌时（用户没说就不用加）：
node $KIT/scripts/new-deck.mjs --out outputs/<name>.html --title "<标题>" --brand brand.json
```
外壳自带封面 + 1 页示例 + 全部导航逻辑。新页面按顺序插到 `<!-- SLIDES -->` 这行锚点**之前**，锚点本身保留（下次还能接着加）。示例页用完删掉，页脚页码按实际位置改。

**4. 写页面**
从 `references/layouts.md` 挑版式片段，替换文案。每条 `section` 结构固定：

```html
<section class="slide" data-layout="cards">
  <div class="kicker">01 · 章节名 <span class="dim">副标题</span></div>
  <h1 class="title">结论式标题，<em>后半句是主张</em></h1>
  <div class="lead">一到两句导语。</div>
  <div class="body"> …版式内容… </div>
  <div class="foot"><div class="fl"><span class="dot"></span>来源</div><div class="pg">03</div></div>
</section>
```
页脚平时只有页码。这一页有量化断言时，才在 `.pg` 前面加 `.fl` 来源行——上面那行是带来源的写法。
封面用 `class="slide cover"`，内部结构见 `assets/template.html`。

`data-layout` 只是给人看的标记，不参与渲染。**导航、目录、页码读数、进度条、全屏按钮全部由 `deck.js` 自动生成，页面里一行都不用写**，也不要自己写。

**5. 校验，再交付**
```bash
node $KIT/scripts/verify.mjs outputs/<name>.html
```
校验会查这些：元素越界、控制台报错、**页脚页码是否连续**、**占位文案是否残留**、正文区是否为空、是否误留多个封面、是否有页面落在 `#stage` 之外（插错位置会被静默丢掉）；正文填充率低于 82% 会给提示（不阻塞，但通常是内容太少或版式选大了）。全过之后还要**逐页看截图**（`/tmp/deck-shot/`）检查对齐与节奏。

**退出码**：`0` 通过，`1` 片子有问题，`2` 缺 playwright——看到 2 去装依赖，不要改页面。末尾以 ⚠ 开头的三类提示（填充率、无来源数字、末页致谢）不阻塞，改不改由你判断。

外壳刚生成时必然是「不通过」的——它本身就是占位内容。替换完、页码改对，才会通过。

## 选版式

| 内容形态 | 版式 | 类名 |
|---|---|---|
| 开场 | 封面 | `.cover` |
| 讲什么、分几段 | 议程 | `.agenda` + `.thesis` |
| 时间/阶段推进 | 时间带 | `.tl` |
| 三五个关键数字 | 数字块 | `.grid4` + `.tile` |
| 构成占比、对比 | 堆叠条形图 | `.bars` `.brow` `.legend` |
| 多环节交接 | 流水线 | `.pipe` `.spine` |
| 一段配置/协议/代码 | 代码面板 + 说明卡 | `.code` + `.grid3` |
| 角色与流程对照 | 左表右流程 | `.two` + 自定义行 |
| 若干并列要点 | 卡片网格 | `.grid3` `.grid4` `.card` |
| 一个公式 / 一把尺子 | 深色公式面板 | 内联深色块 + `.small` |
| 收尾行动项 | 三卡 + 深色结论 | `.card` + `.thesis` |

细节片段见 `references/layouts.md`。一页用哪个版式看内容形态；一份片子整体偏重什么，看 `references/deck-types.md` 的页面配比。

## 硬规则（都是踩过坑换来的）

1. **一页一个重心**。标题已是结论，正文只做证据。
2. **正文必须填满**。正文区留白超过约两成就是空页（`verify.mjs` 的提示线是填充率 82%）——加大字号、补一行或换版式，不要靠留白撑。
3. **卡片可以 `flex:1` 均分列高，但卡片内部要 `justify-content:center`**；给卡片里的文字块加 `flex:1` 才会拉成空心盒子。
4. **左右两栏不要各自垂直居中**，顶边/底边永远对不齐。用等高行 + 占位标题，或让短的一侧 `flex:1`。
5. **深色块一页最多两个**，多了没有重心。
6. **强调色只给主张**，一页不超过三处；数字、标题、结论各一处已是上限。
7. **量化断言必须带来源**。页上出现百分比、倍数或样本量，就在 `.foot .fl` 写清单位、样本与出处；拿不到来源只有两条路——改成定性表述，或删掉这个数字。没有量化断言的页不要留 `.fl`（连圆点一起删），页脚只留页码。
8. **不要为了一页改 CSS**。改不动说明版式选错了，换一个。

## 品牌

**默认不带品牌。** 不传 `--brand`，封面没有品牌行、内页右上没有 logo、标题区也不留 logo 位。品牌在收料时问，用户说空着就不加，不要再劝。

需要品牌时写一份 `brand.json`（可放在任意位置；`logos[].src` 的路径**相对这个 json 文件**，不是相对项目根）：

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

- `name` + `tagline` 显示在封面左上角，形如「某某公司 · 内部技术分享」。填一个就显示一个，两个都空则整行不占位。
- `logos` 放几个就并排几个，自动加细分隔线，顺序即展示顺序。内页标题区会按 logo 实际宽度自动留白，长 kicker 不会压到 logo；不放 logo 就不留白。
- `accent` 只接受 6 位十六进制色值；深色块上的浅色强调会跟着自动算，不用手改。
- 品牌在**生成时**烘进 HTML（logo 转 data URI、封面文案转静态文本）。改完 `brand.json` 要重新跑一次 `new-deck`，已生成的文件不会变。
- `logos[].src` 要填**绝对路径**或相对 json 的路径（`~` 不会被展开）。
- 新 logo 先处理成透明底、统一高度：`node $KIT/scripts/brand.mjs logo.png --out-dir <目标目录>`。
- 只换强调色不动版式：`--accent "#7A5C3E"`。
- `assets/logos/` 下备有一枚现成 logo，可以直接拿来试格式，填它的绝对路径即可。

## 文件地图

```
README.md             给人和 agent 的速览：是什么、怎么用、怎么改
assets/deck.css       设计系统（令牌 + 版式 + 导航 + 打印）
assets/deck.js        运行时（品牌注入 / 缩放 / 翻页 / 目录 / 全屏）
assets/template.html  骨架与占位符
assets/logos/         备用 logo（默认不使用）
scripts/new-deck.mjs  生成外壳
scripts/brand.mjs     处理 logo
scripts/verify.mjs    交付前自检
references/deck-types.md 四类片子的骨架、自检、页面配比与版式偏好
references/layouts.md 11 个版式片段
references/style-guide.md 色值与字号、对齐铁律、加新版式的六步
references/content-rules.md 文案口径
examples/sample-ai-dlc.html 参考样例（16 页，D2 方法论讲解的完整骨架，旧版样式，只参考内容写法）
examples/README.md     样例怎么看
```

## 交付说明（写进回复里）

`←/→` 翻页 · `Home/End` 首末页 · `T` 目录 · `F` 全屏 · `ESC` 退出 · `Ctrl+P` 导 PDF（选「另存为 PDF」，纸张 1280×720，背景图形要勾选）。
