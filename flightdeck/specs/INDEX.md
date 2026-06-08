# specs/ — INDEX

<!-- AUTO:specs -->
### 进行中·完成（active·done）
- [2026-06-08-nonblocking-verify-preflight-slim.md](2026-06-08-nonblocking-verify-preflight-slim.md) — active — 验证由阻塞门降为非阻塞标记——复用 stale 外加可编程锚点字段 verify（有字段即欠验证、值=怎么验，随文件进 archive，preflight 扫 active+archive 确定性重建待验证清单，不依赖手写 cockpit 行）；知识件 stale+verify、工作流 done+verify 照常由 landing --archivable 完整归档、可逆复活；并 preflight 输出瘦身（folder INDEX 仍读只显计数 + docs 载入上下文不刷屏）——兑现随时关不丢上下文
<!-- /AUTO -->
