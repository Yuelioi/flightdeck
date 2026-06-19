---
status: active
synced: true
last_updated: 2026-05-29
when_to_read: before writing or editing any source-code comment
applies_to: [comments, code-style, documentation]
---

# Comments Playbook

写/改任何源码注释**前置**读这份. 这是项目无关的通用规范.

依据 (有疑问回到原始出处, 别凭印象):
- Google Style Guides — 注释解释 *why*, 不复述 *what* (<https://google.github.io/styleguide/>)
- Go Doc Comments — 文档注释写完整句、以标识符开头 (<https://go.dev/doc/comment>)
- 经典原则: **代码说"怎么做", 注释说"为什么"; 版本控制 / issue tracker 持有历史, 注释持有意图.**

---

## 1. 默认不写注释

好的命名 + 类型签名已经在说"代码在干啥". 加注释前先问:

> **删掉这行注释, 半年后的我能看懂这段代码吗?**

答得上 → 别写. 注释不是免费的: 它占行数, 会跟代码漂移, 读者还得分辨它可不可信.

## 2. 要写就只写这四类

注释的合法 use case —— 全是**代码本身表达不出来**的东西:

| 该写 | 例子 |
| --- | --- |
| **为什么 (意图/取舍)** | `// 用轮询而非回调: 第三方 SDK 的回调不保证在主线程` |
| **微妙不变量 / 契约** | `// 调用方保证 dir ∈ {-1,0,1}, 这里不再 normalize` |
| **反直觉行为 / 坑** | `// 必须先 flush 再 close, 否则末尾 buffer 丢` |
| **特定 bug / 平台 workaround** | `// Win10 下 WGC 首帧全黑, 跳过第一帧` |

不写"代码逐行在干啥"——那是冗余 (`i++ // i 加一`). 命名好就不需要.

## 3. 禁忌: 别把"项目过程元信息"塞进注释

注释里**禁止**出现下列东西 —— 它们不回答"代码在干啥/为啥", 只是把项目过程的临时坐标硬塞进源码:

| 禁忌 | 例子 |
| --- | --- |
| spec / 设计文档引用 | `// spec §4.2`, `// 详见 design.md`, `// 见 backlog.md` |
| 计划阶段 / 任务码 | `// Phase 5 实装`, `// P4.a`, `// C2 改的`, `// v1b` |
| reviewer 出处 | `// GPT review 改的`, `// Gemini 推荐`, `// 见 review.md` |
| polish 轮次 / 修复批次 | `// round 3 polish`, `// fix batch A`, `// 修 b63bf12 回归` |
| 日期戳 / 署名 | `// (2026-05-27 校对时已没了)`, `// 张三加的` |
| 历史考古 | `// 之前用 X 改成 Y`, `// 删了旧实现`, `// 跟老 Foo 对齐`, `// Mirrors old Bar deletion` |
| TODO / FIXME 散弹 | `// TODO: 后续改 X`, `// FUTURE-WORK: 优化 Y`, `// 长期可拆` |

**为什么这些是坑**:

1. **会腐烂** —— spec/plan 会被归档/删除/改名, 注释里的引用变成 dangling 指针; 指向的文件可能根本不在仓库里 (e.g. gitignored 的本地文档), 别人 clone 后看到的是死链.
2. **需要解码环** —— `P4.a` / `C2` / `Phase 5` 对没参与那段历史的人 (包括半年后的你) 是噪声.
3. **走错地方** —— 历史属于 git, 待办属于 issue tracker, 设计理由属于 design doc; 它们各有生命周期管理, 塞进注释等于绕过管理.
4. **诱导不读源码** —— "见 spec" 是在邀请读者别读代码去追文档, 而文档可能已经和代码脱节.

## 4. 正例 vs 反例

```go
// ❌ 反例 —— 全是过程元信息, 没说代码为啥这样
// spec §5.2 不做防御 normalization. Phase B 实装. GPT 第 3 轮 review 推荐保留 cache.
// FUTURE-WORK: Foo 幂等化 (P4) 后此 cache 可删.
if dir == c.lastDir {
    return
}

// ✅ 正例 —— 说清"为什么短路"这个非显然的 why
// 短路: 上游会重发同一方向事件, 不去抖游戏会误判成 key-repeat.
if dir == c.lastDir {
    return
}

// ✅ 也对 —— 条件本身够清楚, 啥都不写
if dir == c.lastDir {
    return
}
```

## 5. 历史 / 待办 / 设计理由 —— 各归各位

源码注释里**最多**留就地的意图/不变量. 其余按持久度分流到有生命周期管理的地方:

| 内容 | 去处 |
| --- | --- |
| "为什么改成这样 / 改动历史" | git commit message / PR description |
| 跨会话待办、不阻塞主线 | issue tracker / backlog 文档 |
| 想法尚未成熟 | 草稿 / sketch 文档 |
| 已成形的设计 | design doc |

`TODO` 真要写: 只留**稳定引用** (issue 编号这类不会消失的), 一行问题描述, 不带人名/日期/阶段码. 但更推荐直接开 issue —— 代码里的 TODO 没人追踪, 半年后就是垃圾.

## 6. 自查 (写完一组代码前自己跑一次)

```bash
# 命中下列模式的注释多半违规, 逐条删/改写/搬走
grep -rniE "(spec[ ]*§|spec[ ]*sec|见.*spec|详见|Phase[ ]+[0-9A-G]|[ (]P[0-9]+\.|[ (]C[0-9]+ |GPT[ ]+review|Gemini|reviewer|round[ ]+[0-9]+|FUTURE-WORK|TODO|FIXME|HACK|XXX|之前用|之前是|历史上|跟老|改成|Mirrors|deprecated|202[0-9]-[0-1][0-9])" \
    --include="*.go" --include="*.ts" --include="*.vue" --include="*.py" --include="*.rs" \
    <源码目录>
```

理想**零命中** (`HACK`/`XXX` 极个别可留, 但要能解释为啥不进 tracker).

命中后三选一:
1. **删** —— 注释没必要
2. **改写** —— 只留"为什么/不变量"那部分, 去掉过程坐标
3. **搬走** —— TODO 搬 tracker/backlog, 历史搬 commit message, 然后删注释
