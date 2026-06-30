---
name: xiaomi-financial-tracker
description: Use this skill whenever the user asks to track or analyze Xiaomi financial reports, Xiaomi earnings, Xiaomi business segments, Xiaomi valuation percentiles, Xiaomi broker forecasts, or asks to process period folders like 2025Q1, 2025H1, 2025Q3, or 2025FY. It extracts official Xiaomi report data, maintains auditable CSV tables, generates financial analysis reports, updates recent FY/H1 wide tables, and calculates PE/PB percentile snapshots when valuation history is available.
argument-hint: "report period such as 2025Q1, 2025H1, 2025Q3, 2025FY, or a request to update forecasts/valuation"
---

# Xiaomi Financial Tracker

## Default workspace

Use this workspace by default:

```text
personal-skills/xiaomi-financial-tracker/workspace/
```

For a report period, read inputs from:

```text
workspace/periods/<source_period>/input/
```

Write period outputs to:

```text
workspace/periods/<source_period>/extracted/
workspace/periods/<source_period>/report.md
```

## Input discovery

Accept these inputs:

- Official Xiaomi financial report PDFs.
- Official Xiaomi IR URLs or official PDF URLs in `.md` or `.txt` files.
- Official screenshots or images.
- Broker or investment bank report PDFs.
- CSV, Markdown, or images containing forecasts or PE/PB history.

If the user gives a period like `2025FY`, inspect `workspace/periods/2025FY/input/`. If the folder is missing, tell the user the exact folder path to create.

## Source registration

Every extracted row needs source fields: `source_id`, `source_period`, `source_type`, `source_name`, `source_file`, `source_url`, `publication_date`, and `source_location`.

Use source types from `references/source-priority.md`. Official PDFs and official IR URLs are highest priority. Official screenshots are acceptable but should keep their screenshot filename or location.

## Extraction rules

Before extracting, read:

- `references/data-model.md` for CSV contracts.
- `references/metric-dictionary.md` for canonical metric names and units.
- `references/source-priority.md` for source priority and review rules.

Write extracted rows to these files first:

```text
workspace/periods/<source_period>/extracted/extracted_metrics.csv
workspace/periods/<source_period>/extracted/extracted_forecasts.csv
workspace/periods/<source_period>/extracted/extracted_valuation.csv
workspace/periods/<source_period>/extracted/extraction_notes.md
```

Facts go to `extracted_metrics.csv`. Forecasts, official guidance, and scenarios go to `extracted_forecasts.csv`. PE/PB history goes to `extracted_valuation.csv`.

## Fact vs observation vs forecast boundaries

Do not put forecasts or official guidance into `long_metrics.csv`. They belong in `forecasts.csv`.

Do not put raw source candidates directly into `long_metrics.csv`. The merge script first records them in `metric_observations.csv`, then promotes accepted rows into canonical facts.

If a value is uncertain, set `review_status=needs_user_review`. Do not silently accept unclear OCR, unclear units, or unclear forecast periods.

## Single-quarter derivation

Use these derivations only for eligible flow metrics:

```text
Q2 = H1 - Q1
Q3 = YTD_Q3 - H1
Q4 = FY - YTD_Q3
```

Never derive ratios or point-in-time metrics by subtraction. This includes gross margin, market share, rankings, MAU, connected devices, cash, stores, PE, and PB.

Derived quarter values must have `calculation_method=derived_from_cumulative_delta` and appear in reports with `*` plus a note saying they were derived from cumulative data.

## Review queue rules

Use `workspace/data/review_queue.csv` for conflicts or uncertain rows.

Candidates must be persisted before entering the queue:

- Metric candidates live in `metric_observations.csv`, with `candidate_row_id=observation_id`.
- Forecast candidates live in `forecasts.csv`, with `candidate_row_id=forecast_id`.
- Valuation candidates live in `valuation_history.csv`, with `candidate_row_id=valuation_id`.

The user can approve a candidate by setting `status=user_approved`, then running `resolve_review_queue.py`.

## Report output

Generate `report.md` with exactly these sections:

```markdown
# 小米集团财报跟踪：<source_period>

## 1. 一页结论
## 2. 数据覆盖与缺口
## 3. 核心数据表
## 4. 单季与累计数据
## 5. 分业务板块分析
## 6. 同比和环比变化原因
## 7. 外部影响因素
## 8. 当前基本面判断
## 9. 估值位置
## 10. 未来 3 财年预测
## 11. 风险、挑战与下一期观察清单
## 12. 数据来源、置信度与待复核项
```

If forecast sources are insufficient, say so. If valuation history is insufficient, say so. Do not fabricate predictions or historical percentiles.

## Script usage

After writing extracted files, run scripts from the repository root:

```bash
python3 personal-skills/xiaomi-financial-tracker/scripts/merge_metrics.py --skill-root personal-skills/xiaomi-financial-tracker --period <source_period>
python3 personal-skills/xiaomi-financial-tracker/scripts/merge_forecasts.py --skill-root personal-skills/xiaomi-financial-tracker --period <source_period>
python3 personal-skills/xiaomi-financial-tracker/scripts/merge_valuation.py --skill-root personal-skills/xiaomi-financial-tracker --period <source_period>
python3 personal-skills/xiaomi-financial-tracker/scripts/calculate_valuation_percentiles.py --skill-root personal-skills/xiaomi-financial-tracker
python3 personal-skills/xiaomi-financial-tracker/scripts/build_wide_tables.py --skill-root personal-skills/xiaomi-financial-tracker
```

Use `resolve_review_queue.py` only after the user or LLM has marked review items as approved or rejected.

## Final response format

End with:

- Processed period.
- Main report path.
- Updated data files.
- Updated views.
- Number of review queue items.
- Any missing inputs or degraded sections.
