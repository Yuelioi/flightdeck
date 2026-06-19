# specs/ — INDEX

<!-- AUTO:specs -->
### Active · Done
- [2026-06-19-skills-english-remediation.md](2026-06-19-skills-english-remediation.md) — active — 实测 skills/ 有 184 处中文漂移（10 文件），违反 rules.md 发布面英文红线。已止血：CLAUDE.md 强化对比 + version-bump 硬发版门。本 spec = 一次性翻译整顿：把 10 个 skill 文件翻成纯英文。scope 只管 ship 面（skills/scaffolds/templates/README/banner/字段标签），项目内 CLAUDE.md / flightdeck dogfood deck / 用户 deck 全不管。结构坑：中文 heading 被别处锚链（改名连带改链）、中文约定名 ## 评审纪要 多处引用（统一英文名+更新全部引用）。翻译只动语言不动语义。
- [2026-06-19-cockpit-field-redesign.md](2026-06-19-cockpit-field-redesign.md) — active — 三个真实 3.0 cockpit 实测：叙述字段（Last updated 括号 / Active focus / Next）漏入工作记录（changelog / 目标判据 / 进度日志），每仪式加载 = 主 token 黑洞；In Progress 反而干净（长仅因 summary 长）。大改原则：cockpit=纯恢复载荷，每字段只能是廉价投影或指针大小判断，记录回各自的家（git/plan Progress/spec body/rules/INDEX）只留链接。落：Last updated 砍 changelog、Active focus 退一行标签+链接、Next 退单步+进度移 plan、summary 加上限+In Progress 截断、标准化薄 Pointers 行。
- [2026-06-19-cockpit-accumulator-convergence.md](2026-06-19-cockpit-accumulator-convergence.md) — active — cockpit 两个非-AUTO accumulator（Key Context / Pending Review）堆积陈年内容，现有 drain 纪律+密度门控在却不真 drain（被动等签收/保守判断）。重构：Key Context 不再是永久住址而是中转暂存——耐用条目 landing 时毕业上迁到按类型选的永久家（rules.md / docs / agent 根指令文件，去 CLAUDE.md 写死），临时条目 referent 死即排空；Pending Review 保留显式签收但 landing 主动逼问老条目，停止静默堆积。
<!-- /AUTO -->
