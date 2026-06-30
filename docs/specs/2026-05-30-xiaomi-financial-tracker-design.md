# 小米财报跟踪 Skill 设计

日期：2026-05-30

## 目标

创建 `xiaomi-financial-tracker` skill，用于持续跟踪小米集团财报、核心经营数据、业务板块变化、估值位置和未来三年预测。

该 skill 面向重仓小米股票的业务投资者，重点不是给出买卖指令，而是帮助用户长期看清小米的经营质量、利润结构、业务拐点、风险挑战和估值位置。

## 范围

V1 的核心能力是“官方财报资料 -> 事实数据抽取 -> 单季/累计数据整理 -> 报告和宽表”。

V1 支持以下能力：

- 读取官方财报 PDF、官方财报 URL、官方财报截图、券商或投行研报、公开网页预测资料。
- 抽取小米集团和主要业务板块的核心事实数据。
- 同时保留单季数据和累计数据。
- 维护长期 canonical fact table，并持续追加。
- 保存所有候选观察值和来源登记，保证可追溯。
- 生成最近 5 年年报和中报宽表视图。
- 生成当期财报分析报告。
- 在有可靠历史估值数据时，生成 PE/PB 的 5 年和 10 年历史百分位。
- 在有可靠预测来源时，汇总未来 3 个财年的官方指引、券商预测、公开预测或情景假设。
- 对公开网页预测和券商预测做 LLM 自检，无法确认时再请求用户复核。

V1 不做以下事项：

- 不直接输出买入、卖出、加仓、减仓等投资动作建议。
- 不实现完整自动爬虫系统。
- 不在缺少可靠来源时补造未来 3 年预测。
- 不在缺少足够历史估值序列时强行输出 5 年或 10 年百分位。
- 不承诺所有截图 OCR 都能无人工确认地准确入库。
- 不把预测数据、官方指引和已披露历史事实混为一类。

## Skill 位置

创建目录：

```text
personal-skills/xiaomi-financial-tracker/
```

skill 本体、说明文档、参考资料、脚本、输入输出工作区都放在这个目录下，可以提交到 git。

## 目录结构

```text
personal-skills/xiaomi-financial-tracker/
├── SKILL.md
├── README.md
├── references/
│   ├── metric-dictionary.md
│   ├── data-model.md
│   ├── analysis-framework.md
│   ├── valuation-methodology.md
│   └── source-priority.md
├── scripts/
│   ├── merge_metrics.py
│   ├── merge_forecasts.py
│   ├── merge_valuation.py
│   ├── build_wide_tables.py
│   ├── calculate_valuation_percentiles.py
│   └── resolve_review_queue.py
├── evals/
│   └── evals.json
└── workspace/
    ├── periods/
    │   ├── 2025Q1/
    │   │   ├── input/
    │   │   ├── extracted/
    │   │   └── report.md
    │   ├── 2025H1/
    │   ├── 2025Q3/
    │   └── 2025FY/
    ├── data/
    │   ├── long_metrics.csv
    │   ├── metric_observations.csv
    │   ├── forecasts.csv
    │   ├── valuation_history.csv
    │   ├── valuation_snapshot.csv
    │   ├── source_registry.csv
    │   ├── ingestion_runs.csv
    │   └── review_queue.csv
    └── views/
        ├── recent_5y_fy_h1_wide.md
        ├── recent_5y_fy_h1_wide.csv
        └── valuation_snapshot.md
```

## README 设计

`README.md` 是新用户入口，必须用非技术化语言说明如何使用。

README 必须包含：

- 这个 skill 是做什么的。
- 第一次使用如何准备目录。
- 最小输入组合：至少一个报告期目录，以及官方 PDF、官方 URL、官方截图中的一种。
- 报告期命名规则。
- URL 文件示例。
- 如何把 PDF、截图、URL、研报和估值数据放进 `input/`。
- 如何让 agent 处理某个报告期。
- 处理完成后应该看哪些文件。
- 缺少预测或估值历史数据时会如何降级。
- 哪些数据会自动入库，哪些需要复核。
- 如何查看、编辑并重新处理 `review_queue.csv`。
- 重跑同一报告期不会重复污染主表的说明。
- 原始资料可以提交到 git，但如果含付费研报或个人持仓数据，用户应自行决定是否提交。
- 常见问题，例如“中报为什么会出现 Q2 数据”“年报为什么会出现 Q4 数据”“为什么预测数据没有覆盖事实数据”。

README 示例指令：

```text
请使用 xiaomi-financial-tracker 处理 2025FY
```

README 示例输入目录：

```text
workspace/periods/2025FY/input/
```

README 示例 URL 文件：

```text
official-ir-url.md

https://ir.mi.com/financial-information/quarterly-results
https://ir.mi.com/system/files-encrypted/.../Xiaomi%20Corp_25Q4_ER_ENG%20vF.pdf
```

README 示例主要输出：

```text
workspace/periods/2025FY/report.md
workspace/views/recent_5y_fy_h1_wide.md
workspace/views/valuation_snapshot.md
workspace/data/review_queue.csv
```

## 报告期命名

用户按财报发布节奏创建文件夹。

支持以下报告期命名：

- `YYYYQ1`：一季度报告，例如 `2025Q1`。
- `YYYYH1`：中报或半年报，例如 `2025H1`。
- `YYYYQ3`：三季报或前三季度报告，例如 `2025Q3`。
- `YYYYFY`：年报或全年报告，例如 `2025FY`。

不推荐用 `YYYYQ2` 表示中报，也不推荐用 `YYYYQ4` 表示年报，因为中报和年报同时包含累计数据和单季推导数据。

非财报季资料默认仍绑定到最相关的报告期目录。如果后续需要独立跟踪非财报日估值快照，可新增 `workspace/snapshots/YYYY-MM-DD/`，但不纳入 V1 必做范围。

## 输入规则

每个报告期的原始材料放在：

```text
workspace/periods/<source_period>/input/
```

支持以下输入：

- 官方 PDF 财报文件。
- 官方 PDF 财报 URL，放在 `.md` 或 `.txt` 文件中。
- 官方财报截图或图片。
- 券商或投行研报 PDF。
- 包含预测、估值、历史 PE/PB 的 CSV、Markdown 或截图。

输入可以混放。skill 处理时需要先识别来源类型，再按来源优先级抽取和合并。

缺少预测资料时，报告的未来 3 财年预测部分应明确写“可靠预测来源不足”，并列出需要补充的材料。

缺少估值历史序列时，估值百分位部分应明确写“历史估值序列不足，无法计算 5 年或 10 年百分位”。

## 输出规则

每个报告期生成以下输出：

```text
workspace/periods/<source_period>/extracted/extracted_metrics.csv
workspace/periods/<source_period>/extracted/extracted_forecasts.csv
workspace/periods/<source_period>/extracted/extracted_valuation.csv
workspace/periods/<source_period>/extracted/extraction_notes.md
workspace/periods/<source_period>/report.md
```

全局长期数据输出：

```text
workspace/data/long_metrics.csv
workspace/data/metric_observations.csv
workspace/data/forecasts.csv
workspace/data/valuation_history.csv
workspace/data/valuation_snapshot.csv
workspace/data/source_registry.csv
workspace/data/ingestion_runs.csv
workspace/data/review_queue.csv
```

面向阅读的汇总视图：

```text
workspace/views/recent_5y_fy_h1_wide.md
workspace/views/recent_5y_fy_h1_wide.csv
workspace/views/valuation_snapshot.md
```

## Extracted 中间表契约

agent 从 PDF、截图、URL、研报和网页中抽取数据后，必须先写入报告期目录下的 `extracted/` 中间文件，再由脚本合并到全局数据表。

`extracted_metrics.csv` 字段：

```csv
source_id,source_period,source_type,source_name,source_file,source_url,publication_date,source_location,data_period,period_scope,value_kind,as_of_date,target_period,segment,metric,raw_value,raw_unit,value,unit,yoy,qoq,calculation_method,confidence,review_status,notes
```

`extracted_forecasts.csv` 字段：

```csv
source_id,source_period,source_name,source_type,source_file,source_url,publication_date,source_location,forecast_period,metric,segment,value,unit,scenario,assumptions,confidence,review_status,notes
```

`extracted_valuation.csv` 字段：

```csv
source_id,source_period,source_type,source_name,source_file,source_url,publication_date,source_location,date,metric,value,confidence,review_status,notes
```

`extraction_notes.md` 必须记录：处理了哪些输入、哪些数据自动接受、哪些数据进入复核队列、哪些预测或估值数据因来源不足而降级。

中间表要求：

- 事实指标只能进入 `extracted_metrics.csv`。
- 预测、官方指引和情景假设只能进入 `extracted_forecasts.csv`。
- PE/PB 历史序列只能进入 `extracted_valuation.csv`。
- `source_period/data_period/forecast_period/target_period` 必须按数据含义填写，不得把 `2025H1` 累计数写成 `2025Q2`。
- 所有 extracted 文件都要包含来源字段，使后续合并脚本可以登记 `source_registry.csv`。

## 数据期间模型

报告期文件夹和数据期间必须分开。

`source_period` 表示资料来自哪个财报文件夹。

`data_period` 表示数据本身属于哪个期间。

`period_scope` 表示期间范围。

`value_kind` 表示值的性质。

`as_of_date` 表示点时指标的实际日期。

`target_period` 表示预测或指引的目标期间。

示例：

```csv
data_period,period_scope,value_kind,as_of_date,target_period,segment,metric,value,unit,calculation_method,is_derived,derived_from_keys
2025Q1,quarter,actual_flow,,,Group,total_revenue,111.3,RMB bn,reported,false,
2025H1,cumulative,actual_flow,,,Group,total_revenue,227.3,RMB bn,reported,false,
2025Q2,quarter,actual_flow,,,Group,total_revenue,116.0,RMB bn,derived_from_cumulative_delta,true,"2025H1|2025Q1"
2025YTD_Q3,cumulative,actual_flow,,,Group,total_revenue,340.4,RMB bn,reported,false,
2025Q3,quarter,actual_flow,,,Group,total_revenue,113.1,RMB bn,derived_from_cumulative_delta,true,"2025YTD_Q3|2025H1"
2025FY,cumulative,actual_flow,,,Group,total_revenue,457.3,RMB bn,reported,false,
2025Q4,quarter,actual_flow,,,Group,total_revenue,116.9,RMB bn,derived_from_cumulative_delta,true,"2025FY|2025YTD_Q3"
2025FY,point_in_time,actual_stock,2025-12-31,,Group,cash_reserve,175.1,RMB bn,reported,false,
```

反推单季数据需要在报告正文中展示，但加 `*` 标注“由累计数反推”。

## 主事实表

`long_metrics.csv` 是 canonical fact table，只保存已披露或可从已披露数据可靠计算的事实数据。

预测数据和官方指引不写入 `long_metrics.csv`，统一写入 `forecasts.csv`。

字段：

```csv
fact_id,data_period,period_scope,value_kind,as_of_date,target_period,segment,metric,value,unit,yoy,qoq,calculation_method,is_derived,derived_from_keys,primary_observation_id,confidence,review_status,notes
```

字段说明：

- `fact_id`：事实行唯一 ID，可由自然键 hash 生成。
- `data_period`：指标实际期间，例如 `2025Q4`、`2025FY`、`2025YTD_Q3`。
- `period_scope`：`quarter`、`cumulative`、`point_in_time`。
- `value_kind`：`actual_flow` 或 `actual_stock`。
- `as_of_date`：点时指标日期，流量指标可为空。
- `target_period`：事实表通常为空，保留字段用于兼容特殊事实口径。
- `segment`：业务板块。
- `metric`：指标名，使用 `references/metric-dictionary.md` 中的标准名。
- `value`：标准化后的数值。
- `unit`：标准单位，例如 `RMB bn`、`%`、`million units`、`vehicles`。
- `yoy`：同比，如来源披露或可可靠计算则填写。
- `qoq`：环比，只对允许计算的流量指标填写。
- `calculation_method`：`reported`、`derived_from_cumulative_delta`、`calculated`、`estimated`。
- `is_derived`：是否派生。
- `derived_from_keys`：派生数据的父事实自然键或 `fact_id` 列表。
- `primary_observation_id`：被采纳为事实的观察值 ID。
- `confidence`：`high`、`medium`、`low`。
- `review_status`：`auto_accepted`、`llm_reviewed`、`needs_user_review`、`user_approved`。
- `notes`：口径说明、异常说明、冲突说明。

事实自然键：

```text
data_period + period_scope + value_kind + as_of_date + segment + metric + unit
```

同一事实自然键出现多个候选值时，按来源优先级和复核状态处理，不允许静默覆盖。被覆盖或冲突的数据必须保留在 `metric_observations.csv`，并在需要时写入 `review_queue.csv`。

## 观察值表

`metric_observations.csv` 保存从每个来源抽取到的候选值。它不是最终事实表，而是审计和冲突处理依据。

字段：

```csv
observation_id,ingestion_run_id,source_id,source_period,data_period,period_scope,value_kind,as_of_date,target_period,segment,metric,raw_value,raw_unit,value,unit,yoy,qoq,calculation_method,source_location,confidence,review_status,notes
```

观察值唯一键：

```text
source_id + source_location + data_period + period_scope + value_kind + as_of_date + segment + metric + raw_value + raw_unit
```

重跑同一来源时，观察值按唯一键去重。新的观察值不会直接覆盖事实表，必须经过合并规则或复核队列。

## 预测数据表

`forecasts.csv` 专门保存预测、官方指引和情景假设，不与事实数据混表覆盖。

字段：

```csv
forecast_id,source_id,source_period,forecast_period,source_name,source_type,publication_date,captured_at,version,metric,segment,value,unit,scenario,assumptions,confidence,review_status,source_location,notes
```

预测来源类型：

- 官方指引，`source_type=official_guidance`。
- 券商或投行研报。
- 公开网页预测。
- LLM 情景模型。

预测行唯一 ID 使用 `forecast_id`。预测自然键用于发现同一来源的修订：

```text
source_id + forecast_period + segment + metric + scenario + unit
```

同一券商同一日期同一指标出现修订时，不自动覆盖旧值，新增一条记录并在 `version` 或 `notes` 中说明修订原因或来源页码。

需要复核的预测候选行也必须先写入 `forecasts.csv`，并设置 `review_status=needs_user_review`。对应复核事项的 `candidate_row_id` 使用该行的 `forecast_id`。

预测输出至少尝试覆盖未来 3 个财年。可靠来源不足时，不补造数据，报告中说明缺口。

同一指标不同来源预测差异较大时，不互相覆盖，按来源并列展示。

## 估值数据表

`valuation_history.csv` 用于保存 PE/PB 历史序列。

字段：

```csv
valuation_id,date,metric,value,source_type,source_name,source_url,confidence,review_status,notes
```

估值自然键：

```text
date + metric + source_name
```

需要复核的估值候选行也必须先写入 `valuation_history.csv`，并设置 `review_status=needs_user_review`。对应复核事项的 `candidate_row_id` 使用该行的 `valuation_id`。

估值口径：

- `TTM PE` 用于和市场常见口径对齐。
- `Adjusted TTM PE` 作为核心估值判断主口径。
- `Forward PE` 放在预测和情景估值中，不作为历史百分位主口径。
- `PB` 用于观察资产负债表安全边际和历史估值区间。

估值历史数据合同：

- 用户提供的估值历史 CSV 或截图是最高优先级。
- 公开来源只能作为补缺，必须登记来源。
- V1 不承诺自动抓取完整 PE/PB 历史序列。
- 建议估值历史至少按月，最好按日或周。
- `PE <= 0`、空值、明显异常值不参与百分位计算，并在 `valuation_snapshot.md` 中说明。
- 小米 2018 年上市，若不足 10 年历史，应输出“可得历史百分位”，不得假装已有完整 10 年样本。

估值百分位样本选择规则：

- 同一 `date + metric` 存在多来源时，只选择一个 canonical 样本参与百分位。
- canonical 样本按来源优先级、`review_status` 和置信度选择。
- `review_status=open`、`needs_user_review`、`rejected` 的估值样本不参与百分位。
- 同一 `date + metric` 多来源值冲突且无法自动确定优先级时，写入 `review_queue.csv`，在解决前该日期该指标不参与百分位。

百分位计算规则：

- 5 年百分位使用最近 5 年历史序列。
- 10 年百分位使用最近 10 年历史序列；如果上市历史不足或样本不足，则用可得历史并标注。
- 当前值取 `valuation_history.csv` 中目标指标的最新日期。
- 百分位公式为 `小于等于当前值的有效样本数 / 有效样本总数 * 100`。
- 百分位数值越高，代表估值越接近历史高位。

## 来源登记表

`source_registry.csv` 用于记录每次处理时识别到的原始资料，方便之后追溯。

字段：

```csv
source_id,source_period,source_type,source_name,source_file,source_url,publication_date,content_hash,first_seen_at,last_processed_at,confidence,review_status,notes
```

字段说明：

- `source_id`：来源唯一标识，优先由规范化 URL hash 或文件内容 hash 生成，不用处理时间生成。
- `source_period`：资料放入的报告期目录，例如 `2025FY`。
- `source_type`：`official_pdf`、`official_url`、`official_screenshot`、`broker_report`、`public_web`、`user_csv`。
- `source_name`：来源名称，例如小米 2025 年报、某券商研报、某公开网页。
- `source_file`：本地文件名。
- `source_url`：原始 URL。
- `publication_date`：资料发布日期，无法确认则留空并降低置信度。
- `content_hash`：本地文件内容 hash 或规范化 URL hash。
- `first_seen_at`：首次登记时间。
- `last_processed_at`：最近处理时间。
- `confidence`：来源可信度。
- `review_status`：复核状态。
- `notes`：来源说明、异常或限制。

## 处理批次表

`ingestion_runs.csv` 记录每次运行，帮助排查重复处理和回溯。

字段：

```csv
ingestion_run_id,source_period,started_at,finished_at,input_count,created_observations,created_facts,created_forecasts,review_items,status,notes
```

## 复核队列表

`review_queue.csv` 记录需要人工或后续 LLM 复核的事项。

字段：

```csv
issue_id,target_table,natural_key,existing_row_id,candidate_row_id,source_id,reason,severity,suggested_action,status,resolved_by,resolved_at,resolution_notes
```

字段说明：

- `issue_id`：复核事项 ID。
- `target_table`：目标表，例如 `long_metrics`、`forecasts`、`valuation_history`。
- `natural_key`：冲突或待确认数据对应的自然键。
- `existing_row_id`：当前已采纳行。
- `candidate_row_id`：候选行。
- `source_id`：候选来源。
- `reason`：进入复核的原因。
- `severity`：`high`、`medium`、`low`。
- `suggested_action`：建议动作，例如 `accept_candidate`、`keep_existing`、`manual_check`。
- `status`：`open`、`llm_reviewed`、`user_approved`、`rejected`、`resolved`。
- `resolved_by`：解决者。
- `resolved_at`：解决时间。
- `resolution_notes`：解决说明。

复核流程：

1. skill 将无法自动确认的问题写入 `review_queue.csv`。
2. LLM 可先尝试复核公开网页预测和券商预测，并把 `status` 更新为 `llm_reviewed` 或保持 `open`。
3. 用户可以直接编辑 `status` 和 `resolution_notes`。
4. 重新运行处理或运行 `resolve_review_queue.py` 后，已批准项合并到目标表。
5. 被拒绝项保留在队列中，不删除来源观察值。

## 业务板块

主要板块：

- `Group`
- `Smartphone`
- `AIoT`
- `Internet Services`
- `Smart EV, AI and Other New Initiatives`
- `Valuation`

## 核心指标

集团指标：总营收、毛利率、净利润、经调整净利润、研发开支、现金储备、经营现金流、自由现金流、销售和推广开支、员工数、研发人员数。

智能手机指标：收入、毛利率、出货量、ASP、全球市场份额、中国市场份额、全球和中国排名、高端智能手机出货量占比。

AIoT 指标：收入、毛利率、已连接设备数、拥有五件及以上设备用户数、空调出货量、冰箱出货量、洗衣机出货量、平板/可穿戴/TWS/电视等排名。

智能汽车指标：收入、毛利率、经营利润或亏损、经调整利润、交付车辆数、ASP、门店数量、覆盖城市数量、年度交付目标、汽车研发费用。

互联网服务指标：收入、毛利率、全球 MAU、中国 MAU、广告/游戏/增值服务等分项收入。

估值指标：TTM PE、Adjusted TTM PE、Forward PE、PB、TTM PE 5 年历史百分位、TTM PE 10 年历史百分位、Adjusted TTM PE 5 年历史百分位、Adjusted TTM PE 10 年历史百分位、PB 5 年历史百分位、PB 10 年历史百分位。

## 单位标准化

`references/metric-dictionary.md` 必须定义每个指标的标准单位和是否可反推。

标准化原则：

- 金额默认使用 `RMB bn`。
- 百分比使用 `%`，百分点变化在 `notes` 中说明，不和百分比值混用。
- 智能手机出货量默认使用 `million units`。
- 汽车交付量默认使用 `vehicles`。
- MAU 默认使用 `million users`。
- 连接设备数默认使用 `million devices`。
- 原始值和原始单位保留在 `metric_observations.csv` 的 `raw_value` 和 `raw_unit`。

合并和反推前必须先完成单位标准化。单位或口径不一致时不得自动合并为同一指标。

## 来源优先级

来源优先级从高到低：

- 官方 PDF、公告、IR 链接。
- 用户提供的官方截图。
- 用户提供的券商或投行研报。
- 公开网页预测。
- 媒体转述。

自动合并规则：

- 官方 PDF、公告、IR 链接可在抽取自检通过后自动入库。
- 用户提供的官方截图可在 OCR 清晰、字段明确、与上下文一致时自动入库。
- 公开网页预测需要 LLM 交叉检查来源、日期和口径。
- 券商或投行预测需要 LLM 检查研报来源、发布时间、预测年份和利润口径。
- 不能确认的数据进入 `review_queue.csv`。

冲突处理规则：

- 官方来源之间冲突时进入复核队列。
- 官方 PDF 与官方截图冲突时优先 PDF，截图进入复核队列。
- 预测来源之间冲突时保留多条，不覆盖。
- 单位或口径不一致时不得自动合并为同一指标。

## 单季反推规则

中报、三季报和年报通常同时包含累计信息，skill 需要尽量补齐对应单季数据。

反推公式：

- `Q2 = H1 - Q1`
- `Q3 = YTD_Q3 - H1`
- `Q4 = FY - YTD_Q3`

反推条件：

- 被减数和减数必须是同一指标、同一单位、同一业务板块、同一口径。
- 毛利率、市场份额、排名、MAU、连接设备数、门店数、现金储备等比例或时点指标不得用简单相减反推。
- 出货量、收入、利润、研发开支等流量指标可以反推。
- 反推结果必须标记 `calculation_method=derived_from_cumulative_delta`。
- 反推结果必须记录 `is_derived=true` 和 `derived_from_keys`。
- 报告正文展示反推数据时，在指标或数值旁加 `*`，并注明“由累计数反推”。
- 如果缺少上一累计期数据，或口径不一致，则不反推，写入 `review_queue.csv`。

## 报告结构

每个报告期生成 `report.md`。

结构：

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

报告必须体现：

- 手机基本盘是否承压，压力来自销量、ASP、毛利率还是成本。
- AIoT 是否继续提升收入占比和利润质量。
- 互联网服务是否保持高毛利和用户规模增长。
- 汽车业务处于规模爬坡、利润释放还是亏损扩大阶段。
- 集团利润变化是经营改善、周期变化、成本波动还是一次性因素导致。
- 当前估值百分位是否与基本面变化匹配。
- 未来三年预测的关键假设、来源和主要不确定性。
- 哪些数据缺失，哪些需要用户复核。

## 宽表视图

`recent_5y_fy_h1_wide.md` 和 `recent_5y_fy_h1_wide.csv` 只展示最近 5 年的 `FY` 和 `H1`。

季度数据不进入宽表展示，但继续保存在长表中，用于趋势分析、同比和环比计算。

宽表优先展示核心指标，避免过宽。

核心展示顺序：总体情况、智能手机、AIoT、智能汽车、互联网服务、估值。

宽表的经营指标读取 `long_metrics.csv`，估值指标读取 `valuation_snapshot.csv`。如果 `valuation_snapshot.csv` 不存在或样本不足，宽表估值部分显示“样本不足”。

## 脚本设计

`merge_metrics.py`：

- 合并 `extracted_metrics.csv` 到 `metric_observations.csv`。
- 将可自动接受的观察值合并到 `long_metrics.csv`。
- 执行允许的单季派生，生成 `Q2/Q3/Q4` 派生事实。
- 按事实自然键去重。
- 按来源优先级处理冲突。
- 登记来源并记录处理批次。
- 将无法确认的数据写入 `review_queue.csv`。

`merge_forecasts.py`：

- 合并 `extracted_forecasts.csv` 到 `forecasts.csv`。
- 按 `forecast_id` 去重。
- 保留同一自然键的多版本修订。
- 登记来源并记录处理批次。
- 将口径不清或来源冲突的预测写入 `review_queue.csv`。

`merge_valuation.py`：

- 合并 `extracted_valuation.csv` 到 `valuation_history.csv`。
- 按估值自然键去重。
- 登记来源并记录处理批次。
- 将来源不明、日期不清、同日同指标冲突的数据写入 `review_queue.csv`。

`build_wide_tables.py`：

- 从 `long_metrics.csv` 生成最近 5 年 `FY/H1` 宽表。
- 可读取 `valuation_snapshot.csv` 补充估值部分。
- 输出 Markdown 和 CSV 两种格式。
- 不展示季度数据。

`calculate_valuation_percentiles.py`：

- 读取 `valuation_history.csv`。
- 计算 PE/PB 5 年和 10 年历史百分位。
- 样本不足时输出降级说明。
- 生成 `valuation_snapshot.csv` 和 `valuation_snapshot.md`。

`resolve_review_queue.py`：

- 读取 `review_queue.csv` 中已批准或已拒绝的项。
- 将 `user_approved` 项合并到目标表。
- 保留 rejected 项和来源观察值。

## Skill 工作流

触发条件：用户提到小米财报、小米业绩跟踪、小米基本面分析、小米估值百分位、小米研报预测，或要求处理 `YYYYQ1`、`YYYYH1`、`YYYYQ3`、`YYYYFY` 文件夹。

处理步骤：

1. 确认报告期文件夹存在。
2. 读取 `input/` 中的 PDF、图片、Markdown、文本、CSV。
3. 登记来源到 `source_registry.csv`，并记录运行到 `ingestion_runs.csv`。
4. 识别来源类型和可信度。
5. 抽取事实指标、预测指标和估值指标。
6. 标准化单位和指标名。
7. 对中报、三季报、年报补充单季派生数据。
8. 对公开网页预测和券商预测进行 LLM 自检。
9. 生成 `extracted/` 中间表和 `report.md`。
10. 运行 `merge_metrics.py`、`merge_forecasts.py` 和 `merge_valuation.py` 合并可自动接受的数据。
11. 运行 `calculate_valuation_percentiles.py` 和 `build_wide_tables.py` 更新最近 5 年宽表和估值快照。
12. 向用户报告新增数据、待复核项和输出文件路径。

## 复核机制

自动接受：

- 官方 PDF 中清晰披露的数据。
- 官方 IR 链接中清晰披露的数据。
- 用户提供的官方截图中 OCR 清晰且上下文一致的数据。

LLM 自检后接受：

- 券商研报中口径明确、年份明确、来源明确的预测。
- 公开网页中能交叉验证日期、来源和指标口径的预测。

需要用户复核：

- 来源冲突。
- OCR 不清晰。
- 单位不明确。
- 预测口径不明确。
- 同一指标不同来源差异过大且无法解释。
- 估值历史样本不足或来源不稳定。

## 测试用例

`evals/evals.json` 至少包含以下场景：

- 用户要求处理一个官方 PDF 财报文件夹，期望生成观察值表、事实表、报告和宽表。
- 用户要求处理中报，期望同时出现 `H1` 累计数据和 `Q2` 单季派生数据。
- 官方 PDF 与官方截图同一指标冲突，期望进入复核队列。
- 同一来源重复处理，期望保持幂等，不重复污染主表。
- 后续报告对同一事实重述或修订，期望保留观察值并触发冲突处理。
- 估值历史不足 5 年或 10 年，期望降级输出并说明样本不足。
- 同日券商预测修订，期望保留多版本。
- 点时指标禁止用累计差值反推。

## 成功标准

第一版完成后应满足：

- 用户能按 `workspace/periods/2025FY/input/` 放入资料。
- 用户能用自然语言要求处理某个报告期。
- skill 能生成当期 `report.md`。
- skill 能生成或更新 `long_metrics.csv`、`metric_observations.csv`、`forecasts.csv`、`valuation_history.csv`、`source_registry.csv`、`review_queue.csv`。
- skill 能生成最近 5 年 `FY/H1` 宽表。
- 当估值历史数据充足时，skill 能输出 PE/PB 5 年和 10 年历史百分位。
- 当估值历史数据不足时，skill 能明确说明样本不足，而不是补造结果。
- 当预测来源充足时，skill 能输出未来 3 财年预测。
- 当预测来源不足时，skill 能明确说明缺少哪些输入，而不是补造预测。
- skill 能明确标注官方数据、截图数据、研报预测和公开网页预测的来源与置信度。
- skill 能把无法确认的数据写入复核队列，而不是静默覆盖长期数据。
- README 能让新用户知道如何放文件、如何触发、看哪些输出、如何处理复核队列。

## 已确认决策

- 数据和输出都放在 skill 目录内，可以提交到 git。
- 数据源选择官方财报、官方截图、券商研报、公开网页预测的组合模式。
- 长期事实主表使用 canonical long table，并额外保存来源观察值表。
- 人看宽表只展示最近 5 年年报和中报。
- 中报、三季报、年报既保留累计数据，也展示对应单季数据。
- 单季派生数据在报告中展示，并用 `*` 标注由累计数反推。
- 预测、官方指引和情景假设只进入 `forecasts.csv`，不进入事实主表。
- 估值模块使用 `TTM PE`、`Adjusted TTM PE`、`Forward PE` 和 `PB`。
- 历史百分位输出 PE 和 PB 的 5 年、10 年百分位；样本不足时明确降级。
- 公开网页预测和券商预测先由 LLM 自检，确定不了再让用户复核。
- README 必须面向新用户，说明输入、触发、输出、降级行为和复核方式。
