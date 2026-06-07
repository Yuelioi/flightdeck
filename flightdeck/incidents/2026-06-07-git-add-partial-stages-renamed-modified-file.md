---
status: active
when_to_read: 用 git mv 重命名/归档一个还要改内容的文件后、用 git add 暂存提交前（尤其 Land Routine 把 done 件 git mv 进 archive/ 再翻 status 时）
applies_to: [git, git-mv, staging, rename, RM, R100, land-routine, archive, commit, skills/landing]
last_updated: 2026-06-07
resolved_by:
---

# git add 暂存 RM 文件只捕获 R100 重命名、漏工作区内容半边

## Signature
- symptom: `git status` 显示 `RM <path>`（index 里重命名 + 工作区又改了内容）；commit 后该文件却又变回 ` M`——只提交了纯重命名（`R100`），内容改动漏在工作区
- error_type: —
- where: Land Routine / 归档移动（`git mv` 一个 done 工件进 `archive/` 再翻 `status: done`）后的 `git add` + commit
- trigger: 对同一文件同回合既 `git mv`（重命名，自动暂存）又改内容（status/注记），随后用 `git add <dir>` 或宽匹配只暂存了重命名部分

## 症状/复现

1. `git mv flightdeck/specs/x.md flightdeck/archive/specs/x.md`（重命名被暂存）。
2. 再编辑该文件内容：`status: active → done`、加 Superseded 注记、修 `implements` 路径。
3. `git status --short` 显示 `RM flightdeck/.../x.md`——`R`=index 里重命名已暂存，`M`=工作区内容改动**未**暂存（两个半边）。
4. `git add flightdeck/archive/`（或只 add 了部分路径）后 commit。
5. commit 后 `git status` 该文件又冒出来变 ` M`：纯重命名（`R100`，100% 相同内容）进了 commit，**内容半边没进**，归档件仍标 `status: active`。

本仓实例：相位3 收编 `ff7868e` 只提交了 3 个归档件的 `R100` 重命名，status active→done + 注记漏掉，靠补提交 `7b4fcc2` 收尾。

## 根因

`RM` 是**两个独立暂存条目**：rename（已 staged）+ working-tree modification（未 staged）。`git diff --cached` 显示 `R100` 会让人误以为「这文件已经完整进暂存区」，实际只暂存了重命名那半边。`git mv` 只暂存重命名，之后的内容编辑是新的未暂存改动，必须再 `git add` 一次。`R100` 的 `100` = 相似度 100%，**正是因为内容半边没暂存**才会 100% 相同——它本身就是「漏了内容」的信号，不是「已完整」的信号。

## 修法

- 归档+改内容是**同一逻辑改动**：`git mv` 后**先把内容编辑也 `git add`**，再看 `git diff --cached` 确认显示的是 `R<NN>`（NN<100，带内容差）或 rename+后续 modify 都在，而非纯 `R100`。
- 提交前用 `git status --short` 扫一遍：**任何 `RM` / `MM` 行都意味着该文件有未暂存的半边**，别只信 `git diff --cached --name-status`。
- commit 后再 `git status` 复核工作区是否「干净」；若刚提交的文件又冒出 ` M`，就是半提交了，补一次 add+commit（或 amend，本仓约定优先补提交）。
- 经验法则：**`R100` 出现在你「明明改了内容」的文件上 = 内容漏暂存**。

## Cases
- 2026-06-07 首次：相位3 收编归档 3 个工件，`git mv` 后只暂存了 `R100` 重命名，status→done + Superseded 注记漏在工作区；`ff7868e` 半提交，`7b4fcc2` 补全。
