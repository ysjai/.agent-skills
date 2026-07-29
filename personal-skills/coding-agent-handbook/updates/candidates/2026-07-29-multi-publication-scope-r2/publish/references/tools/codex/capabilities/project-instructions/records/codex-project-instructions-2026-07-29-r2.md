---
record_id: codex-project-instructions-2026-07-29-r2
tool: codex
topic: project-instructions
content_type: reference
learning_level: personal
evidence_class: official-fact
publication_status: published
applicability:
  release_channel: stable
  product_form: cli
  platforms: [macos, linux, windows]
  deployment: local
  verified_versions: [rust-v0.145.0]
support_status: support-not-publicly-confirmed
support_evidence: null
last_verified: 2026-07-29
---

## 官方事实

> **FACT-codex-project-instructions-2026-07-29-r2-01**
> - 断言：以默认项目根标记 `.git` 识别项目根时，Codex 从项目根到当前工作目录收集 `AGENTS.md`。
> - 适用范围（JSON）：`{"deployment":"local","platforms":["macos","linux","windows"],"product_form":"cli","release_channel":"stable","verified_versions":["rust-v0.145.0"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-CODEX-AGENTS-001`，https://raw.githubusercontent.com/openai/codex/rust-v0.145.0/codex-rs/core/src/agents_md.rs
> - 证据快照：`sources/evidence/SRC-CODEX-AGENTS-001/2026-07-29.md`，SHA-256 `d0e60a1f7bcd4e9a41f8634ff120354ea98e4a7fac20ead843f3903e6528ebc8`

> **FACT-codex-project-instructions-2026-07-29-r2-02**
> - 断言：同一目录同时存在 `AGENTS.md` 和 `AGENTS.override.md` 时，`AGENTS.override.md` 优先。
> - 适用范围（JSON）：`{"deployment":"local","platforms":["macos","linux","windows"],"product_form":"cli","release_channel":"stable","verified_versions":["rust-v0.145.0"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-CODEX-AGENTS-001`，https://raw.githubusercontent.com/openai/codex/rust-v0.145.0/codex-rs/core/src/agents_md.rs
> - 证据快照：`sources/evidence/SRC-CODEX-AGENTS-001/2026-07-29.md`，SHA-256 `d0e60a1f7bcd4e9a41f8634ff120354ea98e4a7fac20ead843f3903e6528ebc8`

> **FACT-codex-project-instructions-2026-07-29-r2-03**
> - 断言：该实现的默认项目根标记是 `.git`，并允许配置备用指令文件名。
> - 适用范围（JSON）：`{"deployment":"local","platforms":["macos","linux","windows"],"product_form":"cli","release_channel":"stable","verified_versions":["rust-v0.145.0"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-CODEX-AGENTS-001`，https://raw.githubusercontent.com/openai/codex/rust-v0.145.0/codex-rs/core/src/agents_md.rs
> - 证据快照：`sources/evidence/SRC-CODEX-AGENTS-001/2026-07-29.md`，SHA-256 `d0e60a1f7bcd4e9a41f8634ff120354ea98e4a7fac20ead843f3903e6528ebc8`

## 手工验证练习（未实测运行时）

本 record 是 reference，不是 Lab：没有可归属的 Codex 运行时实测结果。仅在临时、无凭证、非生产的 Git 仓库中进行手工验证。建立根目录、嵌套目录和工作目录，并分别放置下列文件；文件内容仅使用可识别的非敏感文本。

```text
isolated-repo/.git/
isolated-repo/AGENTS.md
isolated-repo/component/AGENTS.md
isolated-repo/component/AGENTS.override.md
isolated-repo/component/work/
```

使用本机已确认版本的 Codex 和既有获批调用方式，在 `component/work/` 发起无副作用请求，要求其仅说明所读取的项目指令来源。手工记录实际版本、启动位置、工具显示或回复中可观察到的文件信息，以及 override 文件出现时的差异。文件布局本身不能证明运行时行为，也不得把未记录的输出当作通过结果。

## 手工验收与清理

仅当记录可与本 record 的适用范围、上述三个事实块及本机版本对应时，才将观察结果用于本地学习。验证结束后删除整个临时 Git 仓库和任何非必要日志；不要在生产仓库、含真实凭证的目录或共享工作树中进行该练习。

## 来源与边界

最后核对：2026-07-29。来源是 `SRC-CODEX-AGENTS-001`。本 record 不建立自动发现、备用文件名的具体配置接口、跨版本兼容性或支持生命周期结论。
