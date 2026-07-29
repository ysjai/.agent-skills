# Candidate 2026-07-29-multi-publication-scope-r2

## 核对范围

修正已发布 bootstrap handbook 的发布状态表述和 Qoder 在线文档快照的适用范围。范围包括 Codex 与 Qoder 的当前 capability records、能力索引、工具入口、共享资料、评估元数据和更新日志；不重新核对产品行为，也不修改任何 r1 record、已有 source registry、evidence snapshot、release manifest 或完整性 ledger。

## 已查来源

- 已发布 `SRC-CODEX-AGENTS-001`、`SRC-CODEX-RELEASE-001`、`SRC-CODEX-SECURITY-001`、`SRC-CODEX-SKILL-001`、`SRC-CODEX-SUBAGENT-001` 及其 2026-07-29 evidence snapshots。
- 已发布 `SRC-QODER-RULES-001`、`SRC-QODER-CONTEXT-001`、`SRC-QODER-HOOKS-001`、`SRC-QODER-PLUGINS-001` 及其 2026-07-29 evidence snapshots。

## 发现与拟议变更

- 首发 r1 records 已经由 release manifest 发布，但其 `publication_status` 仍为 `unverified`，混淆了发布状态与能力或支持状态。为保持已发布 record 不可变，本候选为每个现有能力新增 published r2 record，并在可变 capability index 中将 r1 标为 `superseded`。
- Qoder r1 records 和索引将在线文档快照错误限定为 `stable/web/[web]/cloud`。已发布官方快照没有为这些 records 建立产品版本、发行通道、客户端、平台、部署或生命周期的可绑定范围。Qoder r2 因此仅以 `unversioned-docs-2026-07-29` 路由，并将其余四个范围字段标为 `unspecified`，同时保持 `support-not-publicly-confirmed` 和能力 `unverified`。
- 所有可变入口改为描述已发布 handbook，并将当前链接和评估期望 records 指向 r2；不把文档快照表述为 Qoder 产品版本或支持承诺。

## 受影响 Records 与版本覆盖

- Codex：五个 `rust-v0.145.0` r2 records，r1 保留为历史 record。
- Qoder：六个 `unversioned-docs-2026-07-29` 文档快照 r2 records，r1 保留为历史 record。
- 不新增 source 或 evidence；所有 r2 FACT 复用已发布且哈希匹配的正式 evidence snapshot。

## 未解决项与风险

- Qoder 仍没有已核实的供应商产品版本或支持生命周期。`unversioned-docs-2026-07-29` 仍不是产品版本，不能用于推断任意客户端的当前支持状态。
- Codex `rust-v0.145.0` 的 release 身份已登记，但也没有公开生命周期结论；本候选不改变该限制。
- 发布前仍须对本候选精确 manifest hash 取得人工批准；未经批准不得复制任何 r2 record 或可变资料。
