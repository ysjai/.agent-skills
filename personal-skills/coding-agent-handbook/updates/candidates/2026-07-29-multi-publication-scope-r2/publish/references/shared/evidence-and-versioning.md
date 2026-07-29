# 证据与版本

## 目的

本文件说明已发布 handbook 如何区分事实、建议、版本、审批与发布。它解释资料模型，不重复任何供应商产品行为；工具事实只存在于各自的不可变 record。

## 术语与分类

| 名称 | 含义 | 使用边界 |
| --- | --- | --- |
| `FACT` | record 中可逐条核对的产品行为断言，绑定适用范围、来源、定位、证据快照和快照哈希。 | 只在 `official-fact` record 中使用，不能由文档目录或共享建议替代。 |
| `source` | 具有稳定 `source_id` 的来源登记，记录发布主体、类别、规范性、URL 和核对日期。 | 来源清单本身不证明每一项产品断言。 |
| `evidence` | 与单个 source 对应的人工核对快照，记录定位、访问时间、核对范围和摘要哈希。 | 正式 evidence 位于 `sources/evidence/`；候选 evidence 只有获批后才可发布。 |
| `record` | 带 frontmatter 的版本化学习条目，包含事实或明确分类的建议。 | 发布后字节不可变；事实或发布状态变化要创建新 record。 |
| `index` | 工具、版本或能力的路由页，维护适用范围、状态、生命周期和 record 链接。 | 不复制产品行为事实，不从缺失资料推导“不支持”。 |
| `manifest` | 候选中每个文件的路径、目标路径与 SHA-256，以及整体规范化哈希。 | 是人工审批的完整边界；任何内容变化都必须重算。 |
| `approval` | 人工对候选 ID 与精确 manifest hash 的明确决定。 | 计划批准、agent 判断或模糊“继续”不等于 approval。 |
| `release` | 只复制已批准 manifest 所列目标文件的受控发布结果。 | 未发生 approval 和 release 前，候选不是正式知识。 |

## 事实与建议的显式分类

| 分类 | 可写内容 | 必要说明 |
| --- | --- | --- |
| `official-fact` | 有逐条官方证据的产品行为。 | FACT、适用范围、source、evidence、hash 和最后核对日期。 |
| `established-practice` | 有可复现实践证据支撑的工程方法。 | 适用条件、收益、代价和实践证据或可复现范围。 |
| `local-practice` | 明确属于某组织或仓库的规则。 | 适用组织/仓库、所有者和本地审批边界。 |
| `experimental-guidance` | 尚未有足够实践证据的建议。 | 假设、适用条件、预期收益、代价、风险和验证方法。 |

本 handbook 的共享工程方法属于 `experimental-guidance`，因为没有登记第三方实践来源。它们不能被回答为供应商规定、广泛已证实的成熟实践或默认政策。

## 版本范围与未知状态

回答工具问题时，先报出 record 的 `release_channel`、`product_form`、`platforms`、`deployment`、`verified_versions` 和最后核对日期。版本文本按来源原样保存，不从字符串格式推断兼容性。

- `unverified`：本地资料不能在适用范围内确认能力状态；它不表示不支持。
- `not-covered`：本地资料未覆盖该主题或版本；它不表示不支持。
- `officially-not-supported`：仅在存在范围兼容的官方否定 FACT 时使用。
- `support-not-publicly-confirmed`：来源未建立公开支持生命周期；不能推断仍受支持。

Qoder 当前的路由标签是 `unversioned-docs-2026-07-29`。它仅指向 2026-07-29 的官方在线文档快照，不是 Qoder 供应商发布的产品版本、稳定版承诺、客户端范围或生命周期信息。使用 Qoder 条目前必须先确认实际客户端和版本；在本 handbook 范围外需要重新核对官方资料。

## 候选到发布的可追溯链

1. 将核对过的来源登记为 `source`，并保存候选 `evidence`。
2. 以 FACT 或明确分类建议写入 record；由 index 链接 record，不复制事实。
3. 为 `candidate.md`、每个 evidence 和每个 `publish/` 文件生成排序的 manifest 条目及 SHA-256。
4. 人工明确批准候选 ID 和当前 manifest hash 后，才允许受控发布。
5. 发布仅复制 manifest 中列出的 targets；已发布 record 再由完整性清单锁定。
6. 事实、证据或待发布文件任一变更都会改变 manifest hash，必须重新审批；不能复用旧 approval。

本流程不允许以候选、未完成验证、计划批准或自动化脚本替代人工内容审批。
