---
status: active
when_to_read: 改 regen_cockpit_inprogress / format_row 的 INDEX 行渲染，或新增 active 的 spec/plan 却可能漏写 summary 前
applies_to: [scripts/flightdeck_index.py, regen_cockpit_inprogress, format_row, summary, cockpit]
last_updated: 2026-06-05
---

# active workflow 缺 summary 让 cockpit 进行中投影抛 KeyError

## 现象

`status: active` 的 spec/plan 工件若 frontmatter **漏写 `summary`**，跑 `flightdeck_index.py <deck>`
重生 cockpit 时直接 `KeyError: 'summary'` 崩溃，整次 regen 失败（INDEX/cockpit 都写不出）。

## 根因（2026-06-05 dogfood 实测，修正了 cockpit 早先的归因）

崩点**不在** `format_row`——`format_row` 已是防御写法：

```python
# scripts/flightdeck_index.py，format_row()，SUMMARY_KINDS 分支
return f"{link} {DASH} {status} {DASH} {fm.get('summary', '⚠ summary 缺失')}"
```

缺 `summary` 时它渲染哨兵 `⚠ summary 缺失`，不抛错。

真正的硬下标在 **`regen_cockpit_inprogress`**（cockpit `## 进行中` AUTO 区投影）：

```python
# scripts/flightdeck_index.py，regen_cockpit_inprogress()
row = f"- [{name}]({kind}/{name}) {DASH} {fm['summary']}"   # ← active 工件缺 summary 即 KeyError
```

只有 `status: active` 的 spec/plan 会进这条路径（`idea`/`done`/`scrapped` 被 `status != "active"`
过滤掉），所以触发条件是「**把一个缺 summary 的 workflow 工件翻成 active**」。

> 旁注：`layout_verdict` 里对 workflow 缺 `summary`/`status` 会判 `malformed`（`scripts/flightdeck_index.py`
> 末尾），那是布局判定路径，与 regen 崩溃是两条独立的链路。

## 影响

- `summary` 是 workflow 的**必填**字段（contract 见 `skills/new/SKILL.md`），正常经 `/flightdeck:new`
  创建不会漏——脚本 stamp 时强制带。手搓 frontmatter 或外部工具改写才会落空。
- 一旦命中，`regen` 整体失败，cockpit/INDEX 停在旧值，且报错信息（裸 `KeyError: 'summary'`）
  不指明是哪个文件，排查要逐个翻 active 工件。

## 修法（2026-06-05 已实施）

把 `regen_cockpit_inprogress` 的 `fm['summary']` 改成与 `format_row` 一致的防御取值：

```python
row = f"- [{name}]({kind}/{name}) {DASH} {fm.get('summary', '⚠ summary 缺失')}"
```

回归测试守卫：`scripts/tests/test_flightdeck_index.py::CockpitProjectionRobustnessTest`
——active 工件缺 summary 时投影渲染哨兵、不抛 KeyError。

> 仍可考虑的更狠做法（未做）：regen 前对每个 active workflow 校验必填字段，缺失则报
> 「文件名 + 缺哪个字段」而非哨兵——诊断更友好，但当前哨兵 + 测试已够。
