# Personal Skills

`personal-skills/` 存放你自己创建和维护的本地 skills。

## 目录用途

- 放置个人自建、长期维护或实验中的 skills。
- 适合存放不依赖外部仓库发布节奏、需要快速迭代的工作流。
- 每个 skill 使用独立目录，例如 `personal-skills/my-skill/SKILL.md`。

## 当前内容

- `brainstorming/`：把需求和想法梳理成设计文档。
- `writing-plans/`：根据已批准设计文档或明确确认的无 spec 实现依据生成执行计划。
- `executing-plans/`：按设计文档和执行计划落地实现并验证验收标准；低风险单一任务可使用快速路径。
- `xiaomi-financial-tracker/`：小米财务跟踪相关 skill。
- `deck-kit/`：把内容做成单文件 HTML 演示片（1280×720），带翻页、缩略图目录、全屏放映，可替换与联合展示企业 logo。

其中 `brainstorming/`、`writing-plans/`、`executing-plans/` 是基于 `git-repo-skills/superpowers` 的本地定制版本。

## 添加新 skill

```bash
mkdir -p ~/.agent-skills/personal-skills/my-skill
```

然后在目录中创建 `SKILL.md`：

```markdown
---
name: my-skill
description: 说明这个 skill 做什么，以及什么时候应该触发。
---

# My Skill

具体使用说明。
```

## 安装方式

运行对应平台安装命令，并选择 `personal-skills` 来源：

- OpenCode：`/install-skills-opencode`
- Claude Code：`/user:install-skills-claude`
- Codex：通过 OpenCode / Claude Code 的安装命令安装到 Codex，或手动链接到 `~/.agents/skills/`
- WorkBuddy：软链到 `~/.workbuddy/skills/`

```bash
ln -s ~/.agent-skills/personal-skills/<skill-name> ~/.workbuddy/skills/<skill-name>
```

用软链而不是复制：改仓库里的文件，WorkBuddy 侧立即生效；两边始终是同一份。

## 注意事项

- 目录名、frontmatter 中的 `name`、安装后的链接名建议保持一致。
- OpenCode 和 Codex 可以发现嵌套目录中的 skills，但 Claude Code 更适合扁平结构；为了跨平台稳定，个人 skills 默认保持 `personal-skills/<skill-name>/SKILL.md` 结构。
- 如果多个 skills 属于同一个工作流，优先用 README 说明分组关系，不要轻易移动物理目录，以免破坏既有软链接。
