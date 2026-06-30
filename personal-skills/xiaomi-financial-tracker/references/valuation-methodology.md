# Valuation Methodology

## Metrics

- `TTM PE`: market-standard trailing PE.
- `Adjusted TTM PE`: trailing PE based on adjusted net profit. This is the preferred operating-quality valuation lens.
- `Forward PE`: forecast PE. Use for forecast discussion, not historical percentile calculation.
- `PB`: price-to-book ratio.

## Percentile Formula

For a metric and time window:

```text
percentile = count(valid_samples <= current_value) / count(valid_samples) * 100
```

Higher percentile means the current valuation is closer to the historical high end.

## Valid Samples

Exclude:

- Blank values.
- Non-numeric values.
- `PE <= 0` values.
- Rows with `review_status=open`, `needs_user_review`, or `rejected`.
- Conflicting same-day rows that cannot be resolved by source priority.

## Sample Windows

Calculate 5-year and 10-year windows from the latest available date for each metric.

If a partial sample exists, calculate the percentile and mark `status=available_history_only`.

If no valid sample exists, mark `status=insufficient_history`.

Xiaomi listed in 2018, so a complete 10-year listed-company history may not exist. Do not fabricate a complete 10-year sample.
