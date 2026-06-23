# ⚠ WSL bash shadows Git Bash in tests

SUMMARY: On Windows, WSL bash shadowing Git Bash makes bash-invoked tests fail with returncode 127 — environment noise, not a real failure.
READ WHEN: when scripts/tests that bash-invoke hooks fail with returncode 127

---

## Signature

- symptom: `/bin/bash: E:projectstoolsflightdeckhookssession-start: No such file or directory`
- error_type: —
- where: scripts/tests/test_hooks.py `_run`（subprocess 调 bash 执行 hooks/ 脚本）
- trigger: Windows 上 PATH 把 `bash` 解析到 `C:\WINDOWS\system32\bash.EXE`（WSL）时跑 pytest——17 个 hooks 测试全部 returncode=127

## 症状/复现

`pytest scripts/tests/` 在本机 17 failed / 141 passed，失败全在 `test_hooks.py`；`uv run pytest` 同样失败。stderr 里 Windows 路径的反斜杠被整段吞掉（`E:projectstools…`），exit 127。2026-06-08 同套件曾全绿（rollout 记录"178 tests 绿"），说明是 PATH 环境漂移，非代码回归。

## 根因

我假设「PATH 上的 `bash` = 能吃 Windows 路径的 Git Bash」，实际 `C:\WINDOWS\system32\bash.EXE` 是 WSL 启动器：它把 `E:\projects\...` 当 POSIX 字符串处理、反斜杠被剥掉，目标脚本路径变成不存在的文件 → 127。测试代码用裸 `bash` 名解析，谁排 PATH 前面谁赢。

## 修法

跑 hooks 测试前确认 `(Get-Command bash).Source` 指向 Git Bash（`...\Git\...\bash.exe`），不是 `System32\bash.EXE`。是 WSL 时：临时把 Git Bash 目录前置到 PATH 再跑，或在 Git Bash 终端里跑。判定测试失败是否环境噪音的快捷依据：症状串里 Windows 路径反斜杠被吞 + 127。根治方向（未做）：`test_hooks.py` 显式定位 Git Bash（如经 `git --exec-path` 推导）而非裸 `bash`。

## Cases

- 2026-06-10 首次
