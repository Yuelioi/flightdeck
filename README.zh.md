# Flightdeck

Flightdeck 是一个面向 AI 的 Markdown 长期工作台。新会话无需依赖旧聊天，就能恢复一个目标、
当前事实、下一步、稳定上下文、执行细节和相关链接。

发布产品只有 Markdown 与宿主 manifests；没有服务器、CLI、数据库、schema、generator、私有
checkpoint 图或生成态。

## 文件模型

```text
flightdeck/
  deck.md
  work/<work-id>/
    index.md
    context.md
    plan.md          # 可选的完成汇总
    slices/          # 仅保存从 Plan 展开的持久执行细节
    references/      # 可选；由本 Work 拥有的产物
  knowledge/<subject>/<topic>.md
```

- `deck.md` 只有一份 Open Work 列表；非空时恰好标记一个 Focus，并可保留少量稳定项目链接。
  Focus 只是导航，不是生命周期状态。
- `index.md` 是恢复入口，负责 Goal、Status、Current、Next 和当前执行指针。Work 只有 `Open`、
  `Finished`、`Stopped` 三种状态。
- `context.md` 保存该目标稳定的事实、约束、决策与术语。
- `plan.md` 按需创建，负责阶段顺序和 Slice 完成汇总，不复制 Work 状态。
- Slice 保存必须跨新会话或提交恢复的一个交付物或决定。Step 留在 Slice 内；每个 Slice 都由
  一个 Plan 项链接。
- `knowledge/` 是按真实需求增长的项目操作手册，保存跨 Work 可复用的当前正向实践。

Finished 或 Stopped 的 Work 保留稳定路径，但离开 Deck 的 Open Work 列表。

## 自然语言操作

用户只需用普通语言表达意图：开始一项长期工作、继续指定或 Focus Work、切换会话前保存，
或结束/停止 Work。由 Flightdeck 判断哪些可见文档需要维护。

恢复时读取选中的 Work page、必需 context、已有的低分辨率 Plan、Next 中最多三个必需本地
链接以及实时 Git 状态。其他 Work、Slices、References 和 Knowledge 保持惰性。

Save 只重写恢复语义发生实质变化的文档，绝不自动 stage、commit、push、tag、建分支或创建
私有 Git checkpoint。

## 复杂与不确定的 Work

只有目标确实需要多个阶段或验收项时才创建 Plan；只有某个 Plan 项需要独立持久的 Current 与
Next 时才创建 Slice。

当 Goal 清楚但路线不清楚时，可使用 Wayfinding 阶段，一次解决一个 Decision Slice。
`Not yet specified` 可以保留尚无法精确表述的不确定性；Delivery Slice 必须分开，避免把“已
决定”误作“已交付”。

## 专业 skill 产物

Flightdeck 将受支持、属于某个 Work 的领域上下文、决策、研究、规格、审查和执行拆解写入
owning Work。源码变更、外部系统记录、临时文件和不受支持的产物保留在权威自然位置并链接。

项目级术语仍在根 `CONTEXT.md`，架构决策仍在 `docs/adr/`。Handoff 由普通 Flightdeck Save
代替，不再建立另一份协议文档。

## Knowledge

Knowledge 是按真实需求增长的项目操作手册；每个自然 subject 路径只保存一项可独立应用的
正向实践，例如 `flightdeck/knowledge/ui/form-errors.md`。它既不是宽泛的项目记忆，也不是
强制规则仓库。

当前动作出现项目特有的实践问题时，Work 先读取自己已经链接的相关 Knowledge，再按有限的
subject 路径、文件名和标题搜索。指导只影响判断；普通查阅不留日志，只有新会话仍需要时才
持久链接。只晋升已经验证、很可能跨 Work 复用且可自包含的结论；被事实推翻的指导应重写或
删除，未解决的研究留在 Work。不要增加强制 taxonomy、索引、kind、激活或路由字段、revision、
history、stale 标记、recheck ledger 或 trap 分类。

## 操作边界

Flightdeck 假定同一仓库同一时刻只有一个顶层 AI 会话。该会话可以协调子代理，但必须统一
汇总权威 Work 状态；Flightdeck 不提供跨顶层会话的锁、认领或兼容协议。

## 本地插件

`plugins/flightdeck` 是 Codex 与 Claude 共用的自包含插件包。在本仓库的 Codex marketplace
中运行：

```text
codex plugin add flightdeck@flightdeck-local
```

Claude Code 本地开发可直接加载：

```text
claude --plugin-dir plugins/flightdeck
```

## 文档

- [格式与写作指南](docs/format.md)
- [升级旧版或已偏移的 workspace](docs/upgrade.md)
- [完整示例](examples/deck/README.md)
- [架构决策](docs/adr/)
- [贡献说明](.github/CONTRIBUTING.md) 与 [安全策略](.github/SECURITY.md)
- [English README](README.md)

Flightdeck 使用 MIT License。
