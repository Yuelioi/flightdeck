<!-- BEGIN: flightdeck -->
<!-- Auto-regenerated from flightdeck/cockpit.md by /flightdeck:emit-agents-md.
     Do NOT edit between these markers — your edits will be overwritten on
     next regeneration. Add hand-authored content OUTSIDE the markers. -->

## Current focus

flightdeck 3.0 完善到位（**不急发布、避免迁移债**）。**核心卖点=随时可关、下次 preflight 干净接手、上下文不丢（红线）**。当前主线 = **大瘦身 / de-scope**：3.0 定为格式基线第0版，砍向后兼容/校验子系统、校验只在 walkaround、preflight 纯读零写、热/冷预算——根治 token 失控（preflight 单次 ~9k）。

## 进行中

- [2026-06-08-nonblocking-verify-preflight-slim.md](flightdeck/specs/2026-06-08-nonblocking-verify-preflight-slim.md) — 验证由阻塞门降为非阻塞标记——复用 stale 外加可编程锚点字段 verify（有字段即欠验证、值=怎么验，随文件进 archive，preflight 扫 active+archive 确定性重建待验证清单，不依赖手写 cockpit 行）；知识件 stale+verify、工作流 done+verify 照常由 landing --archivable 完整归档、可逆复活；并 preflight 输出瘦身（folder INDEX 仍读只显计数 + docs 载入上下文不刷屏）——兑现随时关不丢上下文
- [2026-06-08-stage-brand-glyphs.md](flightdeck/specs/2026-06-08-stage-brand-glyphs.md) — 给 7 个 flightdeck 阶段各配一枚彩色 emoji 品牌图标（🛫preflight/🛬landing/🔍walkaround/✍️new/🔄status/🛠️launch/🌉emit-agents），加在各 skill 主报告/完成行；字形映射表落 skills/preflight/protocol.md 作文档级单一真相源；✈️ 留作整体 wordmark；scaffolds/模板/脚本/测试不动（横幅是模型 prose）
- [2026-06-09-descope-backward-compat-and-slim.md](flightdeck/specs/2026-06-09-descope-backward-compat-and-slim.md) — 3.0 定为格式基线第0版：砍掉整个向后兼容/迁移/版本校验子系统（layout verdict/MIGRATION 迁移/legacy 路径全删，3.1 再就地建迁移）；校验只许活在按需跑的 walkaround，preflight 退化纯读零写、landing 仅核心仪式；assume 良构 deck 不做防御性存在检查；incidents 教训吸纳进权威件后退役清理；热/冷路径预算铁律防再膨胀——根治 preflight 固定成本，上下文不丢零损失
- [2026-06-08-nonblocking-verify-preflight-slim-rollout.md](flightdeck/plans/2026-06-08-nonblocking-verify-preflight-slim-rollout.md) — 把'验证非阻塞+preflight瘦身'spec逐文件落地：相位1 脚本TDD（flightdeck_index.py 加 --verify-pending 子命令 + format_row 按 verify 渲染 ⚠未验证/⚠待复核 + 测试）→相位2 治理文案契约（protocol/templates 定 verify 字段语义、stale 拓宽、done 语义、per-kind 通过失败）→相位3 仪式 skill（exit-ritual 门重写+扫描浮出、landing 3a3c+archivable、status done+verify、preflight 扫描+瘦身C+docs计数D）→相位4 套用 hook spec+plan 打 verify+归档清看板 + resync 后新会话 live 实证（停地板）
- [2026-06-09-descope-backward-compat-and-slim-rollout.md](flightdeck/plans/2026-06-09-descope-backward-compat-and-slim-rollout.md) — 把 de-scope spec 逐文件落地：相位1 删向后兼容子系统（flightdeck_index.py 删 verdict/version 6 函数 + --verdict 子命令 + version_mismatch 守卫，TDD 同步删测试；MIGRATION.md 200 行史→极简戳；legacy/pre-3.0 处理）→相位2 命令职责重划（preflight 删 step1/4/4a 收敛纯读零写、landing 剥 version/verdict 留 stale 单仪式、walkaround 删 migration 审查聚焦本版内）→相位3 incidents 吸纳-退役（逐条 triage：可设计防范/仅可警示，吸纳进必经路径后翻 obsolete，过时删）→相位4 热/冷预算扫尾（注入≤25行/preflight SKILL≤45/walkaround≤80 + 冷路径上限 + cockpit 软上限）；每相位测试绿+regen clean+before/after token，行为恢复验收，可逐相位 git revert
- [2026-06-09-stage-brand-glyphs-rollout.md](flightdeck/plans/2026-06-09-stage-brand-glyphs-rollout.md) — 把每命令品牌图标 spec 逐落点落地：protocol.md 建权威字形表 → 7 命令各改运行时报告行加 emoji（launch🛠️/preflight🛫/walkaround🔍/status🔄/landing🛬/new✍️/emit🌉）→ 末轮一致性核对（字形↔表三列、scaffolds/脚本零改动 grep）+ 目标终端目视；纯 SKILL.md/protocol.md prose 编辑，无脚本/测试改动

## 下一步

- **drop-root-index ✅ 已落地归档**：删 root INDEX 全派生链（脚本 3 函数 + `_index_targets` yield + dogfood/scaffold 两份 INDEX.md + 8 处 skill 引用 + model/script-layer 文档校正）；157 测试绿、活 surface 扫描零命中、新 deck e2e --check clean。spec+plan 已 archive。
- **descope（2026-06-09）已签收 done 但仍未 land**：spec 是 `graduate:true` → land 时要把 spec 本体改写进 `docs/` 常驻（较重改写）。**待你确认后单独跑一次 graduate-landing**（本轮 landing 只收 drop-root-index，没碰它）。
- **Parked（各待自身完工/land）**：① hook rollout 相位4 live 实证（resync 后新会话手动跑各家最小矩阵）；② nonblocking-verify rollout、③ stage-brand-glyphs rollout（commits 已落、status 仍 active，待签收 done+land）。
- **Backlog**：#1 写门负例（纯 prompt 低风险）、#7 恢复回归测试（待恢复模型稳定再做，首个核心价值行为测试）。

## Hanging tasks

None.

## More

For full project state, read `flightdeck/cockpit.md`, the folder `INDEX.md` files, and the linked artifacts.

To author a new deck artifact (spec/plan/incident/checklist/chart), run `/flightdeck:new` — it stamps the correct frontmatter + naming and regenerates INDEX/cockpit. Don't hand-write deck artifacts or place them under `docs/`.

<!-- END: flightdeck -->

<!-- Hand-authored content below this line is preserved across emitter runs. -->
