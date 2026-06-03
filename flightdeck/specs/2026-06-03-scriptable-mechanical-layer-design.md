---
status: done
summary: 机械层（INDEX 重生 / walkaround lint / AGENTS emit / 对账）脚本化降 token、模型只留判断；单语言 Python stdlib + markdown fallback 双轨 + rules scripts 开关 + 机械-判断分界 + 字母序；全 rollout 完成（index/init/bump/lint 四脚本）
last_updated: 2026-06-04
---

# Scriptable mechanical layer

## Problem

flightdeck 本质上一半是 **linter + generator**：walkaround 审计、landing 重生 INDEX、emit-agents、status/计数对账。这些机械活现由模型逐字做，token 随 deck 规模线性涨。把机械层下放给**确定性脚本、模型只留判断**——降 token + 拿可测性，且**不破坏纯 markdown / 工具无关**身份（同一 body 发 claude/codex/cursor/gemini）。

## Decisions（已锁，调研背书）

- **单语言 Python，纯 stdlib，零依赖单文件**。多语言端口劝退（N×M 维护、语言间漂移；官方/标准无人这么干）。
- **形态**：暂按职责分多个纯 stdlib 脚本——`flightdeck_index.py`(INDEX regen/check)、`flightdeck_init.py`(scaffold deck)、`bump_version.py`(发布 manifest 同步,maintainer-only);各带 unittest。统一成单 `flightdeck.py <cmd>` 待脚本变多再做(YAGNI)。
- **双轨 fallback**：脚本=快路径；模型手动（= 今天的 prose）=慢路径/通用路径。正是 Anthropic best-practices 的 "with code / without code" 双写模式，非妥协。模型本身就是"通用 runtime"，所以不需要多语言凑覆盖。
- **分界线**：脚本**算事实**（generate / count / lint / extract），模型**做判断**（classify / match / decide / narrate）。docx skill 明文"编辑/判断 do NOT write Python scripts"。判断永不进脚本。
- **`scripts` 是 House Rule（非 frontmatter toggle）**：默认 **manual**；`rules.md` `### Autonomy overrides` 写 `run scripts`（或 `run scripts with <runtime>` 钉死解释器）才 opt-in 快路径。**理由（执行期校正）**：3.0 明文"只保留 `disabled_folders` 一个结构化 toggle"（templates.md:38 / protocol.md:16），新 frontmatter toggle 会破坏该不变量；自动跑代码又是高信任动作 → 默认关、显式 opt-in。走 protocol 标准句表（lenient 子串匹配，跨四工具一致）。
- **版本钉死**：脚本编码 layout 结构/status 合法值，须对 `MIGRATION.md current`；不符则拒跑、退化手动。
- **INDEX 行序 = 文件名字母序**（canonical；手工 append 序无法从文件系统复现）。

## Operation inventory（script vs model）

| 操作 | 归属 | 性质 |
|---|---|---|
| INDEX 重生（folder AUTO + root 计数） | script | generator（已交付） |
| init / scaffold（copy 全布局 verbatim + seed cockpit） | script | generator（已交付，接进 preflight Branch-0；省 ~5k token + 灭 scaffold-ships-verbatim） |
| walkaround 全量审计（Audit 1–10） | script | linter（最大收益，rollout Phase 3） |
| emit-agents-md 标记间重生 | script | generator |
| status 合法性 / 计数对账 | script | check（只读吐 JSON） |
| git reconcile 信号采集 | script 采集 / model 判断 | 半 |
| 知识分类 / routing 匹配 / migration 决策 | model | 判断（永不脚本） |

## Windows / 可移植红线

- 官方 doc skills 全 **POSIX-only、零 Windows 处理**（LD_PRELOAD、`~/.config` 硬路径、grep/nohup/kill）。本项目 Windows-first → **脚本里不碰 shell/bash，纯 Python**，无官方先例可抄。
- 脚本执行跨工具支持：Claude ✅ / Cursor ✅ / Codex 存疑（默认 instruction-only）/ Gemini 没确认 → **fallback 必须留**。
- token 收益方向坐实（脚本读文件在 bash 子进程、**不进模型上下文**，模型只见一行输出 → 上下文成本≈常数、与 deck 规模无关）；全网无精确数字，自测。

## Delivered（PoC，已提交 `6e146c1`）

`scripts/flightdeck_index.py`（纯 stdlib）+ `scripts/tests/`（unittest，TDD）。`regen-index` 从 frontmatter 重生 folder + root INDEX；`--check` 报漂移、exit 1。**当场在本 deck 抓出并修复 4 处 INDEX 漂移**。已扩展：`flightdeck_init.py`（preflight Branch-0 的 scaffold copy + cockpit seed，省 ~5k token，verbatim 灭 scaffold-ships-verbatim）+ `bump_version.py`（version-bump 的 5-manifest 同步 + `--check`）。全套 24 unittest。

## Delivered（全部完成 2026-06-04）

四脚本全交付（纯 stdlib）：`flightdeck_index.py`（INDEX/cockpit 重生 + `--check` + `index_drift`）、`flightdeck_init.py`（scaffold）、`bump_version.py`（发布同步）、`flightdeck_lint.py`（机械审计 Audit 1/4/5/7/8 → JSON）。skill 双轨 + rules `run scripts` 开关 + 版本 guard 均接入（见 [plan：rollout](../plans/2026-06-03-scriptable-mechanical-layer-rollout.md)）。判断永留模型；markdown 慢路径恒为真相源 + fallback。

**未实施（有意）**：单 `flightdeck.py <cmd>` 统一入口仍按 YAGNI 推迟；`walkaround` 全量 prose 压缩（用 lint 替机械段）留作后续独立优化，不阻塞本 spec 收尾。

## Related

- [preflight-tri-review-remediation](../landed/specs/2026-06-03-preflight-tri-review-remediation.md) —— walkaround lint 等其范围重构（A1 拆 migration）落定。
- [incidents/index-row-summary-delimiter](../incidents/index-row-summary-delimiter.md) —— "rows are regenerated, not parsed"；summary 含 ` — ` 的隐患（本脚本"从 frontmatter 重生、不解析旧行"正好绕开）。
