# Source Priority

## Ranking

Use this ranking when sources conflict:

| source_type | priority | notes |
|---|---:|---|
| official_pdf | 100 | Xiaomi official PDF report or announcement |
| official_url | 100 | Xiaomi official IR URL or official PDF URL |
| official_screenshot | 90 | User-provided screenshot of official Xiaomi material |
| user_csv | 80 | User-provided structured data |
| broker_report | 60 | Broker or investment bank report |
| public_web | 50 | Public web page or forecast aggregator |
| media_repost | 20 | Media repost or secondary report |

## Acceptance Rules

- Official PDF and official IR data can be auto accepted when the metric, unit, and period are clear.
- Official screenshots can be auto accepted when OCR is clear and the source context is obvious.
- Broker and public forecast data should be LLM-reviewed first.
- Unclear OCR, unclear units, unclear dates, or conflicting official sources must enter `review_queue.csv`.

## Conflict Rules

- Official PDF or official URL can replace a lower-priority screenshot for the same fact.
- Official-vs-official conflicts must enter the review queue.
- Forecast conflicts are preserved as separate rows and not treated as factual conflicts.
- Valuation conflicts for the same `date + metric` should enter the review queue and be excluded from percentile samples until resolved.
