---
status: active
summary: 实施 incident 错误库生命周期 spec：P1 脚本签名归一化+指纹(纯函数,TDD)→P2 status-aware 匹配(--match-signature,obsolete 也命中)→P3 obsolete 出路由(INDEX/计数排除,镜像 specs scrapped)→P4 incident 模板(flightdeck_new 加 ## Signature+resolved_by+Cases 首行/templates.md)→P5 skill/protocol prose(landing 接脚本+gated 回归+幂等+退役提示/preflight/new/folder-semantics)→P6 迁移现有 incident+全验证(pytest/--check/lint/walkaround)+CHANGELOG
last_updated: 2026-06-05
implements: specs/2026-06-05-incident-error-library-lifecycle.md
---

# incident 错误库生命周期 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 给 flightdeck 的 incident 错误库补上"生(可 grep 的 Signature)→用(确定性签名指纹去重)→死(resolved_by + obsolete 退役出路由 + 回归复活)"的完整生命周期。

**Architecture:** 机械部分进脚本（`flightdeck_index.py` 纯函数 + CLI、`flightdeck_new.py` 模板），判断部分留 skill prose（landing 的 gated 回归/退役）。Signature 放正文（preflight 不读 → 零路由 token），指纹由单一规范函数算（确定性靠单实现）。obsolete 退出 INDEX 路由但留盘 + 仍进 rglob 匹配（回归检测依赖）。

**Tech Stack:** Python 3（stdlib：`re` / `hashlib`），unittest 测试（`uv run --with pytest python -m pytest`），markdown deck 文件。

依据 spec：`flightdeck/specs/2026-06-05-incident-error-library-lifecycle.md`（含 ## 评审纪要 两轮取舍）。

---

## File Structure

| 文件 | 职责 | 动作 |
|---|---|---|
| `scripts/flightdeck_index.py` | 签名归一化/指纹/解析/匹配 + obsolete 出路由 | 改 |
| `scripts/flightdeck_new.py` | incident 创建时 scaffold `## Signature` + `resolved_by` | 改 |
| `scripts/tests/test_flightdeck_index.py` | P1–P3 测试 | 改 |
| `scripts/tests/test_flightdeck_new.py` | P4 测试 | 改 |
| `skills/preflight/templates.md` | incident 模板加 Signature/resolved_by | 改 |
| `skills/preflight/protocol.md` | 命中路径 + 退役语义 + obsolete 双路径 | 改 |
| `skills/preflight/folder-semantics.md` | incident 生命周期 | 改 |
| `skills/landing/SKILL.md` | sweep 接脚本 + gated 回归 + 幂等 + 退役提示 | 改 |
| `skills/preflight/SKILL.md` | catalog 排除 obsolete（多为自动） | 改 |
| `skills/new/SKILL.md` | incident 撰写契约含 Signature | 改 |
| `CHANGELOG.md` | 发布说明 | 改 |
| `flightdeck/incidents/*.md` | 回填现有 3 条的 `## Signature` | 改 |

设计约定（全程一致，后续 task 引用这些名字）：
- `normalize_symptom(s) -> str`
- `signature_fingerprint(symptom, error_type="") -> str`（12 位 hex；**where 不进指纹**）
- `parse_signature(text) -> dict`（键 symptom/error_type/where/trigger；无块→`{}`）
- `match_signature(deck, symptom, error_type="") -> list[dict]`（每条 `{path,status,where}`；含 obsolete）

---

## Phase 1 — 签名归一化 + 指纹 + 解析（纯函数，TDD）

### Task 1: `normalize_symptom`

**Files:**
- Modify: `scripts/flightdeck_index.py`（顶部 import 区 + 新函数，放 `STATUS_ORDER` 之后）
- Test: `scripts/tests/test_flightdeck_index.py`

- [ ] **Step 1: 写失败测试**

在 `test_flightdeck_index.py` 末尾（`if __name__` 之前）加：

```python
class SignatureNormalizeTest(unittest.TestCase):
    def test_quoted_keys_preserved_distinct(self):
        from flightdeck_index import normalize_symptom
        self.assertNotEqual(
            normalize_symptom("KeyError: 'summary'"),
            normalize_symptom("KeyError: 'title'"),
        )

    def test_volatile_tokens_collapsed(self):
        from flightdeck_index import normalize_symptom
        # hex / uuid / 路径 / 行号 / 时间戳 / 长整数 归一后应相等
        a = normalize_symptom("boom at 0x7f3a2b1c /home/alice/p/foo.py line 42 id=123456")
        b = normalize_symptom("boom at 0x99887766 /home/bob/q/foo.py line 99 id=999999")
        self.assertEqual(a, b)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run --with pytest python -m pytest scripts/tests/test_flightdeck_index.py::SignatureNormalizeTest -q`
Expected: FAIL（`ImportError: cannot import name 'normalize_symptom'`）

- [ ] **Step 3: 实现**

在 `scripts/flightdeck_index.py` 顶部 import 区加 `import re, hashlib`（若已有 `re` 则只补 `hashlib`）。在 `STATUS_ORDER = [...]` 之后加：

```python
# 签名归一化：剥掉易变 token（路径/行号/时间戳/hex/uuid/长整数），但保留语义 token
# （如引号包裹的 key）——`KeyError: 'summary'` 与 `'title'` 必须区分。完整规则在此，
# 测试套件（SignatureNormalizeTest）是契约；调整规则须先改测试。
_VOLATILE = [
    (re.compile(r"\b[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}\b"), "_UUID_"),
    (re.compile(r"0x[0-9a-fA-F]+"), "_HEX_"),
    (re.compile(r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}:\d{2}\S*)?"), "_TIME_"),
    (re.compile(r"[A-Za-z]:\\[^\s:]+|(?:/[\w.\-]+){2,}"), "_PATH_"),
    (re.compile(r"\bline\s+\d+\b", re.I), "line _N_"),
    (re.compile(r"\b\d{4,}\b"), "_N_"),
]


def normalize_symptom(s):
    out = (s or "").strip()
    for pat, repl in _VOLATILE:
        out = pat.sub(repl, out)
    return re.sub(r"\s+", " ", out).strip()
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run --with pytest python -m pytest scripts/tests/test_flightdeck_index.py::SignatureNormalizeTest -q`
Expected: PASS（2 passed）

- [ ] **Step 5: 提交**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): 签名归一化 normalize_symptom（剥易变 token、保语义键）"
```

### Task 2: `signature_fingerprint`

**Files:**
- Modify: `scripts/flightdeck_index.py`（紧接 `normalize_symptom`）
- Test: `scripts/tests/test_flightdeck_index.py`

- [ ] **Step 1: 写失败测试**

在 `SignatureNormalizeTest` 后加：

```python
class SignatureFingerprintTest(unittest.TestCase):
    def test_same_after_normalize_same_fp(self):
        from flightdeck_index import signature_fingerprint
        self.assertEqual(
            signature_fingerprint("fail 0x7f3a", "KeyError"),
            signature_fingerprint("fail 0x99aa", "KeyError"),
        )

    def test_distinct_key_distinct_fp(self):
        from flightdeck_index import signature_fingerprint
        self.assertNotEqual(
            signature_fingerprint("KeyError: 'summary'", "KeyError"),
            signature_fingerprint("KeyError: 'title'", "KeyError"),
        )

    def test_where_not_in_fingerprint(self):
        # spec：where 不进主指纹（重构换 where 不应换指纹）
        from flightdeck_index import signature_fingerprint
        import inspect
        self.assertNotIn("where", inspect.signature(signature_fingerprint).parameters)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run --with pytest python -m pytest scripts/tests/test_flightdeck_index.py::SignatureFingerprintTest -q`
Expected: FAIL（ImportError）

- [ ] **Step 3: 实现**

紧接 `normalize_symptom` 之后加：

```python
def signature_fingerprint(symptom, error_type=""):
    """主指纹 = error_type + 归一化 symptom。where **不**进指纹（spec：symptom+error_type
    为主、where 为次/tiebreak，由调用方在多命中时区分）。"""
    key = f"{(error_type or '').strip()}\n{normalize_symptom(symptom)}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run --with pytest python -m pytest scripts/tests/test_flightdeck_index.py::SignatureFingerprintTest -q`
Expected: PASS（3 passed）

- [ ] **Step 5: 提交**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): signature_fingerprint（error_type+归一symptom，where 不进）"
```

### Task 3: `parse_signature`

**Files:**
- Modify: `scripts/flightdeck_index.py`（紧接 `signature_fingerprint`）
- Test: `scripts/tests/test_flightdeck_index.py`

- [ ] **Step 1: 写失败测试**

```python
class ParseSignatureTest(unittest.TestCase):
    SIG = (
        "---\nstatus: active\n---\n# t\n\n"
        "## Signature\n"
        "- symptom: `KeyError: 'summary'`\n"
        "- error_type: KeyError\n"
        "- where: regen_cockpit_inprogress\n"
        "- trigger: active 工件缺 summary\n\n"
        "## 根因\n...\n"
    )

    def test_parses_four_keys(self):
        from flightdeck_index import parse_signature
        sig = parse_signature(self.SIG)
        self.assertEqual(sig["symptom"], "KeyError: 'summary'")   # 反引号被剥
        self.assertEqual(sig["error_type"], "KeyError")
        self.assertEqual(sig["where"], "regen_cockpit_inprogress")
        self.assertEqual(sig["trigger"], "active 工件缺 summary")

    def test_no_block_returns_empty(self):
        from flightdeck_index import parse_signature
        self.assertEqual(parse_signature("---\nstatus: active\n---\n# t\n## 根因\nx\n"), {})
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run --with pytest python -m pytest scripts/tests/test_flightdeck_index.py::ParseSignatureTest -q`
Expected: FAIL（ImportError）

- [ ] **Step 3: 实现**

```python
def parse_signature(text):
    """抽 `## Signature` 块的 key:value 行为 dict（键 symptom/error_type/where/trigger）。
    无块返回 {}。值两端反引号/空白剥掉。"""
    m = re.search(r"^##\s+Signature\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if not m:
        return {}
    sig = {}
    for line in m.group(1).splitlines():
        lm = re.match(r"\s*-\s*(symptom|error_type|where|trigger)\s*:\s*(.*)$", line)
        if lm:
            sig[lm.group(1)] = lm.group(2).strip().strip("`").strip()
    return sig
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run --with pytest python -m pytest scripts/tests/test_flightdeck_index.py::ParseSignatureTest -q`
Expected: PASS（2 passed）

- [ ] **Step 5: 提交**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): parse_signature 解析正文 ## Signature 块"
```

---

## Phase 2 — status-aware 匹配 + CLI

### Task 4: `match_signature`

**Files:**
- Modify: `scripts/flightdeck_index.py`（紧接 `parse_signature`）
- Test: `scripts/tests/test_flightdeck_index.py`

- [ ] **Step 1: 写失败测试**

```python
class MatchSignatureTest(unittest.TestCase):
    def _deck(self, d):
        deck = Path(d)
        (deck / "incidents").mkdir(parents=True)
        return deck

    def _inc(self, deck, name, status, symptom, etype="KeyError"):
        (deck / "incidents" / name).write_text(
            f"---\nstatus: {status}\nwhen_to_read: w\napplies_to: [a]\nlast_updated: 2026-06-05\n---\n"
            f"# t\n\n## Signature\n- symptom: `{symptom}`\n- error_type: {etype}\n- where: foo\n- trigger: t\n",
            encoding="utf-8",
        )

    def test_exact_match_returns_path_and_status(self):
        from flightdeck_index import match_signature
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            self._inc(deck, "2026-06-05-a.md", "active", "KeyError: 'summary'")
            hits = match_signature(deck, "KeyError: 'summary'", "KeyError")
            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0]["status"], "active")
            self.assertTrue(hits[0]["path"].endswith("2026-06-05-a.md"))

    def test_obsolete_still_matched(self):
        # 回归检测依赖：obsolete 不被过滤
        from flightdeck_index import match_signature
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            self._inc(deck, "2026-06-05-b.md", "obsolete", "KeyError: 'summary'")
            hits = match_signature(deck, "KeyError: 'summary'", "KeyError")
            self.assertEqual([h["status"] for h in hits], ["obsolete"])

    def test_signatureless_skipped(self):
        from flightdeck_index import match_signature
        with tempfile.TemporaryDirectory() as d:
            deck = self._deck(d)
            (deck / "incidents" / "old.md").write_text(
                "---\nstatus: active\nwhen_to_read: w\napplies_to: [a]\nlast_updated: 2026-06-05\n---\n# t\n## 根因\nx\n",
                encoding="utf-8")
            self.assertEqual(match_signature(deck, "KeyError: 'summary'", "KeyError"), [])
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run --with pytest python -m pytest scripts/tests/test_flightdeck_index.py::MatchSignatureTest -q`
Expected: FAIL（ImportError）

- [ ] **Step 3: 实现**

```python
def match_signature(deck, symptom, error_type=""):
    """返回主指纹相同的 incident（含 status:obsolete——回归检测依赖）。
    扫 incidents/ 全部 .md（含嵌套 area，rglob）；缺 ## Signature 的跳过（走 AI 模糊层）。
    每条 {path(相对 deck), status, where}。"""
    fp = signature_fingerprint(symptom, error_type)
    hits = []
    inc = Path(deck) / "incidents"
    if not inc.is_dir():
        return hits
    for p in sorted(inc.rglob("*.md")):
        if p.name == "INDEX.md":
            continue
        text = p.read_text(encoding="utf-8")
        sig = parse_signature(text)
        if not sig.get("symptom"):
            continue
        if signature_fingerprint(sig["symptom"], sig.get("error_type", "")) == fp:
            hits.append({
                "path": str(p.relative_to(deck)).replace("\\", "/"),
                "status": parse_frontmatter(text).get("status", ""),
                "where": sig.get("where", ""),
            })
    return hits
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run --with pytest python -m pytest scripts/tests/test_flightdeck_index.py::MatchSignatureTest -q`
Expected: PASS（3 passed）

- [ ] **Step 5: 提交**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): match_signature（status-aware，obsolete 也命中，缺签名跳过）"
```

### Task 5: `--match-signature` CLI

**Files:**
- Modify: `scripts/flightdeck_index.py`（`main()` argparse，约 `:441` 的 `--archivable` 之后 + `:452` 的处理分支之后）
- Test: `scripts/tests/test_flightdeck_index.py`

- [ ] **Step 1: 写失败测试**

```python
class MatchSignatureCliTest(unittest.TestCase):
    def test_cli_prints_status_tab_path(self):
        import io
        from contextlib import redirect_stdout
        from flightdeck_index import main
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            (deck / "incidents").mkdir()
            (deck / "incidents" / "2026-06-05-a.md").write_text(
                "---\nstatus: active\nwhen_to_read: w\napplies_to: [a]\nlast_updated: 2026-06-05\n---\n"
                "# t\n\n## Signature\n- symptom: `KeyError: 'summary'`\n- error_type: KeyError\n- where: foo\n- trigger: t\n",
                encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([str(deck), "--match-signature", "KeyError: 'summary'", "--sig-error-type", "KeyError"])
            self.assertEqual(rc, 0)
            self.assertIn("active", buf.getvalue())
            self.assertIn("2026-06-05-a.md", buf.getvalue())
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run --with pytest python -m pytest scripts/tests/test_flightdeck_index.py::MatchSignatureCliTest -q`
Expected: FAIL（`error: unrecognized arguments: --match-signature`）

- [ ] **Step 3: 实现**

在 `main()` 的 argparse，`--archivable` 之后加：

```python
    ap.add_argument("--match-signature", metavar="SYMPTOM", default=None,
                    help="print incidents whose signature fingerprint matches SYMPTOM (read-only); status<TAB>path")
    ap.add_argument("--sig-error-type", metavar="TYPE", default="",
                    help="error_type to pair with --match-signature (optional)")
```

在 `if args.archivable:` 分支之后加：

```python
    if args.match_signature is not None:
        for h in match_signature(args.deck, args.match_signature, args.sig_error_type):
            print(f"{h['status']}\t{h['path']}")
        return 0
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run --with pytest python -m pytest scripts/tests/test_flightdeck_index.py::MatchSignatureCliTest -q`
Expected: PASS（1 passed）

- [ ] **Step 5: 提交**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): --match-signature CLI（建前/landing 调用，只读）"
```

---

## Phase 3 — obsolete 出路由（镜像 specs scrapped）

### Task 6: `folder_summary` 排除 obsolete（knowledge 计数）

**Files:**
- Modify: `scripts/flightdeck_index.py:107-108`（`folder_summary` 的 specs/scrapped 过滤旁）
- Test: `scripts/tests/test_flightdeck_index.py`

- [ ] **Step 1: 写失败测试**

```python
class ObsoleteCountExcludeTest(unittest.TestCase):
    def test_obsolete_excluded_from_knowledge_count(self):
        from flightdeck_index import folder_summary
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "incidents"
            folder.mkdir()
            for n, s in [("a.md", "active"), ("b.md", "active"), ("c.md", "obsolete")]:
                (folder / n).write_text(
                    f"---\nstatus: {s}\nwhen_to_read: w\napplies_to: [x]\nlast_updated: 2026-06-05\n---\n# t\n",
                    encoding="utf-8")
            self.assertEqual(folder_summary(folder), "2 active")   # obsolete 不计
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run --with pytest python -m pytest scripts/tests/test_flightdeck_index.py::ObsoleteCountExcludeTest -q`
Expected: FAIL（得到 `3 (2 active, 1 obsolete)`）

- [ ] **Step 3: 实现**

`folder_summary` 现有：

```python
    if folder.name == "specs":
        statuses = [s for s in statuses if s != "scrapped"]
```

改为（加 knowledge 排除 obsolete）：

```python
    if folder.name == "specs":
        statuses = [s for s in statuses if s != "scrapped"]
    if folder.name in KNOWLEDGE_KINDS:
        statuses = [s for s in statuses if s != "obsolete"]
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run --with pytest python -m pytest scripts/tests/test_flightdeck_index.py::ObsoleteCountExcludeTest -q`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): knowledge 文件夹 root 计数排除 obsolete"
```

### Task 7: `regen_folder_index` knowledge 路由排除 obsolete

**Files:**
- Modify: `scripts/flightdeck_index.py`（`regen_folder_index` 的两条 knowledge 路径：嵌套分支 `:180-181` 与扁平分支 `:183-185`）
- Test: `scripts/tests/test_flightdeck_index.py`

- [ ] **Step 1: 写失败测试**

```python
class ObsoleteRoutingExcludeTest(unittest.TestCase):
    def test_obsolete_row_absent_from_knowledge_index(self):
        from flightdeck_index import regen_folder_index
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "incidents"
            folder.mkdir()
            (folder / "live.md").write_text(
                "---\nstatus: active\nwhen_to_read: w\napplies_to: [x]\nlast_updated: 2026-06-05\n---\n# t\n",
                encoding="utf-8")
            (folder / "dead.md").write_text(
                "---\nstatus: obsolete\nwhen_to_read: w\napplies_to: [x]\nlast_updated: 2026-06-05\nresolved_by: test_x\n---\n# t\n",
                encoding="utf-8")
            block = regen_folder_index(folder)
            self.assertIn("live.md", block)
            self.assertNotIn("dead.md", block)   # obsolete 不进路由
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run --with pytest python -m pytest scripts/tests/test_flightdeck_index.py::ObsoleteRoutingExcludeTest -q`
Expected: FAIL（dead.md 出现在 block）

- [ ] **Step 3: 实现**

在 `regen_folder_index` 里加一个本地过滤助手，并在两条 knowledge 列名处套用。具体：把扁平分支

```python
    names = sorted(p.name for p in folder.glob("*.md") if p.name != "INDEX.md")
    row_kind = kind if kind in (SUMMARY_KINDS | KNOWLEDGE_KINDS) else "checklists"
    rows = [format_row(row_kind, name, parse_frontmatter((folder / name).read_text(encoding="utf-8"))) for name in names]
```

改为：

```python
    names = sorted(p.name for p in folder.glob("*.md") if p.name != "INDEX.md")
    if kind in KNOWLEDGE_KINDS:   # obsolete 留盘但退出路由（仍可 grep / 仍进 match_signature）
        names = [n for n in names
                 if parse_frontmatter((folder / n).read_text(encoding="utf-8")).get("status") != "obsolete"]
    row_kind = kind if kind in (SUMMARY_KINDS | KNOWLEDGE_KINDS) else "checklists"
    rows = [format_row(row_kind, name, parse_frontmatter((folder / name).read_text(encoding="utf-8"))) for name in names]
```

并把嵌套分支的 `top_files` 同样过滤：

```python
        top_files = sorted(p.name for p in folder.glob("*.md") if p.name != "INDEX.md")
        if kind in KNOWLEDGE_KINDS:
            top_files = [n for n in top_files
                         if parse_frontmatter((folder / n).read_text(encoding="utf-8")).get("status") != "obsolete"]
```

- [ ] **Step 4: 跑测试确认通过 + 全量回归**

Run: `uv run --with pytest python -m pytest scripts/tests/ -q`
Expected: PASS（全绿）

- [ ] **Step 5: 提交**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(flightdeck): knowledge INDEX 路由排除 obsolete（留盘、仍进匹配）"
```

---

## Phase 4 — incident 模板（创建即带 Signature）

### Task 8: `flightdeck_new` incident scaffold + `resolved_by`

**Files:**
- Modify: `scripts/flightdeck_new.py`（`_frontmatter` 加 incident 的 `resolved_by` 空字段；`new()`/body 写入加 incident 专属 body scaffold，当前 body 见 `:82` `path.write_text(f"{fm}\n\n# {title}\n", ...)`）
- Test: `scripts/tests/test_flightdeck_new.py`

- [ ] **Step 1: 写失败测试**

在 `test_flightdeck_new.py` 末尾（`if __name__` 之前）加：

```python
class IncidentSignatureScaffoldTest(unittest.TestCase):
    def test_incident_body_has_signature_and_resolved_by(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            path = new(deck, "incident", slug="x", title="X",
                       when_to_read="w", applies_to=["a"], regen=False)
            text = path.read_text(encoding="utf-8")
            self.assertIn("resolved_by:", text)        # frontmatter 字段（空）
            self.assertIn("## Signature", text)         # 正文 scaffold
            self.assertIn("- symptom:", text)
            self.assertIn("## Cases", text)

    def test_non_incident_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            deck = _deck(d)
            path = new(deck, "checklist", slug="y", title="Y",
                       when_to_read="w", applies_to=["a"], regen=False)
            self.assertNotIn("## Signature", path.read_text(encoding="utf-8"))
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run --with pytest python -m pytest scripts/tests/test_flightdeck_new.py::IncidentSignatureScaffoldTest -q`
Expected: FAIL

- [ ] **Step 3: 实现**

(a) 在 `_frontmatter` 的 knowledge 分支（`else:` 块，写 when_to_read/applies_to/last_updated 处）末尾，对 incident 追加空 `resolved_by`：

```python
        lap.append(f"last_updated: {date}")
        if kind == "incident":
            lines.append("resolved_by:")     # 空=未根治；填 commit/test = 退役依据
```

（注意：把上面伪写的 `lap.append` 对齐到现有真实变量 `lines.append(f"last_updated: {date}")` 之后插入 incident 分支。）

(b) 在写文件处（`:82`），把固定 body 换成按 kind 取 scaffold：

```python
    body = _body_scaffold(kind, title)
    path.write_text(f"{fm}\n\n{body}", encoding="utf-8")
```

并新增：

```python
_INCIDENT_BODY = """# {title}

## Signature
- symptom: `<报错原文 / 可观测症状>`
- error_type: <异常类型/错误码 或 —>
- where: <函数/文件/子系统>
- trigger: <什么动作/场景引发>

## 症状/复现

## 根因

## 修法

## Cases
- {date_placeholder} 首次
"""


def _body_scaffold(kind, title):
    if kind == "incident":
        return _INCIDENT_BODY.format(title=title, date_placeholder="YYYY-MM-DD")
    return f"# {title}\n"
```

- [ ] **Step 4: 跑测试确认通过 + 全量**

Run: `uv run --with pytest python -m pytest scripts/tests/ -q`
Expected: PASS（全绿；注意已有 NewRegenTest 仍过——body 变化不影响 INDEX 行）

- [ ] **Step 5: 提交**

```bash
git add scripts/flightdeck_new.py scripts/tests/test_flightdeck_new.py
git commit -m "feat(flightdeck): incident 创建即 scaffold ## Signature + resolved_by + Cases 首行"
```

### Task 9: `templates.md` incident 模板对齐

**Files:**
- Modify: `skills/preflight/templates.md`（`## knowledge frontmatter — incident / checklist / reference` 节，约 `:85-96`）

- [ ] **Step 1: 编辑**

在该节的 frontmatter 注释里，给 incident 补 `resolved_by`，并在节末补一段 incident 正文模板（含 `## Signature` 四键 + Cases 规则：首行建时即写、`recurrences` 为权威计数、Cases 留最近 N）。具体文本对齐 spec「生」节，关键点：`## Signature` 只 4 键（硬边界）、symptom 可多行、error_type 可 `—`。

- [ ] **Step 2: 验证（无破坏）**

Run: `uv run scripts/flightdeck_lint.py flightdeck`
Expected: `{"findings": []}`（templates.md 是 skill 文档，不影响 deck lint，但确认未连带破坏）

- [ ] **Step 3: 提交**

```bash
git add skills/preflight/templates.md
git commit -m "docs(flightdeck): templates incident 模板加 Signature/resolved_by/Cases 规则"
```

---

## Phase 5 — skill / protocol prose

> 这些是文档行为约定，无单元测试；验证靠 `--check` / `lint` / `walkaround` 不破坏 + 人读一致。每个 task 末尾跑一次 `uv run scripts/flightdeck_lint.py flightdeck` 确认 `findings: []`。

### Task 10: `protocol.md` —— 命中路径 + 退役语义 + obsolete 双路径

**Files:** Modify `skills/preflight/protocol.md`

- [ ] **Step 1: 编辑**，加三段（对齐 spec）：
  1. **命中路径**：遇到报错先 `grep` 原文 / 跑 `flightdeck_index.py <deck> --match-signature "<symptom>"` 查 `incidents/` 是否已知；命中就 append Case 而非新建。
  2. **退役语义**：`resolved_by`（commit SHA / test id）+ `status: obsolete` 是一次刻意动作（落 landing）；obsolete = 根治退役、退出活跃路由、保留作历史；**非"过时无价值"**。
  3. **obsolete 双路径**：obsolete 退出 INDEX 主动推荐路由，但仍可 `grep`、仍进 `--match-signature`/recurrence sweep（回归检测依赖）。
- [ ] **Step 2:** `uv run scripts/flightdeck_lint.py flightdeck` → `findings: []`
- [ ] **Step 3:** `git add skills/preflight/protocol.md && git commit -m "docs(flightdeck): protocol 加命中路径/退役语义/obsolete 双路径"`

### Task 11: `landing/SKILL.md` —— sweep 接脚本 + gated 回归 + 幂等 + 退役提示

**Files:** Modify `skills/landing/SKILL.md`（Step 5a recurrence sweep 段）

- [ ] **Step 1: 编辑**，把 recurrence sweep 改为：
  1. **先跑脚本** `--match-signature`（确定性精确层）→ 命中 active 条目：append Case + `recurrences +1`；**无命中**才落 AI 模糊层（applies_to/语义；三出口：同一条/新建/不确定→问）。
  2. **gated 回归**：命中条目 `status: obsolete` 时**不直接 append**，先确认是否真回归 → 确认后复活（翻 active、清 `resolved_by`、Cases 注"回归，原根治失效"、`recurrences` 累加不重置）。
  3. **幂等**：建前已 `+1` 的条目，sweep 不重复计（按 Case 轮次标识/身份去重）。
  4. **退役提示**：sweep 见 `resolved_by` 非空但仍 `active` 的，提示"是否退役（翻 obsolete）？"——**不自动翻**。
- [ ] **Step 2:** `uv run scripts/flightdeck_lint.py flightdeck` → `findings: []`
- [ ] **Step 3:** `git add skills/landing/SKILL.md && git commit -m "docs(flightdeck): landing sweep 接签名脚本 + gated 回归 + 幂等 + 退役提示"`

### Task 12: `preflight` / `new` / `folder-semantics` 收尾 prose

**Files:** Modify `skills/preflight/SKILL.md`、`skills/new/SKILL.md`、`skills/preflight/folder-semantics.md`

- [ ] **Step 1: 编辑**
  - `preflight/SKILL.md`：catalog 段注明"obsolete 已由 INDEX 排除，不出现在路由 catalog"（多为自动，点一句）。
  - `new/SKILL.md`：incident 撰写契约加"建后填 `## Signature`（4 键硬边界）+ 建前先 `--match-signature` 查重"。
  - `folder-semantics.md`：incidents 段补生命周期（active→obsolete 退役，回归复活）。
- [ ] **Step 2:** `uv run scripts/flightdeck_lint.py flightdeck` → `findings: []`
- [ ] **Step 3:** `git add skills/preflight/SKILL.md skills/new/SKILL.md skills/preflight/folder-semantics.md && git commit -m "docs(flightdeck): preflight/new/folder-semantics 对齐错误库生命周期"`

---

## Phase 6 — 迁移现有 incident + 全验证

### Task 13: 回填现有 3 条 incident 的 `## Signature`

**Files:** Modify `flightdeck/incidents/*.md`（`2026-06-05-active-workflow-missing-summary-keyerror.md`、`index-row-summary-delimiter.md`、`powershell-herestring-in-bash-tool.md`、`scaffold-ships-verbatim.md`）

- [ ] **Step 1:** 给每条加 `## Signature` 块（4 键，从现有正文 `**Symptom**`/`## 现象` 提取），并把分节对齐标准（症状/根因/修法/Cases）。`active-workflow-...keyerror` 那条 symptom=`KeyError: 'summary'`、error_type=KeyError、where=regen_cockpit_inprogress。
- [ ] **Step 2:** 自举验证匹配可用：

Run: `uv run scripts/flightdeck_index.py flightdeck --match-signature "KeyError: 'summary'" --sig-error-type KeyError`
Expected: 打印 `active<TAB>incidents/2026-06-05-active-workflow-missing-summary-keyerror.md`

- [ ] **Step 3:** `git add flightdeck/incidents/ && git commit -m "docs(flightdeck): 回填现有 incident 的 ## Signature（dogfood 迁移）"`

### Task 14: 全套验证 + CHANGELOG

**Files:** Modify `CHANGELOG.md`

- [ ] **Step 1: 全量验证**

```bash
uv run --with pytest python -m pytest scripts/tests/ -q          # 全绿
uv run scripts/flightdeck_index.py flightdeck --check            # clean
uv run scripts/flightdeck_lint.py flightdeck                     # findings: []
```

- [ ] **Step 2: walkaround 自审**（人读，确认无新 drift；尤其 incident 模板/landing 描述与脚本一致）。
- [ ] **Step 3: CHANGELOG** 加一条：incident 错误库生命周期（Signature 命中 / 签名指纹去重 / obsolete 退役 + 回归复活）。
- [ ] **Step 4: 翻 done + 提交**

spec+plan dogfood 通过后翻 `done`（由 landing 智能归档处理），CHANGELOG 提交：

```bash
git add CHANGELOG.md
git commit -m "docs(flightdeck): CHANGELOG 记 incident 错误库生命周期"
```

---

## Self-Review（写完即查）

- **Spec coverage**：生(T8/T9/T13 模板+回填、T1–T3 解析) · 用(T1–T5 指纹+匹配+CLI、T11 sweep 接入、幂等) · 死(T6/T7 obsolete 出路由、T10/T11 退役+gated 回归) · token(T7 出路由、Signature 正文=无路由成本) · 覆盖边界/缺签名走模糊层(T4 测试 + T11 prose) · 回归复活(T11) — 均有 task。
- **Placeholder**：模板里的 `<...>` 是 incident 模板**占位符内容**（产物的一部分，非计划占位），非 plan TODO。
- **Type 一致**：`normalize_symptom`/`signature_fingerprint(symptom,error_type)`/`parse_signature`/`match_signature(deck,symptom,error_type)` 全程一致；CLI `--match-signature` + `--sig-error-type`。
- **已知留给实现的调参**：归一化正则集（测试套件是契约）、Cases 压缩 N（个位~十几）、where 在多命中时的 tiebreak —— 均在 spec/plan 标注，非遗漏。
