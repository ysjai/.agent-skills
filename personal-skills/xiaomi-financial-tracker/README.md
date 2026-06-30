# Xiaomi Financial Tracker

## 这个 skill 做什么

`xiaomi-financial-tracker` 用来长期跟踪小米集团财报。它会帮助你从官方财报 PDF、官方财报链接、官方截图、券商研报和公开预测资料中抽取核心数据，维护可追溯的 CSV 表格，并生成经营分析、估值位置和预测汇总。

这个 skill 只做基本面和估值辅助分析，不直接给出买入、卖出、加仓或减仓指令。

## 快速开始

1. 创建一个报告期目录，例如：

```text
personal-skills/xiaomi-financial-tracker/workspace/periods/2025FY/input/
```

2. 把小米官方 PDF、截图、URL 文件、研报或估值数据放进 `input/`。

3. 对 agent 说：

```text
请使用 xiaomi-financial-tracker 处理 2025FY
```

4. 处理完成后优先看：

```text
workspace/periods/2025FY/report.md
workspace/views/recent_5y_fy_h1_wide.md
workspace/views/valuation_snapshot.md
workspace/data/review_queue.csv
```

## 报告期命名

请按财报发布节奏命名目录：

- `2025Q1`：一季度。
- `2025H1`：中报或半年报。
- `2025Q3`：三季报或前三季度。
- `2025FY`：全年或年报。

不建议用 `2025Q2` 表示中报，也不建议用 `2025Q4` 表示年报。中报和年报会同时包含累计数据，也会推导单季数据。

## 放输入文件

每个报告期的输入都放在：

```text
workspace/periods/<报告期>/input/
```

支持这些文件：

- 官方财报 PDF。
- 官方财报 PDF 链接。
- 官方财报截图或图片。
- 券商或投行研报 PDF。
- 包含 PE/PB 历史、预测或估值数据的 CSV、Markdown、图片。

URL 可以写在 `.md` 或 `.txt` 文件里，例如：

```markdown
# 2025FY 官方资料

https://ir.mi.com/financial-information/quarterly-results
https://ir.mi.com/system/files-encrypted/example/Xiaomi-2025-FY.pdf
```

## 触发处理

常用说法：

```text
请使用 xiaomi-financial-tracker 处理 2025FY
```

```text
请分析小米 2025H1 财报，并更新长期数据表
```

```text
请把 2025Q3 的官方截图和研报预测合并进小米跟踪表
```

## 看输出结果

单期输出：

```text
workspace/periods/<报告期>/report.md
workspace/periods/<报告期>/extracted/extracted_metrics.csv
workspace/periods/<报告期>/extracted/extracted_forecasts.csv
workspace/periods/<报告期>/extracted/extracted_valuation.csv
workspace/periods/<报告期>/extracted/extraction_notes.md
```

长期数据：

```text
workspace/data/long_metrics.csv
workspace/data/metric_observations.csv
workspace/data/forecasts.csv
workspace/data/valuation_history.csv
workspace/data/review_queue.csv
```

阅读视图：

```text
workspace/views/recent_5y_fy_h1_wide.md
workspace/views/valuation_snapshot.md
```

## 单季和累计数据说明

中报、三季报和年报会同时处理累计数据和单季数据。

- `2025H1` 会保留 H1 累计数据，也会在条件满足时推导 `2025Q2`。
- `2025Q3` 会保留前三季度累计数据，也会在条件满足时推导 `2025Q3` 单季。
- `2025FY` 会保留全年数据，也会在条件满足时推导 `2025Q4`。

派生单季数据会用 `*` 标注，表示“由累计数反推”。毛利率、市场份额、MAU、现金储备、门店数、PE、PB 等比例或时点指标不会用简单相减反推。

## 预测和估值数据说明

预测、官方指引和券商假设不会写入事实主表 `long_metrics.csv`，而是写入 `forecasts.csv`。

PE/PB 历史百分位只有在 `valuation_history.csv` 有足够数据时才计算。小米 2018 年上市，如果没有完整 10 年样本，报告会标注“可得历史百分位”，不会假装有完整 10 年历史。

如果没有可靠预测来源，报告会说明“可靠预测来源不足”，并列出需要补充哪些材料。

## 复核队列怎么用

无法自动确认的数据会写入：

```text
workspace/data/review_queue.csv
```

你可以打开这个文件，把某条记录的 `status` 改成：

- `user_approved`：确认采用候选数据。
- `rejected`：确认不采用候选数据。

然后让 agent 重新运行处理，或运行：

```bash
python3 personal-skills/xiaomi-financial-tracker/scripts/resolve_review_queue.py --skill-root personal-skills/xiaomi-financial-tracker
```

## 重跑是否安全

同一报告期可以重复处理。脚本会用稳定 ID 和自然键去重，避免重复污染长期表。

如果同一指标出现不同来源或不同数值，skill 不会静默覆盖，而是按来源优先级处理或写入复核队列。

## 隐私和 Git 提交提醒

这个 skill 的 `workspace/` 默认可以提交到 git。如果你放入付费研报、个人持仓、交易记录或其他敏感资料，请自行决定是否提交这些文件。

## 常见问题

### 为什么中报会出现 Q2 数据？

中报披露 H1 累计数据。如果已有 Q1 数据，收入、利润、出货量等流量指标可以用 `Q2 = H1 - Q1` 推导。

### 为什么年报会出现 Q4 数据？

年报披露 FY 全年数据。如果已有前三季度累计数据，流量指标可以用 `Q4 = FY - YTD_Q3` 推导。

### 为什么预测数据没有覆盖事实数据？

预测、官方指引和事实完成值是不同性质的数据。它们分别进入 `forecasts.csv` 和 `long_metrics.csv`，避免把预期当成已披露事实。

### 为什么没有输出 PE/PB 10 年百分位？

如果历史估值样本不足，skill 会降级为可得历史样本，或明确说明样本不足。
