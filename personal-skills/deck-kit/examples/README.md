# 参考样例

`sample-ai-dlc.html` —— 一份 14 页的 AI-DLC 研发提效分享片子，用来对齐**视觉密度和版式节奏**。客户与内部系统名已做脱敏处理，叙事结构与数据形态保持原样。

## 看什么

- 每页的 kicker / 标题 / 导语 / 正文 / 页脚五段式节奏
- 深浅交替：连续三页同类版式后会插一页深色块或图表
- 卡片里文字的实际长度（不是一两句占位，而是带数字的具体描述）
- 页脚永远有来源和页码

## 注意

这份样例是用本技能**早期版本**做的，CSS 与 JS 内联在文件里，与 `assets/deck.css` 有差异（样例里 logo 用伪元素，只支持单 logo；导航与目录也是早期实现）。

所以：

- ✅ 可以抄它的**内容写法**和**版式组合**
- ❌ 不要抄它的 `<style>` 和 `<script>`
- ❌ 不要把它当起点改（新片子一律从 `assets/template.html` 生成）

新片子的起点永远是：

```bash
node ~/.workbuddy/skills/deck-kit/scripts/new-deck.mjs --out outputs/<name>.html --title "<标题>"
```
