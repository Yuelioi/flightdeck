---
status: active
when_to_read: 改 hook 的 python 运行时探测，或排查 Windows 上 board-sync/Stop hook 为何没生效前
applies_to: [hooks/stop, hooks/session-start, python, windows, board-sync, command-v, store-stub, run-hook.cmd]
last_updated: 2026-06-07
resolved_by: hooks/stop（python 可用性自检 `-c ''`）
---

# Windows python3 桩致 board-sync Stop hook 静默失效

## Signature
- symptom: `Stop hook 退出 0 但 cockpit ## 进行中 / INDEX AUTO 区未被重生；FLIGHTDECK_HOOK_DEBUG 下 python3 跑任何脚本 exit 49`
- error_type: —
- where: hooks/stop —— python 运行时探测循环（`for c in python3 python`）
- trigger: 在 Windows（git-bash）上回合结尾触发 Stop hook，且 `python3` 解析到 Microsoft Store 的 WindowsApps 桩

## 症状/复现

`hooks/stop` 回合末应静默重生 board AUTO 区，但 Windows 上 deck 始终靠 agent/landing 才保持一致——hook 本身从未真正 regen。复现：git-bash 里 `command -v python3` 返回 `/c/Users/<u>/AppData/Local/Microsoft/WindowsApps/python3`（Store 桩），`python3 --version` → `exit 49`（不真跑 Python，本意是弹应用商店）。stop 把所有输出 `>/dev/null 2>&1 || true` 吞掉 + 末尾恒 `exit 0`，故失效完全无声。

## 根因

stop 的探测只做**存在性**检查（`command -v "$c"`），选中第一个"存在"的 `python3`——即 Store 桩。桩可被 `command -v` 找到却不能执行，于是 `flightdeck_index.py` 从未被有效调用。`session-start` 不用 python，故不受影响（注入照常）；只有 board-sync 这条受害，且因双重静默（吞输出 + 恒 exit 0）长期不可见。

## 修法

探测加**可用性自检**：`command -v "$c" >/dev/null 2>&1 && "$c" -c '' >/dev/null 2>&1`——用跑空程序 `-c ''` 确认解释器真能执行（桩 exit 非 0 被跳过），落到真 `python`；候选表补 `py`（Windows 启动器）。同时引入 `FLIGHTDECK_HOOK_DEBUG=1`：在 project-dir/gate/python/regen 各打 stderr 诊断行，破"双重静默"盲区——这类失效以后能 `FLIGHTDECK_HOOK_DEBUG=1` 直接看到选了哪个 python、有没有 regen。

教训：凡"存在即用"的外部运行时探测，在 Windows 上都要防 Store 桩——存在 ≠ 可执行。任何"静默降级 + 恒 exit 0"的设计必须配一个 debug 开关，否则失效不可观测。

## Cases
- 2026-06-07 首次——hook-primary rollout 相位1 写 stop project-dir 泛化测试（断言 temp deck 生成 INDEX.md）时暴露：改完 project-dir 测试仍红，溯因发现 python3 桩。修于同一 commit（`hooks/stop` 可用性自检 + `py` 候选 + HOOK_DEBUG）。
