---
status: active
summary: Phase 2 of launch-recorded-config: force a script runtime by deleting every hand-written markdown fallback across the skills, add a Node port of the 4 user-facing scripts (flightdeck_index/lint/init/new) gated by a byte-parity golden-output harness (codepoint sort, LF, Python json.dumps spacing), narrow launch detection to git+runtime with refusal paths. bump_version stays Python-only.
last_updated: 2026-06-19
implements: specs/2026-06-19-launch-recorded-config.md
---

# Launch-recorded config — Phase 2: runtime force + Node port + parity

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a script runtime *mandatory* (delete every hand-written markdown fallback) and ship a behavior-equivalent **Node** port of the four user-facing scripts (`flightdeck_index` / `flightdeck_lint` / `flightdeck_init` / `flightdeck_new`), locked to the Python reference by a **byte-parity golden-output harness** so node-only users get an identical deck.

**Architecture:** The port is a *faithful translation*, not a redesign — the Python scripts stay the reference implementation; the Node versions must produce byte-identical output. The safety net is built **first**: a parity harness (Task 1) + a shared Node helper lib with unit-level parity tests for the landmine helpers (Task 2: frontmatter parse, **codepoint sort**, **Python-`json.dumps` spacing**, sha1-over-UTF-8). Each script is then ported (Tasks 3–6) and gated by the golden harness before its hand-written markdown fallback prose is deleted (Task 7). Launch detection is narrowed to git+runtime with hard refusals (Task 8). `bump_version` is **not** ported (maintainer-only; user skills never call it — spec §3.3).

**Tech Stack:** Python 3.8+ stdlib (reference), **Node ≥ 18** built-ins only (`crypto`/`fs`/`path`/`child_process`/`JSON`, **zero npm deps** — spec §3.3), `unittest`+`subprocess` for the parity harness (runs both interpreters and byte-diffs), ripgrep for the prose-deletion gates.

---

## Parity contract (spec §3.3 — the spec-level acceptance bar)

Every Node script MUST be byte-identical to its Python twin after these pinned normalizations. **These are the landmines; the golden harness is the arbiter.**

| Landmine | Python reference behavior | Node port MUST |
|---|---|---|
| **Sort order** | `sorted()` = Unicode **code point** order | compare by code point, NOT default `Array.sort()` (UTF-16 code-unit order, differs on non-BMP) — use the `cmpCodepoint` helper (Task 2) |
| **JSON in `consumers:` line** | `json.dumps(sorted(set(x)))` → `["a", "b"]` (separator `", "`) | emit `", "` between items, not `JSON.stringify`'s `","` — use `pyJsonArray` (Task 2) |
| **lint JSON output** | `json.dumps({"findings": …}, ensure_ascii=False, indent=2)` | match Python's `indent=2` shape + insertion key order (`audit`/`severity`/`path`/`message`) + non-ASCII passthrough — use `pyJsonIndent` (Task 2), golden-verified |
| **Fingerprint** | `sha1(key.encode("utf-8")).hexdigest()[:12]` | `crypto.createHash('sha1').update(key,'utf8').digest('hex').slice(0,12)` |
| **Sentinels in rows** | em-dash `—`, `⚠ summary 缺失`, `⚠ 缺失`, `⚠未验证 `, `⚠待复核 `, `recur: N` (literal CJK + emoji) | reproduce the exact UTF-8 bytes |
| **Newlines** | `Path.write_text` translates `\n`→`os.linesep` (CRLF on Windows) | emit **LF** always; **the harness compares LF-normalized** (universal-newline) so the OS-level CRLF quirk on the Python side never masks a real content diff. Golden fixtures stored LF. |
| **No NFC re-normalization** | Python does **not** `.normalize()` on read/write | Node must **not** call `.normalize()` either (matching Python = passthrough); fixtures are pre-pinned NFC so the question never arises |
| **Path slashes** | `str(rel).replace("\\","/")` → POSIX in output | same: always POSIX-slash output paths |
| **`rglob`/`glob` order** | `sorted(...)` applied explicitly before emission | replicate the explicit sort; never rely on `fs.readdirSync` order |

**`runtime` dispatch:** skills choose the call form from the `rules.md` frontmatter `runtime` field — `uv run <pkg>/scripts/<name>.py` / `python <…>.py` / `node <…>.js`. The `.py` and `.js` share a basename stem (`flightdeck_index.py` ↔ `flightdeck_index.js`).

---

## File structure (this phase touches)

| File | Responsibility | Action |
|---|---|---|
| `scripts/tests/parity/fixture_deck/**` | pinned golden fixture deck (NFC, LF) exercising every row/branch | **create** |
| `scripts/tests/parity/git_fixture.sh` `/ .py` helper | seed a throwaway git repo + Sync anchor for git-dependent subcommands | **create** |
| `scripts/tests/test_parity.py` | run py + js per invocation, LF-normalize, byte-diff stdout + mutated tree | **create** |
| `scripts/flightdeck_lib.js` | shared Node helpers: `parseFrontmatter`, `cmpCodepoint`, `sortCp`, `pyJsonArray`, `pyJsonIndent`, `fingerprint`, constants | **create** |
| `scripts/tests/test_flightdeck_lib_parity.py` | unit parity for the lib helpers vs their Python equals | **create** |
| `scripts/flightdeck_index.js` | Node port of `flightdeck_index.py` (all subcommands) | **create** |
| `scripts/flightdeck_lint.js` | Node port of `flightdeck_lint.py` (all audits) | **create** |
| `scripts/flightdeck_init.js` | Node port of `flightdeck_init.py` | **create** |
| `scripts/flightdeck_new.js` | Node port of `flightdeck_new.py` | **create** |
| `skills/preflight/exit-ritual.md` | landing textbook | **modify**: delete `§ INDEX regeneration` / `§ Script fast path` hand-rebuild prose |
| `skills/status/SKILL.md` | status flip | **modify**: delete step 5/5a fast-path + always-valid fallback |
| `skills/landing/SKILL.md` | landing | **modify**: delete step 3 hand fallback |
| `skills/new/SKILL.md` | artifact authoring | **modify**: delete Fast-path / no-runtime fallback split → script is the only path |
| `skills/launch/SKILL.md` | first-run | **modify**: narrow probe to git+runtime, add refusal paths, stamp `runtime`, print pick-list |
| `skills/walkaround/SKILL.md` | audit | **modify**: "optional fast path" wording → script is the path |
| `skills/preflight/protocol.md` | Rule resolution order | **modify**: `runtime` field selects call form (uv/python/node) |
| `scripts/run_tests.md` or rules note | how to run JS tests | **modify**: document `node --test` + parity gate |

> Two verification classes: **code tasks** (1–6) are golden/unit gated; **prose tasks** (7–8) are gated by `rg` (fallback prose gone) + the full pytest suite staying green + the English gate `rg -lP '\p{Han}' skills scaffolds` empty.

---

### Task 1: Parity harness — golden fixture deck + dual-interpreter byte-diff

Build the safety net **before** any port. The harness runs the Python script and (when it exists) the Node script over an identical fixture copy, LF-normalizes, and asserts byte-equality of stdout and of every mutated `.md`. Until a `.js` exists its tests skip — so this task lands green and arms incrementally.

**Files:**
- Create: `scripts/tests/parity/fixture_deck/` (a full deck — see Step 1)
- Create: `scripts/tests/test_parity.py`

- [ ] **Step 1: Build the fixture deck**

Create `scripts/tests/parity/fixture_deck/` as a real flightdeck deck pinned to **LF + NFC**, deliberately exercising every row branch and subcommand. Minimum contents:

- `cockpit.md` — with `## In Progress` + `<!-- AUTO:inprogress -->…<!-- /AUTO -->`, `## Next`, `## Hanging Tasks`.
- `rules.md` — frontmatter `version: 3.0` + `runtime: uv` + `agents_md: off` (+ one illegal value variant tested via copy mutation, not in the base).
- `specs/INDEX.md` + `specs/2026-01-02-alpha.md` (`status: active`, `summary:`), `specs/2026-01-01-done-thing.md` (`status: done`), `specs/some-idea.md` (`status: idea`, dateless), one spec with a non-BMP char in `summary` (e.g. an emoji) to force the codepoint-sort path.
- `plans/INDEX.md` + a plan with `implements: specs/2026-01-02-alpha.md` (`status: active`), a `done` plan implementing the done spec, an **orphan** plan (no `implements`).
- `incidents/INDEX.md` + an incident with a full `## Signature` block (`symptom`/`error_type`/`where`/`trigger`) and `recurrences: 3`; a `status: stale` incident; a `status: obsolete` incident; a nested `incidents/<area>/INDEX.md` (with `purpose:` + `last_updated:`) + one incident inside it.
- `checklists/INDEX.md` + one active checklist; `docs/INDEX.md` + a `stale` doc with `when_to_update:` + one with `verify:`; `references/INDEX.md` + an imported file carrying a `synced: true` + `last_updated:` and a `consumers: [...]` line.
- `archive/incidents/` with one archived incident (signature scan must include it) and `archive/specs/` with a `verify:`-bearing archived spec (verify-pending must include archive).

Keep filenames ASCII; put the non-BMP char only in *field values* so sorting of filenames stays trivial but the codepoint helpers still get exercised by row content.

- [ ] **Step 2: Write the harness**

```python
# scripts/tests/test_parity.py
"""Byte-parity harness: every Node script must match its Python twin.

Runs `python <name>.py <args>` and `node <name>.js <args>` over identical
fixture copies, LF-normalizes (Python's write_text emits CRLF on Windows; the
parity contract is *content*, spec §3.3 "换行恒 LF"), and asserts equality of
stdout and of the full mutated .md tree. Skips when node is absent or the .js
does not exist yet — so it arms incrementally as ports land.
"""
import os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
FIXTURE = Path(__file__).resolve().parent / "parity" / "fixture_deck"
HAVE_NODE = shutil.which("node") is not None


def _lf(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n")


def _copy_deck():
    d = Path(tempfile.mkdtemp())
    shutil.copytree(FIXTURE, d / "flightdeck")
    return d / "flightdeck"


def _run(interp, script, deck, extra):
    cmd = interp + [str(SCRIPTS / script), str(deck), *extra]
    p = subprocess.run(cmd, capture_output=True)
    return p.returncode, _lf(p.stdout), _lf(p.stderr)


def _tree_snapshot(deck: Path):
    out = {}
    for p in sorted(deck.rglob("*.md")):
        out[str(p.relative_to(deck)).replace("\\", "/")] = _lf(p.read_bytes())
    return out


class ParityBase(unittest.TestCase):
    stem = None  # e.g. "flightdeck_index"

    def assert_parity(self, extra, mutates=False):
        if not HAVE_NODE:
            self.skipTest("node not on PATH")
        js = SCRIPTS / f"{self.stem}.js"
        if not js.is_file():
            self.skipTest(f"{js.name} not ported yet")
        py_deck = _copy_deck(); js_deck = _copy_deck()
        rc_py, out_py, _ = _run([sys.executable], f"{self.stem}.py", py_deck, extra)
        rc_js, out_js, _ = _run(["node"], f"{self.stem}.js", js_deck, extra)
        self.assertEqual(out_py, out_js, f"stdout diff for {self.stem} {extra}")
        self.assertEqual(rc_py, rc_js, f"exit-code diff for {self.stem} {extra}")
        if mutates:
            self.assertEqual(_tree_snapshot(py_deck), _tree_snapshot(js_deck),
                             f"mutated-tree diff for {self.stem} {extra}")
```

- [ ] **Step 3: Add the index subcommand matrix (skips until Task 3)**

```python
class IndexParity(ParityBase):
    stem = "flightdeck_index"
    def test_regen(self):            self.assert_parity([], mutates=True)
    def test_check(self):            self.assert_parity(["--check"])
    def test_archivable(self):       self.assert_parity(["--archivable"])
    def test_advance(self):          self.assert_parity(["--advance-candidates"])
    def test_verify_pending(self):   self.assert_parity(["--verify-pending"])
    def test_match_signature(self):  self.assert_parity(["--match-signature", "boom"])
    # --sync-status / --*-consumers depend on ~/.flightdeck and are covered by a
    # dedicated env-pinned test (Task 3 Step N) to avoid touching the real home dir.

class LintParity(ParityBase):
    stem = "flightdeck_lint"
    def test_default(self):          self.assert_parity([])

class InitParity(ParityBase):
    stem = "flightdeck_init"
    # init/new take a fresh target + --date/--user; covered by their own
    # deterministic tests (Tasks 5/6) that pin date/user, not the deck-fixture matrix.

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Run — all skip (no .js yet), suite green**

Run: `uv run --with pytest pytest scripts/tests/test_parity.py -v`
Expected: all tests **skipped** ("… not ported yet" / "node not on PATH"), 0 failures.

- [ ] **Step 5: Commit**

```bash
git add scripts/tests/parity scripts/tests/test_parity.py
git commit -m "test(parity): golden fixture deck + dual-interpreter byte-diff harness (skips until ports land)"
```

---

### Task 2: Shared Node helper lib + unit parity

The landmine helpers, isolated and unit-parity-tested against Python before any script leans on them.

**Files:**
- Create: `scripts/flightdeck_lib.js`
- Create: `scripts/tests/test_flightdeck_lib_parity.py`

- [ ] **Step 1: Write `flightdeck_lib.js`**

Export, with these exact semantics:

```js
'use strict';
const crypto = require('crypto');

const DASH = '—'; // em dash —, the INDEX row delimiter

// Code-point comparison (NOT default UTF-16). Iterate code points.
function cmpCodepoint(a, b) {
  const ai = Array.from(a), bi = Array.from(b); // Array.from splits by code point
  const n = Math.min(ai.length, bi.length);
  for (let i = 0; i < n; i++) {
    const x = ai[i].codePointAt(0), y = bi[i].codePointAt(0);
    if (x !== y) return x < y ? -1 : 1;
  }
  return ai.length - bi.length;
}
const sortCp = (arr) => [...arr].sort(cmpCodepoint);

// Python json.dumps(list_of_str) with default separators: ["a", "b"]
function pyJsonArray(items) {
  return '[' + items.map((s) => JSON.stringify(s)).join(', ') + ']';
}

// Python json.dumps(obj, ensure_ascii=False, indent=2): match shape + key order.
// Implemented as a recursive serializer to control separators exactly.
function pyJsonIndent(value, level = 0) { /* full impl — see Step 2 test as the spec */ }

// sha1(utf8)[:12]
function fingerprint(key) {
  return crypto.createHash('sha1').update(key, 'utf8').digest('hex').slice(0, 12);
}

// Leading ---fenced frontmatter → {key: value}; {} when absent. Mirrors
// flightdeck_index.parse_frontmatter exactly (one `key: value` per line,
// first colon splits, both sides trimmed).
function parseFrontmatter(text) {
  const lines = text.split('\n');
  if (!lines.length || lines[0].trim() !== '---') return {};
  const fm = {};
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].trim() === '---') break;
    const idx = lines[i].indexOf(':');
    if (idx !== -1) fm[lines[i].slice(0, idx).trim()] = lines[i].slice(idx + 1).trim();
  }
  return fm;
}

module.exports = { DASH, cmpCodepoint, sortCp, pyJsonArray, pyJsonIndent, fingerprint, parseFrontmatter };
```

> `parseFrontmatter` note: Python splits on `\n` after `splitlines()` which also splits `\r`. Since the harness/runtime reads files that may contain `\r\n`, **strip `\r` first** (`text.replace(/\r\n/g, '\n')`) inside `parseFrontmatter` to match `splitlines()` behavior.

- [ ] **Step 2: Write the unit-parity test (Python computes the expected, JS must match)**

`scripts/tests/test_flightdeck_lib_parity.py` shells `node -e` to call each helper on a battery of inputs and compares to the Python reference:

```python
import json, subprocess, shutil, unittest
from pathlib import Path
import sys; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from flightdeck_index import signature_fingerprint, parse_frontmatter

LIB = Path(__file__).resolve().parent.parent / "flightdeck_lib.js"
HAVE_NODE = shutil.which("node") is not None

def node_eval(expr):
    js = f"const L=require({json.dumps(str(LIB))});process.stdout.write(String({expr}));"
    return subprocess.run(["node", "-e", js], capture_output=True, text=True).stdout

@unittest.skipUnless(HAVE_NODE, "node not on PATH")
class LibParity(unittest.TestCase):
    def test_sort_codepoint(self):
        items = ["b", "a", "Z", "é", "\U0001F600x", "ab", "aa"]
        py = sorted(items)
        js = json.loads(node_eval(f"JSON.stringify(L.sortCp({json.dumps(items)}))"))
        self.assertEqual(py, js)
    def test_py_json_array(self):
        items = ["/x", "/a", "/a"]
        py = json.dumps(sorted(set(items)))
        js = node_eval(f"L.pyJsonArray({json.dumps(sorted(set(items)))})")
        self.assertEqual(py, js)
    def test_fingerprint(self):
        self.assertEqual(signature_fingerprint("boom\nbang", "KeyError"),
                         node_eval('L.fingerprint("KeyError\\nboom bang")'))  # mirror normalize rule
    def test_frontmatter(self):
        txt = "---\nversion: 3.0\nruntime: uv\n---\nbody\n"
        py = parse_frontmatter(txt)
        js = json.loads(node_eval(f"JSON.stringify(L.parseFrontmatter({json.dumps(txt)}))"))
        self.assertEqual(py, js)
    def test_py_json_indent(self):
        obj = {"findings": [{"audit": "status", "severity": "CRITICAL",
                             "path": "x/y.md", "message": "缺 status"}]}
        py = json.dumps(obj, ensure_ascii=False, indent=2)
        js = node_eval(f"L.pyJsonIndent({json.dumps(obj)})")
        self.assertEqual(py, js)
```

> The `test_fingerprint` expected value must mirror `signature_fingerprint`'s key construction (`error_type + "\n" + normalize_symptom(symptom)`); when porting `--match-signature` in Task 3 the normalize rule moves into the lib — adjust this test to call `L.fingerprintSymptom(symptom, errorType)` then.

- [ ] **Step 3: Run → fails on `pyJsonIndent` (stub) + any helper drift**

Run: `uv run --with pytest pytest scripts/tests/test_flightdeck_lib_parity.py -v`
Expected: FAIL on `test_py_json_indent` (stub returns undefined) until Step 4.

- [ ] **Step 4: Implement `pyJsonIndent` to match Python `indent=2`**

Recursive serializer: objects → `{\n` + `"k": <val>` lines joined `,\n`, indented `level*2+2` spaces, closing `}` at `level*2`; arrays similarly with `[`/`]`; scalars via `JSON.stringify` (strings) / `String` (numbers) / `true|false|null`. Empty object → `{}`, empty array → `[]` (Python `indent` emits these compact). Non-ASCII passes through (don't escape — mirrors `ensure_ascii=False`).

- [ ] **Step 5: Run → green; Commit**

Run: `uv run --with pytest pytest scripts/tests/test_flightdeck_lib_parity.py -v` → PASS

```bash
git add scripts/flightdeck_lib.js scripts/tests/test_flightdeck_lib_parity.py
git commit -m "feat(node): shared parity helpers (codepoint sort, py-json spacing, sha1, frontmatter) + unit parity"
```

---

### Task 3: Port `flightdeck_index.js`

Faithful translation of all 772 lines / every subcommand, gated by `IndexParity` (Task 1 Step 3). Translate function-by-function against `scripts/flightdeck_index.py`; lean on `flightdeck_lib.js` for the landmine helpers. **Each subcommand's parity test is the per-function acceptance check.**

**Files:**
- Create: `scripts/flightdeck_index.js`
- Reference: `scripts/flightdeck_index.py` (the spec)
- Test: `scripts/tests/test_parity.py::IndexParity`

- [ ] **Step 1: Port the pure helpers** (gated by extending `test_flightdeck_lib_parity.py` as needed): `normalize_symptom` (the `_VOLATILE` regex list — translate each Python regex to JS `RegExp`, **preserving flags**: `re.I`→`i`; `\b`, `\d`, `\S` behave the same; the `_TIME_`/`_PATH_` alternations port verbatim), `signature_fingerprint`/`parse_signature`, `format_row`, `parse_frontmatter` (lib), `replace_auto_block`, `_area_row`, `_specs_grouped_body`, `_truncate_inprogress_summary` (note: `len(head)` counts **code points** in Python on a `str`; use `Array.from(head).length` in JS, and slice by code point).
- [ ] **Step 2: Port the deck scanners** preserving the **explicit `sorted()`** at each emission point and the `rglob` dedupe-by-resolved-path set (use `fs.realpathSync` for the `seen` set): `regen_folder_index`, `regen_cockpit_inprogress`, `match_signature`, `archivable_done`/`archivable_obsolete`, `spec_advance_candidates`, `verify_pending`, `index_drift`, `_index_targets`.
- [ ] **Step 3: Port the git + sync helpers**: `last_anchor_ref`/`changed_since_anchor` (`child_process.execFileSync("git", ["-C", deck, …])`, swallow ENOENT/non-zero like the Python `except`), `_resolve_master_root` (`os.homedir()+"/.flightdeck"`), consumer read/write (`_read_consumers`/`_write_consumers_line` using `pyJsonArray`), `register/list/prune_consumers`, `sync_status`.
- [ ] **Step 4: Port `main` + argparse** — replicate flag names, the **subcommand dispatch order** (archivable → advance → match-signature → changed-since-anchor → verify-pending → sync-status → register → list → prune → default regen), the `--check` drift exit code (1 on drift), the regen "create minimal INDEX when missing" branch, and the stdout strings (`"regenerated: …"` / `"already clean"` / `"DRIFT: …"` / `"clean"`, TAB-joined rows). Force LF on every `writeFileSync` (write `'\n'`-joined content; do not let anything inject `\r`).
- [ ] **Step 5: Run the index parity matrix**

Run: `uv run --with pytest pytest scripts/tests/test_parity.py::IndexParity -v`
Expected: PASS (was skipping). If a row diffs, the failing subcommand names the offending function.

- [ ] **Step 6: sync/consumer env-pinned parity** — add a test that points `HOME`/`USERPROFILE` at a temp dir holding a fake `~/.flightdeck` master, runs `--sync-status` + `--list-consumers` under both interpreters, byte-diffs. (Kept separate so the matrix never touches the real home dir.)
- [ ] **Step 7: Commit**

```bash
git add scripts/flightdeck_index.js scripts/tests/test_parity.py scripts/tests/test_flightdeck_lib_parity.py
git commit -m "feat(node): port flightdeck_index.js — byte-parity on all subcommands"
```

---

### Task 4: Port `flightdeck_lint.js`

Faithful translation of all audits, gated by `LintParity`. Reuses `flightdeck_index.js` (import its `indexDrift`, `parseFrontmatter`, the KIND constant sets).

**Files:**
- Create: `scripts/flightdeck_lint.js`
- Reference: `scripts/flightdeck_lint.py`
- Test: `scripts/tests/test_parity.py::LintParity`

- [ ] **Step 1: Port constants + `_strip_code`/`_clean_target`/`_finding`** — the `FENCE_RE`/`INLINE_CODE_RE`/`LINK_RE` regexes (JS needs `s`/`m` flags for the fence; the backreference `\1` for matched fence run-length ports directly), `VAGUE_TOKENS` (incl. the CJK `任何`/`所有`), `LEGAL_SETTINGS`, `REQUIRED_SECTIONS` patterns.
- [ ] **Step 2: Port every audit** preserving severity strings + message text **verbatim** (incl. the CJK `when_to_update` message and `sorted(legal)` rendering — `sorted({"uv","python","node"})` → `['node', 'python', 'uv']`; the JS must render the same Python-list-repr `['a', 'b']`, so add a `pyListRepr` helper or reuse `pyJsonArray` with single-quote variant — **match Python `str(sorted(set))` which uses single quotes**): `audit_status`, `audit_orphan_plans`, `audit_index_consistency`, `audit_dangling_refs`, `audit_stray`, `audit_required_structure`, `audit_when_to_update`, `audit_settings`.

> ⚠ Landmine: Python renders `{sorted(legal)}` as a **Python list repr with single quotes** (`['node', 'python', 'uv']`), not JSON double quotes. The Node port MUST emit single-quoted Python-style list repr here, or the message bytes differ. Add `pyListRepr(items)` → `"['" + items.join("', '") + "']"` (empty → `"[]"`).

- [ ] **Step 3: Port `lint()` aggregation order + `main`** — same audit call order, `json.dumps({"findings": findings}, ensure_ascii=False, indent=2)` via `pyJsonIndent`, the `--repo-root` default (deck parent), and the exit-1-when-blocking rule (any CRITICAL/WARNING).
- [ ] **Step 4: Run lint parity**

Run: `uv run --with pytest pytest scripts/tests/test_parity.py::LintParity -v` → PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/flightdeck_lint.js
git commit -m "feat(node): port flightdeck_lint.js — byte-parity on findings JSON"
```

---

### Task 5: Port `flightdeck_init.js`

**Files:**
- Create: `scripts/flightdeck_init.js`
- Reference: `scripts/flightdeck_init.py`
- Test: extend `scripts/tests/test_parity.py` with an `InitParity` deterministic test

- [ ] **Step 1: Port `init` + `main`** — `copytree(SCAFFOLD, deck)` → recursive copy (preserve bytes, LF), then the four `text.replace(...)` substitutions **including the backticked `Stage: \`<lifecycle stage>\`` literal** (matches the Phase-1 fix), `FileExistsError`→ throw + `refused:` message + exit 2, `--name/--user/--date/--focus/--next` defaults (date default = today; for parity tests **always pass `--date`/`--user`** to pin nondeterminism).
- [ ] **Step 2: Deterministic parity test** — run both with `--name p --user 月离 --date 2026-06-03 --focus f --next n` into fresh temp targets, byte-diff the entire created `flightdeck/` tree (LF-normalized).

```python
class InitDeterministic(ParityBase):
    stem = "flightdeck_init"
    def test_seed(self):
        if not HAVE_NODE: self.skipTest("node")
        if not (SCRIPTS / "flightdeck_init.js").is_file(): self.skipTest("not ported")
        # init takes a *target* (not a deck) — run each into its own temp dir, compare trees
        ...
```

- [ ] **Step 3: Run → PASS; Commit**

```bash
git add scripts/flightdeck_init.js scripts/tests/test_parity.py
git commit -m "feat(node): port flightdeck_init.js — byte-parity on seeded deck"
```

---

### Task 6: Port `flightdeck_new.js`

**Files:**
- Create: `scripts/flightdeck_new.js`
- Reference: `scripts/flightdeck_new.py` (read it first; 156 lines)
- Test: extend `scripts/tests/test_parity.py`

- [ ] **Step 1: Read `flightdeck_new.py`** to capture its exact frontmatter stamping, slug rule (`^[a-z0-9-]+$`), date-prefix rule (prefix iff `status != idea`; `doc` always dateless), folder map, and INDEX-regen call.
- [ ] **Step 2: Port `flightdeck_new.js`** preserving the naming/frontmatter/refusal contract and the post-write `flightdeck_index` invocation (the JS new must call the **JS** index when `runtime: node`, but for parity the test pins both to write the same files — call the same-language sibling).
- [ ] **Step 3: Deterministic parity test** — stamp a plan + an incident + a dateless idea spec under both, byte-diff the created file + regenerated INDEX.
- [ ] **Step 4: Run → PASS; Commit**

```bash
git add scripts/flightdeck_new.js scripts/tests/test_parity.py
git commit -m "feat(node): port flightdeck_new.js — byte-parity on stamped artifact + INDEX"
```

---

### Task 7: Delete the hand-written markdown fallbacks (runtime now mandatory)

Now that a runtime is required and the Node port exists, every "no runtime → rebuild by hand in markdown" double-write is dead code (spec §3.2). Delete it; the script is the only path. **Prose-only; gate with `rg` + pytest + English gate.**

**Files:** `skills/preflight/exit-ritual.md`, `skills/status/SKILL.md`, `skills/landing/SKILL.md`, `skills/new/SKILL.md`, `skills/walkaround/SKILL.md`

- [ ] **Step 1: exit-ritual.md** — delete `§ INDEX regeneration` / `§ Script fast path` hand-rebuild prose (the manual AUTO-block reconstruction) **and** the `Fallback (no Python runtime …)` anchor branch (Phase 1 deliberately left the runtime half of that branch; remove it now). Keep the `no anchor yet` half.
- [ ] **Step 2: status/SKILL.md** — delete step 5/5a fast-path + always-valid hand fallback; the status flip + INDEX regen is the script, unconditionally.
- [ ] **Step 3: landing/SKILL.md** — delete step 3 hand fallback.
- [ ] **Step 4: new/SKILL.md** — collapse Fast-path / no-runtime fallback into one: the script stamps the artifact (delete the "by hand" contract duplication, or demote it to a one-line "the script is the authority" pointer).
- [ ] **Step 5: walkaround/SKILL.md** — "optional fast path" wording → the mechanical audits run via `flightdeck_lint.py`/`flightdeck_index.py`, full stop.
- [ ] **Step 6: Verify**

Run: `rg -n 'no runtime|no Python runtime|hand[- ]?rebuild|by hand|fallback' skills` → review each remaining hit; the runtime-fallback ones must be gone (legit non-runtime uses of "fallback" — e.g. preflight's `## Next` empty fallback — stay).
Run: `rg -lP '\p{Han}' skills scaffolds` → empty.
Run: `uv run --with pytest pytest scripts/tests/ -q` → green.

- [ ] **Step 7: Commit**

```bash
git add skills/preflight/exit-ritual.md skills/status/SKILL.md skills/landing/SKILL.md skills/new/SKILL.md skills/walkaround/SKILL.md
git commit -m "feat(skill): force runtime — delete hand-written markdown fallbacks across the rituals"
```

---

### Task 8: Narrow launch detection + runtime dispatch (spec §4 / §5 runtime half)

**Files:** `skills/launch/SKILL.md`, `skills/preflight/protocol.md`

- [ ] **Step 1: launch/SKILL.md probe + refusal** — rewrite the "You MUST NOT inspect the repo" rule to "**only** git-existence + runtime detection (`uv` > `python` > `node`); project content untouched". Add the two hard refusals (spec §4.2): no git → `⚠ flightdeck requires git — run \`git init\`, then re-run launch.`; no runtime → `⚠ flightdeck needs a script runtime — install uv (recommended), python, or node, then re-run launch.`
- [ ] **Step 2: launch stamps `runtime` + prints pick-list** — write `runtime: <detected>` + `agents_md: off` into `rules.md` frontmatter zero-prompt (delegate to `flightdeck_init` which already copies the scaffold — extend init to accept `--runtime` and stamp it, or have launch edit the field post-init; pick one and note it). Print the non-blocking pick-list (spec §4.4 — final wording is publish-surface English, settled at implementation).
- [ ] **Step 3: protocol.md runtime dispatch** — Rule resolution order gains: skills select the script call form from the `runtime` field (`uv run …`/`python …`/`node …`); a recorded runtime that is not found → hard-fail the script step with `⚠ recorded runtime '<x>' not found — update rules.md (runtime:) or reinstall` (spec §5); preflight stays read-only but appends `⚠ recorded runtime broken`.
- [ ] **Step 4: Verify** — `rg -lP '\p{Han}' skills` empty; `uv run python scripts/flightdeck_lint.py flightdeck` no new findings; manual read-through of launch refusal wording.
- [ ] **Step 5: Commit**

```bash
git add skills/launch/SKILL.md skills/preflight/protocol.md
git commit -m "feat(skill): launch narrows probe to git+runtime, stamps runtime, refuses on missing; runtime dispatch in protocol"
```

---

### Task 9: Full-phase verification

- [ ] **Step 1: Full suite (both interpreters)**

Run: `uv run --with pytest pytest scripts/tests/ -q` → green (parity tests now run, not skip; `test_hooks.py` WSL-bash noise per the known incident is not a Phase-2 regression).
Run (node present): confirm `node --version` ≥ 18 and the parity matrix actually executed (not skipped) — `pytest scripts/tests/test_parity.py -v` shows PASS, not skip.

- [ ] **Step 2: Cross-runtime regen identity on the dogfood deck** — `node scripts/flightdeck_index.js flightdeck --check` and `uv run python scripts/flightdeck_index.py flightdeck --check` both print `clean` (or identical drift).
- [ ] **Step 3: English gate** — `rg -lP '\p{Han}' skills scaffolds` empty.
- [ ] **Step 4: No-fallback residue** — `rg -n 'no Python runtime|no runtime → ' skills` empty.
- [ ] **Step 5: Phase-2 done** — Tasks 1–8 committed + Steps green → the phase can flip `done` via `/flightdeck:status` (the ritual, not by hand). Phase 3 (`agents_md`/`runtime` field *reads* wired into landing/status/emit-agents-md; runtime-broken hard-fail) is a separate plan.

---

## Self-review (against the spec)

- **§3.2 force runtime / delete fallbacks** → Task 7 covers exit-ritual/status/landing/new/walkaround; Task 8 covers launch. ✅
- **§3.3 Node port of the 4 scripts** → Tasks 3–6; **`bump_version` excluded** ✅; **zero npm deps** (built-ins only) ✅.
- **§3.3 parity contract (spec-level)** → Task 1 harness + Task 2 helpers + the per-script golden gates encode every pinned rule (codepoint sort, LF, NFC-passthrough, JSON spacing, single-quote list repr). ✅
- **§4 launch narrowing + refusals + pick-list + zero-prompt stamp** → Task 8. ✅
- **§5 runtime dispatch + recorded-runtime-broken hard-fail** → Task 8 Step 3 (the *dispatch* + broken-runtime rule). The `agents_md` field *read* and the landing/status field-reading wiring are **Phase 3** — out of scope here (noted Task 9 Step 5).
- **§8 open items**: Node floor pinned at **≥ 18** (`Array.from` codepoint split, `crypto`, `fs` all ≥ 18; `fs.globSync` not used — explicit recursive walk + sort instead, sidestepping the §8 Node-22 `globSync` question). Illegal-value reporting is already Phase-1's `audit_settings`; the Node `flightdeck_lint.js` reproduces it (Task 4).
- **Placeholder scan**: the script-port tasks intentionally reference the Python source as the line-level spec (a faithful port) rather than re-typing 1400 lines; every *new* logic surface (harness, lib helpers, the parity landmines) carries full code. The port acceptance is mechanical (golden byte-diff), not prose. No "TBD"/"handle edge cases" left.
- **Type consistency**: helper names are stable across tasks (`cmpCodepoint`/`sortCp`/`pyJsonArray`/`pyJsonIndent`/`pyListRepr`/`fingerprint`/`parseFrontmatter`); `pyListRepr` (single-quote, Task 4) is distinct from `pyJsonArray` (double-quote JSON, Task 2) — both defined, used where Python uses `str(sorted)` vs `json.dumps` respectively.
