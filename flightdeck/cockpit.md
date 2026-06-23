# Cockpit — flightdeck (the flightdeck project itself)

Updated: 2026-06-24 · 月离 · Stage: 子计划 #1/5「协议 authoring」**执行完毕** —— 三份草稿落 `work/ai-native-redesign/`（micro-core 2989 chars ≤ budget、deep protocol 五节、coverage-check 33 类零孤儿），全部验证绿、各自 commit；plan 标 done 待 land。plan 3（旧 stage/land）仍 staged 待 land

Focus: AI-native 重设 brainstorm（少结构·多信任 AI）→ `specs/2026-06-23-ai-native-redesign.md`；stage/land plan 3 暂 parked（staged 待 land）

Pointers: 配置 → rules.md · 约定/偏好 → CLAUDE.md · artifact → 各 folder INDEX · 历史 → archive/

## In Progress

<!-- AUTO:inprogress -->
- [2026-06-22-stage-land-lifecycle.md](specs/2026-06-22-stage-land-lifecycle.md) — Two-phase lifecycle replacing the checkpoint/soft-landing/full-landing split: st…
- [2026-06-23-ai-native-redesign.md](specs/2026-06-23-ai-native-redesign.md) — 少结构·多信任 AI 重设——砍流程/迁移/冗余三痛。两动词 preflight(手动进场)/persist(自动 turn-end),手动命令仅 prefli…
<!-- /AUTO -->

## Staged (awaiting land)

<!-- AUTO:staged -->
### Done (awaiting land)
- [2026-06-23-stage-land-model-one-pass.md](plans/2026-06-23-stage-land-model-one-pass.md) — Rewrite the three-tier (checkpoint/soft-landing/full-landing) + signal 1/2/3 mod…
- [2026-06-24-ai-native-protocol-authoring.md](plans/2026-06-24-ai-native-protocol-authoring.md) — Author the new preflight skill's two-layer protocol — a ≤3000-char always-loaded…
<!-- /AUTO -->

## Next

- **AI-native 重设 — 设计收敛完毕,进执行** — spec 已重写成单一线性决策记录(`specs/2026-06-23-ai-native-redesign.md`):**两目录** work/(在飞)+ knowledge/(持久,按域,类型靠标题行)· **两命令** preflight(进场)+ walkaround(审计)· **机械全砍**(零 YAML、无 INDEX、无 status;路由头 `SUMMARY`/`READ WHEN`/`RECHECK WHEN`,`---` 收尾)· **协议定死在插件**(微核心进场载 + 深层 `skills/preflight/protocol.md` 按需;不进 CLAUDE.md/不注入)· **冷内容**(未定/过期/通用)进 `~/.flightdeck`。位置即状态(active/done),细粒度状态走 cockpit。外审 3 份(`tmp/ds·claude·gpt`)已三拣,4 处澄清(load≠inject、冷层 mtime 无 git 兜底、细粒度状态、walkaround 表述)已折进 spec,无推翻设计。
  - **✓ 子计划 #1/5「协议 authoring」已执行完毕**(plan `2026-06-24-ai-native-protocol-authoring.md` 标 done)。产出 3 草稿在 `work/ai-native-redesign/`:`micro-core.md`(2989 chars,**注**:spec 附录初稿 3253>3000 超预算,已逐字紧缩 ~264 字到 budget 内,4 不变量/双动词/depth 指针全保留——**#4 wiring 时从 `work/micro-core.md` 接,别从 spec 附录**)、`protocol.md`(五节,与 depth 指针 1:1)、`coverage-check.md`(33 类 3.0 规则→新形态 disposition,零孤儿)。commits `01ebfbf`/`e78e3b1`/`237fa0a`。
  - **▶ 下一步**:① 人读 3 草稿英文散文(tone+sense,= plan `verify:` 行)→ 满意后可 land(plan #1 + 仍 staged 的 plan 3);② 再挑下个子计划。**其余 4 子计划**:② 迁移脚本(等新形态实体,草稿已是协议实体)· ③ derive-listing 小工具 · ④ 杀旧 skill/重连插件(把草稿接成真 skill)· ⑤ 产品化(缓)。
- （**parked**，focus 已切走）**review + land plan 3** — 通读 6 文件英文散文（`exit-ritual`/`protocol`/`landing`/`status`/`preflight`(SKILL+templates+folder-semantics)/`bootstrap`）确认 tone+自洽；满意后 `/flightdeck:landing` → 归档 plan 3 + graduate spec `2026-06-22-stage-land-lifecycle` → `docs/`。验证 = plan `verify:` 行；grep 旧术语已清零（仅留 2 处「not three tiers / no checkpoint ritual」negative mention）。**Downstream**（未做，plan 末「Downstream」节）：`docs/session-flow.md` 等 deck 内文档 + README/CHANGELOG 的 soft-landing 提及，land 时会被 stale-flag。
- （**parked**）本地缓存已同步当前构建（`build_stamp` `current`），多日 dogfood 中；跨项目 `--fanout` live 实证待做（需第二个消费 deck）→ `checklists/local-plugin-testing.md`。

## Key Context

- **#4 wiring 接 `work/ai-native-redesign/micro-core.md`(2989 chars 紧缩版),非 spec 附录初稿(3253>3000 超 budget)** —— 微核心硬上限 3000 chars(`wc -m`),附录逐字版超标,已紧缩；附录是历史底稿,实体真相 = work/ 三草稿。

## Pending Review

- ⚠待复核 **AI-native 协议 authoring 3 草稿**(子计划 #1/5,commits `01ebfbf`/`e78e3b1`/`237fa0a`,均**发布面英文散文**):`work/ai-native-redesign/micro-core.md`(≤3000-char 微核心)、`protocol.md`(深层五节)、`coverage-check.md`(3.0→新形态 disposition 表)。**复核英文措辞 + 微核心是否真装下全部 §形态 决定 + coverage 表 disposition 是否服人**;满意即可 land(graduate 时随设计走)。验证 = plan `verify:` 行。
- ⚠待复核 **plan 3 stage/land 重写**（6 commits `89baf18`→`e85bd26`）：三层/signal 模型 → stage/land 两段，改了 6 个发布面英文散文（`exit-ritual` 模型源 + `protocol`/`landing`/`status`/`preflight`/`bootstrap` 引用）。**复核英文措辞 + 跨文件自洽**；满意即 land（graduate spec）。详 `plans/2026-06-23-stage-land-model-one-pass.md`。
- ⚠待复核 `docs/script-layer.md`：脚本层文档未补 `--register/list/prune-consumers` + `sync_status` 这批 flag；doc 仍 `status: stale`，下次补齐。
- [marker 自带化 英文散文]（已 commit `1348619` + 同步本地缓存）本会话翻 vendorable-master「自带 marker+stub」约定 + `marker-missing` 安全网,改了**发布面英文散文**:`skills/sync/SKILL.md`（boundary-marker 节 + mode-A 状态表 + mode-C re-stamp + 报告 banner）、`skills/walkaround/SKILL.md`（Audit 15 WARN 文案）、`skills/preflight/protocol.md` + `templates.md`（旧「母库无 marker」断言翻转）。canonical stub 措辞 = `## Project overrides` + 斜体注（用户已选 B）。**复核英文措辞是否合意**;设计真相 → `docs/shared-knowledge-sync.md`。

## Hanging Tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
