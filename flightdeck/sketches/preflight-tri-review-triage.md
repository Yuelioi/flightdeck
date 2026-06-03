---
status: active
summary: 三方审核 preflight 的问题盘点，按 减重/纠错/不紧急 分类；减重主刀=拆 migration 出 preflight + status 审计收窄；结论是不上脚本（保持纯 markdown / 工具无关）
---

# Preflight 三方审核 — 问题归类（待决策，未动手）

来源：`debriefs/claude.txt` `ds.txt` `gpt.txt`（同一轮 preflight skill 的三模型审核）。每条标 `[C]`=claude `[D]`=ds `[G]`=gpt 出处；多标=被交叉印证。gpt 自述只读了 2/3，但它的核心两条（拆 migration、status 扫描不可扩展）与读全的 ds/claude 重合，故非残缺读产物。

**前置结论（已更新，2026-06-03）**：原写"不引入脚本"已被推翻。调研（见 [scriptable-mechanical-layer](../specs/2026-06-03-scriptable-mechanical-layer-design.md)）确认脚本可作为**机械层加速器 + markdown fallback（官方双轨）**引入，不破坏工具无关性。但本清单的减重项**仍以内容架构为主**——脚本与重构正交：先做 A1/A2 等范围重构，机械层脚本化单独走那份 spec/plan。下列各项不依赖脚本。

---

## A. 减重（降体量 / 可扩展性）

- **A1. 拆 migration 出 preflight** `[G]` — 把 version/current/layout_need_update/pre-2.2/pre-3.0/1.x 这棵嵌套决策树移到独立 `/flightdeck:migrate`（或仅版本不符时才加载的 companion）；preflight 只 detect → report "run /flightdeck:migrate" → stop。**单笔收益最大**：砍掉最重一块，且只在版本不符时加载。
- **A2. status 审计收窄（Step 7）** `[D][G][C]` — 现写"Scan each folder INDEX row"全局逐行扫描，但 preflight 只加载了 checklists/incidents 的 INDEX，根本没读 specs/plans/sketches/charts/debriefs 的 INDEX → **实际跑不动**，且 200 specs 时成本爆炸。改：只做根 INDEX 计数浅比对（可疑就提示"walkaround 会深查"），深度逐行审计归 walkaround。
- **A3. git reconcile 降为 heuristic 信号** `[G]` — "branch 匹配 Active focus？""status clean 但 cockpit 说 in-progress？"本质不可靠（feature/auth ↔ "improve login UX" 无法自动判等）。定义为 heuristic 而非 mismatch，减 prose + 降误报。
- **A4. 拆 protocol.md** `[G]` — 现已≈操作系统规范，过大。拆 core / routing / lifecycle / migration，按需加载。（与 A1 协同：migration 段直接进 migrate skill。）

## B. 纠错（正确性 / 一致性）

- **B1. silent version bump 矛盾** `[D]` — Step 2 子情况三"silently bump rules.md version"紧跟末尾"Never migrate (or stamp) silently"，直接打架。定调：兼容升级允许静默→把末句限定为"仅结构性迁移"；或要求都问→改 Step 2 为 "ask then bump"。**优先**。
- **B2. rules.md mandatory vs optional 矛盾** `[C]` — folder-semantics 说 "OPTIONAL project config"，protocol/templates 说 mandatory。统一口径。
- **B3. Step 0 门禁在无 deck 时盲区** `[D][G][C]` — 首次运行 rules.md 不存在，Step 0 却要 "Read rules.md"→file-not-found；且 Step 0/Step 1 重复读 rules.md。改：无 cockpit/rules 时 skip 门禁直进 Branch-0；Step 0 只读 `### Autonomy overrides` 的 preflight 行（非全量解析）。
- **B4. last_updated bump 规则跨文件不一致** `[C]` — protocol（"auto-bumped by status/landing"）/ exit-ritual（4 触发点）/ templates（知识文件"每次有意义变更"）三处措辞各异。protocol 设唯一信源、区分 workflow vs knowledge，余者引用不重述。
- **B5. Land Routine 与 INDEX 再生顺序** `[C]` — exit-ritual Step 3（regen INDEX）与 Step 3a（landing 又触发 INDEX 变更）分裂。明确：所有 landing 操作完成后统一再生 INDEX。
- **B6. INDEX=cache、frontmatter=truth 未声明** `[G]` — Root INDEX / Folder INDEX / frontmatter 三层来源，frontmatter 才是真相、其余派生。写进 protocol，避免生成器失效时口径不明。
- **B7. routing catalog 漏 charts/** `[D]` — charts 也可带 when_to_read/applies_to，protocol 还把 charts 列为"need outside perspective"来源，但 Step 6 只读 checklists+incidents。补 charts/ 进路由，或在 SKILL 显式声明"charts 不参与自动路由"+理由。
- **B8. cockpit 80 行执行责任人未定** `[C]` — preflight（读时）/ landing（写后）/ walkaround（审计）谁触发未定。**注：本次已删 cockpit 模版的 hygiene footer，执行实际落在 landing/exit-ritual——可借此一并在文档里钉死责任人 = landing。**

## C. 不紧急（措辞 / 清晰度 / 低影响）

- **C1.** `[C]` "穿针"中文术语混入英文 protocol.md → 改 "thread-the-needle" 或删比喻。
- **C2.** `[C]` skip_when 缺路由使用示例 → 在 Step 6 路由或 protocol 场景表补一例。
- **C3.** `[C]` rules.md 模板用 HTML 注释（被 matching 跳过）→ 模板旁加 "Remove the `<!-- -->` wrapper to activate"。
- **C4.** `[D]` 双 "Step 0" 与清单 "0. Branch-0" 编号撞车 → 门禁改名 "Pre-step / Gate check"。
- **C5.** `[G]` "Don't reread cockpit" 对 LLM 不现实 → 改 "Read once and cache"，语义更准。
- **C6.** `[D]` Land-readiness ≥5 文件阈值对大仓略敏感 → 暂保留，无大碍。
- **C7.** `[C]` walkaround 在审核文档集里缺席 → 审核范围所限，非真 bug；可在 protocol 注明其职责清单。

---

## 建议动手顺序（供决策，未执行）

1. **B1 / B3**（纠错，便宜且消歧义）—— 顺手做。
2. **A1 拆 migration**（减重主刀）—— 大改，独立一轮 spec。
3. **A2 status 收窄 + A3 git heuristic**（减重，和 preflight 主流程同改）。
4. **A4 / B4 / B6 拆 protocol + 权威口径**（文档架构，可随 A1 一起）。
5. C 类随手清。

**Revisit when**：决定动 preflight 时回到本清单逐项勾。源 txt（claude/ds/gpt）建议消化进本 sketch 后清理（.txt 无 frontmatter，留在 debriefs/ 会被 walkaround 当 stray）。
