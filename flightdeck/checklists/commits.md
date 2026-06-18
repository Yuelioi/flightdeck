---
status: active
synced: true
last_updated: 2026-05-29
when_to_read: before writing a commit message / staging files / preparing a PR
applies_to: [commit, git, staging, message, push, pr]
portable: true   # §通用 部分项目无关; §项目覆盖 是本仓库专属, 移植时整段替换
---
# Commits Playbook

写 commit / 整理提交时**前置**读这份.

依据:

- Conventional Commits 1.0.0 ([https://www.conventionalcommits.org/](https://www.conventionalcommits.org/))
- Chris Beams《How to Write a Git Commit Message》([https://cbea.ms/git-commit/](https://cbea.ms/git-commit/))

---

## 通用 (项目无关)

### 1. 格式: `type(scope): subject`

```
feat(auth): add refresh-token rotation

老 access token 过期后客户端被强登出. 引入 refresh token
轮换, server 端单次使用 + 失效旧 token.

BREAKING CHANGE: /login 响应去掉 token 字段, 改 accessToken + refreshToken
```

**type**(必填):

| type         | 用于                  |
| ------------ | --------------------- |
| `feat`     | 新功能                |
| `fix`      | 修 bug                |
| `refactor` | 不改行为的重构        |
| `perf`     | 性能优化              |
| `docs`     | 仅文档                |
| `test`     | 仅测试                |
| `build`    | 构建系统 / 依赖       |
| `ci`       | CI 配置               |
| `chore`    | 杂项 (不进上述任何类) |
| `revert`   | 回滚某 commit         |

- **scope**(可选): 受影响的模块/包, e.g. `fix(parser):`. 没有明确单一模块就省略.
- **BREAKING CHANGE**: 破坏性变更在 body 起一段 `BREAKING CHANGE: ...`, 或 type 后加 `!` (`feat!:`).

### 2. Subject 行

- **祈使句现在时**: "add X" / "fix Y", 不是 "added" / "adds" / "fixing". (判据: 补全成 "If applied, this commit will ___".)
- **`type:` 后小写开头**, 句尾**不加句号**.
- **≤50 字符** 为佳 (硬上限 72). 一句话说不完 → 改动可能不原子, 见 §4.

### 3. Body (需要时才写)

- 跟 subject **空一行**隔开.
- **72 字符折行**.
- 讲 **what & why**, 不讲 **how** —— how 看 diff 就知道, 但"为什么这么改 / 解决什么问题 / 取舍了什么"是 diff 表达不出的.
- subject 已经说清的小改动 (typo / 显然的 fix) 不必硬写 body.

### 4. 原子提交

- **一个 commit = 一个逻辑改动**. 能用 "and" 描述 → 多半该拆.
- 重构和功能改动分开提交 (review 时一眼看清哪些是行为变更).
- 不把"顺手"的无关改动 (格式化 / 重命名 / 清理) 卷进功能 commit.

### 5. 不带 AI 署名

不写 `Co-Authored-By: <AI>`, 不写 `🤖 Generated with ...`. 提交前 `git log` 扫一眼历史风格对齐.

---

## 项目覆盖 (本仓库专属)

### 双 shell：多行 commit message 别串 shell

本仓库同时挂 **Bash** 工具和 **PowerShell** 工具. 给原生命令(`git commit` 等)传多行串前, 先认清选的工具是哪个 shell:

- **PowerShell 工具** → here-string `@'...'@`(结束 `'@` 必须顶列零缩进).
- **Bash 工具** → 真 heredoc(`git commit -F - <<'EOF' … EOF`)或 `-F <file>`; **别用 `@'...'@`** —— bash 没有 here-string, `@` 会当字面量混进 subject(`@ chore: …`).
- 最稳, 跨 shell 通用: 把信息写进文件, `git commit -F <file>`.

→ 错题本 [archive/incidents/powershell-herestring-in-bash-tool.md](../archive/incidents/powershell-herestring-in-bash-tool.md)(已 3 次, 由 promotion gate 升级到此后退役归档).

### 暂存前扫 `RM`/`MM`（重命名+内容改动）

`git mv` 重命名文件后再编辑内容，`git status --short` 会显示 `RM`（index 已暂存重命名、工作区内容未暂存）；`R100` = 内容改动**未暂存**（只提交了纯重命名）。**提交前扫一遍 `RM`/`MM` 行，对命中的文件再 `git add <file>` 暂存内容**，直到 `git status --short` 干净（或只剩预期的未跟踪文件）再 commit。
