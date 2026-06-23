# ⚠ skill prose links into the dogfood deck
SUMMARY: A markdown link / relative path inside skills/ prose can resolve into this dogfood deck instead of the user's — and it ships to every user.
READ WHEN: before adding a markdown link or relative path inside any skills/ prose
---

## Signature
- symptom: `skill 散文里的相对链接 ../../docs/why-no-hooks.md 从 skills/preflight/ 解析到仓库根 docs/（无此文件）；真正的文件在 dogfood deck flightdeck/docs/ 下`
- error_type: dangling-link
- where: skills/**（SKILL.md / protocol.md / exit-ritual.md / templates.md / folder-semantics.md）
- trigger: 在 shipped skill 散文里写一条指向 deck 内容（flightdeck/docs/ 等）或深度算错的相对链接

## 症状/复现

写 checkpoint 的 canonical 定义时，在 `skills/preflight/exit-ritual.md` 插了
`[docs/why-no-hooks.md](../../docs/why-no-hooks.md)`。从 `skills/preflight/` 解析，
`../../docs/` = **仓库根** `docs/`（只有 architecture/comparison/philosophy/README），
没有 `why-no-hooks.md`。该文件其实在 dogfood deck 的 `flightdeck/docs/why-no-hooks.md`。
质量评审才抓出这条死链。

## 根因

（assumption，非粗心）：我把 `skills/` 当成能自由引用本仓库任何文件——但 `skills/` 是
**shipped 产物**，用户安装后它在 plugin 缓存里运行，用户项目里**没有** `flightdeck/docs/`
（那是本仓库自己的 dogfood deck，记录"维护 flightdeck 工具"的内部知识）。于是任何从
shipped skill 指向 `flightdeck/…` 或算错深度的相对链接，对**每个真实用户都是悬空链**。

## 修法

- shipped skill 散文里的链接**只许指向 `skills/` 内部**（相对路径在 skills 树内闭合，
  如 `../preflight/exit-ritual.md#anchor`）。
- 要引 deck 才有的理由（why-no-hooks 之类），**别深链 deck**——把理由**内联成散文**
  （"consistent with flightdeck's deliberate no-startup-hooks design"），或指向 shipped
  的公开文档（仓库根 `docs/`）。
- 写完自检：对新加的每条 skill 链接，确认目标在 `skills/` 树内、相对深度正确；
  `flightdeck/…` 路径绝不出现在 `skills/` 散文里。

## Cases
- 2026-06-06 首次（checkpoint 特性 exit-ritual.md 的 why-no-hooks 死链，评审拦下）
