# AI 厂商信息源地图

> 供 ai-frontier-radar skill 使用。标注每个源的来源类型、自动抓取适用性、是否通常带明确日期。
> 优先使用"自动抓取适用性：高"且"通常带明确日期：是"的官方源做确认；候选发现源用于找线索，手动核验源仅供人工参考。

---

## 来源类型说明

| 类型标签 | 含义 | 可用置信度标签 |
|----------|------|---------------|
| 官方博客/公告 | 厂商官方发布的文章或公告页 | `[官方]` |
| 官方发布页 | GitHub Release、具体仓库 Release/Tag 页、Hugging Face 模型页、平台 Changelog | `[官方]` |
| 候选发现源 | 官方 GitHub 组织页、产品入口页、抓取受限的官方新闻页 | 候选发现用途，不单独作为确认依据 |
| 权威媒体 | TechCrunch、The Verge、Reuters 等独立媒体 | `[媒体报道]`（不可标 `[官方]`） |
| 手动核验源 | 微信公众号等需人工查阅、无法自动抓取的渠道 | 不进入自动主流程 |

> **媒体规则**：权威媒体报道可进入"确定区"，但只能标 `[媒体报道]`，不能标 `[官方]`。
> 无明确发布时间的媒体报道只能进入"待核验线索"。

---

## OpenAI

**别名：** OpenAI、open ai  
**优先搜索关键词：** `OpenAI news {date}`、`OpenAI announcement {date}`、`ChatGPT update {date}`

| 来源名 | URL | 来源类型 | 通常带明确日期 | 自动抓取适用性 | 备注 |
|--------|-----|----------|---------------|---------------|------|
| OpenAI 博客 | https://openai.com/blog | 官方博客/公告 | 是 | 高 | |
| OpenAI 新闻 | https://openai.com/news | 官方博客/公告 | 是 | 高 | |
| OpenAI 研究 | https://openai.com/research | 官方博客/公告 | 是 | 高 | |

---

## Anthropic

**别名：** Anthropic、Claude AI  
**优先搜索关键词：** `Anthropic news {date}`、`Claude AI update {date}`、`Anthropic announcement {date}`

| 来源名 | URL | 来源类型 | 通常带明确日期 | 自动抓取适用性 | 备注 |
|--------|-----|----------|---------------|---------------|------|
| Anthropic 新闻 | https://www.anthropic.com/news | 官方博客/公告 | 是 | 高 | |
| Anthropic 研究 | https://www.anthropic.com/research | 官方博客/公告 | 是 | 高 | |

---

## Google / DeepMind

**别名：** Google AI、Google DeepMind、DeepMind、Gemini  
**优先搜索关键词：** `Google AI news {date}`、`DeepMind announcement {date}`、`Gemini update {date}`

| 来源名 | URL | 来源类型 | 通常带明确日期 | 自动抓取适用性 | 备注 |
|--------|-----|----------|---------------|---------------|------|
| Google AI 博客 | https://blog.google/technology/ai/ | 官方博客/公告 | 是 | 高 | |
| DeepMind 博客 | https://deepmind.google/discover/blog/ | 官方博客/公告 | 是 | 高 | |
| Google Research 博客 | https://research.google/blog/ | 官方博客/公告 | 是 | 高 | |

---

## xAI

**别名：** xAI、Grok、马斯克 AI  
**优先搜索关键词：** `xAI news {date}`、`Grok update {date}`、`xAI announcement {date}`

| 来源名 | URL | 来源类型 | 通常带明确日期 | 自动抓取适用性 | 备注 |
|--------|-----|----------|---------------|---------------|------|
| xAI 开发者 Release Notes | https://docs.x.ai/developers/release-notes | 官方发布页 | 是 | 高 | API/产品更新首选确认源 |
| xAI 开发者 Models | https://docs.x.ai/developers/models | 官方发布页 | 是 | 高 | 模型发布与价格变更可核验 |
| xAI GitHub | https://github.com/xai-org | 候选发现源 | 需点入确认 | 中 | 组织页适合候选发现；具体仓库发布日期需进一步点入确认 |
| xAI 新闻页 | https://x.ai/news | 候选发现源 | 是 | 低 | 官方新闻入口，但抓取常受限，以搜索为主 |
| Grok 发布公告（X/Twitter） | https://twitter.com/xai | 候选发现源 | 是 | 低 | 官方账号可作线索发现；X 平台抓取受限 |

---

## Meta AI

**别名：** Meta AI、Meta、LLaMA、Llama、Meta FAIR  
**优先搜索关键词：** `Meta AI news {date}`、`Llama release {date}`、`Meta AI announcement {date}`

| 来源名 | URL | 来源类型 | 通常带明确日期 | 自动抓取适用性 | 备注 |
|--------|-----|----------|---------------|---------------|------|
| Meta Newsroom AI 标签 | https://about.fb.com/news/tag/ai/ | 官方博客/公告 | 是 | 高 | 更稳定的官方 AI 新闻入口 |
| Meta Llama GitHub | https://github.com/meta-llama | 候选发现源 | 需点入确认 | 中 | 组织页适合候选发现；具体仓库发布日期需进一步点入确认 |
| Llama Hugging Face | https://huggingface.co/meta-llama | 官方发布页 | 是 | 高 | 模型更新带日期 |

---

## Perplexity

**别名：** Perplexity AI、Perplexity  
**优先搜索关键词：** `Perplexity AI news {date}`、`Perplexity announcement {date}`、`Perplexity update {date}`

| 来源名 | URL | 来源类型 | 通常带明确日期 | 自动抓取适用性 | 备注 |
|--------|-----|----------|---------------|---------------|------|
| Perplexity 开发文档 Changelog | https://docs.perplexity.ai/changelog | 官方发布页 | 是 | 高 | API/平台更新首选确认源 |
| Perplexity 博客 | https://www.perplexity.ai/blog | 候选发现源 | 是 | 低 | 官方博客存在抓取限制，以搜索进入为主 |
| Perplexity GitHub | https://github.com/perplexityai | 候选发现源 | 需点入确认 | 低 | 组织页更适合候选发现；开源内容有限，以搜索为主 |

---

## Mistral

**别名：** Mistral AI、Mistral  
**优先搜索关键词：** `Mistral AI news {date}`、`Mistral release {date}`、`Mistral announcement {date}`

| 来源名 | URL | 来源类型 | 通常带明确日期 | 自动抓取适用性 | 备注 |
|--------|-----|----------|---------------|---------------|------|
| Mistral 博客 | https://mistral.ai/news/ | 官方博客/公告 | 是 | 高 | |
| Mistral 文档 Changelogs | https://docs.mistral.ai/resources/changelogs | 官方发布页 | 是 | 高 | API/模型/平台更新首选确认源 |
| Mistral Hugging Face | https://huggingface.co/mistralai | 官方发布页 | 是 | 高 | 模型更新带日期，首选确认源 |
| Mistral GitHub | https://github.com/mistralai | 候选发现源 | 需点入确认 | 中 | 组织页适合候选发现；具体仓库发布日期需进一步点入确认 |

---

## 月之暗面 / Kimi

**别名：** 月之暗面、Moonshot AI、Kimi、kimi.ai  
**优先搜索关键词：** `月之暗面 新闻 {date}`、`Kimi AI 更新 {date}`、`Moonshot AI news {date}`

| 来源名 | URL | 来源类型 | 通常带明确日期 | 自动抓取适用性 | 备注 |
|--------|-----|----------|---------------|---------------|------|
| Kimi 官网 | https://kimi.ai | 官方博客/公告 | 不稳定 | 低 | 主要是产品入口，以搜索为主 |
| Moonshot 官网 | https://www.moonshot.cn | 官方博客/公告 | 不稳定 | 低 | 站点结构不稳定，以搜索为主 |
| 微信公众号：月之暗面 | — | 手动核验源 | 是 | 不适用 | 仅供人工参考，不进入自动主流程 |

---

## 小米 Mimo / Xiaomi MiMo

**别名：** 小米 MiMo、Xiaomi MiMo、MiMo、小米大模型  
**优先搜索关键词：** `小米 MiMo 新闻 {date}`、`Xiaomi MiMo AI {date}`、`MiMo model release {date}`

| 来源名 | URL | 来源类型 | 通常带明确日期 | 自动抓取适用性 | 备注 |
|--------|-----|----------|---------------|---------------|------|
| GitHub XiaomiMiMo | https://github.com/XiaomiMiMo | 官方发布页 | 是 | 高 | 开源发布首选确认源 |
| 小米集团官网 | https://www.mi.com | 官方博客/公告 | 不稳定 | 低 | 企业官网入口，非新闻归档，仅作候选 |
| mi.com/about/ai | https://mi.com/about/ai | 官方博客/公告 | 需复核 | 低 | 页面结构不确定，不宜作为主流程源 |

---

## DeepSeek

**别名：** DeepSeek、深度求索、DeepSeek AI  
**优先搜索关键词：** `DeepSeek news {date}`、`DeepSeek release {date}`、`深度求索 新闻 {date}`

| 来源名 | URL | 来源类型 | 通常带明确日期 | 自动抓取适用性 | 备注 |
|--------|-----|----------|---------------|---------------|------|
| DeepSeek GitHub | https://github.com/deepseek-ai | 官方发布页 | 是 | 高 | Release 页带时间戳，首选确认源 |
| DeepSeek Hugging Face | https://huggingface.co/deepseek-ai | 官方发布页 | 是 | 高 | 模型更新带日期 |
| DeepSeek 官网 | https://www.deepseek.com | 官方博客/公告 | 需复核 | 中 | `/news` 路径存在性需复核，不宜直接依赖 |

---

## 智谱 AI / Zhipu AI

**别名：** 智谱 AI、Zhipu AI、智谱华章、GLM、ChatGLM、BigModel  
**优先搜索关键词：** `智谱 AI 新闻 {date}`、`Zhipu AI news {date}`、`GLM update {date}`、`ChatGLM release {date}`

| 来源名 | URL | 来源类型 | 通常带明确日期 | 自动抓取适用性 | 备注 |
|--------|-----|----------|---------------|---------------|------|
| THUDM GitHub | https://github.com/THUDM | 官方发布页 | 是 | 高 | 开源模型发布首选确认源 |
| 智谱 AI 官网 | https://www.zhipuai.cn | 官方博客/公告 | 需复核 | 低 | 站点结构不确定，以搜索为主 |
| BigModel 开放平台 | https://open.bigmodel.cn | 官方发布页 | 需复核 | 中 | 平台更新日志可能带日期，需实际验证 |

---

## MiniMax

**别名：** MiniMax、MiniMax AI、海螺 AI、Hailuoai  
**优先搜索关键词：** `MiniMax AI news {date}`、`MiniMax 新闻 {date}`、`海螺 AI 更新 {date}`

| 来源名 | URL | 来源类型 | 通常带明确日期 | 自动抓取适用性 | 备注 |
|--------|-----|----------|---------------|---------------|------|
| MiniMax 官网 | https://www.minimaxi.com | 官方博客/公告 | 需复核 | 低 | 站点结构不确定，以搜索为主 |
| 海螺 AI | https://hailuoai.com | 官方博客/公告 | 需复核 | 低 | 产品入口，是否有新闻归档需复核 |
| MiniMax API 平台 | https://api.minimax.chat | 官方发布页 | 需复核 | 低 | Changelog 存在性需实际验证 |

---

## 通用权威媒体源

主要用于"候选发现"阶段，不用于官方确认。若媒体页面本身带明确发布时间，可作为 `[媒体报道]` 条目的日期证据；进入确定区时只能标 `[媒体报道]`。

| 媒体 | URL | 来源类型 | 通常带明确日期 | 自动抓取适用性 | 备注 |
|------|-----|----------|---------------|---------------|------|
| TechCrunch AI | https://techcrunch.com/category/artificial-intelligence/ | 权威媒体 | 是 | 高 | |
| The Verge AI | https://www.theverge.com/ai-artificial-intelligence | 权威媒体 | 是 | 高 | |
| VentureBeat AI | https://venturebeat.com/category/ai/ | 权威媒体 | 是 | 中 | |
| Reuters Technology | https://www.reuters.com/technology/ | 权威媒体 | 是 | 中 | |
| 36kr AI | https://36kr.com/information/AI | 权威媒体 | 是 | 中 | |
| 机器之心 | https://www.jiqizhixin.com | 权威媒体 | 是 | 中 | |
| 量子位 | https://www.qbitai.com | 权威媒体 | 是 | 中 | |

---

## 使用优先级说明

1. **首选**：自动抓取适用性"高"且"通常带明确日期：是"的源 → 用于官方确认，可标 `[官方]`
2. **次选**：自动抓取适用性"中"的源 → 用于候选发现或辅助确认
3. **谨慎使用**：标注"需复核"的源 → 仅作候选，不能作为日期证据的单一依据
4. **候选发现源**：用于发现线索，需再点入具体官方页面、Release、HF 或 Changelog 才能做确认
5. **不进入自动流程**：手动核验源（如微信公众号）
6. **权威媒体**：可进入确定区，只标 `[媒体报道]`，不标 `[官方]`；无明确日期则只能进待核验
