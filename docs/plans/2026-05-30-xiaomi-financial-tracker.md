# Xiaomi Financial Tracker Implementation Plan

> Steps use checkbox (`- [ ]`) syntax for progress tracking.

**Goal:** Build `personal-skills/xiaomi-financial-tracker`, a user-friendly skill for tracking Xiaomi financial reports, maintaining auditable CSV data, generating report outputs, and calculating valuation percentiles when data is available.

**Architecture:** The skill is prompt/workflow-led: `SKILL.md` tells the agent how to ingest user-provided PDFs, URLs, screenshots, forecasts, and valuation files. Deterministic CSV operations live in small Python scripts so merges, de-duplication, review queues, wide tables, and valuation percentiles are repeatable and auditable.

**Tech Stack:** Markdown skill files, CSV data files, Python 3 standard library only, optional agent-side PDF/OCR/web extraction handled by the runtime and existing tools.

---

## File Map

- Create `personal-skills/xiaomi-financial-tracker/SKILL.md`: trigger metadata and end-to-end workflow instructions.
- Create `personal-skills/xiaomi-financial-tracker/README.md`: new-user guide for folder layout, inputs, outputs, reruns, and review queue.
- Create `personal-skills/xiaomi-financial-tracker/references/metric-dictionary.md`: canonical segments, metrics, units, flow/stock classification, derivation rules.
- Create `personal-skills/xiaomi-financial-tracker/references/data-model.md`: extracted file contracts, facts/observations/forecasts/valuation boundaries, and period semantics.
- Create `personal-skills/xiaomi-financial-tracker/references/analysis-framework.md`: report template and analytical checklist.
- Create `personal-skills/xiaomi-financial-tracker/references/valuation-methodology.md`: PE/PB percentile contract and edge cases.
- Create `personal-skills/xiaomi-financial-tracker/references/source-priority.md`: source ranking, conflict handling, and review rules.
- Create `personal-skills/xiaomi-financial-tracker/scripts/csv_utils.py`: shared CSV, hashing, row-key, and atomic write helpers.
- Create `personal-skills/xiaomi-financial-tracker/scripts/merge_metrics.py`: merge extracted metric observations into observations, facts, sources, runs, and review queue.
- Create `personal-skills/xiaomi-financial-tracker/scripts/merge_forecasts.py`: merge extracted forecasts into `forecasts.csv` with version-preserving IDs.
- Create `personal-skills/xiaomi-financial-tracker/scripts/merge_valuation.py`: merge extracted valuation history into `valuation_history.csv` with review queue handling.
- Create `personal-skills/xiaomi-financial-tracker/scripts/calculate_valuation_percentiles.py`: calculate PE/PB percentile snapshot with sample-size degradation.
- Create `personal-skills/xiaomi-financial-tracker/scripts/build_wide_tables.py`: build recent 5-year FY/H1 wide tables and optional valuation section.
- Create `personal-skills/xiaomi-financial-tracker/scripts/resolve_review_queue.py`: apply user-approved review queue items.
- Create `personal-skills/xiaomi-financial-tracker/evals/evals.json`: realistic skill evaluation prompts.
- Create `personal-skills/xiaomi-financial-tracker/workspace/periods/.gitkeep`, `workspace/data/*.csv`, and `workspace/views/.gitkeep`: committed empty workspace scaffold with headers.

## Task 1: Create Skill Scaffold And CSV Schemas

**Files:**
- Create: `personal-skills/xiaomi-financial-tracker/README.md`
- Create: `personal-skills/xiaomi-financial-tracker/workspace/periods/.gitkeep`
- Create: `personal-skills/xiaomi-financial-tracker/workspace/views/.gitkeep`
- Create: `personal-skills/xiaomi-financial-tracker/workspace/data/long_metrics.csv`
- Create: `personal-skills/xiaomi-financial-tracker/workspace/data/metric_observations.csv`
- Create: `personal-skills/xiaomi-financial-tracker/workspace/data/forecasts.csv`
- Create: `personal-skills/xiaomi-financial-tracker/workspace/data/valuation_history.csv`
- Create: `personal-skills/xiaomi-financial-tracker/workspace/data/valuation_snapshot.csv`
- Create: `personal-skills/xiaomi-financial-tracker/workspace/data/source_registry.csv`
- Create: `personal-skills/xiaomi-financial-tracker/workspace/data/ingestion_runs.csv`
- Create: `personal-skills/xiaomi-financial-tracker/workspace/data/review_queue.csv`

- [ ] **Step 1: Create directories**

Run: `mkdir -p personal-skills/xiaomi-financial-tracker/{references,scripts,evals,workspace/periods,workspace/data,workspace/views}`

Expected: directories exist under `personal-skills/xiaomi-financial-tracker/`.

- [ ] **Step 2: Create empty workspace markers**

Create two empty files:

```text
personal-skills/xiaomi-financial-tracker/workspace/periods/.gitkeep
personal-skills/xiaomi-financial-tracker/workspace/views/.gitkeep
```

Expected: git can track empty period and view directories.

- [ ] **Step 3: Create canonical CSV files with headers**

Create files with these first lines exactly:

```csv
fact_id,data_period,period_scope,value_kind,as_of_date,target_period,segment,metric,value,unit,yoy,qoq,calculation_method,is_derived,derived_from_keys,primary_observation_id,confidence,review_status,notes
```

```csv
observation_id,ingestion_run_id,source_id,source_period,data_period,period_scope,value_kind,as_of_date,target_period,segment,metric,raw_value,raw_unit,value,unit,yoy,qoq,calculation_method,source_location,confidence,review_status,notes
```

```csv
forecast_id,source_id,source_period,forecast_period,source_name,source_type,publication_date,captured_at,version,metric,segment,value,unit,scenario,assumptions,confidence,review_status,source_location,notes
```

```csv
valuation_id,date,metric,value,source_type,source_name,source_url,confidence,review_status,notes
```

```csv
metric,current_date,current_value,window_years,sample_start,sample_end,sample_count,valid_sample_count,percentile,status,notes
```

```csv
source_id,source_period,source_type,source_name,source_file,source_url,publication_date,content_hash,first_seen_at,last_processed_at,confidence,review_status,notes
```

```csv
ingestion_run_id,source_period,started_at,finished_at,input_count,created_observations,created_facts,created_forecasts,review_items,status,notes
```

```csv
issue_id,target_table,natural_key,existing_row_id,candidate_row_id,source_id,reason,severity,suggested_action,status,resolved_by,resolved_at,resolution_notes
```

Expected: data files are present and contain only one header row.

- [ ] **Step 4: Write README with new-user workflow**

Create `README.md` with these sections in this order:

```markdown
# Xiaomi Financial Tracker

## 这个 skill 做什么
## 快速开始
## 报告期命名
## 放输入文件
## 触发处理
## 看输出结果
## 单季和累计数据说明
## 预测和估值数据说明
## 复核队列怎么用
## 重跑是否安全
## 隐私和 Git 提交提醒
## 常见问题
```

Expected: README explicitly shows `workspace/periods/2025FY/input/`, a URL file example, `请使用 xiaomi-financial-tracker 处理 2025FY`, `report.md`, `recent_5y_fy_h1_wide.md`, `valuation_snapshot.md`, automatic-vs-review rules, forecast/valuation degradation behavior, and how to edit then rerun `review_queue.csv`.

- [ ] **Step 5: Verify scaffold**

Run: `python3 - <<'PY'
from pathlib import Path
root = Path('personal-skills/xiaomi-financial-tracker')
required = ['README.md','workspace/data/long_metrics.csv','workspace/data/metric_observations.csv','workspace/data/forecasts.csv','workspace/data/review_queue.csv']
missing = [p for p in required if not (root / p).exists()]
assert not missing, missing
print('scaffold ok')
PY`

Expected: `scaffold ok`.

## Task 2: Write Skill Workflow And References

**Files:**
- Create: `personal-skills/xiaomi-financial-tracker/SKILL.md`
- Create: `personal-skills/xiaomi-financial-tracker/references/metric-dictionary.md`
- Create: `personal-skills/xiaomi-financial-tracker/references/data-model.md`
- Create: `personal-skills/xiaomi-financial-tracker/references/analysis-framework.md`
- Create: `personal-skills/xiaomi-financial-tracker/references/valuation-methodology.md`
- Create: `personal-skills/xiaomi-financial-tracker/references/source-priority.md`

- [ ] **Step 1: Write SKILL metadata**

Create `SKILL.md` frontmatter:

```yaml
---
name: xiaomi-financial-tracker
description: Use this skill whenever the user asks to track or analyze Xiaomi financial reports, Xiaomi earnings, Xiaomi business segments, Xiaomi valuation percentiles, Xiaomi broker forecasts, or asks to process period folders like 2025Q1, 2025H1, 2025Q3, or 2025FY. It extracts official Xiaomi report data, maintains auditable CSV tables, generates financial analysis reports, updates recent FY/H1 wide tables, and calculates PE/PB percentile snapshots when valuation history is available.
argument-hint: "report period such as 2025Q1, 2025H1, 2025Q3, 2025FY, or a request to update forecasts/valuation"
---
```

Expected: skill can be discovered by name and description.

- [ ] **Step 2: Write SKILL body**

Include workflow sections:

```markdown
# Xiaomi Financial Tracker

## Default workspace
## Input discovery
## Source registration
## Extraction rules
## Fact vs observation vs forecast boundaries
## Single-quarter derivation
## Review queue rules
## Report output
## Script usage
## Final response format
```

Expected: body tells the agent to never mix forecasts into `long_metrics.csv`, to mark derived quarter values with `*`, to produce `extraction_notes.md`, to produce `report.md` with the 12 sections from the design, and to report paths at completion.

- [ ] **Step 3: Write data model reference**

Create `data-model.md` with the exact extracted contracts:

```csv
source_id,source_period,source_type,source_name,source_file,source_url,publication_date,source_location,data_period,period_scope,value_kind,as_of_date,target_period,segment,metric,raw_value,raw_unit,value,unit,yoy,qoq,calculation_method,confidence,review_status,notes
```

```csv
source_id,source_period,source_name,source_type,source_file,source_url,publication_date,source_location,forecast_period,metric,segment,value,unit,scenario,assumptions,confidence,review_status,notes
```

```csv
source_id,source_period,source_type,source_name,source_file,source_url,publication_date,source_location,date,metric,value,confidence,review_status,notes
```

Expected: `data-model.md` states that facts go to `extracted_metrics.csv`, predictions and official guidance go to `extracted_forecasts.csv`, PE/PB history goes to `extracted_valuation.csv`, and period fields must not mix cumulative labels with single-quarter labels.

- [ ] **Step 4: Write metric dictionary**

Create `metric-dictionary.md` with a table containing columns:

```markdown
| segment | metric | canonical_unit | value_kind | can_derive_quarter | notes |
```

Cover the full KPI set from the design: group revenue/profit/margin/R&D/cash/cash flow/employee metrics, smartphone revenue/margin/shipments/ASP/share/rank/high-end mix, AIoT revenue/margin/connected devices/multi-device users/home appliance shipments/device ranks, smart EV revenue/margin/profit/deliveries/ASP/stores/cities/delivery target/R&D, internet service revenue/margin/MAU/sub-segment revenue, and valuation PE/PB metrics.

Expected: flow metrics such as revenue and shipments have `can_derive_quarter=yes`; stock/ratio metrics such as cash, MAU, margin, stores, PE, PB have `can_derive_quarter=no`.

- [ ] **Step 5: Write analysis framework**

Create `analysis-framework.md` with the exact report headings from the spec and analytical prompts for smartphone, AIoT, internet services, smart EV, group profitability, external factors, valuation, forecasts, and risks.

Expected: report generation has a consistent template.

- [ ] **Step 6: Write valuation methodology**

Create `valuation-methodology.md` documenting: `TTM PE`, `Adjusted TTM PE`, `Forward PE`, `PB`, sample windows, `PE <= 0` exclusion, sample shortage behavior, and percentile formula `count(values <= current) / count(values) * 100`.

Expected: PE/PB percentiles are not fabricated when history is missing.

- [ ] **Step 7: Write source priority**

Create `source-priority.md` with source ranking: official PDF/IR, official screenshot, broker report, public web, media repost. Include conflict rules and review queue triggers.

Expected: source conflict behavior matches the design doc.

## Task 3: Implement Shared CSV Utilities

**Files:**
- Create: `personal-skills/xiaomi-financial-tracker/scripts/csv_utils.py`

- [ ] **Step 1: Create utility functions**

Implement functions with these names and behaviors:

```python
read_csv_rows(path, fieldnames): returns list[dict], creates empty file with header when missing
write_csv_rows(path, fieldnames, rows): writes header and rows atomically
append_unique_rows(path, fieldnames, rows, key_func): appends rows whose keys are new
stable_id(prefix, parts): sha256 hash over normalized parts, returns prefix_hash12
now_iso(): UTC ISO timestamp ending with Z
```

Expected: all scripts share one CSV implementation and deterministic IDs.

- [ ] **Step 2: Verify utility import**

Run: `python3 - <<'PY'
import sys
sys.path.insert(0, 'personal-skills/xiaomi-financial-tracker/scripts')
from csv_utils import stable_id
assert stable_id('x', ['a','b']).startswith('x_')
print('csv utils ok')
PY`

Expected: `csv utils ok`.

## Task 4: Implement Metric Merge Script

**Files:**
- Create: `personal-skills/xiaomi-financial-tracker/scripts/merge_metrics.py`

- [ ] **Step 1: Implement CLI contract**

Support command:

```bash
python3 personal-skills/xiaomi-financial-tracker/scripts/merge_metrics.py --skill-root personal-skills/xiaomi-financial-tracker --period 2025FY
```

The script reads `workspace/periods/<period>/extracted/extracted_metrics.csv`, registers sources, records an ingestion run, updates `metric_observations.csv`, merges accepted rows into `long_metrics.csv`, derives allowed single-quarter facts, and writes conflicts to `review_queue.csv`.

Expected: missing extracted file exits cleanly with message `No extracted metrics found for <period>` and status 0.

- [ ] **Step 2: Implement observation ingestion**

For each extracted metric row, create `observation_id` from source and row content, preserve `raw_value/raw_unit`, and append only if the observation key is new.

Expected: rerunning the same period does not duplicate observations.

- [ ] **Step 3: Implement fact merge**

For rows with `review_status` equal to `auto_accepted`, `llm_reviewed`, or `user_approved`, calculate fact natural key:

```text
data_period|period_scope|value_kind|as_of_date|segment|metric|unit
```

If no fact exists, insert it. If same key and same value exists, keep existing. If same key and different value exists, compare source priority, confidence, unit, and calculation method. Official PDF/IR can replace lower-priority official screenshots while preserving the replaced observation and creating a review note. Official-vs-official conflicts, unit conflicts, and unclear calculation method conflicts create `review_queue.csv` issues instead of overwriting.

Expected: facts are canonical and conflicts are visible.

- [ ] **Step 4: Implement single-quarter derivation**

After accepted facts are merged, derive quarter rows only for flow metrics where `can_derive_quarter=yes` in `metric-dictionary.md`:

```text
Q2 = H1 - Q1
Q3 = YTD_Q3 - H1
Q4 = FY - YTD_Q3
```

Set `is_derived=true`, `calculation_method=derived_from_cumulative_delta`, and `derived_from_keys` to the parent fact IDs. Do not derive margins, shares, rankings, MAU, connected devices, cash, stores, PE, or PB. Missing parent facts or unit mismatch creates a review item.

Expected: single-quarter derivation is deterministic and unsafe derivations are blocked.

- [ ] **Step 5: Verify merge with sample input**

Create `workspace/periods/2099FY/extracted/extracted_metrics.csv` with two identical rows and run merge twice.

Expected: `metric_observations.csv` and `long_metrics.csv` each get one logical row for that sample fact, not four.

## Task 5: Implement Forecast Merge Script

**Files:**
- Create: `personal-skills/xiaomi-financial-tracker/scripts/merge_forecasts.py`

- [ ] **Step 1: Implement CLI contract**

Support command:

```bash
python3 personal-skills/xiaomi-financial-tracker/scripts/merge_forecasts.py --skill-root personal-skills/xiaomi-financial-tracker --period 2025FY
```

The script reads `workspace/periods/<period>/extracted/extracted_forecasts.csv`, registers sources, records an ingestion run, and updates `forecasts.csv` plus `review_queue.csv`.

Expected: missing extracted file exits cleanly with message `No extracted forecasts found for <period>` and status 0.

- [ ] **Step 2: Preserve forecast versions**

Generate `forecast_id` from stable business fields only: `source_id`, `forecast_period`, `metric`, `segment`, `value`, `unit`, `scenario`, `assumptions`, and `publication_date`. Do not include `captured_at` or `notes` in the ID. Keep multiple versions for the same source/date/metric when stable fields differ.

Expected: broker revisions are not overwritten, and rerunning the same forecast row does not append a duplicate.

- [ ] **Step 3: Persist forecast review candidates**

Rows requiring review are still written to `forecasts.csv` with `review_status=needs_user_review`. The corresponding `review_queue.csv` issue uses `candidate_row_id=forecast_id`.

Expected: `resolve_review_queue.py` can find the forecast candidate row by ID.

- [ ] **Step 4: Verify forecast merge**

Run with two forecast rows sharing the same natural key but different values.

Expected: both rows are present in `forecasts.csv`.

## Task 6: Implement Valuation Merge Script

**Files:**
- Create: `personal-skills/xiaomi-financial-tracker/scripts/merge_valuation.py`

- [ ] **Step 1: Implement CLI contract**

Support command:

```bash
python3 personal-skills/xiaomi-financial-tracker/scripts/merge_valuation.py --skill-root personal-skills/xiaomi-financial-tracker --period 2025FY
```

The script reads `workspace/periods/<period>/extracted/extracted_valuation.csv`, registers sources, records an ingestion run, appends stable rows to `valuation_history.csv`, and writes unclear or conflicting valuation rows to `review_queue.csv`.

Expected: missing extracted file exits cleanly with message `No extracted valuation found for <period>` and status 0.

- [ ] **Step 2: Implement valuation de-duplication**

Use natural key `date|metric|source_name`. If the same key and same value already exists, do not append. If same key and different value exists, append a `review_queue.csv` item instead of overwriting.

Expected: repeated imports are idempotent and conflicts are visible.

- [ ] **Step 3: Persist valuation review candidates**

Rows requiring review are still written to `valuation_history.csv` with `review_status=needs_user_review`. The corresponding `review_queue.csv` issue uses `candidate_row_id=valuation_id`.

Expected: `resolve_review_queue.py` can find the valuation candidate row by ID.

- [ ] **Step 4: Verify valuation merge**

Run with two identical valuation rows and one conflicting row.

Expected: one valuation row is inserted, the duplicate is skipped, and the conflicting row creates one review item.

## Task 7: Implement Valuation Percentiles

**Files:**
- Create: `personal-skills/xiaomi-financial-tracker/scripts/calculate_valuation_percentiles.py`

- [ ] **Step 1: Implement CLI contract**

Support command:

```bash
python3 personal-skills/xiaomi-financial-tracker/scripts/calculate_valuation_percentiles.py --skill-root personal-skills/xiaomi-financial-tracker
```

The script reads `workspace/data/valuation_history.csv` and writes `valuation_snapshot.csv` plus `workspace/views/valuation_snapshot.md`.

Expected: empty history writes a Markdown note saying valuation history is insufficient.

- [ ] **Step 2: Implement percentile rules**

For each metric in `TTM PE`, `Adjusted TTM PE`, `PB`, calculate 5-year and 10-year windows from the latest date. Exclude blank, non-numeric, and `PE <= 0` values. Exclude rows with `review_status=open`, `needs_user_review`, or `rejected`. For the same `date|metric`, select one canonical row by source priority and confidence; if values conflict and cannot be resolved, skip that `date|metric` sample and create or preserve a review item. Percentile formula is `count(values <= current) / count(values) * 100`.

Expected: a partial but valid window produces `status=available_history_only`; zero valid samples produce `status=insufficient_history`; no percentile is fabricated without data.

- [ ] **Step 3: Verify with sample history**

Create sample monthly PB rows and run the script.

Expected: `valuation_snapshot.csv` contains 5-year and 10-year rows. A partial 10-year sample is calculated with `status=available_history_only`; only zero valid samples produce `status=insufficient_history`.

## Task 8: Implement Wide Table Builder

**Files:**
- Create: `personal-skills/xiaomi-financial-tracker/scripts/build_wide_tables.py`

- [ ] **Step 1: Implement CLI contract**

Support command:

```bash
python3 personal-skills/xiaomi-financial-tracker/scripts/build_wide_tables.py --skill-root personal-skills/xiaomi-financial-tracker
```

The script reads `long_metrics.csv` and optional `valuation_snapshot.csv`, then writes `workspace/views/recent_5y_fy_h1_wide.csv` and `.md`.

Expected: no quarterly periods appear in the wide table.

- [ ] **Step 2: Restrict periods**

Include only `YYYYFY` and `YYYYH1`, latest five years by year.

Expected: `2025Q1`, `2025Q2`, `2025Q3`, and `2025Q4` are excluded.

- [ ] **Step 3: Verify wide table**

Seed facts for `2025FY`, `2025H1`, and `2025Q3`, then run builder.

Expected: output contains `2025FY` and `2025H1`, not `2025Q3`.

## Task 9: Implement Review Queue Resolver

**Files:**
- Create: `personal-skills/xiaomi-financial-tracker/scripts/resolve_review_queue.py`

- [ ] **Step 1: Implement CLI contract**

Support command:

```bash
python3 personal-skills/xiaomi-financial-tracker/scripts/resolve_review_queue.py --skill-root personal-skills/xiaomi-financial-tracker
```

The script reads `review_queue.csv` and applies `status=user_approved` rows when target table and candidate row can be found.

Expected: rejected/open rows remain untouched.

- [ ] **Step 2: Implement safe behavior**

If a review item cannot be resolved because target or candidate is missing, keep it and add `resolution_notes` explaining the missing reference.

Expected: resolver never deletes unresolved review items.

## Task 10: Add Evals And Validation

**Files:**
- Create: `personal-skills/xiaomi-financial-tracker/evals/evals.json`

- [ ] **Step 1: Create eval prompts**

Create evals for: official PDF processing, H1 deriving Q2, PDF-vs-screenshot source priority, conflict queue, idempotent rerun, later report restating or revising the same fact, source registry and ingestion run updates, valuation insufficient history, valuation extracted merge conflict, broker forecast revision, forecast review then resolve, and point-in-time no-derive behavior.

Expected: eval file is valid JSON with `skill_name=xiaomi-financial-tracker`.

- [ ] **Step 2: Run JSON validation**

Run: `python3 -m json.tool personal-skills/xiaomi-financial-tracker/evals/evals.json >/dev/null`

Expected: command exits 0.

- [ ] **Step 3: Run script smoke tests**

Run each script with `--skill-root personal-skills/xiaomi-financial-tracker` on an empty workspace.

Expected: no traceback; scripts either update empty outputs or print clear missing-input messages.

## Task 11: Final Manual Review

**Files:**
- Review all files under `personal-skills/xiaomi-financial-tracker/`
- Review `docs/specs/2026-05-30-xiaomi-financial-tracker-design.md`

- [ ] **Step 1: Check spec coverage**

Verify the implementation has: README, SKILL body, references, CSV headers, observations/facts split, forecasts separate from facts, review queue schema, single-quarter derivation rules, and valuation percentile degradation.

Expected: every design requirement has a concrete file or script.

- [ ] **Step 2: Check for placeholders**

Run: `python3 - <<'PY'
from pathlib import Path
patterns = ['TB' + 'D', 'TO' + 'DO', '待' + '定', 'implement' + ' later']
root = Path('personal-skills/xiaomi-financial-tracker')
matches = []
for path in root.rglob('*'):
    if path.is_file():
        text = path.read_text(errors='ignore')
        for pattern in patterns:
            if pattern in text:
                matches.append((str(path), pattern))
if matches:
    raise SystemExit(matches)
print('no placeholders')
PY`

Expected: no matches.

- [ ] **Step 3: Check git diff**

Run: `git diff -- docs/specs/2026-05-30-xiaomi-financial-tracker-design.md docs/plans/2026-05-30-xiaomi-financial-tracker.md personal-skills/xiaomi-financial-tracker`

Expected: only Xiaomi tracker design, plan, and skill files are changed.
