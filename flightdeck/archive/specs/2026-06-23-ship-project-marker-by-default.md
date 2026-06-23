---
status: done
summary: Master shared files ship the project-section boundary marker + an empty project-overrides stub so consumers never hand-author the marker; closes the silent-data-loss path where a marker-less consumer file gets its local additions overwritten by --sync-pull. Adds a walkaround/sync-status WARN safety net for marker-less drifted synced files.
last_updated: 2026-06-23
---

# Ship the project-section marker by default

## 问题

`PROJECT_MARKER`（`<!-- flightdeck:project-specific -->`）是 sync 分区单写者的唯一边界锚，
但它**只活在 sync SKILL / `docs/shared-knowledge-sync.md` 的散文里**——母库文件按现约定
不带 marker（doc 第 37 行、sync SKILL 第 21 行：“the master's own files carry no marker”）。
于是用户在最需要它的那一刻（首次 vendor 完、想加项目笔记）**看不到这个契约**。

更糟：它不是“难添加”，是**静默数据丢失陷阱**。`scripts/flightdeck_index.py` 的
`shared_region()` 和 `pull_shared()` 在 `body.find(PROJECT_MARKER) == -1` 时，把
**整个 consumer body** 当 shared：

```python
def pull_shared(consumer_text, master_text):
    ...
    idx = body.find(PROJECT_MARKER)
    if idx == -1:
        return fm + master_body      # ← consumer 本地补充被母库整段覆盖，无警告无 diff
```

复现路径：vendor 一个无 marker 的 checklist → 用户在末尾直接追加项目笔记（不知道要先加 marker）
→ 下次 `--sync-pull` 静默覆盖。

## 决定

采纳**方案 A + 安全网**（在对话中收敛；A 比“sync skill 首次 vendor 后追加 stub”的 B 更
机械、不依赖 AI 记得做，契合 sync 的 zero-AI 取向）：

### A. 母库 shared 文件自带 marker + stub

每个**打算被 vendor 的**母库 shared 文件（checklist / doc）以固定收尾结构结束：

```
<!-- flightdeck:project-specific -->

## Project overrides

_This section is yours — sync never overwrites anything below the marker above._
```

- `shared_fingerprint` 本就只算 marker **以上** → stub 不进指纹，不影响 `in-sync` 判定。
- mode-B 首次 vendor 整文件拷 → marker + stub 自动随行，用户在 stub 下填即可，
  **永不需要知道 / 拼写 marker**。
- 母库文件**自身**那段 stub 是惰性模板（只在 vendor 时作种子）；母库自己不消费它。
- 这翻转旧约定“母库文件不带 marker”——doc / SKILL 的相应散文要改：可 vendor 的母库 shared
  文件**应当**以 marker + stub 收尾（纯内部、不外发的母库文件仍可无 marker）。

### promote（mode C）交互

promote 把 consumer 的 shared body（marker 以上）上提母库同 relpath。上提后**要给母库补回
marker + stub**，否则新上提的母库文件退化成无 marker，破坏 A 的不变量。

### 安全网：marker-less drifted synced 文件 WARN

A 让常路正确，但兜不住用户**删掉或拼错** marker。加一道检测：对满足
「`synced: true` ∧ 本地 body 与母库 shared 指纹不一致 ∧ 文件无 marker」的文件报
WARN（如 `--sync-status` 输出一类状态 + walkaround 一条 INFO/WARN）：
“local additions will be overwritten on next pull — add the project-specific marker first”。
捕获异常路的残余静默丢失风险。

## 影响面

- `~/.flightdeck/**` 现有可 vendor 文件（comments.md / commits.md / subagent-guide.md 等）补 marker + stub。
- 本仓 vendored 副本随之 re-pull（commits.md 已手加 marker，需对齐 stub 措辞）。
- `docs/shared-knowledge-sync.md`：改“母库无 marker”约定 → “可 vendor 母库文件带 marker + stub”。
- `skills/sync/SKILL.md`：boundary-marker 节、mode-B、mode-C(promote) 散文同步。
- `scaffolds/full/**`：若 scaffold 含示例 vendored 文件，示范 marker + stub 收尾。
- `scripts/flightdeck_index.py` / `.js`：新增 marker-less-drift WARN（保持 py/js byte-parity + 测试）。
- `skills/walkaround/SKILL.md`：sync drift 审计纳入这条 WARN。

## 非目标

- 不改 fingerprint 算法 / `synced` 标记语义 / relpath 不变量 / consumers 注册表。
- 不引入 marker 以下内容的任何同步（项目段仍永不上推/下拉）。
- 不强制纯内部母库文件带 marker（只约束“打算被 vendor 的”那批）。

## 失败模式溯源（recurrence anchor）

根因：把“边界锚”这个用户必须遵守的契约，做成了**不可见、需手工逐字 authored 的隐式耦合**，
且缺省（无 marker）恰好是数据丢失而非安全失败。教训：任何“用户必须逐字写对、否则静默吃数据”
的契约，应当**随产物自带**（correct-by-default）+ **检测异常**（fail-loud），不能只靠散文交代。
