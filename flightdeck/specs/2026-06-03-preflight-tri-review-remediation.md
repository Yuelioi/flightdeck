---
status: active
summary: preflight 三方审核(claude/ds/gpt)19 项整改总账 spec（由同名 sketch 提升）；减重 A1/A3/A4 已并入 token-reduction spec，纠错 B + 措辞 C 在本 spec 跟踪；记录每项处置/done/deferred
last_updated: 2026-06-03
---

# Preflight 三方审核整改（remediation）

> 由 `sketches/preflight-tri-review-triage.md` **提升**而来（2026-06-03）。提升原因：清单已进入执行（B/C 多项已改、减重项已并入 token-reduction spec），留在 sketches/ 不再反映现状。本 spec 是这轮审核 **19 项发现的单一去向账本**——减重 A 项的实现归 [token-reduction spec](2026-06-03-token-reduction-design.md)，本 spec 不重述其设计，只记处置。

来源：`debriefs/2026-06-03-rules-simplification-tri-review.md` 等（同一轮 preflight skill 的三模型审核）。每条标 `[C]`=claude `[D]`=ds `[G]`=gpt 出处；多标=被交叉印证。

**前置结论**：脚本可作为机械层加速器 + markdown fallback（官方双轨）引入，不破坏工具无关性（见 [scriptable-mechanical-layer](2026-06-03-scriptable-mechanical-layer-design.md)）。减重与重构正交：内容架构重构在本 spec / token-reduction spec，机械层脚本化单独走那份 spec/plan。

## 处置总览（2026-06-03）

| 项 | 类 | 状态 | 去向 / 证据 |
|---|---|---|---|
| A1 拆 migration 出 preflight | 减重 | ⏳ deferred | [token-reduction](2026-06-03-token-reduction-design.md) Remaining（结构性，较大） |
| A2 status 审计收窄(Step 7) | 减重 | ✅ done | SKILL Step 7 "loaded folders only"，深查归 walkaround |
| A3 git reconcile 降 heuristic | 减重 | ✅ done | SKILL Step 4/5 改 fuzzy 启发式信号（只报明确背离、不猜等价），~12→4 行 |
| A4 拆 protocol.md | 减重 | ⏳ deferred | token-reduction Remaining（与 A1 协同） |
| B1 silent version bump 矛盾 | 纠错 | ✅ done | SKILL Step 2 末句限定"仅结构性迁移；兼容 bump 为唯一允许的静默 stamp" |
| B2 rules.md mandatory vs optional | 纠错 | ✅ done | folder-semantics 改"文件强制(3-file 契约)、内容可选"，与 protocol/templates 对齐 |
| B3 Step 0 门禁无 deck 盲区 | 纠错 | ✅ done | 门禁改"resolve per protocol"（不再 Read rules.md）+ Branch-0 先跑（`d9b1aa8`） |
| B4 last_updated bump 跨文件不一致 | 纠错 | ✅ done | 收成 4-trigger 单一指针，protocol 区分 workflow/knowledge |
| B5 Land/INDEX 再生顺序 | 纠错 | ✅ done | exit-ritual 新增 "INDEX regeneration — scope rules" 专节 + land routine 不内联 |
| B6 INDEX=cache、frontmatter=truth | 纠错 | ✅ done | protocol 声明 INDEX derived-from-frontmatter、frontmatter 为 single source of truth |
| B7 routing catalog 漏 charts/ | 纠错 | ✅ done | SKILL Step 6 显式声明"charts 不参与自动路由 + 理由"（deliberate browse / 可能是大导入树） |
| B8 cockpit 80 行执行责任人 | 纠错 | ✅ done | protocol 新增"三仪式职责分工表"钉死：trim owner=landing，walkaround 仅 flag，preflight 不碰 |
| C1 "穿针" jargon | 措辞 | ✅ done | protocol behavioral-override 去比喻（`cdaa244`） |
| C2 skip_when 缺示例 | 措辞 | ✅ done | protocol routing 段加 `skip_when: editing tests only` 例 |
| C3 rules.md 模板 HTML 注释提示 | 措辞 | ✅ done | templates 改"delete its `<!-- -->` wrapper to activate；注释行被 matching 跳过" |
| C4 双 Step 0 编号撞车 | 措辞 | ✅ done | preflight 门禁标题 Step 0 → "Gate — model-invocation check"（仅 preflight 有撞车；其余 4 skill 保留 Step 0 约定） |
| C5 "Don't reread"→"read once & cache" | 措辞 | ✅ done | SKILL Step 3 改"read each once and treat as cached for the rest of the ritual" |
| C6 Land-readiness ≥5 阈值 | 措辞 | ✅ closed | 决定保留，无大碍 |
| C7 walkaround 在审核集缺席 | 措辞 | ✅ done | protocol"三仪式职责分工表"列明 walkaround 职责（status/orphan/dangling/stray 深审） |

**剩余开放**：仅减重 A1/A3/A4（结构性大改，[token-reduction spec](2026-06-03-token-reduction-design.md) 跟踪）。**纠错 B + 措辞 C 全 15 项已结**（B1–B8、C1–C7）。

---

## 原始三方审核清单（归档，按 减重/纠错/不紧急 分类）

### A. 减重（降体量 / 可扩展性）

- **A1. 拆 migration 出 preflight** `[G]` — 把 version/current/layout_need_update/pre-2.2/pre-3.0/1.x 决策树移到独立 `/flightdeck:migrate`（或仅版本不符时加载的 companion）；preflight 只 detect → report → stop。单笔收益最大。
- **A2. status 审计收窄（Step 7）** `[D][G][C]` — 原"Scan each folder INDEX row"全局扫描但 preflight 没读那些 INDEX → 实际跑不动；改只对已加载文件夹做浅检，深审归 walkaround。
- **A3. git reconcile 降为 heuristic 信号** `[G]` — branch↔Active focus / status↔in-progress 本质不可靠，定义为 heuristic 而非 mismatch，减 prose + 降误报。
- **A4. 拆 protocol.md** `[G]` — 现已≈操作系统规范，过大。拆 core / routing / lifecycle / migration，按需加载。

### B. 纠错（正确性 / 一致性）

- **B1. silent version bump 矛盾** `[D]` — Step 2"silently bump version"紧跟"Never migrate/stamp silently"，打架。定调：兼容升级允许静默→末句限定"仅结构性迁移"。
- **B2. rules.md mandatory vs optional 矛盾** `[C]` — folder-semantics 说 OPTIONAL，protocol/templates 说 mandatory。统一：文件强制、内容可选。
- **B3. Step 0 门禁在无 deck 时盲区** `[D][G][C]` — 首次运行 rules.md 不存在却要 Read；且 Step0/Step1 重复读。改：门禁抽象 resolve、Branch-0 先跑。
- **B4. last_updated bump 规则跨文件不一致** `[C]` — protocol/exit-ritual/templates 三处措辞各异。protocol 设唯一信源、区分 workflow vs knowledge。
- **B5. Land Routine 与 INDEX 再生顺序** `[C]` — exit-ritual regen-INDEX 与 landing 触发 INDEX 变更分裂。明确：landing 操作完成后统一再生。
- **B6. INDEX=cache、frontmatter=truth 未声明** `[G]` — 三层来源 frontmatter 才是真相、其余派生。写进 protocol。
- **B7. routing catalog 漏 charts/** `[D]` — charts 也可带 when_to_read/applies_to，但 Step 6 只读 checklists+incidents。补路由，或显式声明不参与+理由。
- **B8. cockpit 80 行执行责任人未定** `[C]` — preflight/landing/walkaround 谁触发未定。删 hygiene footer 后落在 landing/exit-ritual。

### C. 不紧急（措辞 / 清晰度 / 低影响）

- **C1.** `[C]` "穿针"中文术语混入英文 protocol → 改 thread-the-needle 或删比喻。
- **C2.** `[C]` skip_when 缺路由示例 → 补一例。
- **C3.** `[C]` rules.md 模板用 HTML 注释（被 matching 跳过）→ 加"删 `<!-- -->` 以激活"。
- **C4.** `[D]` 双 Step 0 与清单 "0. Branch-0" 编号撞车 → 门禁改名。
- **C5.** `[G]` "Don't reread cockpit" 对 LLM 不现实 → 改 "Read once and cache"。
- **C6.** `[D]` Land-readiness ≥5 阈值对大仓略敏感 → 暂保留。
- **C7.** `[C]` walkaround 在审核文档集里缺席 → 审核范围所限；可在 protocol 注明职责清单。

## Related

- [token-reduction](2026-06-03-token-reduction-design.md) — 减重 A1/A3/A4 的实现归属；本 spec 不重述
- [scriptable-mechanical-layer](2026-06-03-scriptable-mechanical-layer-design.md) — 脚本机械层（A 项的正交前置）
