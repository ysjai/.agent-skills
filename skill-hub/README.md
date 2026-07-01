# SkillHub Skills

`skill-hub/` 存放从 SkillHub 下载的第三方 skills。

## 目录用途

- 作为 SkillHub skills 的本地缓存目录。
- 由 `/download-skills` 或 `/install-skills-*` 命令下载和更新。
- 源目录通常是 `skill-hub/<slug>/`，每个 skill 目录内包含 `SKILL.md`。

## 常用操作

- 下载但不安装：运行 `/download-skills`，选择 SkillHub 来源。
- 下载并安装：运行 `/install-skills-opencode`、`/install-skills-claude` 或 `/install-skills-codex`，选择 SkillHub 来源。
- 更新已下载内容：运行 `/update-skills`，选择 SkillHub 来源。

## 注意事项

- 这里的内容通常来自外部平台，安装前应确认来源可信。
- `skillhub CLI` 只在下载或更新 SkillHub skills 时需要；如果只使用本地自建或 Git 仓库来源，可以不安装。
- 已安装到平台目录的 skill 通常是指向这里的软链接，更新源目录后，重启对应平台即可加载新内容。
