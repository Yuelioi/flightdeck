---
status: active
summary: 实现 /flightdeck:new + flightdeck_new.py——TDD 建脚本（kind→folder 常量表、按-kind frontmatter、命名 dateless/dated、参数校验报错、调 flightdeck_index regen + status-aware stdout），再建 skills/new/SKILL.md（fast path + 权威撰写契约 fallback），接发现钩子（protocol 节 + emit 模板行 + description），验证 + dogfood，最后文档 + 发布提醒
last_updated: 2026-06-04
implements: specs/2026-06-04-new-artifact-authoring-convention-design.md
---

# /flightdeck:new 撰写入口 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 提供一个确定性的"撰写入口"——`/flightdeck:new` skill 包 `flightdeck_new.py`，把"放哪 + 按-kind frontmatter + 命名 + regen"从每次推导变成一次盖章。

**Architecture:** 仿 `launch`（skill 包 `flightdeck_init.py`）。`flightdeck_new.py`（Python stdlib）做机械层：校验参数 → 按 kind→folder 常量表落目录 → 命名（idea dateless / 否则带日期）→ 盖按-kind frontmatter → 写 `# Title` 骨架 → 调 `flightdeck_index.main([deck])` regen。`skills/new/SKILL.md` 是 markdown fallback + 权威"撰写契约"。发现靠 protocol 节 + emit 模板行 + skill description（改不了外部 brainstorming，故常驻指针）。

**Tech Stack:** Python 3 stdlib（argparse/datetime/re/pathlib）；stdlib `unittest`（运行：`uv run python -m unittest`）；markdown（SKILL + docs）。`flightdeck_new.py` 复用 `flightdeck_index` 的 regen，不重复实现派生。

---

## File Structure

- **Create** `scripts/flightdeck_new.py` — 机械层：校验 + 命名 + frontmatter + 落目录 + 调 regen。一个职责（建工件），≈100 行。
- **Create** `scripts/tests/test_flightdeck_new.py` — happy path + 错误路径（stdlib unittest，仿 `test_flightdeck_init.py`）。
- **Create** `skills/new/SKILL.md` — `/flightdeck:new`：fast path + 权威撰写契约 fallback（自动发现，无需注册）。
- **Modify** `skills/preflight/protocol.md` — 加一节 canonical "Authoring new artifacts"。
- **Modify** `skills/emit-agents-md/SKILL.md`（emit 模板）— AGENTS.md 块加一行 authoring 指针。
- **Modify** `README.md` / `README.zh.md` / `adapters/claude/README.md` / `adapters/gemini/README.md` — 命令表/清单加 `new`。

---

## Task 1: `flightdeck_new.py` 核心（命名 + 按-kind frontmatter + 写骨架，happy path）

**Files:**
- Create: `scripts/flightdeck_new.py`
- Create: `scripts/tests/test_flightdeck_new.py`

- [ ] **Step 1: 写失败测试** (`scripts/tests/test_flightdeck_new.py`)

```python
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flightdeck_new import new


def _deck(d):
    """Make a minimal deck skeleton (folders only) under temp dir d."""
    deck = Path(d) / "flightdeck"
    for f in ["specs", "plans", "incidents", "checklists", "charts"]:
        (deck / f).mkdir(parents=True)
    return deck


class NewHappyPathTest(unittest.TestCase):
    def test_idea_spec_is_dateless_with_minimal_frontmatter(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            path = new(deck, "spec", slug="my-idea", title="My Idea",
                       status="idea", regen=False)
            self.assertEqual(path, deck / "specs" / "my-idea.md")
            text = path.read_text(encoding="utf-8")
            self.assertIn("status: idea", text)
            self.assertNotIn("last_updated:", text)   # idea omits last_updated
            self.assertIn("# My Idea", text)

    def test_active_spec_gets_date_prefix_and_last_updated(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            path = new(deck, "spec", slug="real-design", title="Real Design",
                       status="active", summary="a gist", date="2026-06-04", regen=False)
            self.assertEqual(path, deck / "specs" / "2026-06-04-real-design.md")
            text = path.read_text(encoding="utf-8")
            self.assertIn("status: active", text)
            self.assertIn("summary: a gist", text)
            self.assertIn("last_updated: 2026-06-04", text)

    def test_plan_carries_implements(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            path = new(deck, "plan", slug="roll-it", title="Roll It",
                       status="active", implements="specs/x.md", date="2026-06-04", regen=False)
            self.assertEqual(path, deck / "plans" / "2026-06-04-roll-it.md")
            self.assertIn("implements: specs/x.md", path.read_text(encoding="utf-8"))

    def test_knowledge_defaults_active_and_carries_routing_fields(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            path = new(deck, "incident", slug="oops", title="Oops",
                       when_to_read="before X", applies_to=["a", "b"],
                       date="2026-06-04", regen=False)
            self.assertEqual(path, deck / "incidents" / "2026-06-04-oops.md")
            text = path.read_text(encoding="utf-8")
            self.assertIn("status: active", text)           # knowledge default
            self.assertIn("when_to_read: before X", text)
            self.assertIn("applies_to: [a, b]", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd scripts/tests && uv run python -m unittest test_flightdeck_new -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'flightdeck_new'`

- [ ] **Step 3: 写实现** (`scripts/flightdeck_new.py`)

```python
"""flightdeck_new.py — create a new deck artifact with correct frontmatter + naming + regen.

The mechanical "authoring entry": instead of an agent re-deriving where a spec/plan/
incident/checklist/chart goes, what frontmatter it needs, and remembering to regen the
INDEX/cockpit, this stamps it deterministically. Mirrors flightdeck_init.py. Pure stdlib.
"""

import argparse
import datetime
import re
import sys
from pathlib import Path

import flightdeck_index  # sibling in scripts/; reused for regen after create

KIND_FOLDER = {
    "spec": "specs",
    "plan": "plans",
    "incident": "incidents",
    "checklist": "checklists",
    "chart": "charts",
}
WORKFLOW = {"spec", "plan"}
KNOWLEDGE = {"incident", "checklist", "chart"}
SLUG_RE = re.compile(r"^[a-z0-9-]+$")
_DEFAULT_STATUS = {
    "spec": "idea", "plan": "idea",
    "incident": "active", "checklist": "active", "chart": "active",
}


def _frontmatter(kind, status, date, summary, implements, when_to_read, applies_to):
    lines = ["---", f"status: {status}"]
    if kind in WORKFLOW:
        if summary:
            lines.append(f"summary: {summary}")
        if status != "idea":            # idea-stage workflow omits last_updated (convention)
            lines.append(f"last_updated: {date}")
        if implements:
            lines.append(f"implements: {implements}")
    else:                               # knowledge — routing fields required
        lines.append(f"when_to_read: {when_to_read}")
        lines.append(f"applies_to: [{', '.join(applies_to)}]")
        lines.append(f"last_updated: {date}")
    lines.append("---")
    return "\n".join(lines)


def new(deck, kind, slug, title, status=None, summary="", implements=None,
        when_to_read=None, applies_to=None, date=None, regen=True):
    """Create one deck artifact; return its Path. Raises ValueError/FileExistsError."""
    date = date or datetime.date.today().isoformat()
    status = status or _DEFAULT_STATUS[kind]

    folder = Path(deck) / KIND_FOLDER[kind]
    filename = f"{slug}.md" if status == "idea" else f"{date}-{slug}.md"
    path = folder / filename
    if path.exists():
        raise FileExistsError(f"artifact already exists: {path}")

    fm = _frontmatter(kind, status, date, summary, implements, when_to_read, applies_to)
    path.write_text(f"{fm}\n\n# {title}\n", encoding="utf-8")

    if regen:
        flightdeck_index.main([str(deck)])
    return path
```

> Note: validation guards are added in Task 2 (the happy-path tests above pass valid input, so they go green now). `import flightdeck_index` resolves because a script's own dir is on `sys.path[0]`, and the test inserts `scripts/` on the path.

- [ ] **Step 4: 跑测试确认通过**

Run: `cd scripts/tests && uv run python -m unittest test_flightdeck_new -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/flightdeck_new.py scripts/tests/test_flightdeck_new.py
git commit -m "feat(flightdeck): flightdeck_new.py 核心——命名+按kind frontmatter+写骨架"
```

---

## Task 2: 参数校验（非法即报错退出）

**Files:**
- Modify: `scripts/flightdeck_new.py` (在 `new()` 落盘前加 guards)
- Modify: `scripts/tests/test_flightdeck_new.py` (加错误路径 test class)

- [ ] **Step 1: 写失败测试**（追加到 `test_flightdeck_new.py`，在 `if __name__` 之前）

```python
class NewValidationTest(unittest.TestCase):
    def test_unknown_kind_raises(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            with self.assertRaises(ValueError):
                new(deck, "widget", slug="x", title="X", regen=False)

    def test_illegal_slug_raises(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            for bad in ["Has Space", "中文", "Upper", "under_score", ""]:
                with self.assertRaises(ValueError):
                    new(deck, "spec", slug=bad, title="X", regen=False)

    def test_missing_title_raises(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            with self.assertRaises(ValueError):
                new(deck, "spec", slug="x", title="", regen=False)

    def test_knowledge_without_routing_fields_raises(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            with self.assertRaises(ValueError):
                new(deck, "incident", slug="x", title="X", regen=False)  # no when_to_read/applies_to

    def test_implements_on_knowledge_raises(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            with self.assertRaises(ValueError):
                new(deck, "incident", slug="x", title="X", when_to_read="w",
                    applies_to=["a"], implements="specs/x.md", regen=False)

    def test_refuses_if_exists(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            new(deck, "spec", slug="dup", title="Dup", status="idea", regen=False)
            with self.assertRaises(FileExistsError):
                new(deck, "spec", slug="dup", title="Dup", status="idea", regen=False)
```

- [ ] **Step 2: 跑确认失败**

Run: `cd scripts/tests && uv run python -m unittest test_flightdeck_new.NewValidationTest -v`
Expected: FAIL（`test_unknown_kind_raises` 会 KeyError 而非 ValueError；其余多数未拦截）

- [ ] **Step 3: 在 `new()` 顶部加 guards**（`scripts/flightdeck_new.py`，置于 `new()` 第一行 docstring 之后、`date =` 之前）

```python
    if kind not in KIND_FOLDER:
        raise ValueError(f"unknown kind: {kind!r} (one of: {', '.join(sorted(KIND_FOLDER))})")
    if not slug or not SLUG_RE.match(slug):
        raise ValueError(
            f"illegal slug: {slug!r} — must match ^[a-z0-9-]+$ "
            "(lowercase ascii / digits / hyphens, e.g. new-artifact-entrypoint)"
        )
    if not title:
        raise ValueError("title is required")
    _status = status or _DEFAULT_STATUS[kind]
    if kind in KNOWLEDGE and (not when_to_read or not applies_to):
        raise ValueError(f"{kind} requires --when-to-read and --applies-to (required routing fields)")
    if implements and kind not in WORKFLOW:
        raise ValueError(f"--implements is workflow-only; not valid for kind {kind!r}")
```

Then change the existing `status = status or _DEFAULT_STATUS[kind]` line to reuse `_status` (delete the duplicate; set `status = _status`). Final order in `new()`: guards → `date = ...` → `status = _status` → folder/filename → exists-check → write → regen.

- [ ] **Step 4: 跑确认通过（含 Task 1 的 happy path 不回归）**

Run: `cd scripts/tests && uv run python -m unittest test_flightdeck_new -v`
Expected: PASS (10 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/flightdeck_new.py scripts/tests/test_flightdeck_new.py
git commit -m "feat(flightdeck): flightdeck_new.py 参数校验——非法 kind/slug/字段报错"
```

---

## Task 3: regen 集成 + CLI main + status-aware stdout

**Files:**
- Modify: `scripts/flightdeck_new.py` (加 `main()` + stdout 区分；`new()` 的 regen 已在 Task 1)
- Modify: `scripts/tests/test_flightdeck_new.py` (加 regen-clean test)

- [ ] **Step 1: 写失败测试**（追加 test class）

```python
import flightdeck_index


class NewRegenTest(unittest.TestCase):
    def _full_deck(self, d):
        """A deck with the INDEX/cockpit files regen needs (copy from scaffold)."""
        import shutil
        scaffold = Path(__file__).resolve().parent.parent.parent / "scaffolds" / "full" / "flightdeck"
        deck = Path(d) / "flightdeck"
        shutil.copytree(scaffold, deck)
        return deck

    def test_regen_after_active_spec_leaves_index_clean(self):
        with tempfile.TemporaryDirectory() as d:
            deck = self._full_deck(d)
            new(deck, "spec", slug="demo", title="Demo",
                status="active", summary="demo gist", date="2026-06-04", regen=True)
            # index_drift returns a list of drift labels; empty == clean
            self.assertEqual(flightdeck_index.index_drift(deck), [])
```

- [ ] **Step 2: 跑确认通过（`new(..., regen=True)` 已调 `flightdeck_index.main`）**

Run: `cd scripts/tests && uv run python -m unittest test_flightdeck_new.NewRegenTest -v`
Expected: PASS（若 `index_drift` 签名不符，改用 `flightdeck_index.main([str(deck), "--check"])` 断言返回 0）

- [ ] **Step 3: 加 `main()` + status-aware stdout**（`scripts/flightdeck_new.py` 末尾）

```python
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Create a new flightdeck deck artifact (frontmatter + naming + INDEX/cockpit regen)."
    )
    ap.add_argument("deck", help="path to the flightdeck/ deck root")
    ap.add_argument("kind", choices=sorted(KIND_FOLDER))
    ap.add_argument("--slug", required=True, help="filename slug: ^[a-z0-9-]+$")
    ap.add_argument("--title", required=True, help="human title (becomes the H1)")
    ap.add_argument("--status", default=None,
                    choices=["idea", "active", "done", "scrapped", "obsolete", "superseded"])
    ap.add_argument("--summary", default="", help="one-line gist (drives the INDEX row)")
    ap.add_argument("--implements", default=None, help="workflow only: specs/<x>.md")
    ap.add_argument("--when-to-read", dest="when_to_read", default=None)
    ap.add_argument("--applies-to", dest="applies_to", default=None, help="comma-separated tags")
    ap.add_argument("--date", default=None, help="YYYY-MM-DD (default: today; override for backfill)")
    args = ap.parse_args(argv)

    applies = [t.strip() for t in args.applies_to.split(",")] if args.applies_to else None
    try:
        path = new(args.deck, args.kind, slug=args.slug, title=args.title,
                   status=args.status, summary=args.summary, implements=args.implements,
                   when_to_read=args.when_to_read, applies_to=applies, date=args.date)
    except (ValueError, FileExistsError) as e:
        print(f"refused: {e}")
        return 2

    status = args.status or _DEFAULT_STATUS[args.kind]
    print(f"created {args.kind} at {path}")
    if args.kind in WORKFLOW and status == "idea":
        print("INDEX updated; cockpit unchanged (status=idea)")
    elif args.kind in WORKFLOW:
        print("INDEX + cockpit (## 进行中) updated")
    else:
        print("folder INDEX updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 全测试 + CLI 冒烟**

Run: `cd scripts/tests && uv run python -m unittest test_flightdeck_new -v` → Expected: PASS (11 tests)
Run（CLI 冒烟，临时 deck）:
```bash
cd /e/projects/tools/flightdeck && D=$(mktemp -d) && uv run scripts/flightdeck_init.py "$D" --user t --date 2026-06-04 >/dev/null && uv run scripts/flightdeck_new.py "$D/flightdeck" spec --slug cli-demo --title "CLI Demo" --status idea && rm -rf "$D"
```
Expected: 打印 `created spec at .../specs/cli-demo.md` + `INDEX updated; cockpit unchanged (status=idea)`

- [ ] **Step 5: Commit**

```bash
git add scripts/flightdeck_new.py scripts/tests/test_flightdeck_new.py
git commit -m "feat(flightdeck): flightdeck_new.py CLI + regen 集成 + status-aware stdout"
```

---

## Task 4: `skills/new/SKILL.md`（fast path + 权威撰写契约 fallback）

**Files:**
- Create: `skills/new/SKILL.md`

- [ ] **Step 1: 写 `skills/new/SKILL.md`**（完整内容）

````markdown
---
name: new
description: Create a new flightdeck deck artifact (spec / plan / incident / checklist / chart) with correct per-kind frontmatter, naming, and auto-regenerated INDEX/cockpit — use this instead of hand-writing the file. Triggered by /flightdeck:new.
---

# Flightdeck New — author a deck artifact

The **authoring entry**. When you (or an external authoring skill like brainstorming /
writing-plans) need to produce a deck artifact, use this instead of hand-deriving the
location, frontmatter, naming, and INDEX/cockpit regen. It is the single authority for
**how a deck artifact is shaped** — the fast path stamps it via a script; the fallback
below is the same contract for hand-authoring.

**Shell-first handoff:** create the shell here first, then write the body into the
returned path. Don't write content elsewhere and move it afterward.

## Fast path (a Python runtime is reachable)

```
uv run <flightdeck-pkg>/scripts/flightdeck_new.py <deck> <kind> \
    --slug <kebab-slug> --title "<Title>" [--status idea|active|done] \
    [--summary "..."] [--implements specs/<x>.md] \
    [--when-to-read "..."] [--applies-to tag1,tag2]
```

It prints the created path. Then write the artifact body into that file.

## Authoring contract (also the no-runtime fallback — do this by hand)

**kind → folder**

| kind | folder |
|---|---|
| spec | `specs/` |
| plan | `plans/` |
| incident | `incidents/` |
| checklist | `checklists/` |
| chart | `charts/` |

**Naming:** `[<date>-]<slug>.md`. Add the `<YYYY-MM-DD>-` prefix **iff `status != idea`**;
an `idea` artifact is **dateless**. **Never auto-append `-design`** — `new-artifact.md` ✓,
not `new-artifact-design.md` (only if "design" is genuinely part of your slug).
**slug rule:** lowercase ascii, digits, hyphens only (`^[a-z0-9-]+$`). To make a slug from
a title: drop non-ascii, spaces → `-`, lowercase, keep `a-z0-9-`.

**Per-kind frontmatter**
- workflow (`spec` / `plan`): `status` + `summary` (recommended) + `last_updated` (omit for `idea`) + `implements:` (plan, optional).
- knowledge (`incident` / `checklist` / `chart`): `status` + `when_to_read` + `applies_to: [..]` + `last_updated` (all required).

**Default status:** workflow → `idea` (park; flip to `active` to start — that adds the date prefix). knowledge → `active` (knowledge is consumable the moment it exists; that's why its default differs from workflow's).

**After writing:** run `uv run <flightdeck-pkg>/scripts/flightdeck_index.py <deck>` to
regenerate INDEX + cockpit. An `active` workflow artifact projects into cockpit `## 进行中`;
an `idea` does not.

**If the target file already exists:** the script refuses; by hand, pick a different slug
or remove/rename the existing file first.

## Relationship to landing

`landing` already knows the knowledge-artifact convention and creates incidents/checklists
during the wrap ritual. `/flightdeck:new` is **usable for knowledge but not the required
path** there — both share the same frontmatter truth; use whichever fits the moment.
````

- [ ] **Step 2: 确认 skill 自动可用（无需注册）**

Run: `grep -n "skills" .claude-plugin/plugin.json`
Expected: `"skills": "./skills/"` —— 目录指针，`skills/new/SKILL.md` 自动发现。

- [ ] **Step 3: Commit**

```bash
git add skills/new/SKILL.md
git commit -m "feat(flightdeck): /flightdeck:new skill（fast path + 权威撰写契约）"
```

---

## Task 5: 发现钩子（protocol 节 + emit 模板行）

**Files:**
- Modify: `skills/preflight/protocol.md` (加 "Authoring new artifacts" 节)
- Modify: `skills/emit-agents-md/SKILL.md` (AGENTS.md 块模板加一行)

- [ ] **Step 1: protocol.md 加一节**

在 `skills/preflight/protocol.md` 末尾（"## Common mistakes" 一类章节之后，或文件尾部）加：

```markdown
## Authoring new artifacts

Producing a new deck artifact (spec / plan / incident / checklist / chart) — including from
an external authoring skill (brainstorming / writing-plans) — goes through **`/flightdeck:new`**
(script: `scripts/flightdeck_new.py`), which stamps the correct per-kind frontmatter + naming
and regenerates INDEX/cockpit. The full contract (kind→folder, naming, per-kind frontmatter,
default status, slug rule) lives in `skills/new/SKILL.md`. Author the shell there first, then
write the body into the returned path — do not hand-derive a path or write to `docs/`.
```

- [ ] **Step 2: emit-agents-md 模板加一行**

`skills/emit-agents-md/SKILL.md` 中生成 AGENTS.md flightdeck 块的模板里，加一行 authoring 指针（在静态规则区，不在 cockpit 派生区）：

```
New deck artifact (spec/plan/incident/checklist/chart) → run /flightdeck:new (stamps frontmatter+naming, regenerates INDEX/cockpit); never hand-write to docs/.
```

（先 `grep -n "BEGIN: flightdeck\|cockpit\|Active focus" skills/emit-agents-md/SKILL.md` 定位模板的静态行区，照其格式插入。）

- [ ] **Step 3: 确认 description 已含发现关键词**

Run: `grep -n "description:" skills/new/SKILL.md`
Expected: 含 `spec`, `plan`, `frontmatter`, `INDEX/cockpit`, `instead of hand-writing` —— skill-routing 命中"建工件"意图。

- [ ] **Step 4: Commit**

```bash
git add skills/preflight/protocol.md skills/emit-agents-md/SKILL.md
git commit -m "docs(flightdeck): 发现钩子——protocol Authoring 节 + AGENTS.md 模板指针"
```

---

## Task 6: 全量验证 + dogfood

**Files:** 无（验证 only）

- [ ] **Step 1: 全测试套件**

Run: `cd /e/projects/tools/flightdeck/scripts/tests && uv run python -m unittest discover -s . -p 'test_*.py' 2>&1 | grep -E "^(Ran|OK|FAILED)"`
Expected: `OK`（原 67 + 新增 11 = 78 左右）

- [ ] **Step 2: dogfood —— 临时 deck 上建各 kind 并验 regen clean**

```bash
cd /e/projects/tools/flightdeck && D=$(mktemp -d) && uv run scripts/flightdeck_init.py "$D" --user t --date 2026-06-04 >/dev/null \
 && uv run scripts/flightdeck_new.py "$D/flightdeck" spec --slug s1 --title "S1" --status active --summary g \
 && uv run scripts/flightdeck_new.py "$D/flightdeck" incident --slug i1 --title "I1" --when-to-read "before x" --applies-to a,b \
 && uv run scripts/flightdeck_index.py "$D/flightdeck" --check \
 && rm -rf "$D" && echo "dogfood OK"
```
Expected: spec 行打印 cockpit 已更新、incident 行打印 folder INDEX 已更新、`--check` 输出 `clean`、最后 `dogfood OK`。

- [ ] **Step 3: dogfood 删后 --check（本仓库不留垃圾）**

确认 Step 2 用的是临时 deck（已 `rm -rf`）；本仓库 deck 未被写入。
Run: `cd /e/projects/tools/flightdeck && uv run scripts/flightdeck_index.py flightdeck --check`
Expected: `clean`

- [ ] **Step 4: lint 干净**

Run: `cd /e/projects/tools/flightdeck && uv run scripts/flightdeck_lint.py flightdeck`
Expected: `{"findings": []}`

- [ ] **Step 5: Commit（若验证触发任何微调）**

```bash
git add -A && git commit -m "test(flightdeck): /flightdeck:new 全量验证 + dogfood 通过" || echo "nothing to commit"
```

---

## Task 7: 对外文档

**Files:**
- Modify: `README.md` / `README.zh.md` (命令表加 `new`)
- Modify: `adapters/claude/README.md` (skill-tree + uninstall 列表加 `new`)
- Modify: `adapters/gemini/README.md` (非-preflight 仪式清单加 `new`)

- [ ] **Step 1: README.md 命令表**

在 `### Commands` 表里、`/flightdeck:launch` 行之后加一行（`grep -n "flightdeck:launch" README.md` 定位）：
```markdown
| `/flightdeck:new` | Author a deck artifact (spec/plan/incident/checklist/chart) — stamps frontmatter + naming, regenerates INDEX/cockpit. Use instead of hand-writing. |
```

- [ ] **Step 2: README.zh.md 命令表**

对应位置加：
```markdown
| `/flightdeck:new` | 撰写 deck 工件（spec/plan/incident/checklist/chart）—— 盖 frontmatter + 命名、重生 INDEX/cockpit。代替手搓。 |
```

- [ ] **Step 3: adapters/claude/README.md**

`grep -n "skills/launch\|skills/status\|preflight,launch" adapters/claude/README.md` 定位；在 skill-tree 加 `~/.claude/skills/new/  # /flightdeck:new — author a deck artifact` 一节（含 `└── SKILL.md`），并把 uninstall 的 `{preflight,launch,landing,...}` 两处（bash + powershell）加入 `new`。

- [ ] **Step 4: adapters/gemini/README.md**

把"非-preflight 仪式"清单 `launch / landing / walkaround / emit-agents-md / status` 改为含 `new`。

- [ ] **Step 5: 确认无悬空引用 + Commit**

Run: `cd /e/projects/tools/flightdeck && grep -rn "flightdeck:new" README.md README.zh.md adapters/`
Expected: 各处命令表/清单均含 new；无断链。
```bash
git add README.md README.zh.md adapters/claude/README.md adapters/gemini/README.md
git commit -m "docs(flightdeck): README + adapters 命令清单加 /flightdeck:new"
```

---

## Task 8: 发布提醒（不在本计划执行）

3.0 发布时（`flightdeck/checklists/version-bump.md` step 3 写 `## [3.0.0]` CHANGELOG 段），把新命令写进 `Added`：

> **`/flightdeck:new`** — 撰写入口：确定性盖按-kind frontmatter + 命名 + 重生 INDEX/cockpit，外部 authoring skill 交接给它而非手搓。

本次**不**改 `CHANGELOG.md`（`bump_version.py --check` 要求顶部标题与清单 semver `2.3.0` 一致）。

---

## Self-Review

**Spec coverage（逐节核对 spec）：**
- 组件（脚本 + SKILL + 发现钩子）→ Task 1–3（脚本）/ Task 4（SKILL）/ Task 5（钩子）✓
- 实现约定·kind→folder 常量表 → Task 1 `KIND_FOLDER` + SKILL 表 ✓
- 命名 dateless/dated + 不追加 -design → Task 1 `filename` 逻辑 + SKILL 命名段（含负例）✓
- 按-kind frontmatter + idea 省 last_updated → Task 1 `_frontmatter` ✓
- 参数校验（非法 kind/slug、缺 title、knowledge 必填路由字段、--implements 仅 workflow、已存在拒绝）→ Task 2 ✓
- 默认 status（workflow=idea / knowledge=active + 理由）→ Task 1 `_DEFAULT_STATUS` + SKILL 注明 ✓
- regen + status-aware stdout（消 idea 误导）→ Task 3 ✓
- slug 显式 + 统一 slugify → Task 1 `SLUG_RE` + SKILL slug 段 ✓
- 定稿 description → Task 4 frontmatter ✓
- landing 关系一句 → Task 4 SKILL "Relationship to landing" ✓
- 发现钩子三件套（protocol 节 + emit 模板行 + description）→ Task 5 ✓
- scriptable 一致性（test + 自动发现）→ Task 1–3 测试 + Task 4 Step 2 ✓
- 验证（错误路径测试 + dogfood 删后 --check + lint）→ Task 2/6 ✓
- 实现顺序验证前置于文档 → Task 6（验证）在 Task 7（文档）之前 ✓
- 发布提醒（CHANGELOG at release）→ Task 8 ✓
- 拒绝项（--force/--no-regen/--auto-slug/TBD）→ 计划中均未实现，符合 ✓

**Placeholder scan：** 脚本/测试/SKILL 均完整逐字；doc-sweep 给 grep 定位 + 确切插入文本。无 TBD/TODO/“类似 Task N”。

**Type/命名一致性：** `new()` 签名（deck, kind, slug, title, status, summary, implements, when_to_read, applies_to, date, regen）在 Task 1/2/3 测试与实现一致；`KIND_FOLDER`/`WORKFLOW`/`KNOWLEDGE`/`SLUG_RE`/`_DEFAULT_STATUS` 常量名贯穿一致；CLI flag（--slug/--title/--status/--summary/--implements/--when-to-read/--applies-to/--date）与 `new()` 参数对应；regen 复用 `flightdeck_index.main([deck])`，`--check` 复用 `index_drift`/`main([deck,"--check"])`。
