# specs/ — INDEX

<!-- AUTO:specs -->
### Active · Done
- [2026-06-23-ai-native-redesign.md](2026-06-23-ai-native-redesign.md) — active — 少结构·多信任 AI 重设——砍流程/迁移/冗余三痛。两动词 preflight(手动进场)/persist(自动 turn-end),手动命令仅 preflight + walkaround(审计)、其余折进自动 persist 或消失;热层=项目 repo(git,每轮 commit)+ 冷层=母库 ~/.flightdeck(不版本化,只存未定/过期/通用)。项目 deck = cockpit.md(仪表盘)+ rules.md(项目约定,进场常读)+ uses.md(引用订阅)+ work/(在飞,superpowers 产出原样放)+ knowledge/(持久知识,按领域嵌套,类型=标题行)。零 YAML(改用轻量路由头 SUMMARY/READ WHEN/RECHECK WHEN,--- 收尾)/ 无 INDEX / 无 status 机(位置即状态);grep+走树路由、mtime+body 判新鲜;协议两层定死在插件里。设计已锤定 = 决策记录,剩 authoring + 迁移执行。
- [2026-06-22-stage-land-lifecycle.md](2026-06-22-stage-land-lifecycle.md) — active — Two-phase lifecycle replacing the checkpoint/soft-landing/full-landing split: stage (auto every turn-end -- knowledge persisted as pending-review, done marked but not archived, board converged, auto local commit) and land (manual valve -- archive + flip pending-review knowledge live; push still asks).
<!-- /AUTO -->
