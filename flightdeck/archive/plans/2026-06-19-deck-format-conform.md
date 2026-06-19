---
status: done
summary: Implement the deck format conformer: new flightdeck_conform.py/.js (py/js byte-parity) that deletes non-schema frontmatter fields across all active files + adds missing section skeletons on cockpit.md/rules.md and stamps rules runtime/agents_md, printing a missing-required-field worklist; plus a thin /flightdeck:conform skill that runs the script then does the AI semantic-fill pass; excludes archive and stray folders; no registry, no history.
last_updated: 2026-06-20
implements: specs/2026-06-19-deck-format-conform.md
---

# Deck format conform — implementation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a deck formatter that conforms any deck to the current canonical shape — a script does the mechanical pass (delete non-schema frontmatter fields across all active files, stamp rules recorded-config, add missing cockpit/rules section skeletons, print a missing-required worklist), and a thin `/flightdeck:conform` skill runs the script then does the AI semantic-fill pass.

**Architecture:** New mutating script `flightdeck_conform.py` + Node twin `.js` (byte-parity, like the alpha.4 ports). It **only ever touches frontmatter + appends missing cockpit/rules sections** — it never rewrites cockpit body labels or deletes sections (that destructive/judgment reshaping is the AI pass's job). The `/flightdeck:conform` skill orchestrates: run script (per recorded `runtime`) → AI reads cockpit.md/rules.md fully + the script's worklist files → fills semantics → report.

**Tech Stack:** Python 3.8+ stdlib only (mirrors `flightdeck_index.py`); Node built-ins only, zero npm; `unittest` + the existing `scripts/tests/parity` harness.

## Global Constraints

- **py/js byte-parity (spec §3.3 / alpha.4 contract):** codepoint sort, LF newlines, UTF-8 NFC, stable JSON (Python `json.dumps` spacing), dates via `--date` arg — never wall-clock. Every script behavior must be identical across `.py`/`.js`, locked by `scripts/tests/parity`.
- **Pure stdlib (py) / built-ins only, zero npm (js).**
- **Publishing surface is English-only** (`scripts/` + `skills/`): `rg -lP '\p{Han}' scripts skills` must stay empty (except the kept `VAGUE_TOKENS` + Unicode-fixture lines already whitelisted).
- **Scope = active deck only:** `cockpit.md`, `rules.md`, and non-archive `.md` under `specs/ plans/ incidents/ checklists/ docs/ references/` (incl. legal area nesting). **Exclude `archive/` and any folder not in that set.**
- **Legal field-set source = `skills/preflight/protocol.md` § Frontmatter field reference + `templates.md` per-kind schema.** Do not invent fields.
- **No registry, no history, no undo file.** Deletion is permanent (non-git decks have no rollback).
- **Two modes:** default = apply + write; `--check` = dry-run, print planned changes, write nothing, exit 1 if any change is pending (mirrors `flightdeck_index --check`).

---

### Task 1: Per-kind field-set constants + drift-guard test

**Files:**
- Create: `scripts/flightdeck_conform.py` (constants + module skeleton only this task)
- Test: `scripts/tests/test_flightdeck_conform.py`

**Interfaces:**
- Produces: `LEGAL_FIELDS: dict[str, set[str]]` and `REQUIRED_FIELDS: dict[str, set[str]]` keyed by kind (`spec/plan/incident/checklist/reference/doc/rules`); `kind_of(deck, path) -> str | None` (folder→kind, `rules.md`→`"rules"`, `cockpit.md`→`None`/skip, archive→`None`).

- [ ] **Step 1: Write the failing test** pinning the legal/required sets (changing a set must require changing this test = intentional drift guard) and `kind_of` routing.

```python
from flightdeck_conform import LEGAL_FIELDS, REQUIRED_FIELDS, kind_of
def test_required_subset_of_legal():
    for k, req in REQUIRED_FIELDS.items():
        assert req <= LEGAL_FIELDS[k], k
def test_spec_legal_set_pinned():
    assert LEGAL_FIELDS["spec"] == {"status","summary","last_updated","note","supersedes","related","graduate","verify"}
def test_knowledge_required_pinned():
    assert REQUIRED_FIELDS["checklist"] == {"status","when_to_read","applies_to","last_updated"}
def test_kind_of_routes_and_excludes_archive(tmp_path):
    assert kind_of(tmp_path, tmp_path/"checklists"/"x.md") == "checklist"
    assert kind_of(tmp_path, tmp_path/"archive"/"specs"/"x.md") is None
    assert kind_of(tmp_path, tmp_path/"cockpit.md") is None
```

- [ ] **Step 2: Run → FAIL** (`uv run pytest scripts/tests/test_flightdeck_conform.py -q`; module/constants absent).
- [ ] **Step 3: Implement** `LEGAL_FIELDS`/`REQUIRED_FIELDS` (transcribe from `templates.md`: spec/plan/incident/checklist/reference/doc sets incl. optional `note/implements/supersedes/related/graduate/verify/when_to_update/skip_when/recurrences/resolved_by/synced`; `rules` = `{version,runtime,agents_md}`) + `kind_of` (reuse `flightdeck_index.FOLDER` constants where possible; archive path → None).
- [ ] **Step 4: Run → PASS.**
- [ ] **Step 5: Commit** `feat(conform): per-kind field-set constants + routing`.

---

### Task 2: Frontmatter delete (mechanical core, `--check` + apply)

**Files:**
- Modify: `scripts/flightdeck_conform.py`
- Test: `scripts/tests/test_flightdeck_conform.py`

**Interfaces:**
- Consumes: `LEGAL_FIELDS`, `kind_of`, `flightdeck_index.parse_frontmatter`.
- Produces: `prune_frontmatter(text, kind) -> (new_text, removed: list[str])` (drops keys ∉ `LEGAL_FIELDS[kind]`, preserves order + body byte-for-byte); `conform_file(path, kind, apply: bool) -> Changes`.

- [ ] **Step 1: Write the failing test** — a checklist with `portable: true` + `when_to_read/applies_to/...` → `portable` removed, all legal fields + body untouched; `--check` writes nothing.

```python
def test_prune_drops_nonschema_keeps_legal_and_body():
    text = "---\nstatus: active\nwhen_to_read: x\napplies_to: [a]\nlast_updated: 2026-06-19\nportable: true\n---\n# body\n"
    out, removed = prune_frontmatter(text, "checklist")
    assert removed == ["portable"]
    assert "portable" not in out and "# body" in out and "when_to_read: x" in out
```

- [ ] **Step 2: Run → FAIL.**
- [ ] **Step 3: Implement** `prune_frontmatter` (line-filter the `---`-fenced block, keep non-`key:` lines like comments, preserve everything after the closing `---` verbatim) + `conform_file`.
- [ ] **Step 4: Run → PASS.**
- [ ] **Step 5: Commit** `feat(conform): frontmatter schema-delete with check/apply`.

---

### Task 3: rules.md recorded-config stamp

**Files:** Modify `scripts/flightdeck_conform.py`; Test `scripts/tests/test_flightdeck_conform.py`

**Interfaces:** Produces `stamp_rules(text, runtime) -> new_text` — inserts `version: 3.0` (if absent), `agents_md: off` (if absent), `runtime: <detected>` (if absent), into the frontmatter without disturbing existing keys/order.

- [ ] **Step 1: Write failing test** — rules.md missing all three → gets `version: 3.0`, `runtime: <passed>`, `agents_md: off`; an existing `version`/`agents_md` is left untouched.
- [ ] **Step 2: Run → FAIL.**
- [ ] **Step 3: Implement** `stamp_rules` (runtime value comes from a probe `detect_runtime()` = `uv`>`python`>`node`, same order as launch; injected via `--runtime` arg for determinism/parity).
- [ ] **Step 4: Run → PASS.**
- [ ] **Step 5: Commit** `feat(conform): stamp rules version/runtime/agents_md`.

---

### Task 4: cockpit/rules missing-section skeletons (append-only)

**Files:** Modify `scripts/flightdeck_conform.py`; Test `scripts/tests/test_flightdeck_conform.py`

**Interfaces:** Produces `add_missing_sections(text, which) -> (new_text, added: list[str])` where `which ∈ {"cockpit","rules"}`. Canonical section lists are constants: `COCKPIT_SECTIONS = ["## Next","## In Progress","## Key Context","## Pending Review","## Hanging Tasks"]`, `RULES_SECTIONS = ["## House rules","### Project conventions","### Rules"]`. **Append-only** — never deletes or reorders (deletion/relabel is the AI pass).

- [ ] **Step 1: Write failing test** — a cockpit missing `## Key Context` + `## Pending Review` gets each appended with a `- (none)` placeholder; an `## In Progress` that already exists is not duplicated.
- [ ] **Step 2: Run → FAIL.**
- [ ] **Step 3: Implement** `add_missing_sections` (detect by heading regex; append skeleton with placeholder; `## In Progress` skeleton includes the `<!-- AUTO:inprogress -->`/`<!-- /AUTO -->` markers).
- [ ] **Step 4: Run → PASS.**
- [ ] **Step 5: Commit** `feat(conform): append missing cockpit/rules sections`.

---

### Task 5: CLI — walk in-scope, apply, print worklist + `--check`

**Files:** Modify `scripts/flightdeck_conform.py` (the `main()` + arg parser); Test `scripts/tests/test_flightdeck_conform.py`

**Interfaces:** Produces `main(argv) -> int`. Default: applies prune+stamp+sections to every in-scope file, then prints the **missing-required worklist** `<relpath>\t<missing-field>` (one line per missing required field, sorted) on stdout for the AI pass. `--check`: prints the same planned changes prefixed, writes nothing, exits 1 if anything pending. UTF-8 stdout (`reconfigure`, like `flightdeck_index`).

- [ ] **Step 1: Write failing test** — a temp deck (cockpit + rules + a checklist missing `when_to_read` + an archived file) → after `main([deck])`: `portable` gone, rules stamped, cockpit sections added, **archived file untouched**, stdout worklist contains `checklists/<f>.md\twhen_to_read`.
- [ ] **Step 2: Run → FAIL.**
- [ ] **Step 3: Implement** `main` (walk `REGEN_FOLDERS`-style in-scope set excluding archive + cockpit/rules special-casing; `--date`/`--runtime` args for determinism).
- [ ] **Step 4: Run → PASS.**
- [ ] **Step 5: Commit** `feat(conform): CLI walk + worklist + --check`.

---

### Task 6: Node port + parity

**Files:** Create `scripts/flightdeck_conform.js`; Modify `scripts/tests/test_parity.py` (add a `ConformParity` class)

**Interfaces:** `flightdeck_conform.js` mirrors the Python CLI byte-for-byte (stdout worklist + mutated tree).

- [ ] **Step 1: Add parity test** `class ConformParity(ParityBase): stem="flightdeck_conform"` with `test_apply` (`mutates=True`) + `test_check`.
- [ ] **Step 2: Run → FAIL/skip** (`.js` absent).
- [ ] **Step 3: Port** `flightdeck_conform.js` using `flightdeck_lib.js` helpers (codepoint sort, LF, NFC, stable JSON) exactly as the alpha.4 ports do.
- [ ] **Step 4: Run → PASS** (`uv run pytest scripts/tests/test_parity.py -q`; both interpreters byte-identical).
- [ ] **Step 5: Run full suite** `uv run pytest scripts/tests/ -q` → all green; **Han gate** `rg -lP '\p{Han}' scripts` clean. Commit `feat(conform): node port + byte-parity`.

---

### Task 7: `/flightdeck:conform` skill (orchestration + AI semantic-fill pass)

**Files:** Create `skills/conform/SKILL.md`; Modify `skills/walkaround/SKILL.md` (Audit 16 note → "fix via /flightdeck:conform"); Modify `.claude-plugin/*` + adapter manifests if commands are enumerated there (grep `walkaround` to find the list).

**Interfaces:** Prose skill. Flow: (1) run `flightdeck_conform` per recorded `runtime`; (2) AI reads `cockpit.md` + `rules.md` fully and reshapes to `templates.md` canonical — normalize old labels (`**Last updated**`→`Updated`+`Stage`, `**Active focus**`→`Focus`, `**指针**`→`Pointers`), delete non-canonical sections/fields (e.g. `**Context**`), preserving values; (3) for each worklist line, AI reads that file and authors the missing field; (4) report `─── 🩹 conform ───` with counts. State the **dry-run-first** default (`--check`, show diff) given non-git decks are irreversible.

- [ ] **Step 1:** Write `skills/conform/SKILL.md` (English; sections: when to use, the two passes, the script call forms per runtime, the AI reshape rules, the irreversibility/dry-run note, output banner).
- [ ] **Step 2:** Update `walkaround` Audit 16 to point its fix at `/flightdeck:conform`; register the command wherever the other `/flightdeck:*` commands are listed (manifests/README table).
- [ ] **Step 3:** Verify: `rg -lP '\p{Han}' skills` clean; manually dry-run the skill against the dogfood deck (`flightdeck_conform flightdeck --check`) and confirm the planned changes read correctly.
- [ ] **Step 4: Commit** `feat(conform): /flightdeck:conform skill + walkaround handoff`.

---

## Self-review notes

- **Spec coverage:** §3 five categories → Tasks 2 (多删), 3+4 (cockpit/rules 细致 mechanical part), 5 (worklist→AI 填义 handoff), Task 7 AI pass (细致 reshape + 填义); §2 scope/exclusions → Task 1 `kind_of` + Task 5 walk; §5 no-registry/irreversible → Task 7 dry-run note; §6 walkaround relation → Task 7 Step 2.
- **Split script vs AI:** the script is deliberately **non-destructive on cockpit/rules bodies** (append-only sections); all destructive cockpit reshaping (delete `**Context**`, relabel) is the AI pass — keeps the mechanical layer safe and the judgment in the model.
- **Open micro-decision for the executor:** whether `references/` participates (it is imported/hand-maintained — Task 1 includes it in `LEGAL_FIELDS`; if the team wants references exempt from frontmatter-pruning, drop it from the walk in Task 5).
