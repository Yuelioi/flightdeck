---
status: obsolete
when_to_read: before changing flightdeck's git-mode inference, the Land Routine move, or any code that assumes a deck sitting inside a git repo is itself git-tracked
applies_to: [git, gitignore, no-git, land-routine, git-mv, commit, skills/preflight/protocol.md, skills/preflight/exit-ritual.md, flightdeck_init]
last_updated: 2026-06-09
resolved_by: skills/preflight/protocol.md §Rule resolution order（git 判定加 ignore 检查） + skills/preflight/exit-ritual.md landing Step0（land move 永远普通 mv）
---

# 被 gitignore 的 deck：git-mode 判定的接缝

## Signature
- symptom: `fatal: not under version control, source=flightdeck/specs/...`
- error_type: —
- where: Land Routine 的 move（`git mv`）+ landing 的 git/no-git 判定 + commit 步
- trigger: 在一个**外层有 git、但 `flightdeck/` 被单独 gitignore** 的项目上跑 landing 归档

## 症状/复现

用户在真实项目里把 `flightdeck/` 放进 `.gitignore`（deck 不进代码库历史，常见做法）。landing 归档一个 done spec 时：
1. `git mv specs/X.md archive/specs/X.md` → `fatal: not under version control`（文件被 ignore，git 不认）。
2. 退回手工 `mv` + 随后的 `flightdeck_index.py` regen 次序错位 → specs/INDEX 一时对不上 → **看起来像「脚本误报 already clean」**（实测脚本无 bug：临时 deck 上 flip→move→regen 全对、幂等也对）。
3. deck 实际是 no-git，命中老的 no-git 分支 → **写了 `archive/HISTORY.md`**（用户：「有 git 的项目还在用 HISTORY」）。
4. 上述即兴补救（git mv 失败、两次 regen、手工改两 INDEX、灌一大段 HISTORY/cockpit 散文）→ 一次 landing 烧 ~9k token。

## 根因

（assumption，不是脚本缺陷）git-mode 判定是**二元**的——「deck root（=`flightdeck/` 的父目录）有没有 `.git`」。它只问「外层是不是 git 仓」，**没建模「外层有 git、但 deck 子目录被 ignore」**这个最常见的真实场景。于是判定说「git」，`git mv`/`git add` 却对被 ignore 的文件失败，AI 只能在 git/no-git 之间即兴横跳。脚本被冤枉了——真凶在上游的 move + 判定。

## 修法/防回归

- **git 判定加 ignore 检查**：deck 走 git ⟺ 祖先有 `.git` **且** `git -C <deck> check-ignore .` 为空。被 ignore 的 `flightdeck/` 判为 deck 级 no-git（即便外层代码仓有 git）。
- **land move 永远普通 `mv`，绝不 `git mv`**：普通 mv 对被跟踪（随后 commit 自识别 rename）和 no-git 两种 deck 都成立。
- **顺带根治 HISTORY**：no-git 不再写任何流水账——`archive/` 文件本身 + `git log` 就是落地记录（standing decision，见 CHANGELOG 3.0「Removed」）。
- **别再把「脚本说 already clean」当脚本 bug**：先核 move 是否真成功、regen 次序是否对。脚本只读 frontmatter 生成行，是确定性的。

## Cases
- 2026-06-06 首次（来自某真实项目 YHFish 的 landing transcript：gitignored deck，git mv 失败 + 误写 HISTORY + 9k token）
