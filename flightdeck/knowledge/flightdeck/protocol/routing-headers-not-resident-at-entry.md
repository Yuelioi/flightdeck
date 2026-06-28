# ⚠ routing headers never entered context at entry

SUMMARY: preflight's "scan headers only when filenames don't settle relevance" framing kept every `READ WHEN:` out of context, so routing never fired and subscriptions were dead weight — fixed by making the header map eager (scanned every entry) with bodies lazy, ranked by READ-WHEN shape.
READ WHEN: changing preflight's loading model / step 3 / the derived-listing trigger; or a deck's knowledge & subscriptions never seem to route (a `READ WHEN:` that should fire doesn't)
RECHECK WHEN: the preflight loading steps (SKILL.md step 1/3) or the derived-listing framing in operations.md change

---

## 根因

旧 step 3 把「grep 路由头」框成**条件兜底**——「*When `ls` + filenames don't settle relevance*, run a derived-listing」。于是默认入口路径 = 读 briefing+cockpit、`ls` 出文件名就完事,`SUMMARY:`/`READ WHEN:` 那两行**永不进上下文**。step 1 的「Fold each subscribed path into the routing tree」也只被理解成「知道有这文件名」。

后果很硬:一条 `READ WHEN: before editing any comment` 这样的触发器,**靠的就是那行 READ-WHEN 驻留在上下文里**才可能 fire;入口不读头 → 触发器没有承载体 → 订阅与本地知识全成死重。2026-06-26 用户在两个外部参考 deck 实测:AI 跑 preflight 后自陈「根本没读订阅开头,连本仓库知识开头也没读」。dogfood 当场也复现(本会话开头我自己只 `ls` 没读头)。

与 `sibling-workflow-leaves-cockpit-stale` / `persist-knowledge-scan-no-heartbeat` **同源**:协议散文把一个 load-bearing 动作写成「可选/兜底」,没有 forcing function → AI 顺着省掉。这是 flightdeck 头号风险（无机械自纠偏）的又一尖锐子型。

## 修法(已落地)

「先地图后领土」两跳,把扫头从兜底提为入口默认:

- **hop1 地图(每次入口必做)**:扫本地 `knowledge/` + 订阅子树的路由头(title + SUMMARY + READ-WHEN)。头是故意做成一行的,便宜;`READ WHEN:` 不驻留就不能 fire。= 现有 derived-listing,改成**无条件**跑。
- **给地图排序**(主看 READ-WHEN 形状,glyph 辅证,**不加字段**):proactive「before \<日常动作>」/ checklist → 当活约束前台常驻;reactive「when \<症状/故障>」/ `# ⚠` trap → 只挂索引,症状出现才拉 body。comments/commits 这类约定不分任务常驻。
- **hop2 领土(懒)**:某文件 READ-WHEN 当真对上手头任务,才读 body。「lazy」核心值保住,只是现在正确地只管 body。

改动面(按 `outer-ring-docs-drift` 连外圈):`skills/preflight/SKILL.md` step 1+3、`operations.md` Derived listing 段、`README.md` / `README.zh.md` 第 2 步。

## 为什么稳(外部 + 规模验证)

- **两个独立记忆系统各自重新推导出同一模式**:claude-mem 3-layer search、ReMe hop-based recall = 「先地图后领土」;ReMe 还把 `when_to_use` 条件本身当检索主键(= 我们让扫头成默认)。这与 `external-memory-borrowings` 中的 #5/#3 结论一致。不是新风险,是成熟套路。
- **规模下更值钱**:外部参考 deck A 的 76 个知识里 **65 个是 reactive trap**;若平权全当「必读约束」前台顶着 = 噪音淹死人。分层后只有 8 个 checklist 占注意力,65 个 trap 等症状。地图照样一眼扫完。deck B(59,36 trap / 11 checklist / 12 note)同样分得干净。**推导规则跨域稳**(二进制逆向 vs 前端自动化,两个无关域)。

## 改不了的

仍靠 AI 记得「入口扫头 + 按 READ-WHEN 排序」——把「忘了扫」从沉默变显形(协议明写默认+排序),非物理强制。walkaround 是兜底网。
