---
status: active
summary: 实现机械 section-single-writer sync：flightdeck_index.py/.js 加边界锚 + shared-region 指纹 + 机械 pull，sync_status 重键为指纹（stale/in-sync），CLI --sync-pull/--check，Node 端 byte-parity；迁移 commits/comments 插锚（本仓+母库）；sync skill 删 back-flow 改机械、preflight 入口加机械刷新前步 + zero-write 精确化、templates/protocol 记锚约定、walkaround 同步新状态
last_updated: 2026-06-20
implements: specs/2026-06-20-sync-mechanical-pull.md
---

# Sync mechanical pull — implementation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the timestamped, AI-merged shared-knowledge sync with a purely mechanical section-single-writer model — a boundary marker splits each vendored file into a master-owned shared region and a consumer-owned project region; staleness is a content fingerprint; the pull is a script-side text splice (zero AI tokens).

**Architecture:** All sync logic lives in `flightdeck_index.py` (+ its `.js` byte-parity twin): a `PROJECT_MARKER` constant, shared-region extraction, a fingerprint over the normalized shared region, and a mechanical `pull_shared` splice. `sync_status` is re-keyed from `last_updated` to the fingerprint (states collapse to `in-sync`/`stale`). A new `--sync-pull` CLI applies the splice. Then the skill/prose layer (sync, preflight, walkaround, templates/protocol) is updated to the new model, and the two existing vendored files are migrated by inserting the marker.

**Tech Stack:** Python 3.8+ stdlib only (`hashlib`, `unicodedata`); Node built-ins only, zero npm; `unittest` + the existing `scripts/tests/parity` harness.

## Global Constraints

- **py/js byte-parity (spec §4.4 contract):** codepoint sort, LF newlines, UTF-8 NFC, stable JSON, dates via `--date` — never wall-clock. Every behavior identical across `.py`/`.js`, locked by `scripts/tests/test_parity.py`.
- **Pure stdlib (py) / built-ins only, zero npm (js).**
- **Publishing surface English-only** (`scripts/` + `skills/`): `rg -lP '\p{Han}' scripts skills` stays clean (except already-whitelisted `VAGUE_TOKENS` / Unicode-fixture lines).
- **Boundary marker literal (exact):** `<!-- flightdeck:project-specific -->`.
- **Master root:** fixed `~/.flightdeck` (`_resolve_master_root`, unchanged).
- **Fingerprint regime:** `hashlib.sha1(utf8(normalized)).hexdigest()[:12]` — same as `signature_fingerprint`; js mirrors `flightdeck_lib.fingerprint`.
- **Routine sync is AI-zero** (script only); AI appears only in `promote` (unchanged) and the non-git `diff+confirm` gate.

---

### Task 1: Shared-region extraction + fingerprint (py)

**Files:**
- Modify: `scripts/flightdeck_index.py` (add constant + 4 helpers near `signature_fingerprint`)
- Test: `scripts/tests/test_flightdeck_index.py`

**Interfaces:**
- Produces: `PROJECT_MARKER: str`; `shared_region(text) -> str` (body above the marker, frontmatter stripped; whole body when no marker); `shared_fingerprint(text) -> str` (12-hex). Also internal `_strip_frontmatter(text) -> str`, `_normalize_shared(s) -> str`.

- [ ] **Step 1: Write the failing test**

```python
from flightdeck_index import PROJECT_MARKER, shared_region, shared_fingerprint

def test_shared_region_splits_at_marker():
    text = ("---\nstatus: active\n---\n# Title\n\nshared body\n\n"
            f"{PROJECT_MARKER}\n## Project-specific\nlocal\n")
    assert shared_region(text) == "# Title\n\nshared body\n\n"

def test_shared_region_no_marker_is_whole_body():
    text = "---\nx: 1\n---\nonly shared\n"
    assert shared_region(text) == "only shared\n"

def test_fingerprint_ignores_frontmatter_and_project_and_trailing_ws():
    a = ("---\nwhen_to_read: A\n---\n# T\n\nbody\n\n"
         f"{PROJECT_MARKER}\nproj A\n")
    b = ("---\nwhen_to_read: B-localized\n---\n# T\n\nbody  \n\n\n"  # trailing ws + blank
         f"{PROJECT_MARKER}\nproj B different\n")
    assert shared_fingerprint(a) == shared_fingerprint(b)

def test_fingerprint_changes_with_shared_content():
    a = "---\n---\nbody one\n"
    b = "---\n---\nbody two\n"
    assert shared_fingerprint(a) != shared_fingerprint(b)
```

- [ ] **Step 2: Run → FAIL** (`uv run pytest scripts/tests/test_flightdeck_index.py -k shared -q`; names undefined).

- [ ] **Step 3: Implement** (place after `signature_fingerprint`, ~line 54)

```python
PROJECT_MARKER = "<!-- flightdeck:project-specific -->"


def _strip_frontmatter(text):
    """Body after a leading ---fenced frontmatter block (whole text when none)."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "".join(lines[i + 1:])
    return text


def shared_region(text):
    """Master-owned region: frontmatter-stripped body up to PROJECT_MARKER;
    the whole body when the marker is absent (pure-shared file)."""
    body = _strip_frontmatter(text)
    idx = body.find(PROJECT_MARKER)
    return body if idx == -1 else body[:idx]


def _normalize_shared(s):
    """Canonicalize for fingerprint compare: NFC, LF, strip per-line trailing
    whitespace, drop trailing blank lines."""
    s = unicodedata.normalize("NFC", s).replace("\r\n", "\n").replace("\r", "\n")
    s = "\n".join(line.rstrip() for line in s.split("\n"))
    return s.rstrip("\n")


def shared_fingerprint(text):
    """12-hex sha1 of the normalized shared region (signature_fingerprint regime)."""
    norm = _normalize_shared(shared_region(text))
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:12]
```

Add `import unicodedata` at the top with the other stdlib imports.

- [ ] **Step 4: Run → PASS** (`uv run pytest scripts/tests/test_flightdeck_index.py -k shared -q`).
- [ ] **Step 5: Commit** `feat(sync): shared-region extraction + fingerprint`.

---

### Task 2: Mechanical pull splice (py)

**Files:**
- Modify: `scripts/flightdeck_index.py`
- Test: `scripts/tests/test_flightdeck_index.py`

**Interfaces:**
- Consumes: `PROJECT_MARKER`, `_strip_frontmatter`.
- Produces: `pull_shared(consumer_text, master_text) -> str` — consumer frontmatter + marker + project section kept verbatim; the shared region replaced by the master's body.

- [ ] **Step 1: Write the failing test**

```python
from flightdeck_index import pull_shared, PROJECT_MARKER, shared_fingerprint

def test_pull_replaces_shared_keeps_frontmatter_and_project():
    consumer = ("---\nsynced: true\nwhen_to_read: localized\n---\n# Old\n\nold shared\n\n"
                f"{PROJECT_MARKER}\n## Project-specific\nMY local rule\n")
    master = "---\nconsumers: [x]\n---\n# New\n\nnew shared\n"
    out = pull_shared(consumer, master)
    assert "when_to_read: localized" in out      # consumer frontmatter kept
    assert "consumers" not in out                 # master frontmatter dropped
    assert "new shared" in out and "old shared" not in out
    assert "MY local rule" in out                 # project section kept
    assert out.count(PROJECT_MARKER) == 1

def test_pull_is_idempotent_under_fingerprint():
    consumer = (f"---\nsynced: true\n---\nold\n\n{PROJECT_MARKER}\nproj\n")
    master = "---\n---\n# T\n\nfresh shared\n"
    out = pull_shared(consumer, master)
    assert shared_fingerprint(out) == shared_fingerprint(master)

def test_pull_no_marker_becomes_master_body():
    consumer = "---\nsynced: true\n---\nold whole body\n"
    master = "---\n---\nnew whole body\n"
    out = pull_shared(consumer, master)
    assert "new whole body" in out and "old whole body" not in out
    assert out.startswith("---\nsynced: true\n---\n")
```

- [ ] **Step 2: Run → FAIL.**
- [ ] **Step 3: Implement**

```python
def _split_frontmatter(text):
    """Return (frontmatter_incl_fences_or_'', body)."""
    lines = text.splitlines(keepends=True)
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "".join(lines[:i + 1]), "".join(lines[i + 1:])
    return "", text


def pull_shared(consumer_text, master_text):
    """Mechanical splice: keep consumer frontmatter + marker + project section,
    replace the shared region with the master's body."""
    fm, body = _split_frontmatter(consumer_text)
    master_body = _strip_frontmatter(master_text)
    idx = body.find(PROJECT_MARKER)
    if idx == -1:
        return fm + master_body
    tail = body[idx:]                       # marker + project section
    shared = master_body.rstrip("\n") + "\n\n"
    return fm + shared + tail
```

- [ ] **Step 4: Run → PASS.**
- [ ] **Step 5: Commit** `feat(sync): mechanical pull splice`.

---

### Task 3: Re-key `sync_status` to the fingerprint (py)

**Files:**
- Modify: `scripts/flightdeck_index.py:559-601` (`sync_status`)
- Test: `scripts/tests/test_flightdeck_index.py`

**Interfaces:**
- Produces: `sync_status(deck) -> [(state, relpath)]` with states `in-sync` / `stale` / `dangling` / `master-missing` (the `upstream-changed`/`locally-ahead` timestamp split is removed — shared is master-authoritative, so any difference is `stale`).

- [ ] **Step 1: Write the failing test** (uses a temp deck + temp master via monkeypatching `_resolve_master_root`)

```python
import flightdeck_index as idx

def _mk(p, text): p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text, encoding="utf-8")

def test_sync_status_stale_vs_insync(tmp_path, monkeypatch):
    deck = tmp_path / "deck"; master = tmp_path / "master"
    monkeypatch.setattr(idx, "_resolve_master_root", lambda: master)
    _mk(master / "checklists/commits.md", "---\n---\n# T\n\nSHARED v2\n")
    _mk(deck / "checklists/commits.md",
        f"---\nsynced: true\n---\n# T\n\nSHARED v2\n\n{idx.PROJECT_MARKER}\nlocal\n")
    _mk(deck / "checklists/comments.md", "---\nsynced: true\n---\n# T\n\nSHARED old\n")
    assert idx.sync_status(deck) == [("in-sync", "checklists/commits.md"),
                                     ("stale", "checklists/comments.md")]
```

- [ ] **Step 2: Run → FAIL** (still emits `upstream-changed`/`locally-ahead`).

- [ ] **Step 3: Implement** — replace the `last_updated` comparison block (the `proj_lu`/`mast_lu` lines) with:

```python
        master_text = master_file.read_text(encoding="utf-8")
        state = "in-sync" if shared_fingerprint(text) == shared_fingerprint(master_text) else "stale"
        out.append((state, rel))
```

Read the consumer's full text once (rename the per-file read so `text` is available): change the top of the loop to keep `text = p.read_text(...)` and derive `fm = parse_frontmatter(text)`. Update the docstring states list.

- [ ] **Step 4: Run → PASS.**
- [ ] **Step 5: Commit** `feat(sync): re-key sync_status to shared fingerprint`.

---

### Task 4: `--sync-pull` CLI (py)

**Files:**
- Modify: `scripts/flightdeck_index.py` (`main` arg parser + dispatch)
- Test: `scripts/tests/test_flightdeck_index.py`

**Interfaces:**
- Produces: `--sync-pull` (apply mechanical pull to every `stale` vendored file; prints `pulled\t<rel>` per file) and `--sync-pull --check` (dry-run: prints `would-pull\t<rel>`, writes nothing, exit 1 if any stale). `master-missing` → print nothing, exit 0 (graceful).

- [ ] **Step 1: Write the failing test**

```python
def test_sync_pull_applies_and_check_is_dryrun(tmp_path, monkeypatch, capsys):
    deck = tmp_path / "deck"; master = tmp_path / "master"
    monkeypatch.setattr(idx, "_resolve_master_root", lambda: master)
    _mk(master / "checklists/commits.md", "---\n---\n# T\n\nFRESH\n")
    cpath = deck / "checklists/commits.md"
    _mk(cpath, f"---\nsynced: true\n---\n# T\n\nOLD\n\n{idx.PROJECT_MARKER}\nlocal\n")
    # --check: writes nothing, exit 1
    rc = idx.main([str(deck), "--sync-pull", "--check"])
    assert rc == 1 and "OLD" in cpath.read_text(encoding="utf-8")
    # apply: shared replaced, project kept
    rc = idx.main([str(deck), "--sync-pull"])
    body = cpath.read_text(encoding="utf-8")
    assert rc == 0 and "FRESH" in body and "OLD" not in body and "local" in body
```

- [ ] **Step 2: Run → FAIL.**

- [ ] **Step 3: Implement** — add the arg and a dispatch block before the INDEX-regen tail of `main`:

```python
    ap.add_argument("--sync-pull", action="store_true",
                    help="apply mechanical shared-knowledge pull: replace each stale "
                    "synced:true file's shared region with its master's (keeps "
                    "frontmatter + project section). With --check: report only, exit 1 if any stale.")
```
```python
    if args.sync_pull:
        master_root = _resolve_master_root()
        if master_root is None:
            return 0
        pending = False
        for state, rel in sync_status(args.deck):
            if state != "stale":
                continue
            pending = True
            if args.check:
                print(f"would-pull\t{rel}")
                continue
            cpath = Path(args.deck) / rel
            new = pull_shared(cpath.read_text(encoding="utf-8"),
                              (master_root / rel).read_text(encoding="utf-8"))
            cpath.write_text(new, encoding="utf-8")
            print(f"pulled\t{rel}")
        return 1 if (args.check and pending) else 0
```

- [ ] **Step 4: Run → PASS.**
- [ ] **Step 5: Commit** `feat(sync): --sync-pull CLI (apply + --check)`.

---

### Task 5: Node port + byte-parity

**Files:**
- Modify: `scripts/flightdeck_index.js` (mirror Tasks 1–4); `scripts/flightdeck_lib.js` if a shared helper is cleaner
- Test: `scripts/tests/test_parity.py` (extend `IndexParity`); `scripts/tests/parity/fixture_deck` (+ a master fixture)

**Interfaces:** `flightdeck_index.js` exports/behaves identically: `PROJECT_MARKER`, `sharedRegion`, `sharedFingerprint`, `pullShared`, re-keyed `syncStatus`, `--sync-pull`.

- [ ] **Step 1: Add parity coverage.** `sync_status`/`--sync-pull` need a master root; the parity harness can point `~/.flightdeck` at a fixture via a junction OR the test sets `HOME`/`USERPROFILE` to a temp dir containing `.flightdeck`. Add to `IndexParity`:

```python
def test_sync_pull_check(self):
    self.assert_parity(["--sync-pull", "--check"])
```
(Seed the temp HOME's `~/.flightdeck/checklists/commits.md` with a shared body differing from the fixture deck's, so both interpreters see one `would-pull` line. Mirror the `_copy_deck` helper with a `_seed_master` helper that sets `env` for both subprocesses.)

- [ ] **Step 2: Run → FAIL/skip** (js lacks the new functions).

- [ ] **Step 3: Port** into `flightdeck_index.js`, mirroring the py exactly: `PROJECT_MARKER` constant; `stripFrontmatter`; `sharedRegion`; `normalizeShared` (NFC via `s.normalize('NFC')`, `\r\n?`→`\n`, per-line `replace(/\s+$/,'')`, strip trailing `\n`); `sharedFingerprint` via `fingerprint()` from `flightdeck_lib`; `splitFrontmatter`; `pullShared`; re-keyed `syncStatus`; `--sync-pull`/`--check` in the arg loop + dispatch.

- [ ] **Step 4: Run → PASS** (`uv run pytest scripts/tests/test_parity.py -q`).
- [ ] **Step 5: Run full suite** `uv run pytest scripts/tests/ -q` → green; **Han gate** `rg -lP '\p{Han}' scripts` clean. Commit `feat(sync): node port + byte-parity`.

---

### Task 6: Migrate the two vendored files (insert the marker)

**Files:**
- Modify: `flightdeck/checklists/commits.md`, `flightdeck/checklists/comments.md` (repo) **and** `~/.flightdeck/checklists/commits.md`, `~/.flightdeck/checklists/comments.md` (master)

**Interfaces:** none (data migration). After this, `flightdeck_index.py <deck> --sync-status` reports both `in-sync`.

- [ ] **Step 1:** In each **repo** consumer file, insert a line `<!-- flightdeck:project-specific -->` immediately **above** the `## 项目覆盖` heading (so title+intro+通用 are the shared region; `## 项目覆盖` and below are project). The **master** files have no `## 项目覆盖` section — they need **no** marker (pure-shared).
- [ ] **Step 2: Verify** `uv run scripts/flightdeck_index.py flightdeck --sync-status` → both `in-sync` (fingerprint of repo shared region == master body). If `stale`, the repo shared body drifted from master — reconcile by hand (master is authority) before continuing.
- [ ] **Step 3: Commit** `chore(sync): insert project-specific marker into vendored checklists`.

---

### Task 7: Rewrite the `sync` skill + marker convention + walkaround states

**Files:**
- Modify: `skills/sync/SKILL.md`; `skills/preflight/templates.md`; `skills/walkaround/SKILL.md`

**Interfaces:** prose. English-only.

- [ ] **Step 1: `skills/sync/SKILL.md`** — rewrite to the mechanical model:
  - **Drop §C back-flow** (`locally-ahead` push) entirely. Keep **promote** (new file consumer→master, AI-judged generality) and **fanout** (now a pure-script `--sync-pull` loop over `--list-consumers`).
  - Pull (§A) becomes: run `flightdeck_index.py <deck> --sync-pull [--check]` (call form per recorded `runtime`); states are `in-sync` / `stale` / `dangling` / `master-missing`; **no AI merge** — the script splices. Keep the `dangling`/`master-missing` handling.
  - Document the **boundary marker** `<!-- flightdeck:project-specific -->`: shared region above (master-owned), project section below (consumer-owned, never pulled/pushed); frontmatter routing stays consumer-local.
  - Irreversibility note: non-git deck → `--sync-pull --check` first (diff), then apply.
- [ ] **Step 2: `skills/preflight/templates.md`** — in the vendored-file / `synced` guidance, add the marker convention (one short subsection: the literal marker, what's above/below, that pull is mechanical).
- [ ] **Step 3: `skills/walkaround/SKILL.md`** — update the sync-drift audit that reads `sync_status` states: replace `upstream-changed`/`locally-ahead` handling with `stale` → INFO "shared knowledge stale — `/flightdeck:sync`"; keep `dangling` → report, `master-missing` → don't report. Update the skill's `description` frontmatter line accordingly.
- [ ] **Step 4: Verify** `rg -lP '\p{Han}' skills` clean. Commit `docs(sync): rewrite sync skill to mechanical model + marker convention`.

---

### Task 8: preflight entry refresh + zero-write precision + deck-rule escape hatch

**Files:**
- Modify: `skills/preflight/SKILL.md`; `skills/preflight/protocol.md`

**Interfaces:** prose. English-only.

- [ ] **Step 1: `skills/preflight/protocol.md`** — precision-edit the zero-write rule: state it as **"preflight performs no *judgment* writes"** (no `Updated` bump, no INDEX regen, no artifact/status writes). Add that a **deterministic shared-knowledge refresh** is a distinct mechanical layer (same category as the turn-end INDEX hook), run **before** the preflight read, never part of the checklist. Document the boundary marker + shared/project regions in the data-model section.
- [ ] **Step 2: `skills/preflight/SKILL.md`** — add a **Step 0.5 "Shared-knowledge refresh (mechanical, pre-read)"** *before* the catalog warm-up:
  - Run `flightdeck_index.py <deck> --sync-pull` (call form per recorded `runtime`). **git deck:** apply + report one line `↻ synced N shared file(s) from master` (reversible via git). **non-git deck:** run `--sync-pull --check` first, show the diff, and **ask** before applying (irreversible — same discipline as conform).
  - `master-missing` → silent no-op. State explicitly: this is the **only** write preflight triggers, it touches **only** vendored shared regions, and preflight's own checklist remains zero-write.
  - **Escape hatch:** a deck `### Rules` entry (e.g. "sync: detect-only on entry") downgrades this to read-only `--sync-pull --check` + a one-line stale note (no auto-write), per the rule-resolution order.
- [ ] **Step 3:** Update the preflight `description` frontmatter + the output-format banner note to mention the refresh line.
- [ ] **Step 4: Verify** `rg -lP '\p{Han}' skills` clean; dry-run `flightdeck_index.py flightdeck --sync-pull --check` against the dogfood deck reads `0 stale`. Commit `docs(sync): preflight entry refresh + zero-write precision`.

---

## Self-review notes

- **Spec coverage:** §2 single-writer → Tasks 2/7 (drop back-flow, mechanical pull); §3 marker → Tasks 1/6/7/8; §4 fingerprint key → Tasks 1/3; §5 lazy pull/fanout → Tasks 4/7; §6 zero-write reconciliation → Task 8; §7 整改面 → Tasks 5 (index+parity), 6 (migration), 7 (sync skill + walkaround + templates), 8 (preflight + protocol); §8 promote-stays-AI → Task 7 (kept).
- **Type consistency:** `shared_region` / `shared_fingerprint` / `pull_shared` / `_strip_frontmatter` / `_split_frontmatter` used identically across Tasks 1–4; js mirrors as `sharedRegion`/`sharedFingerprint`/`pullShared` (Task 5).
- **Marker literal** is identical everywhere: `<!-- flightdeck:project-specific -->`.
- **Open micro-decision for the executor:** the turn-end-hook optimization (spec §6) is intentionally **not** a task — it's an environment-specific hook change; ship the entry refresh first, add the hook as a follow-up if warm-project freshness proves worth it.
