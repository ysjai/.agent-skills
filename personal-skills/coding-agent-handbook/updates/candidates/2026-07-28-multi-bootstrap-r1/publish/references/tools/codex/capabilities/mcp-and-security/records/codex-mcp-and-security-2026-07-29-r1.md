---
record_id: codex-mcp-and-security-2026-07-29-r1
tool: codex
topic: mcp-and-security
content_type: reference
learning_level: team
evidence_class: official-fact
publication_status: unverified
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

> **FACT-codex-mcp-and-security-2026-07-29-r1-01**
> - 断言：核对的配置 schema 包含 `approval_policy` 与 `sandbox_mode` 两个配置概念。
> - 适用范围（JSON）：`{"deployment":"local","platforms":["macos","linux","windows"],"product_form":"cli","release_channel":"stable","verified_versions":["rust-v0.145.0"]}`
> - 最后核对：2026-07-29
> - 证据：`SRC-CODEX-SECURITY-001`，https://raw.githubusercontent.com/openai/codex/rust-v0.145.0/codex-rs/core/config.schema.json
> - 证据快照：`sources/evidence/SRC-CODEX-SECURITY-001/2026-07-29.md`，SHA-256 `e74f9684f263232c366c14210f17d8a13c2cfcec8cc6b14a64a9c695d540a65f`

## 最小权限建议（非产品事实）

把审批和沙箱视为需要保留的安全边界：仅授予完成当前任务所需的最小文件、网络和工具权限；对每项 MCP 或外部连接分别审查其数据范围；在引入凭证前确认存储、日志与撤销路径。不要把本 record 用作绕过审批、扩大网络访问、解除沙箱或传递真实凭证的依据。

## 手工语法检查练习（未执行网络）

在隔离、无凭证、非生产目录创建仅含占位字符串的配置片段。该片段只用于 TOML 语法检查，不应被加载为真实配置：

```toml
approval_policy = "<仅在本机 schema 中核对的值>"
sandbox_mode = "<仅在本机 schema 中核对的值>"
```

可使用本机 Python 标准库的 `tomllib.loads()` 读取该文本，并只将“能够解析”为语法验收。不得启动 Codex、连接 MCP 服务器、发起网络请求、写入真实配置或提供任何密钥。解析成功不证明占位值受运行时接受，也不证明其安全效果。

## 来源与边界

最后核对：2026-07-29。来源是 `SRC-CODEX-SECURITY-001`。本 record 没有 MCP 服务器配置、认证、网络访问、审批取值、沙箱取值、默认值或组合效果的官方事实；这些问题须在目标版本的官方资料中另行核对。
