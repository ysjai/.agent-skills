# Git Repo Skills

`git-repo-skills/` 存放通过 Git 仓库引入的 skills。

## 目录用途

- 管理外部 Git 仓库中的 skills。
- 支持作为 git submodule 跟踪，也支持手动 clone。
- 适合存放第三方维护、需要定期同步上游的 skill 集合。

## 典型结构

```text
git-repo-skills/
├── anthropics-skills/
├── superpowers/
└── <repo>/
```

每个仓库内部可能是单个 skill，也可能包含多个 skills。安装命令会递归扫描仓库中的 `SKILL.md`。

扫描时会忽略 `.git/`、`template/`、`examples/` 以及常见平台或编辑器专用目录（如 `codex/`、`cursor/`、`gemini/`、`kiro/`、`vscode/`）。若同名 skill 重复出现，只保留首个并报告重复项，避免整组安装时冲突。

## 添加仓库

推荐通过安装命令添加：

- OpenCode：`/install-skills-opencode`，选择 `git-repo-skills`
- Claude Code：`/user:install-skills-claude`，选择 `git-repo-skills`
- Codex：通过 OpenCode / Claude Code 的安装命令安装到 Codex，或手动链接到 `~/.agents/skills/`

也可以手动添加子模块：

```bash
cd ~/.agent-skills
git submodule add <repo-url> git-repo-skills/<repo-name>
git submodule update --init git-repo-skills/<repo-name>
```

## 更新仓库

运行 `/update-skills`，选择 `git-repo-skills` 来源。

更新逻辑会优先同步子模块；如果发现手动 clone 且含 `.git` 的目录，会提示是否注册为子模块。

## 平台安装差异

- OpenCode：支持整组安装，也支持单独安装某个 skill。
- Claude Code：安装时必须展开为多个独立 skill 链接，因为它偏好 `skills/<name>/SKILL.md` 的扁平结构。
- Codex：支持递归发现嵌套 `SKILL.md`，也支持整组安装。

## 注意事项

- 这里只放 Git 仓库目录和本 README；安装/更新命令会忽略非目录文件。
- 不要直接修改第三方仓库内容，除非你打算维护自己的 fork。
- 更新子模块前，先确保 `~/.agent-skills` 工作区没有未提交的重要改动。
