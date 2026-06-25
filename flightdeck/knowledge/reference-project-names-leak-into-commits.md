# ⚠ reference-project names leak into committed artifacts

SUMMARY: A project name / path handed to you only as design reference must never land in a committed flightdeck artifact (commit message, spec, cockpit, knowledge) — this repo is public-bound and ships, so anonymize reference decks to neutral labels + portable facts.
READ WHEN: before committing, or writing a spec / cockpit / knowledge file, that draws on another project you were pointed at purely as reference

---

## 出处

设计「读头分层」时,用户给了两个外部 deck 当**验证参考**。我把它们的**项目名**写进了 commit message + cockpit + knowledge 文件——而本仓库是 public(GitHub-bound)、会 ship,等于把用户的其它项目名公开泄露。用户当场叫停:「我给你参考用的,你给我暴露了,万一我的项目是隐私呢?」

## 根因

**「给你看」≠「授权写进 git」。** 参考资料是过程输入,不是产物。committed 面(commit message / specs / cockpit / knowledge / README——任何进版本库的东西)会被 push、被 ship、被检索,留痕不可控;而设计**只需要可复用的结构事实**,不需要是谁。

## 规则

引用外部项目做参考时,committed 面一律**匿名化**:

- 用中性标号:「外部参考 deck A / deck B」「某用户项目」。
- 只留**可移植的事实**:规模、结构、分布(如「76 知识、65 reactive trap」「59 知识、11 checklist」),这些才是设计依据。
- **不留**:项目名、仓库名、绝对/相对路径、URL、任何能反推身份的独有术语。
- 对话里出现名字没关系(那是过程);**手指要落到 git 之前**过一遍这条。

## 范围

适用任何会进 git 的写入。不适用于一次性的对话回复 / 临时工具调用(那些不留痕)。历史里既有的泄露:**不回溯重写**(用户定:之前的算了),只保证此后干净。
