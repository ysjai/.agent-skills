# Data Model

## Extracted Metrics

`extracted_metrics.csv` contains factual operating or financial metrics extracted from official reports, screenshots, or other sources.

```csv
source_id,source_period,source_type,source_name,source_file,source_url,publication_date,source_location,data_period,period_scope,value_kind,as_of_date,target_period,segment,metric,raw_value,raw_unit,value,unit,yoy,qoq,calculation_method,confidence,review_status,notes
```

Rules:

- Use this file only for historical facts or reliably derived historical facts.
- Do not put forecasts, official guidance, or broker target assumptions here.
- `data_period` is the period the metric describes, not the folder name.
- `2025H1` cumulative data must stay `data_period=2025H1` and `period_scope=cumulative`.
- `2025Q2` single-quarter data must use `data_period=2025Q2` and `period_scope=quarter`.

## Extracted Forecasts

`extracted_forecasts.csv` contains official guidance, broker forecasts, public forecasts, and scenario assumptions.

```csv
source_id,source_period,source_name,source_type,source_file,source_url,publication_date,source_location,forecast_period,metric,segment,value,unit,scenario,assumptions,confidence,review_status,notes
```

Rules:

- Use `source_type=official_guidance` for company targets such as EV delivery targets.
- Keep broker forecasts from different sources as separate rows.
- Do not overwrite forecasts from other sources.
- If the forecast period or profit basis is unclear, set `review_status=needs_user_review`.

## Extracted Valuation

`extracted_valuation.csv` contains PE/PB time-series points.

```csv
source_id,source_period,source_type,source_name,source_file,source_url,publication_date,source_location,date,metric,value,confidence,review_status,notes
```

Rules:

- Use this file for historical PE/PB series only.
- Do not use forecast PE as historical PE.
- If a valuation row comes from OCR and the number is not clear, set `review_status=needs_user_review`.

## Global Tables

`long_metrics.csv` is the canonical fact table.

`metric_observations.csv` stores all extracted metric candidates for audit and conflict handling.

`forecasts.csv` stores all forward-looking data and official guidance.

`valuation_history.csv` stores PE/PB history.

`review_queue.csv` stores conflicts and uncertain candidates.

## Period Semantics

Use these period names:

- `YYYYQ1`: first quarter.
- `YYYYH1`: first half cumulative.
- `YYYYYTD_Q3`: first nine months cumulative.
- `YYYYFY`: full year cumulative.
- `YYYYQ2`, `YYYYQ3`, `YYYYQ4`: single-quarter data.

`source_period` is the folder where the source was placed. `data_period` or `forecast_period` is the period described by the data.
