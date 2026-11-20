# 版式片段

每条都是可直接拷贝的骨架，把中文占位换成你的内容即可。所有类名在 `assets/deck.css` 里定义。

片段里的 inline 样式是版式本身的一部分（栏宽比例、行内间距），照抄即可；**写新页时不要自己再加 inline 样式**，需要新结构就按 `style-guide.md` 最后那节把版式补进 CSS。

每个片段都标了**插入位置**：

- **整页**：从 `<section class="slide">` 开始，整块替换或追加
- **片段**：只粘贴到已存在的 `<div class="body">` 内部，不要再套一层 `.body`

标「片段」的版式只负责正文区，外层 `<section class="slide">`、`kicker / title / lead / foot` 仍要按 SKILL.md 的页面结构自己补齐。

页脚里的 `.fl` 来源行只在有量化断言时加；没有数字的页只留 `.pg` 一个页码。

---

## 1. 封面 `.cover`

**插入位置**：整页。

**何时**：开场第一页。一页只讲一件事：这是什么、谁来听、谁在讲。

```html
<section class="slide cover">
  <div class="grid-bg"></div>
  <div class="inner">
    <div class="brandline"><span>公司 · 部门 / 场合</span></div>
    <h1>
      <span>主标题前半句，</span>
      <span class="accent">后半句给主张</span>
    </h1>
    <div class="sub">一到两句导语：解决什么问题、听众能带走什么。</div>
    <div class="motif">
      <div class="mrow">
        <span><b>S1</b>阶段一</span><em>›</em>
        <span><b>S2</b>阶段二</span><em>›</em>
        <span><b>S3</b>阶段三</span>
      </div>
      <div class="mcap">一行说明这排字代表什么</div>
    </div>
    <div class="meta">
      <div class="who"><b>分享人 · 职位</b><br>日期 · 场合</div>
      <div class="kpis">
        <div class="kpi"><div class="kv">10<span class="tu">周</span></div><div class="kl">周期</div></div>
        <div class="kpi"><div class="kv">3</div><div class="kl">试点项目</div></div>
      </div>
    </div>
  </div>
</section>
```

**注意**：`motif` 和 `kpis` 都可省略（删掉整块即可）；标题超过两行就把前半句压短，57px 字号下第三行会顶到导语。

---

## 2. 议程 `.agenda` + `.thesis`

**插入位置**：整页。

**何时**：讲 6 页以上，需要先给听众地图；或需要先抛主张定调。

```html
<section class="slide">
  <div class="kicker">00 · 议程 <span class="dim">先算清，再谈快慢</span></div>
  <h1 class="title">五段内容，<em>回答同一个问题</em></h1>
  <div class="lead">「要回答的那个问题是什么？」——为什么它需要被拆开讲。</div>
  <div class="body">
    <div style="display:grid;grid-template-columns:1.12fr .88fr;gap:28px;flex:1;min-height:0">
      <div class="agenda">
        <div class="row"><div class="idx">01</div>
          <div><div class="tt">段落标题</div><div class="dd">一句话说明这一段讲什么</div></div>
          <div class="pg">P3–P5</div></div>
        <div class="row"><div class="idx">02</div>
          <div><div class="tt">段落标题</div><div class="dd">一句话说明</div></div>
          <div class="pg">P6–P7</div></div>
        <div class="row"><div class="idx">03</div>
          <div><div class="tt">段落标题</div><div class="dd">一句话说明</div></div>
          <div class="pg">P8–P10</div></div>
      </div>
      <div class="thesis">
        <div class="lb">主张</div>
        <div class="st">一句话立场，<br>可以分两行。</div>
        <div class="ft">证据边界：多少案例、多长周期、数据从哪来。</div>
      </div>
    </div>
  </div>
  <div class="foot"><div class="pg">02</div></div>
</section>
```

**注意**：`.agenda` 的每一行自动等分高度；3–6 行都好看，超过 6 行改双列。页码范围必须与正文实际页码一致。

---

## 3. 时间带 `.tl`

**插入位置**：片段，放进 `.body` 内；通常与 `.grid4`、`.note` 上下排列。

**何时**：阶段推进、项目节奏、迭代过程。3–6 个阶段。

```html
<div class="tl">
  <div class="step">
    <div class="w">W1–W2</div>
    <div class="n">阶段名</div>
    <div class="d">做了什么，一句话</div>
    <div class="out"><b>产出</b>交付了什么</div>
    <div class="dt">09.02 – 09.11</div>
  </div>
  <div class="step">…同上…</div>
</div>
```

**注意**：`.dt` 用 `margin-top:auto` 吸底，所以每格四行文字长度可以不一样，日期仍对齐。阶段超过 6 个改用两行或合并。

---

## 4. 数字块 `.grid4` + `.tile`

**插入位置**：片段，放进 `.body` 内。

**何时**：三到四个关键数字，配一句解释。

```html
<div class="grid4">
  <div class="tile"><div class="tv">29.6<span class="tu">h</span></div><div class="tl">一个标准需求 ≈ 多少工时</div></div>
  <div class="tile"><div class="tv">4.65<span class="tu">天</span></div><div class="tl">单位当量交付周期</div></div>
  <div class="tile"><div class="tv">16.20</div><div class="tl">一个迭代交付的当量总量</div></div>
  <div class="tile"><div class="tv">11<span class="tu">/ 11</span></div><div class="tl">首批需求全部完成定级</div></div>
</div>
```

**注意**：数字必须带单位或口径；`.tl` 控制在一行半以内，超了换 `.grid3`。

---

## 5. 堆叠条形图 `.bars`

**插入位置**：片段，放进 `.body` 内，`.legend` 在 `.bars` 之上。

**何时**：展示构成占比、多期对比。纯 CSS，不引图表库。

```html
<div class="legend">
  <span><i style="background:var(--blue)"></i>开发</span>
  <span><i style="background:var(--accent)"></i>测试</span>
  <span><i style="background:#C8D8E4"></i>其他</span>
</div>
<div class="bars fill">
  <div class="brow">
    <div class="bl">0715 迭代</div>
    <div class="track">
      <span style="width:47%;background:var(--blue)">47%</span>
      <span style="width:52%;background:var(--accent)">52%</span>
      <span style="width:1%;background:#C8D8E4"></span>
    </div>
    <div class="bv">1,240h</div>
  </div>
</div>
<div class="axis"><div></div><div class="ticks"><span>0</span><span>50%</span><span>100%</span></div><div></div></div>
```

**注意**：每段宽度加起来必须是 100%；段内文字只在宽度 ≥ 12% 时写；颜色从 `var(--blue) / var(--accent) / #C8D8E4` 三档取，不要引入新色。

`class="bars fill"` 让条形在正文区纵向均匀分布；只有 3–4 行时尤其需要，否则下方会空出三分之一。

---

## 6. 流水线 `.pipe` + `.spine`

**插入位置**：片段，放进 `.body` 内；`.spine` 与 `.grid3` 依次排在其下。

**何时**：多环节交接、链路、角色分工。每格有固定产物时最合适。

```html
<div class="pipe">
  <div class="st">
    <div class="sn">S1</div>
    <div class="sr">角色名</div>
    <div class="sa">这一段做什么</div>
    <div class="sk2">约束 · 一句限制条件</div>
    <div class="sf">产物路径或文件名</div>
  </div>
  <div class="arw">›</div>
  <div class="st">…同上…</div>
</div>
<div class="spine">
  <div class="sk">SPINE</div>
  <div class="sv">贯穿全链路的唯一主键是什么</div>
  <div class="sd">一句补充</div>
</div>
```

**注意**：`.sf` 自动吸底对齐；5 格是舒适上限，6 格以上文字要压到 10px 且容易挤。

流水线下方接 `.grid3` 时，如果给 `.grid3` 加 `flex:1` 填满剩余高度，三张卡会各撑到 250px 以上——内容不足就成空心盒。要么卡片写满三行，要么改用两卡 + 一行说明。

---

## 7. 代码 / 配置面板 `.code`

**插入位置**：片段，放进 `.body` 内，自带两栏。

**何时**：展示一段协议、配置、用例、命令行。深色块是页面唯一的重色。

```html
<div style="display:grid;grid-template-columns:1.02fr .98fr;gap:24px;flex:1;min-height:0">
  <div style="display:flex;flex-direction:column;gap:10px;min-height:0">
    <div class="label">这段代码在做什么</div>
    <div class="code fit" style="flex:1;min-height:0">
<pre><span class="k">Feature:</span> 场景名

  <span class="k">Scenario:</span> 一句话  <span class="c">[AC-3]</span>
    <span class="v">Given</span> 前置状态
    <span class="v">When</span>  动作
    <span class="v">Then</span>  断言</pre>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;gap:10px;min-height:0">
    <div class="label">读法</div>
    <div class="card" style="flex:1;justify-content:center">…</div>
  </div>
</div>
```

**注意**：`.code` 是 `white-space:pre`，换行必须靠源码里的真实换行，一行一个 `<span>` 不要拆。代码块和右侧卡片要在同一高度区间（左边 `flex:1`，右边卡片 `flex:1`）。

代码不足 12 行时，用 `class="code fit"` 并把内容包进 `<pre>`，让它在深色块里垂直居中；不要给 `.code` 直接加 flex，行内 `<span>` 会被拆成独立行。

---

## 8. 左表右流程 `.two` 变体

**插入位置**：片段，放进 `.body` 内，自带两栏。

**何时**：角色职责 × 执行流程，或问题 × 对策的对照。

```html
<div class="two" style="flex:1;min-height:0">
  <div style="display:flex;flex-direction:column;gap:10px;min-height:0">
    <div class="label">角色怎么分工</div>
    <div style="border:1px solid var(--line);border-radius:9px;overflow:hidden;flex:1;display:flex;flex-direction:column">
      <div style="display:grid;grid-template-columns:66px 1fr;flex:1;min-height:0;align-items:center;background:#EEF5FB">
        <div style="padding:12px 14px;font-size:11.5px;font-weight:800;color:var(--navy)">角色</div>
        <div style="padding:12px 14px;font-size:12px;color:var(--ink2);line-height:1.6">负责什么 · <b class="strong">不再做什么</b></div>
      </div>
      <div style="display:grid;grid-template-columns:66px 1fr;flex:1;min-height:0;align-items:center;border-top:1px solid var(--line2)">
        <div style="padding:12px 14px;font-size:11.5px;font-weight:800;color:var(--navy)">角色</div>
        <div style="padding:12px 14px;font-size:12px;color:var(--ink2);line-height:1.6">负责什么</div>
      </div>
      <div style="display:grid;grid-template-columns:66px 1fr;flex:1;min-height:0;align-items:center;border-top:1px solid var(--line2)">
        <div style="padding:12px 14px;font-size:11.5px;font-weight:800;color:var(--navy)">角色</div>
        <div style="padding:12px 14px;font-size:12px;color:var(--ink2);line-height:1.6">负责什么</div>
      </div>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;gap:8px;min-height:0">
    <div class="label">流程怎么走</div>
    <div style="flex:1;display:flex;flex-direction:column;gap:6px">
      <div style="flex:1;display:flex;align-items:center;gap:10px;background:#F4F9FD;border:1px solid #DCE9F4;border-radius:6px;padding:0 13px;font-size:11.8px;color:var(--ink2)">
        <b class="mono" style="color:var(--blue);width:24px">01</b>节点说明
      </div>
    </div>
  </div>
</div>
```

**注意**：两栏都靠 `flex:1` 撑满，每行也 `flex:1`。**每行必须带 `min-height:0`**，否则内容多的那一行会把别行挤扁，行高就不均。第一行是表头（浅蓝底），从第二行开始填数据。

---

## 9. 卡片网格 `.grid3` / `.grid4`

**插入位置**：片段，放进 `.body` 内。

**何时**：若干并列要点，每条一句话解释。3、4、6 张都行。

```html
<div class="grid3">
  <div class="card">
    <div class="ct"><span class="num red">1</span>要点标题</div>
    <div class="cd">两行以内的解释，具体、可验证。</div>
  </div>
</div>
```

6 张用两行 × 三列：

```html
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:13px;flex:1;min-height:0">
  …6 个 .card…
</div>
```

**注意**：卡片可以 `flex:1` 均分列高，但卡片内部要 `justify-content:center`，否则文字堆在顶部、下方留一片空。不要给卡片里的文字块单独加 `flex:1`。

---

## 10. 深色公式 / 结论面板

**插入位置**：片段，放进 `.body` 内；成对使用时与左栏共享同一个网格。

**何时**：一页只有一个核心公式、一个核心结论时。

```html
<div style="background:var(--navy);border-radius:10px;padding:24px 26px;color:#fff">
  <div style="font-size:10.5px;letter-spacing:.16em;opacity:.55;font-weight:700">标签</div>
  <div style="margin-top:10px;font-size:30px;font-weight:800">E = (O + 4M + P) ÷ 6</div>
  <div style="margin-top:10px;font-size:12.2px;line-height:1.75;opacity:.82">
    解释一行<br>再解释一行 <b style="color:var(--accent-soft)">高亮片段</b>
  </div>
</div>
```

收尾页用 `.thesis`（见版式 2），自带标签 + 主张 + 分隔线。

**注意**：深色块里的强调用 `var(--accent-soft)`（`--accent` 与白混合后的浅色），不要用 `--accent` 原色——深底上对比不足。换品牌色时它会自动跟随。

---

## 11. 收尾：三张行动卡 + 结论

**插入位置**：片段，放进 `.body` 内（外层 `<section>`、`kicker/title` 与 `.foot` 自己补）。

**何时**：最后一页，给听众可执行的动作。

```html
<div style="display:grid;grid-template-columns:1.08fr .92fr;gap:26px;flex:1;min-height:0">
  <div style="display:flex;flex-direction:column;min-height:0">
    <div class="label" style="margin-bottom:11px">回去可以马上做的三件事</div>
    <div style="flex:1;display:flex;flex-direction:column;justify-content:space-between;gap:11px">
      <div class="card"><div class="ct"><span class="num red">1</span>动作标题</div><div class="cd">为什么这件事最容易开始。</div></div>
      <div class="card"><div class="ct"><span class="num red">2</span>动作标题</div><div class="cd">一句说明。</div></div>
      <div class="card"><div class="ct"><span class="num red">3</span>动作标题</div><div class="cd">一句说明。</div></div>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;min-height:0">
    <div class="label" style="margin-bottom:11px;visibility:hidden" aria-hidden="true">&nbsp;</div>
    <div class="thesis" style="flex:1">
      <div class="lb">TAKEAWAY</div>
      <div class="st">三句话总结，<br>一句一行。</div>
      <div class="ft">留给听众的问题。</div>
    </div>
  </div>
</div>
```

**注意**：右侧那个 `visibility:hidden` 的占位 label 是让左右顶边对齐的关键，不要删。整块之后可以再加一条通栏 `.note`。
