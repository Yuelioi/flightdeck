# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-10 by 月离 (descope 签收 land+graduate：spec→`docs/descope-baseline.md` 常驻、plan 归档；连同 drop-root-index，de-scope 主线整体收口。)
**Active focus**: flightdeck 3.0 完善到位（**不急发布、避免迁移债**）。**核心卖点=随时可关、下次 preflight 干净接手、上下文不丢（红线）**。当前主线 = **大瘦身 / de-scope**：3.0 定为格式基线第0版，砍向后兼容/校验子系统、校验只在 walkaround、preflight 纯读零写、热/冷预算——根治 token 失控（preflight 单次 ~9k）。

## 进行中

<!-- AUTO:inprogress -->
- [2026-06-08-nonblocking-verify-preflight-slim.md](specs/2026-06-08-nonblocking-verify-preflight-slim.md) — 验证由阻塞门降为非阻塞标记——复用 stale 外加可编程锚点字段 verify（有字段即欠验证、值=怎么验，随文件进 archive，preflight 扫 active+archive 确定性重建待验证清单，不依赖手写 cockpit 行）；知识件 stale+verify、工作流 done+verify 照常由 landing --archivable 完整归档、可逆复活；并 preflight 输出瘦身（folder INDEX 仍读只显计数 + docs 载入上下文不刷屏）——兑现随时关不丢上下文
- [2026-06-08-stage-brand-glyphs.md](specs/2026-06-08-stage-brand-glyphs.md) — 给 7 个 flightdeck 阶段各配一枚彩色 emoji 品牌图标（🛫preflight/🛬landing/🔍walkaround/✍️new/🔄status/🛠️launch/🌉emit-agents），加在各 skill 主报告/完成行；字形映射表落 skills/preflight/protocol.md 作文档级单一真相源；✈️ 留作整体 wordmark；scaffolds/模板/脚本/测试不动（横幅是模型 prose）
- [2026-06-08-nonblocking-verify-preflight-slim-rollout.md](plans/2026-06-08-nonblocking-verify-preflight-slim-rollout.md) — 把'验证非阻塞+preflight瘦身'spec逐文件落地：相位1 脚本TDD（flightdeck_index.py 加 --verify-pending 子命令 + format_row 按 verify 渲染 ⚠未验证/⚠待复核 + 测试）→相位2 治理文案契约（protocol/templates 定 verify 字段语义、stale 拓宽、done 语义、per-kind 通过失败）→相位3 仪式 skill（exit-ritual 门重写+扫描浮出、landing 3a3c+archivable、status done+verify、preflight 扫描+瘦身C+docs计数D）→相位4 套用 hook spec+plan 打 verify+归档清看板 + resync 后新会话 live 实证（停地板）
- [2026-06-09-stage-brand-glyphs-rollout.md](plans/2026-06-09-stage-brand-glyphs-rollout.md) — 把每命令品牌图标 spec 逐落点落地：protocol.md 建权威字形表 → 7 命令各改运行时报告行加 emoji（launch🛠️/preflight🛫/walkaround🔍/status🔄/landing🛬/new✍️/emit🌉）→ 末轮一致性核对（字形↔表三列、scaffolds/脚本零改动 grep）+ 目标终端目视；纯 SKILL.md/protocol.md prose 编辑，无脚本/测试改动
<!-- /AUTO -->

## 下一步

- **de-scope 主线整体收口 ✅**：4 相位 + drop-root-index 全部 land；descope spec 已 graduate → `docs/descope-baseline.md` 常驻（职责边界 / 无向后兼容 / 校验只在 walkaround / 预算铁律的单一真相源），相关 plan 归档。
- **接下来（Parked，各待自身完工/land）**：① hook rollout 相位4 live 实证（resync 后新会话手动跑各家最小矩阵）；② nonblocking-verify rollout、③ stage-brand-glyphs rollout（commits 已落、status 仍 active，待签收 done+land）。
- **Backlog**：#1 写门负例（纯 prompt 低风险）、#7 恢复回归测试（待恢复模型稳定再做，首个核心价值行为测试）。

## 关键上下文

- **de-scope 红线**：核心卖点「上下文不丢」零损失——只砍指令散文 + 向后兼容/校验机制，cockpit+INDEX 恢复载荷不动。
- **de-scope 单一真相源**：`docs/descope-baseline.md`（职责边界·无向后兼容·校验只在 walkaround·preflight 纯读零写·热/冷预算；含两轮外评结论）。原 spec 已 graduate 至此、plan 归档。
- **测试/度量**：`uv run pytest scripts/tests/`；`wc -m` 作 token 代理。记忆 `flightdeck-3.0-descope-v0`。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
