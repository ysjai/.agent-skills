# 更新日志

## 2026-07-29-multi-publication-scope-r2

已发布修正候选，替换可变入口并新增 11 个 r2 records。

- Codex r2 records 将已完成受控发布这一状态明确写为 `publication_status: published`；r1 records 保留为不可变历史记录。
- Qoder r2 records 同样使用 `publication_status: published`，并将 `unversioned-docs-2026-07-29` 限定为官方文档快照路由标签。Qoder 的发行通道、产品形态、平台和部署范围均为 `unspecified`，能力状态仍为 `unverified`，支持状态仍为 `support-not-publicly-confirmed`。
- 所有 capability indexes 将 r1 标记为 `superseded`，并链接 r2 current records；工具总览、版本索引、共享资料、handbook 索引和评估元数据不再把已发布资料表述为未审批候选。
- 本次不新增来源或 evidence，所有官方事实继续使用首发 release 中的正式 source/evidence snapshot。

限制：Qoder 文档快照不是供应商产品版本，也不建立任何特定客户端、平台、部署或生命周期支持结论；Codex `rust-v0.145.0` 也没有在本 handbook 中获得生命周期支持结论。
