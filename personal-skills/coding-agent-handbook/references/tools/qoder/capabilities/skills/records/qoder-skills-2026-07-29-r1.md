---
record_id: qoder-skills-2026-07-29-r1
tool: qoder
topic: skills
content_type: reference
learning_level: personal
evidence_class: official-fact
publication_status: unverified
applicability:
  release_channel: stable
  product_form: web
  platforms: [web]
  deployment: cloud
  verified_versions: [unversioned-docs-2026-07-29]
support_status: support-not-publicly-confirmed
support_evidence: null
last_verified: 2026-07-29
---
本 record 只记录 2026-07-29 官方在线文档快照中的插件与 Skill 资料。`unversioned-docs-2026-07-29` 不是供应商产品版本，不能作为任何客户端或生命周期的支持承诺。

> **FACT-qoder-skills-2026-07-29-r1-01**
> - 断言：Qoder Plugins 文档将 Skills 列为插件可包含的组件，并说明每个 Skill 是包含 YAML frontmatter 和 Markdown 正文的独立目录，其入口文件为 `SKILL.md`。
> - 适用范围（JSON）：`{"deployment":"cloud","platforms":["web"],"product_form":"web","release_channel":"stable","verified_versions":["unversioned-docs-2026-07-29"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-QODER-PLUGINS-001`，https://docs.qoder.com/qoder-plugins
> - 证据快照：`sources/evidence/SRC-QODER-PLUGINS-001/2026-07-29.md`，SHA-256 `f4260ed69b86c072831e1593ae34ae01f8db0c97889b521dd7a0944bb98b2bb7`

> **FACT-qoder-skills-2026-07-29-r1-02**
> - 断言：Qoder Plugins 文档说明 `description` 是 Qoder 判断何时调用 Skill 的关键字段，`name` 默认使用 Skill 目录名。
> - 适用范围（JSON）：`{"deployment":"cloud","platforms":["web"],"product_form":"web","release_channel":"stable","verified_versions":["unversioned-docs-2026-07-29"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-QODER-PLUGINS-001`，https://docs.qoder.com/qoder-plugins
> - 证据快照：`sources/evidence/SRC-QODER-PLUGINS-001/2026-07-29.md`，SHA-256 `f4260ed69b86c072831e1593ae34ae01f8db0c97889b521dd7a0944bb98b2bb7`

> **FACT-qoder-skills-2026-07-29-r1-03**
> - 断言：Qoder Plugins 文档区分跨项目分发的插件与单项目使用的 standalone skill，并将后者的位置说明为 `.qoder/skills`。
> - 适用范围（JSON）：`{"deployment":"cloud","platforms":["web"],"product_form":"web","release_channel":"stable","verified_versions":["unversioned-docs-2026-07-29"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-QODER-PLUGINS-001`，https://docs.qoder.com/qoder-plugins
> - 证据快照：`sources/evidence/SRC-QODER-PLUGINS-001/2026-07-29.md`，SHA-256 `f4260ed69b86c072831e1593ae34ae01f8db0c97889b521dd7a0944bb98b2bb7`

> **FACT-qoder-skills-2026-07-29-r1-04**
> - 断言：Qoder Plugins 文档的客户端支持矩阵在该文档快照中将 Skills (`SKILL.md`) 标为 Qoder Desktop、Qoder CLI、JetBrains Plugin 和 QoderWork 支持的组件。
> - 适用范围（JSON）：`{"deployment":"cloud","platforms":["web"],"product_form":"web","release_channel":"stable","verified_versions":["unversioned-docs-2026-07-29"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-QODER-PLUGINS-001`，https://docs.qoder.com/qoder-plugins
> - 证据快照：`sources/evidence/SRC-QODER-PLUGINS-001/2026-07-29.md`，SHA-256 `f4260ed69b86c072831e1593ae34ae01f8db0c97889b521dd7a0944bb98b2bb7`

## 手工练习

这不是已实测 Lab。先在隔离项目副本中只检查现有 `plugin.json`、声明的路径和每个 `SKILL.md` 的 frontmatter，再确认当前客户端的官方资料是否与该快照相符。不要把插件中的 Skill 与 standalone 位置混用，也不要根据目录存在推断自动发现、自动加载或所有客户端都有相同行为。

若要试用 Skill，应只使用无机密、无生产连接的样例，并在人工确认当前客户端的可用范围后再执行。
