---
status: done
summary: 落地 v2 spec：母库解析固定 ~/.flightdeck + synced 去别名 + consumers 注册表(register/list/prune)+ /flightdeck:sync --fanout 编排 + 配置面清理 + v1 迁移补注册。
last_updated: 2026-06-19
implements: specs/2026-06-19-shared-knowledge-sync-v2.md
---

# shared-knowledge-sync v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 shared-knowledge-sync 的母库解析塌成固定约定 `~/.flightdeck`、`synced_from` 去别名为 `synced` 标记、给母库加 `consumers` 注册表 + register/list/prune primitive 与 `/flightdeck:sync --fanout` 编排。

**Architecture:** 脚本层 `scripts/flightdeck_index.py` 提供纯函数 + 三个母库 primitive flag（`--register-consumer` / `--list-consumers` / `--prune-consumers`）；`--fanout` 是 sync skill 的编排（跑 `--list-consumers` 再逐 deck pull），非脚本 flag。`consumers` 以**单行 JSON 数组**存共享文件 frontmatter（兼容现有标量行 `parse_frontmatter`）；消费 deck 路径以 `Path(p).resolve().as_posix()` 规范化作去重主键。母库解析恒为 `Path.home() / ".flightdeck"`，逃生口 = symlink / junction。

**Tech Stack:** Python 3（stdlib：`pathlib` / `json` / `os` / `argparse`），`unittest` + `unittest.mock`，`uv run pytest`。测试母库解析靠 mock `flightdeck_index.Path.home`。

**约定**：每个 `uv run pytest` 命令在仓库根跑。提交信息用中文 body（项目沟通偏好）。**本仓只本地 commit，绝不 push**（rules.md）。

---

### Task 1: 母库解析固定 `~/.flightdeck` + `sync_status` 改 `synced` 键

把 `_resolve_master_root` 塌成固定约定（去 `deck` 入参），`sync_status` 改以 `synced: true` 标记为入口、用消费文件自身 relpath 去母库找源、输出 2 元组。先把测试夹具与用例改成 v2 行为（对旧码失败），再改码。

**Files:**
- Modify: `scripts/flightdeck_index.py`（`_resolve_master_root` ~423-449；`sync_status` ~452-495；`--sync-status` 打印 ~608-611）
- Test: `scripts/tests/test_flightdeck_index.py`（`SyncStatusTest` ~848-953）

- [ ] **Step 1: 重写 SyncStatusTest 夹具 + 用例（失败先行）**

把 `SyncStatusTest` 整段（848 行 `class SyncStatusTest` 到 953 行结尾）替换为：

```python
class SyncStatusTest(unittest.TestCase):
    """flightdeck_index.sync_status — 共享知识漂移只读扫描（v2：固定母库 + synced 标记）。"""

    def _master_file(self, master, relpath, last_updated, consumers=None):
        p = master / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        extra = f"consumers: {json.dumps(consumers)}\n" if consumers is not None else ""
        p.write_text(
            f"---\nstatus: active\nwhen_to_read: x\napplies_to: [y]\n"
            f"{extra}last_updated: {last_updated}\n---\n# {p.stem}\n",
            encoding="utf-8",
        )

    def _consumer(self, root):
        deck = root / "consumer"
        (deck / "checklists").mkdir(parents=True)
        (deck / "rules.md").write_text("---\nversion: 3.0\n---\n", encoding="utf-8")
        return deck

    def _vendored(self, deck, relpath, last_updated):
        p = deck / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            f"---\nstatus: active\nsynced: true\n"
            f"when_to_read: x\napplies_to: [y]\nlast_updated: {last_updated}\n---\n# {p.stem}\n",
            encoding="utf-8",
        )

    def _home(self, fake_home):
        # 母库恒为 ~/.flightdeck —— 测试里把 Path.home() 指到 fake_home，母库 = fake_home/.flightdeck
        return mock.patch.object(flightdeck_index.Path, "home", return_value=fake_home)

    def test_states_and_ignores_unsynced(self):
        from flightdeck_index import sync_status
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            master = root / ".flightdeck"
            self._master_file(master, "checklists/commits.md", "2026-06-20")
            deck = self._consumer(root)
            self._vendored(deck, "checklists/commits.md", "2026-06-18")   # 母库更新 → upstream-changed
            self._vendored(deck, "checklists/ahead.md", "2026-06-25")     # 母库无源 → dangling（源不存在）
            (deck / "checklists" / "local.md").write_text(
                "---\nstatus: active\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-18\n---\n# local\n",
                encoding="utf-8",
            )
            with self._home(root):
                states = {rel: st for st, rel in sync_status(deck)}
            self.assertEqual(states["checklists/commits.md"], "upstream-changed")
            self.assertEqual(states["checklists/ahead.md"], "dangling")
            self.assertNotIn("checklists/local.md", states)

    def test_locally_ahead_and_in_sync(self):
        from flightdeck_index import sync_status
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            master = root / ".flightdeck"
            self._master_file(master, "checklists/commits.md", "2026-06-18")
            self._master_file(master, "checklists/comments.md", "2026-06-10")
            deck = self._consumer(root)
            self._vendored(deck, "checklists/commits.md", "2026-06-18")   # 相等 → in-sync
            self._vendored(deck, "checklists/comments.md", "2026-06-25")  # 项目更新 → locally-ahead
            with self._home(root):
                states = {rel: st for st, rel in sync_status(deck)}
            self.assertEqual(states["checklists/commits.md"], "in-sync")
            self.assertEqual(states["checklists/comments.md"], "locally-ahead")

    def test_master_missing_when_no_flightdeck_home(self):
        from flightdeck_index import sync_status
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)                 # root 下不建 .flightdeck → 母库缺席
            deck = self._consumer(root)
            self._vendored(deck, "checklists/commits.md", "2026-06-18")
            with self._home(root):
                self.assertEqual(sync_status(deck)[0][0], "master-missing")

    def test_read_only_writes_nothing(self):
        from flightdeck_index import sync_status
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            master = root / ".flightdeck"
            self._master_file(master, "checklists/commits.md", "2026-06-20")
            deck = self._consumer(root)
            self._vendored(deck, "checklists/commits.md", "2026-06-18")
            before = {p: p.read_text(encoding="utf-8") for p in deck.rglob("*.md")}
            with self._home(root):
                sync_status(deck)
            after = {p: p.read_text(encoding="utf-8") for p in deck.rglob("*.md")}
            self.assertEqual(before, after)
```

确保测试文件顶部已 import（若缺则加）：`import json`、`from unittest import mock`、`import flightdeck_index`。

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py::SyncStatusTest -v`
Expected: FAIL —— 旧 `_resolve_master_root(deck)` 仍需 deck 参 / `sync_status` 仍读 `synced_from` 且返回 3 元组，新用例解包 `st, rel` 会报错。

- [ ] **Step 3: 改 `_resolve_master_root`（固定约定、去 deck 参）**

把 `scripts/flightdeck_index.py` 的 `_resolve_master_root` 整个函数（423-449）替换为：

```python
def _resolve_master_root():
    """Resolve the shared-knowledge master deck root, or None.

    Fixed convention: ``~/.flightdeck``. To keep the master elsewhere, make
    ``~/.flightdeck`` a symlink or directory junction to it — ``is_dir()``
    follows both. Returns the path when it resolves to a directory, else None
    (the caller treats None as ``master-missing`` and skips gracefully)."""
    root = Path.home() / ".flightdeck"
    return root if root.is_dir() else None
```

- [ ] **Step 4: 改 `sync_status`（synced 键、自身 relpath 找源、2 元组）**

把 `sync_status`（452-495）整个函数替换为：

```python
def sync_status(deck):
    """共享知识漂移只读扫描：对每个带 `synced: true` 的工件，用其**自身 relpath**
    去母库找同路径源、比 `last_updated`，返回 (state, relpath)。写任何文件都不。

    母库根解析见 `_resolve_master_root`（固定 `~/.flightdeck`）。状态：
      upstream-changed  母库更新（母库 last_updated 更大）→ /flightdeck:sync 可拉
      in-sync           相等
      locally-ahead     项目更新 → /flightdeck:sync push 可回流母库
      dangling          母库根在、但同 relpath 源不是可读文件（缺失/类型错配）
      master-missing    母库根 ~/.flightdeck 不存在 → 整 deck 优雅跳过
    路径相对 deck、POSIX 斜杠；按 relpath 排序。排除 archive/。"""
    deck = Path(deck)
    master_root = _resolve_master_root()
    master_ok = master_root is not None
    out = []
    for p in deck.rglob("*.md"):
        if p.name == "INDEX.md" or "archive" in p.relative_to(deck).parts:
            continue
        try:
            fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        except OSError:
            continue
        if str(fm.get("synced", "")).strip().lower() != "true":
            continue
        rel = str(p.relative_to(deck)).replace("\\", "/")
        if not master_ok:
            out.append(("master-missing", rel))
            continue
        master_file = master_root / rel
        if not master_file.is_file():
            out.append(("dangling", rel))
            continue
        proj_lu = fm.get("last_updated", "")
        mast_lu = parse_frontmatter(master_file.read_text(encoding="utf-8")).get("last_updated", "")
        if mast_lu > proj_lu:          # ISO 日期字符串比较 == 时序比较
            state = "upstream-changed"
        elif mast_lu < proj_lu:
            state = "locally-ahead"
        else:
            state = "in-sync"
        out.append((state, rel))
    return sorted(out, key=lambda t: t[1])
```

- [ ] **Step 5: 改 `--sync-status` 打印为 2 列**

把 608-611 的打印块替换为：

```python
    if args.sync_status:
        for state, path in sync_status(args.deck):
            print(f"{state}\t{path}")
        return 0
```

同时把 `--sync-status` 的 help 文案（578-580）里 `synced_from` 改 `synced`、`shared_master` 去掉：

```python
    ap.add_argument(
        "--sync-status",
        action="store_true",
        help="print (state<TAB>relpath) for every artifact carrying `synced: true`, "
        "comparing last_updated against the same-relpath source under ~/.flightdeck (read-only)",
    )
```

- [ ] **Step 6: 跑测试确认通过**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py::SyncStatusTest -v`
Expected: PASS（4 个用例全绿）。

- [ ] **Step 7: 提交**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(sync): 母库解析固定 ~/.flightdeck + sync_status 改 synced 标记"
```

---

### Task 2: `consumers` frontmatter 助手 + `--register-consumer`

加 JSON 数组读写助手与路径规范化，实现幂等注册（relpath 须是母库已存在文件）。

**Files:**
- Modify: `scripts/flightdeck_index.py`（imports 15-22 加 `import json`；新增助手 + `register_consumer`；argparse + dispatch）
- Test: `scripts/tests/test_flightdeck_index.py`（新增 `ConsumersRegistryTest`）

- [ ] **Step 1: 写失败测试**

在 `SyncStatusTest` 之后追加：

```python
class ConsumersRegistryTest(unittest.TestCase):
    """consumers 注册表：register / list / prune（对母库 frontmatter 读改写）。"""

    def _mfile(self, master, relpath, consumers=None):
        p = master / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        extra = f"consumers: {json.dumps(consumers)}\n" if consumers is not None else ""
        p.write_text(
            f"---\nstatus: active\nwhen_to_read: x\napplies_to: [y]\n{extra}"
            f"last_updated: 2026-06-19\n---\n# {p.stem}\n",
            encoding="utf-8",
        )
        return p

    def test_register_is_idempotent_and_normalizes(self):
        from flightdeck_index import register_consumer, _read_consumers
        with tempfile.TemporaryDirectory() as d:
            master = Path(d) / ".flightdeck"
            self._mfile(master, "checklists/commits.md")
            deckdir = Path(d) / "projA" / "flightdeck"
            deckdir.mkdir(parents=True)
            register_consumer(master, "checklists/commits.md", str(deckdir))
            # 再注册同 deck（带尾斜杠变体）→ 不重复增长
            register_consumer(master, "checklists/commits.md", str(deckdir) + os.sep)
            fm = flightdeck_index.parse_frontmatter(
                (master / "checklists/commits.md").read_text(encoding="utf-8"))
            self.assertEqual(_read_consumers(fm), [deckdir.resolve().as_posix()])

    def test_register_rejects_non_file_relpath(self):
        from flightdeck_index import register_consumer
        with tempfile.TemporaryDirectory() as d:
            master = Path(d) / ".flightdeck"
            (master / "checklists").mkdir(parents=True)
            deckdir = Path(d) / "projA"
            deckdir.mkdir()
            with self.assertRaises(ValueError):
                register_consumer(master, "checklists/", str(deckdir))      # 目录非文件
            with self.assertRaises(ValueError):
                register_consumer(master, "checklists/missing.md", str(deckdir))  # 不存在
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py::ConsumersRegistryTest -v`
Expected: FAIL —— `ImportError: cannot import name 'register_consumer'`。

- [ ] **Step 3: 加 `import json`**

把 15-22 行的 import 区里加一行（按字母序插在 `import hashlib` 后）：

```python
import json
```

- [ ] **Step 4: 实现助手 + `register_consumer`**

紧接 `_resolve_master_root` 之后插入：

```python
def _norm_deck(p):
    """Canonical dedupe key for a consumer deck path: resolved, POSIX slashes."""
    return Path(p).resolve().as_posix()


def _read_consumers(fm):
    """Parse the `consumers` frontmatter value (single-line JSON array) into a
    list of strings. Returns [] when absent or unparseable."""
    raw = fm.get("consumers")
    if not raw:
        return []
    try:
        val = json.loads(raw)
    except (ValueError, TypeError):
        return []
    return [str(x) for x in val] if isinstance(val, list) else []


def _write_consumers_line(text, consumers):
    """Return `text` with its frontmatter `consumers:` line set to a sorted,
    deduped single-line JSON array. Inserts the line before the closing `---`
    when absent. Assumes a leading `---`-fenced block exists."""
    payload = json.dumps(sorted(set(consumers)))
    lines = text.splitlines(keepends=True)
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return text
    for i in range(1, end):
        if lines[i].split(":", 1)[0].strip() == "consumers":
            lines[i] = f"consumers: {payload}\n"
            return "".join(lines)
    lines.insert(end, f"consumers: {payload}\n")
    return "".join(lines)


def register_consumer(master_root, relpath, deck):
    """Add `deck` (normalized) to master file `relpath`'s `consumers` list.
    Idempotent. Raises ValueError when `relpath` is not an existing file under
    `master_root` (the registration is a no-op then; callers warn, don't abort)."""
    target = Path(master_root) / relpath
    if not target.is_file():
        raise ValueError(f"not a master file: {relpath}")
    text = target.read_text(encoding="utf-8")
    consumers = _read_consumers(parse_frontmatter(text))
    consumers.append(_norm_deck(deck))
    target.write_text(_write_consumers_line(text, consumers), encoding="utf-8")
    return True
```

- [ ] **Step 5: 加 argparse + dispatch**

在 `--sync-status` 的 `ap.add_argument` 之后加：

```python
    ap.add_argument(
        "--register-consumer", nargs=2, metavar=("DECK", "RELPATH"), default=None,
        help="register consumer DECK as a consumer of master file RELPATH (idempotent); "
        "DECK path is resolve()-normalized; RELPATH must be an existing master file",
    )
    ap.add_argument(
        "--list-consumers", action="store_true",
        help="print each registered consumer deck (union across master files), reachable dirs only; read-only",
    )
    ap.add_argument(
        "--prune-consumers", action="store_true",
        help="remove consumer entries whose deck dir is confirmed gone (parent reachable, neither exists nor lexists); "
        "the ONLY mutating consumer op",
    )
```

在 `if args.sync_status:` 块之后加 dispatch（list/prune 的实现见 Task 3/4，但 flag 一并声明，dispatch 先放 register；list/prune dispatch 在后续任务补全函数后即生效——为避免 NameError，本步连同 list/prune dispatch 一起放，函数在 Task 3/4 补）：

```python
    if args.register_consumer is not None:
        deck_arg, rel = args.register_consumer
        try:
            register_consumer(args.deck, rel, deck_arg)
            print(f"registered\t{_norm_deck(deck_arg)}\t{rel}")
            return 0
        except ValueError as e:
            print(f"register failed: {e}", file=sys.stderr)
            return 1

    if args.list_consumers:
        for c in list_consumers(args.deck):
            print(c)
        return 0

    if args.prune_consumers:
        for rel, c in prune_consumers(args.deck):
            print(f"pruned\t{rel}\t{c}")
        return 0
```

> 注：`list_consumers` / `prune_consumers` 在本步尚未定义，但只有在传 `--list-consumers` / `--prune-consumers` 时才会被调用——Task 2 的测试不触发它们，故 Task 2 测试通过；Task 3/4 补全函数后这两条 dispatch 即可用。

- [ ] **Step 6: 跑测试确认通过**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py::ConsumersRegistryTest::test_register_is_idempotent_and_normalizes scripts/tests/test_flightdeck_index.py::ConsumersRegistryTest::test_register_rejects_non_file_relpath -v`
Expected: PASS（2 个）。

- [ ] **Step 7: 提交**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(sync): consumers 注册表助手 + --register-consumer（幂等、规范化、relpath 须文件）"
```

---

### Task 3: `--list-consumers`（并集去重、纯读、只返回可达）

**Files:**
- Modify: `scripts/flightdeck_index.py`（新增 `list_consumers`）
- Test: `scripts/tests/test_flightdeck_index.py`（`ConsumersRegistryTest` 加用例）

- [ ] **Step 1: 写失败测试**

在 `ConsumersRegistryTest` 内追加：

```python
    def test_list_consumers_union_dedup_reachable_only(self):
        from flightdeck_index import list_consumers
        with tempfile.TemporaryDirectory() as d:
            master = Path(d) / ".flightdeck"
            a = Path(d) / "projA" / "flightdeck"; a.mkdir(parents=True)
            b = Path(d) / "projB" / "flightdeck"; b.mkdir(parents=True)
            gone = (Path(d) / "projGONE" / "flightdeck").resolve().as_posix()  # 不存在目录
            self._mfile(master, "checklists/commits.md",
                        consumers=[a.resolve().as_posix(), gone])
            self._mfile(master, "checklists/comments.md",
                        consumers=[a.resolve().as_posix(), b.resolve().as_posix()])
            got = list_consumers(master)
            self.assertEqual(got, sorted([a.resolve().as_posix(), b.resolve().as_posix()]))
            self.assertNotIn(gone, got)        # 不可达目录被跳过
            # 纯读：母库文件未被改写
            self.assertIn(gone, flightdeck_index._read_consumers(
                flightdeck_index.parse_frontmatter(
                    (master / "checklists/commits.md").read_text(encoding="utf-8"))))
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py::ConsumersRegistryTest::test_list_consumers_union_dedup_reachable_only -v`
Expected: FAIL —— `ImportError: cannot import name 'list_consumers'`。

- [ ] **Step 3: 实现 `list_consumers`**

紧接 `register_consumer` 之后插入：

```python
def list_consumers(master_root):
    """Union of every master shared file's `consumers`, normalized + sorted.

    Pure read: a deck whose dir is currently unreachable is **skipped from this
    result** but never removed from any file (network drive offline / unmounted
    / symlink target temporarily down must not be mistaken for permanent
    removal — that is `prune_consumers`'s job). Excludes archive/ and INDEX.md."""
    master_root = Path(master_root)
    seen = set()
    for p in master_root.rglob("*.md"):
        if p.name == "INDEX.md" or "archive" in p.relative_to(master_root).parts:
            continue
        try:
            fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        except OSError:
            continue
        for c in _read_consumers(fm):
            seen.add(_norm_deck(c))
    return sorted(c for c in seen if Path(c).is_dir())
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py::ConsumersRegistryTest -v`
Expected: PASS（含既有 register 用例）。

- [ ] **Step 5: 提交**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(sync): --list-consumers（并集去重、纯读、只返回可达 deck）"
```

---

### Task 4: `--prune-consumers`（保守剔除 + lexists 守卫）

**Files:**
- Modify: `scripts/flightdeck_index.py`（新增 `prune_consumers`）
- Test: `scripts/tests/test_flightdeck_index.py`（`ConsumersRegistryTest` 加用例）

- [ ] **Step 1: 写失败测试**

在 `ConsumersRegistryTest` 内追加：

```python
    def test_prune_removes_only_confirmed_gone(self):
        from flightdeck_index import prune_consumers, _read_consumers
        with tempfile.TemporaryDirectory() as d:
            master = Path(d) / ".flightdeck"
            alive = Path(d) / "projA" / "flightdeck"; alive.mkdir(parents=True)
            # gone：父目录 projGONE 存在、deck 本身不存在 → 应剔除
            gone_parent = Path(d) / "projGONE"; gone_parent.mkdir()
            gone = (gone_parent / "flightdeck").resolve().as_posix()
            # unreachable：父目录都不存在（整盘离线模拟）→ 不剔除
            unreachable = (Path(d) / "noSuchDrive" / "x" / "flightdeck").resolve().as_posix()
            self._mfile(master, "checklists/commits.md",
                        consumers=[alive.resolve().as_posix(), gone, unreachable])
            removed = prune_consumers(master)
            self.assertIn(("checklists/commits.md", gone), removed)
            kept = _read_consumers(flightdeck_index.parse_frontmatter(
                (master / "checklists/commits.md").read_text(encoding="utf-8")))
            self.assertIn(alive.resolve().as_posix(), kept)
            self.assertIn(unreachable, kept)       # 父不可达 → 保守保留
            self.assertNotIn(gone, kept)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py::ConsumersRegistryTest::test_prune_removes_only_confirmed_gone -v`
Expected: FAIL —— `ImportError: cannot import name 'prune_consumers'`。

- [ ] **Step 3: 实现 `prune_consumers`**

紧接 `list_consumers` 之后插入：

```python
def prune_consumers(master_root):
    """Remove, from every master file's `consumers`, decks that are *confirmed
    gone*: parent dir reachable (`is_dir()`) AND the deck itself neither
    `exists()` nor `os.path.lexists()`. The lexists() guard keeps a symlinked
    deck whose target is temporarily unreachable; a fully-unreachable parent
    (offline drive) means we cannot confirm removal, so we keep it. The ONLY
    mutating consumer op. Returns [(file_relpath, removed_deck), ...]."""
    master_root = Path(master_root)
    removed = []
    for p in master_root.rglob("*.md"):
        if p.name == "INDEX.md" or "archive" in p.relative_to(master_root).parts:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        consumers = _read_consumers(parse_frontmatter(text))
        if not consumers:
            continue
        kept = []
        for c in consumers:
            cp = Path(c)
            confirmed_gone = cp.parent.is_dir() and not cp.exists() and not os.path.lexists(c)
            if confirmed_gone:
                removed.append((str(p.relative_to(master_root)).replace("\\", "/"), c))
            else:
                kept.append(c)
        if len(kept) != len(consumers):
            p.write_text(_write_consumers_line(text, kept), encoding="utf-8")
    return removed
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py -v`
Expected: PASS（全文件，含 SyncStatusTest + ConsumersRegistryTest）。

- [ ] **Step 5: 提交**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -m "feat(sync): --prune-consumers（保守剔除 + lexists 守卫防误删）"
```

---

### Task 5: 改写 `skills/sync/SKILL.md`（解析/synced/register/fanout/banner）

无单元测试；改完人工核对一遍措辞自洽 + 与脚本 flag 名对齐。

**Files:**
- Modify: `skills/sync/SKILL.md`

- [ ] **Step 1: 改「母库解析」节（10-17 行）**

替换为单条规则：

```markdown
## 母库解析（master resolution）

固定约定：母库根 = `~/.flightdeck`（即脚本 `_resolve_master_root`，无入参）。是目录则用；否则 `master-missing`，每文件优雅跳过并报告（vendored 文件自洽，照常可用）。**逃生口**：母库想放别处，把 `~/.flightdeck` 做成指向它的符号链接；Windows 无管理员权限用目录联接 `mklink /J %USERPROFILE%\.flightdeck <target>`（`is_dir()` 两者都跟随）。
```

- [ ] **Step 2: 改 §A 状态处理（去 synced_from 措辞、补 register、2 列）**

把 §A 第 1 步 `--sync-status` 描述改为「每个 vendored 文件一行 `state<TAB>relpath`」；`upstream-changed` 项把「逐字保留项目的 `## 项目覆盖` 段 + 整个 frontmatter」保留不变（v2 行为一致）；`dangling` 项保留既有「问用户：删本地副本 / 保留 / 改指（去 `synced`）」。

- [ ] **Step 3: 改 §B 首次下发（stamp synced + 滤 consumers + register）**

§B 第 3 步 `synced_from: <母库相对路径>` 改为：

```markdown
3. 往其 frontmatter 戳 `synced: true`，并**滤掉母库的 `consumers` 键**（母库专属，不进消费副本）。
```

§B 末尾加一步：

```markdown
6. 注册消费者：对母库跑 `flightdeck_index.py <母库根> --register-consumer <本 deck 绝对路径> <母库相对路径>`（幂等；失败只警告，不回滚已落地的 vendor）。
```

- [ ] **Step 4: 改 §C promote（同样 stamp + register）**

§C promote 分支末尾补：「给本地文件盖 `synced: true` 后，同样对母库跑 `--register-consumer <本 deck> <相对路径>`。」

- [ ] **Step 5: 新增 §D 扇出 + 改 Report banner**

在 §C 后加：

```markdown
### D. 扇出：母库改动推全下游（`/flightdeck:sync --fanout`）

母库端一键把改动扇出到所有已注册消费 deck：
1. `flightdeck_index.py <母库根> --list-consumers` → 拿可达消费 deck 集合（空 → no-op，报「注册表为空」）。
2. **串行**遍历，对每个下游 deck 跑正常 pull（§A）：`--sync-status` 算该 deck `upstream-changed`，正文替换、逐字保 `## 项目覆盖`、frontmatter 不动。每个 deck 路径作显式入参，不切 cwd。
3. **失败隔离**：单 deck 失败（权限/锁/损坏/目录缺席）记一条、继续其余。
4. （可选）跑 `--prune-consumers` 清确认消失的 deck。

`--fanout` 是本 skill 的编排，**不是脚本 flag**；脚本只提供 register/list/prune 三个 primitive。
```

把 Report 的 banner（65-69 行）改为：

```markdown
```
─── 🔄 sync ───
[Synced]  N pulled · M in-sync · K locally-ahead · D dangling
[Master]  <已解析母库根>   (或 "master-missing — ~/.flightdeck 不存在/非目录，已跳过")
```
（`--fanout` 模式额外逐 deck 一行 `<deck>: pulled N / in-sync / skipped / error <因>` + 总计。）
```

- [ ] **Step 6: 改 Don't do / 顶部描述里残留的 `synced_from`**

通读 SKILL.md，把所有 `synced_from` 改 `synced`（如开头 `母库（master deck）…` 段、§C「已 vendored、`synced_from`」等），把「事实=`--sync-status`」保留。

- [ ] **Step 7: 提交**

```bash
git add skills/sync/SKILL.md
git commit -m "docs(sync): SKILL 改 ~/.flightdeck 解析 + synced 标记 + consumers 注册 + 扇出"
```

---

### Task 6: 配置面 + 协议/文档清理（删旧描述、不留 deprecated）

**Files:**
- Modify: `flightdeck/rules.md`、`scaffolds/full/flightdeck/rules.md`、`.gitignore`、`skills/preflight/protocol.md`、`skills/preflight/templates.md`、`skills/walkaround/SKILL.md`

- [ ] **Step 1: 删 `flightdeck/rules.md` 的 `shared_master`**

删第 3 行 `shared_master: $FLIGHTDECK_SHARED_MASTER`，frontmatter 留 `version: 3.0`。

- [ ] **Step 2: 删 scaffold rules.md 的 `shared_master` 注释行**

`scaffolds/full/flightdeck/rules.md` 删第 3 行整条 `# shared_master: ...` 注释（v2 无此字段，留着会误导新 deck）。

- [ ] **Step 3: 删 `.gitignore` 的 `.shared-master` 块**

删 24-26 行（注释 2 行 + `**/.shared-master`）。

- [ ] **Step 4: 改协议/模板/walkaround 措辞**

逐文件 grep `shared_master` / `.shared-master` / `synced_from` / `FLIGHTDECK_SHARED_MASTER`，按 v2 改：
- `skills/preflight/protocol.md`、`skills/preflight/templates.md`：母库解析描述改「固定 `~/.flightdeck`」；字段表 `synced_from` 改 `synced`（布尔标记，无路径）；新增 `consumers`（母库专属、消费副本剔除）。
- `skills/walkaround/SKILL.md`：sync Audit 改为——校验 `synced` 文件的 `relpath` 不变量（母库无同 relpath 源 → `dangling`）+ 消费端出现 `consumers` 键判非法 + dangling/upstream-changed 漂移提示；去掉 env/指针措辞。

> 实现者注：用 `Grep` 工具按上述 4 词逐文件定位再改，确保无残留旧描述（**删不留 deprecated**）。

- [ ] **Step 5: 全仓残留扫描**

Run（PowerShell/Grep 均可）：搜 `shared_master`、`FLIGHTDECK_SHARED_MASTER`、`\.shared-master`、`synced_from`，确认只剩 `flightdeck/archive/`（历史，不动）与本 plan/spec 自身（描述性提及）命中。
Expected: 无 `skills/`、`scaffolds/`、`scripts/`、`flightdeck/rules.md`、`.gitignore` 的活跃命中。

- [ ] **Step 6: 提交**

```bash
git add flightdeck/rules.md scaffolds/full/flightdeck/rules.md .gitignore skills/preflight/protocol.md skills/preflight/templates.md skills/walkaround/SKILL.md
git commit -m "chore(sync): 清除 shared_master/.shared-master/synced_from 旧描述，协议改 ~/.flightdeck + synced + consumers"
```

---

### Task 7: 【CHECKPOINT — 仓库外，需用户确认】移母库 + 四账户 CLAUDE.md

> ⚠ 本任务动**仓库外**文件，不可由子代理自动执行。执行到此**停下，向用户复述将做的动作并取得明确同意**后再做。spec「落地（仓库外）」对应此步。

**动作（确认后）：**
- [ ] **Step 1: 把母库挪到 `~/.flightdeck`**

将 `E:\projects\agent\flightdeck` 的内容落到 `C:\Users\yl\.flightdeck`。两种实现二选一，**问用户**：
- (a) 物理移动：`Move-Item E:\projects\agent\flightdeck C:\Users\yl\.flightdeck`（用户拍板「真移到」时选此）。
- (b) 目录联接（保留原位 + 入口）：`cmd /c mklink /J C:\Users\yl\.flightdeck E:\projects\agent\flightdeck`。

- [ ] **Step 2: 同步四账户全局 CLAUDE.md「跨项目资产库」措辞**

`C:\Users\yl\.claude-accounts\*\CLAUDE.md`（max / mino / yueli999 / yuelili 四份）里「跨项目资产库 = `E:\projects\agent\`」相关段落，按母库新位置更新；改完按全局 CLAUDE.md §多账户同步流程（推平 + 核对 hash）确认**四份逐字一致**。

- [ ] **Step 3: 验证母库就位**

Run: `python scripts/flightdeck_index.py flightdeck --sync-status`
Expected: 本仓 vendored 文件（`comments.md`/`commits.md`）报 `in-sync`（或 `upstream-changed`），**不再** `master-missing`。

（本步无仓库内提交。）

---

### Task 8: v1 迁移 — 补注册本仓两文件

> 依赖 Task 7（母库已在 `~/.flightdeck`）。

**Files:** 无（命令，写母库 frontmatter）

- [ ] **Step 1: 注册本仓为两文件的消费者**

设本仓 deck 绝对路径 = `E:\projects\tools\flightdeck\flightdeck`。对母库跑：

```powershell
python scripts/flightdeck_index.py $env:USERPROFILE\.flightdeck --register-consumer E:\projects\tools\flightdeck\flightdeck checklists/comments.md
python scripts/flightdeck_index.py $env:USERPROFILE\.flightdeck --register-consumer E:\projects\tools\flightdeck\flightdeck checklists/commits.md
```

- [ ] **Step 2: 验证 + 试扇出**

Run: `python scripts/flightdeck_index.py $env:USERPROFILE\.flightdeck --list-consumers`
Expected: 输出含本仓 deck 路径（规范化 POSIX）。
迁移闭合：母库 `comments.md`/`commits.md` 的 `consumers` 均含本仓。

（本步无仓库内提交；母库变更在 `~/.flightdeck`，属仓库外。）

---

### Task 9: CHANGELOG + cockpit Key Context + 全量验证

**Files:**
- Modify: `CHANGELOG.md`、`flightdeck/cockpit.md`（Key Context 段）

- [ ] **Step 1: CHANGELOG 折进 3.0 alpha 现有条目**

在 `CHANGELOG.md` 的 shared-knowledge-sync 条目里补 v2 简化（母库固定 `~/.flightdeck`、`synced` 去别名、`consumers` 注册 + fanout），**删除**任何 `shared_master`/env/`synced_from`/`.shared-master` 旧措辞（不留 deprecated）。

- [ ] **Step 2: 更新 cockpit Key Context**

把 `flightdeck/cockpit.md` Key Context 里 `shared-knowledge-sync` 那行的解析描述改为 v2（固定 `~/.flightdeck`、`synced` 标记、`consumers`/fanout）。

- [ ] **Step 3: 全量测试 + INDEX 自洽**

Run: `uv run pytest scripts/tests/`
Expected: 全绿。

Run: `python scripts/flightdeck_index.py flightdeck --check`
Expected: `clean`。

- [ ] **Step 4: 提交**

```bash
git add CHANGELOG.md flightdeck/cockpit.md
git commit -m "docs(sync): CHANGELOG + cockpit 更新到 v2，清旧 shared_master 描述"
```

- [ ] **Step 5: landing**

实现全绿后走 `/flightdeck:landing` 收尾（归档 spec/plan、更新 cockpit、本地 commit）。

---

## Self-Review（plan↔spec 覆盖核对）

- Part 1 母库解析固定 → Task 1（`_resolve_master_root`）+ Task 6（rules/scaffold/gitignore/协议）+ Task 7（落地移库）。✓
- Part 1 symlink/junction 逃生口 → Task 5 Step 1 + Task 7 Step 1(b)。✓
- Part 2 `synced_from`→`synced` + relpath 找源 + 不变量 → Task 1（sync_status）+ Task 6（walkaround 校验不变量）。✓
- Part 3 `consumers` 字段 + 单行 JSON 存储 + 规范化 → Task 2。✓
- Part 3 register（relpath 须文件、幂等、失败不阻断）→ Task 2 + Task 5 Step 3/4。✓
- Part 3 list（纯读、可达过滤）→ Task 3。✓
- Part 3 prune（保守 + lexists）→ Task 4。✓
- Part 3 vendor 滤 consumers + stamp synced → Task 5 Step 3。✓
- Part 3 fanout 编排（串行/失败隔离/banner/非脚本 flag）→ Task 5 Step 5。✓
- 状态语义（master-missing vs dangling 分桶）→ Task 1（sync_status 逻辑）。✓
- 首次部署/迁移补注册 → Task 8（显式步 + 验收）。✓
- 边界（跨 OS/并发/广播/可观察性）→ 非目标，无需任务。✓
- 验收：pytest 全绿（Task 9 Step 3）、端到端 sync-status（Task 7 Step 3）、幂等（Task 2 测试）、迁移闭合（Task 8 Step 2）、四账户一致（Task 7 Step 2）。✓

类型/命名一致性：`_resolve_master_root()`（无参）、`sync_status` 返回 `(state, relpath)`、`register_consumer(master_root, relpath, deck)`、`list_consumers(master_root)`、`prune_consumers(master_root)`、`_norm_deck`/`_read_consumers`/`_write_consumers_line`、flag `--register-consumer`/`--list-consumers`/`--prune-consumers` —— 全 plan 内一致。✓
