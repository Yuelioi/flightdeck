# 一个 spec 的完整流向

## 一句话

一个 spec 沿 **status 轴**（`idea → active → done`）往前走，沿 **location 轴**（源文件夹 ↔ `archive/`）被 **landing** 搬运。两根轴互相独立——把它们叠在一起，就是历史上"done = 已归档"混乱的根源。`status` 说"走到哪一步"，`location` 说"还在不在活动区"，**landing 是唯一的搬运者**。

## 两根轴（先分清）

| 轴 | 取值 | 是什么 |
|---|---|---|
| **status** | `idea / active / done` | 走到哪一步。**显式 frontmatter 值**。 |
| **location** | 源文件夹 / `archive/` | 还在不在活动区。**派生**（看是否在 `archive/` 下），**不是 frontmatter 字段**，但是一等概念：它驱动**路由**（`archive/` 整个被排除出路由图）与**归档判断**。 |

铁律：`archived` / `landed` **从来不是 status 值**，没有文件写 `status: landed`；**只有 landing 的 Land Routine 能把东西搬进 `archive/`**，status 永不归档。

knowledge 工件（graduate 后沉进 `docs/` 的那份）走自己的 status 轴：`{active, stale, obsolete}`——`stale`（疑似过期·待复核）是黄灯，`obsolete`（已确认死亡）是排水触发态，与 workflow 的 `done` 对称（见 `model-architecture.md` § 两条正交轴）。`superseded` 已从 knowledge status 枚举中删除；取代关系用 `supersedes` 溯源边标注，不是状态值。

## 完整流向（一张图）

```
  idea                 active                      done                      archive/
  ───────────          ─────────────────          ─────────────────         ───────────────
  spec 诞生   ─flip─▶   开工            ─批准/签收─▶  工作完成        ─landing─▶  历史冻结
  status:idea          status:active               status:done               （从 specs/ 移走）
  无日期前缀            自动加 YYYY-MM-DD- 前缀      留在 specs/ 直到被搬
  只在 specs/INDEX      进 cockpit ## In Progress     （done ≠ archived）
  不在 cockpit          │
                        │ 可派生出 plan（plans/，frontmatter implements: specs/<x>.md）
                        ▼
                    plan 同样走 idea→active→done；active 期间每个 task 边界做
                    checkpoint（同步 cockpit ## Next + plan 的 ## Progress current: 指针）
                                                                          │
                                       知识 graduate ──▶ docs/（当前真相，常驻、完工不归档）
```

## 逐阶段

1. **idea —— 诞生 / 捕获。** 新 spec 默认 `status: idea`：未启动的设计，**无日期前缀**，只出现在 `specs/INDEX` 的"待启动"池，**不进 cockpit**。（若写下来就已经在做，可合法直接起 `active`，跳过 idea。）

2. **active —— 开工（唯一改名点）。** `idea → active` 只是**翻一个字段**：自动补 `YYYY-MM-DD-` 前缀（幂等——已有前缀就跳过），并在 cockpit `## In Progress` 浮现。无文件移动、无关系边重写。每次翻转 bump `last_updated`。

3. **（并行）plan —— 把设计变可执行。** spec 可派生 `plans/` 下的 plan，plan 用 `implements: specs/<x>.md` 指回。plan 自己也走 `idea→active→done`；`active` 期间，**每个 plan-task 边界**做一次 **checkpoint**（轻量看板同步：cockpit `## Next` + plan 的 `## Progress` `current:` 指针，**只写盘、不 commit**），让中途关掉再开能无损接手。

4. **done —— 完成接缝。** `active → done` 的触发源是**用户断言的批准/签收**（一个事实），AI **不**自评完成、也不靠 smoke-check 判定。`→done` 是 status 轻仪式与 landing 重仪式之间的**唯一接缝**：到达 done 即把控制权交给 landing 收尾。**done 只翻 status，不归档**。

5. **land —— 唯一的搬运者。** 一个 `done` 有两种合法位置：**done-but-unlanded**（还在 `specs/`，因为仍有 `active` 文件指向它）或 **done-and-archived**（已进 `archive/`）。landing 在**回合结束前**跑一次（debounce：把本回合所有 done 聚到同一次 landing），每次都**重扫所有** done-in-place 文件，凡入边已清空的就扫进 `archive/`——所以 done-but-unlanded **自动排干**，不会滞留。

6. **graduate —— 知识沉淀进 docs/。** 结构性/约束性的设计稿——定义了后续代码必须遵守的规范、或大概率被反复参考的那种——完工后它的耐久知识沉淀进 `docs/`（**当前的真相**，常驻、完工不归档）。**active 的 `docs/` 在真相优先级上压过 `archive/` 里的旧 spec。**

   **两条路，用哪条取决于该结构性知识是否已有 docs 条目在管：**

   - **graduate（新建）**：全新结构域——在 frontmatter 打 `graduate: true` 标记（可在整个 active 生命周期内任意时刻补标）；landing 时把 spec **本体改写成解释性 docs**（"当前真相"视角）并**搬进 `docs/`**，源 `specs/` 下的文件随改写一并移走，**不留 archive 双胞胎**。改写后的 doc 补齐 `when_to_read` / `applies_to` / `when_to_update`（spec 本无这些字段，不补则脱离保鲜网）。无 `graduate: true` hint → 普通归档，不二次识别。
   - **更新既有 doc**：该知识已有 `docs/` 条目在管其主题 → 实现时直接改那份既有 doc，不 graduate 成新文件，spec 走普通归档路。（本 spec 自身走的就是这条路——它的耐久知识沉进 `model-architecture.md`/`spec-lifecycle.md`，frontmatter 不打 `graduate: true`，不是遗漏，是用对了路。）

   幂等键：`graduate: true` 的 done spec **仍在 `specs/`** 才触发改写——一旦 landing 改写移走，触发键消失，preflight 扫不到、不重复改写；landing 中途失败源文件还在，preflight 接着做。

## 关键不变量（最容易踩的）

- **done ≠ archived。** 到 `done` 文件仍在源文件夹；只有 landing 真的跑过才算归档。AI 绝不在没跑 landing 时声称某项已归档。
- **rejected = 直接删文件**（仅在用户明确指示下）。git log 是历史，commit body 记一行原因。**没有 `scrapped` 状态、没有墓碑分组**。
- **landing 失败不回滚 `done`。** `done` 断言的是"用户批准"，不是"landing 的 smoke-check 过了"，二者正交。landing 中途失败，文件仍停在 done-but-unlanded，下次 landing 扫到它。
- **谁动什么：** `status` 仪式做 `idea→active`（轻）；`done` 把棒交给 `landing`；只有 `landing` 搬进 `archive/`、回写 cockpit、重生成 INDEX。

> 出处：`skills/preflight/protocol.md` § Lifecycle / § The two axes；checkpoint 细节见 `skills/preflight/exit-ritual.md` § Checkpoint。
