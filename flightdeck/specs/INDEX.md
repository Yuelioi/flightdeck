# specs/ — INDEX

<!-- AUTO:specs -->
### 进行中·完成（active·done）
- [2026-06-10-drop-root-index.md](2026-06-10-drop-root-index.md) — active — 删 root flightdeck/INDEX.md 及其派生链：cockpit 是唯一的板，root INDEX 纯机制件、其唯一可见产物(preflight 计数行)相对 cockpit 进行中+step3 Routing catalog 完全冗余。删脚本 regen_root_index/folder_summary/imported_summary + yield root（保留 FOLDER_ORDER/IMPORTED_KINDS，仍被 REGEN_FOLDERS+lint 用）、相关测试、dogfood+scaffold 两份 INDEX.md、preflight step2/报告首行、walkaround Audit5 根计数、landing/exit-ritual 刷新 root 表述、protocol 文件夹图根 token、templates root 段。folder INDEX 全保留、恢复载荷红线零影响。
- [2026-06-09-descope-backward-compat-and-slim.md](2026-06-09-descope-backward-compat-and-slim.md) — active — 3.0 定为格式基线第0版：砍掉整个向后兼容/迁移/版本校验子系统（layout verdict/MIGRATION 迁移/legacy 路径全删，3.1 再就地建迁移）；校验只许活在按需跑的 walkaround，preflight 退化纯读零写、landing 仅核心仪式；assume 良构 deck 不做防御性存在检查；incidents 教训吸纳进权威件后退役清理；热/冷路径预算铁律防再膨胀——根治 preflight 固定成本，上下文不丢零损失
- [2026-06-08-stage-brand-glyphs.md](2026-06-08-stage-brand-glyphs.md) — active — 给 7 个 flightdeck 阶段各配一枚彩色 emoji 品牌图标（🛫preflight/🛬landing/🔍walkaround/✍️new/🔄status/🛠️launch/🌉emit-agents），加在各 skill 主报告/完成行；字形映射表落 skills/preflight/protocol.md 作文档级单一真相源；✈️ 留作整体 wordmark；scaffolds/模板/脚本/测试不动（横幅是模型 prose）
- [2026-06-08-nonblocking-verify-preflight-slim.md](2026-06-08-nonblocking-verify-preflight-slim.md) — active — 验证由阻塞门降为非阻塞标记——复用 stale 外加可编程锚点字段 verify（有字段即欠验证、值=怎么验，随文件进 archive，preflight 扫 active+archive 确定性重建待验证清单，不依赖手写 cockpit 行）；知识件 stale+verify、工作流 done+verify 照常由 landing --archivable 完整归档、可逆复活；并 preflight 输出瘦身（folder INDEX 仍读只显计数 + docs 载入上下文不刷屏）——兑现随时关不丢上下文
<!-- /AUTO -->
