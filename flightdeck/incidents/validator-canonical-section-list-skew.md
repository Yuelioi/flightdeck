---
status: active
when_to_read: 改 cockpit 的 canonical section 集合(增删/改名/调 AUTO marker)之前,或新增任何「脚本/skill 硬编码镜像了 templates.md/index 真相」的清单时
applies_to: [scripts/flightdeck_conform.py, scripts/flightdeck_conform.js, skills/walkaround/SKILL.md, skills/preflight/templates.md, scripts/flightdeck_index.py]
last_updated: 2026-06-23
resolved_by:
---

# Validator canonical-section list skews from templates/index

## Signature
- symptom: cockpit 缺一个 canonical section（如 `## Staged (awaiting land)`），但 walkaround Audit 16 + `conform --check` + `index --check` 全报 clean，无人检出
- error_type: —
- where: scripts/flightdeck_conform.py `COCKPIT_SECTIONS` / scripts/flightdeck_conform.js / skills/walkaround/SKILL.md `Audit 16`
- trigger: 往 cockpit 加/改一个 canonical section（或任何「真相在 templates.md/index、却被脚本或 skill 散文硬编码成镜像清单」的集合），只改真相源、漏改下游硬编码拷贝

## Symptom / repro

隔壁消费 deck 的 cockpit 缺 `## Staged (awaiting land)`，但所有校验全说没问题：walkaround Audit 16 不报 missing section、`conform --check` exit 0、`index --check` clean。结果是这一节既不会被补出，也永远不会被填——谁都不让它出现。

## Root cause

cockpit 的 canonical section 集合有**单一真相源**：`skills/preflight/templates.md`（模板）+ `scripts/flightdeck_index.py`（AUTO 块 regen）。但两个校验器各自**硬编码了一份拷贝**，没从真相源派生：

- `flightdeck_conform.py` 的 `COCKPIT_SECTIONS`（append-only 补缺——列表里没有就不补、`--check` 就不报）；
- walkaround `SKILL.md` Audit 16 的 canonical 字段清单（散文里手写）。

stage/land 生命周期（spec `2026-06-22-stage-land-lifecycle`）往模板 + index 加了 `## Staged (awaiting land)`（带 `AUTO:staged` marker），却没同步这两份硬编码拷贝。于是死角闭合：缺这节的 deck，conform 不补（清单里没有）、index 也不补（`regen_cockpit_staged` 只在 `<!-- AUTO:staged -->` marker 已存在时才 regen，line 745），两个安全网互相让路。

这与 [outer-ring-docs-drift](outer-ring-docs-drift.md) **不是同一签名**：那个是外圈*人类叙事文档*（README/docs/.github）脱离协议漂移；这个是*内圈校验器*把真相源的清单硬编码成镜像而 skew。

## Fix

改 canonical section 集合时，下游硬编码拷贝必须一并更新：`conform` 的 `COCKPIT_SECTIONS`（`.py` + `.js` 孪生）+ walkaround Audit 16 清单；并给带 `AUTO` marker 的 section 在 conform 的 `_section_body` / `sectionBody` 加骨架分支（返回带 marker 的空块，否则补出的空壳 index 填不进去）。

**根治方向（留待）**：让校验器从单一真相源派生该清单（导出/读 templates 或 index 的 section 集合），而非各自硬编码——彻底消除「改一处漏三处」。

## Cases
- 2026-06-23 首次 —— 隔壁消费 deck cockpit 缺 `## Staged (awaiting land)`，walkaround Audit 16 + `conform --check` + `index --check` 全报 clean，无人检出。源仓核实 conform/walkaround 两份硬编码清单漏了该 section（stage/land 生命周期引入时未同步）。修复见 commit `285f8be`（conform `.py`/`.js` + 测试 + walkaround Audit 16 补 `## Staged`）。
