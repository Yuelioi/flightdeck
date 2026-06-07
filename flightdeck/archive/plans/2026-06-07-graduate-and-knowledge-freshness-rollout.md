---
status: done
summary: 逐文件落地 graduate + when_to_update/stale + status{active,stale,obsolete}：相位1 脚本/lint 机械核心(TDD)→相位2 skill 散文→相位3 docs/incident 对齐→相位4 dogfood 迁移+全验证
last_updated: 2026-06-07
implements: specs/2026-06-07-graduate-and-knowledge-freshness.md
---

# graduate + 知识保鲜 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让结构性设计 spec 完工后变身常驻 docs，给 docs 配 `when_to_update`→`stale` 失效信号，并把 knowledge status 收成 `{active, stale, obsolete}`（`obsolete`=knowledge 版 `done` 排水态）。

**Architecture:** 先落**脚本/lint 机械核心**（status 枚举、钉扣边、obsolete 排水、match_signature 扩 archive、when_to_update 形式校验、stale 渲染、锚点 helper），全部 TDD；再改**skill 散文**（行为层：graduate 前置问/收尾、双仪式 stale 检测、排空 obsolete）；再**对齐 docs/incident**；最后 **dogfood 迁移 + 全验证**。脚本是确定性事实层、可单测；散文是判断/行为层、由 spec 当内容真相源、靠阅读 + 自检验证。

**Tech Stack:** Python 3.8+ stdlib（`flightdeck_index.py` / `flightdeck_lint.py`），`unittest`（`scripts/tests/`，跑 `uv run pytest scripts/tests/`），markdown skill 散文（`skills/preflight/*`、`skills/new`、`skills/landing`）。

**内容真相源**：散文任务的"写什么"以 spec `specs/2026-06-07-graduate-and-knowledge-freshness.md` 的对应 § 为准；本 plan 给**每文件该新增/改动的确切要点 + 源 §**，不重复整段散文（避免与 spec 重复漂移）。

**约定**：每个脚本任务 TDD（先写失败测试→看红→最小实现→看绿→commit）。所有 commit 本地，**绝不 push**（House Rule）。Bash 工具传中文 commit body 用 heredoc（见 incident `powershell-herestring-in-bash-tool`）。

---

## 相位 1 — 脚本/lint 机械核心（TDD）

### Task 1: status 枚举改 `{active, stale, obsolete}`

**Files:**
- Modify: `scripts/flightdeck_lint.py:43`
- Test: `scripts/tests/test_flightdeck_lint.py`（`AuditStatusTest`）

- [ ] **Step 1: 写失败测试** — 加进 `AuditStatusTest`：

```python
def test_knowledge_superseded_is_illegal(self):
    with tempfile.TemporaryDirectory() as d:
        deck = Path(d)
        (deck / "docs").mkdir()
        (deck / "docs" / "a.md").write_text(
            "---\nstatus: superseded\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-07\n---\n# t\n",
            encoding="utf-8",
        )
        warns = _by_audit(audit_status(deck), "status")
        self.assertTrue(any("illegal status `superseded`" in f["message"] for f in warns))

def test_knowledge_stale_is_legal(self):
    with tempfile.TemporaryDirectory() as d:
        deck = Path(d)
        (deck / "docs").mkdir()
        (deck / "docs" / "a.md").write_text(
            "---\nstatus: stale\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-07\n---\n# t\n",
            encoding="utf-8",
        )
        self.assertEqual(_by_audit(audit_status(deck), "status"), [])
```

- [ ] **Step 2: 跑测试看红**

Run: `uv run pytest scripts/tests/test_flightdeck_lint.py -k "superseded_is_illegal or stale_is_legal" -v`
Expected: FAIL（`superseded` 当前合法、`stale` 当前非法——与新断言相反）

- [ ] **Step 3: 改枚举** — `scripts/flightdeck_lint.py:43`：

```python
KNOWLEDGE_STATUSES = {"active", "stale", "obsolete"}
```

- [ ] **Step 4: 跑测试看绿**

Run: `uv run pytest scripts/tests/test_flightdeck_lint.py -k "superseded_is_illegal or stale_is_legal" -v`
Expected: PASS

- [ ] **Step 5: 全 lint 测试回归**（确认无既有用例依赖旧枚举）

Run: `uv run pytest scripts/tests/test_flightdeck_lint.py -v`
Expected: 全 PASS（若有旧用例写 `status: superseded` 断言合法，按新枚举更新它们）

- [ ] **Step 6: commit**

```bash
git add scripts/flightdeck_lint.py scripts/tests/test_flightdeck_lint.py
git commit -F - <<'EOF'
feat(lint): knowledge status 枚举改 {active, stale, obsolete}

删 superseded 状态值（实施 spec §3）；stale 合法、superseded 非法。
EOF
```

---

### Task 2: 钉扣边只留 `implements`（drop `superseded_by`），`supersedes` 不钉扣

**Files:**
- Modify: `scripts/flightdeck_index.py:345,358`（`_active_inbound_targets`）
- Test: `scripts/tests/test_flightdeck_index.py`
- 源 §：spec §3「保留 supersedes = 纯溯源标注、不是归档钉扣边」

- [ ] **Step 1: 写失败测试** — 新建 doc 带 `supersedes` / 旧 `superseded_by` 都不应钉扣目标：

```python
def test_supersedes_edge_does_not_pin_target(self):
    with tempfile.TemporaryDirectory() as d:
        deck = Path(d)
        (deck / "docs").mkdir()
        (deck / "docs" / "new.md").write_text(
            "---\nstatus: active\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-07\nsupersedes: docs/old.md\n---\n# new\n",
            encoding="utf-8",
        )
        from flightdeck_index import _active_inbound_targets
        self.assertNotIn("docs/old.md", _active_inbound_targets(deck))

def test_superseded_by_no_longer_pins(self):
    with tempfile.TemporaryDirectory() as d:
        deck = Path(d)
        (deck / "docs").mkdir()
        (deck / "docs" / "x.md").write_text(
            "---\nstatus: active\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-07\nsuperseded_by: docs/old.md\n---\n# x\n",
            encoding="utf-8",
        )
        from flightdeck_index import _active_inbound_targets
        self.assertNotIn("docs/old.md", _active_inbound_targets(deck))
```

- [ ] **Step 2: 跑测试看红**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py -k "supersedes_edge_does_not_pin or superseded_by_no_longer_pins" -v`
Expected: `supersedes_…` 预计已 PASS（supersedes 本不在钉扣字段）；`superseded_by_…` FAIL（当前 `superseded_by` 仍钉扣）

- [ ] **Step 3: 删 `superseded_by` 钉扣** — `scripts/flightdeck_index.py:358`：

```python
            for field in ("implements",):
                v = fm.get(field)
                if v:
                    targets.add(v.strip())
```

并更新 docstring（line 345）去掉 `superseded_by`：`"...经结构化边（implements:）指向的目标路径集。"`。

- [ ] **Step 4: 跑测试看绿**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py -k "supersedes_edge_does_not_pin or superseded_by_no_longer_pins" -v`
Expected: PASS

- [ ] **Step 5: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -F - <<'EOF'
feat(index): 钉扣边只留 implements，supersedes 纯溯源不钉扣

修 spec 内部矛盾：若 supersedes/superseded_by 钉扣，新件 active 永指旧件、
旧件永不排空。删 superseded_by 钉扣（superseded 状态值已退役），supersedes
仅作溯源标注、不进 --archivable 钉扣集（实施 spec §3）。
EOF
```

---

### Task 3: `obsolete` knowledge 排水（与 done 同一搬运逻辑）

**Files:**
- Modify: `scripts/flightdeck_index.py`（新增 `archivable_obsolete(deck)`；扩 `--archivable` CLI 同时输出 done + obsolete）
- Test: `scripts/tests/test_flightdeck_index.py`
- 源 §：spec §3「obsolete = knowledge 版 done」「preflight + landing 排空 obsolete」+ §4 图

- [ ] **Step 1: 写失败测试** — `obsolete` knowledge 进可排水集；`active`/`stale` 不进：

```python
def test_archivable_includes_obsolete_knowledge(self):
    with tempfile.TemporaryDirectory() as d:
        deck = Path(d)
        (deck / "incidents").mkdir()
        for name, st in (("dead.md", "obsolete"), ("live.md", "active"), ("amber.md", "stale")):
            (deck / "incidents" / name).write_text(
                f"---\nstatus: {st}\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-07\n---\n# {name}\n",
                encoding="utf-8",
            )
        from flightdeck_index import archivable_obsolete
        self.assertEqual(archivable_obsolete(deck), ["incidents/dead.md"])
```

- [ ] **Step 2: 跑测试看红**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py -k archivable_includes_obsolete -v`
Expected: FAIL（`archivable_obsolete` 未定义）

- [ ] **Step 3: 实现 `archivable_obsolete`**（紧邻 `archivable_done`，index 约 line 383 后）：

```python
def archivable_obsolete(deck):
    """status:obsolete 的 knowledge 工件（incidents/checklists/docs）——已死·待归档，
    与 archivable_done 对称：obsolete 是 knowledge 版 done 排水态，无钉扣概念
    （superseded_by 已退役），扫到即可排进 archive/。确定性、可复现。"""
    deck = Path(deck)
    result = []
    for kind in sorted(KNOWLEDGE_KINDS):
        folder = deck / kind
        if not folder.is_dir():
            continue
        for p in sorted(folder.rglob("*.md")):
            if p.name == "INDEX.md":
                continue
            fm = parse_frontmatter(p.read_text(encoding="utf-8"))
            if fm.get("status") == "obsolete":
                result.append(str(p.relative_to(deck)).replace("\\", "/"))
    return sorted(result)
```

- [ ] **Step 4: 跑测试看绿**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py -k archivable_includes_obsolete -v`
Expected: PASS

- [ ] **Step 5: 扩 `--archivable` CLI 同时输出 done + obsolete** — 在 `--archivable` 处理处（index 约 line 542）打印 `sorted(set(archivable_done(deck)) | set(archivable_obsolete(deck)))`。加一条 CLI 级测试断言两类都出现（用 `main()`/`capsys` 或直接调函数并集）。

- [ ] **Step 6: 跑全 index 测试回归 + commit**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py -v`
Expected: 全 PASS

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -F - <<'EOF'
feat(index): obsolete knowledge 排水（archivable_obsolete）

obsolete = knowledge 版 done 排水态；--archivable 同时输出可排 done + obsolete，
landing/preflight 用同一套搬运逻辑排进 archive（实施 spec §3）。
EOF
```

---

### Task 4: `match_signature` 扩到扫 `archive/incidents/`

**Files:**
- Modify: `scripts/flightdeck_index.py:65`（`match_signature`）
- Test: `scripts/tests/test_flightdeck_index.py`
- 源 §：spec §3「incident 回归 tripwire 随之搬家——sweep 扩到也扫 archive/incidents/」

- [ ] **Step 1: 写失败测试** — 退役 incident 在 `archive/incidents/` 下仍能被签名命中：

```python
def test_match_signature_reaches_archived_incidents(self):
    with tempfile.TemporaryDirectory() as d:
        deck = Path(d)
        (deck / "archive" / "incidents").mkdir(parents=True)
        (deck / "archive" / "incidents" / "old.md").write_text(
            "---\nstatus: obsolete\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-07\n---\n"
            "# old\n## Signature\n- symptom: boom on parse\n- error_type: ValueError\n- where: p.py\n- trigger: bad input\n",
            encoding="utf-8",
        )
        from flightdeck_index import match_signature
        hits = match_signature(deck, "boom on parse", "ValueError")
        self.assertTrue(any("old.md" in h for h in hits))
```

- [ ] **Step 2: 跑测试看红**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py -k match_signature_reaches_archived -v`
Expected: FAIL（当前只扫 `incidents/`）

- [ ] **Step 3: 改 `match_signature`** — 在 `incidents/` 之外**也**遍历 `archive/incidents/`（rglob）；把扫描根改成两根并集，逐文件同样 `parse_signature` + 指纹比对。更新 docstring（line 67）注明含 `archive/incidents/`。

- [ ] **Step 4: 跑测试看绿**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py -k match_signature -v`
Expected: PASS（既有 `incidents/` 命中用例不回归）

- [ ] **Step 5: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -F - <<'EOF'
feat(index): match_signature 扩到扫 archive/incidents/

obsolete incident 现排进 archive；回归 sweep 须能在 archive 命中退役 incident
（复发=un-archive 复活，实施 spec §3）。
EOF
```

---

### Task 5: `when_to_update` lint 形式地板

**Files:**
- Modify: `scripts/flightdeck_lint.py`（新增 `audit_when_to_update(deck)`，并入 `lint()` 聚合）
- Test: `scripts/tests/test_flightdeck_lint.py`
- 源 §：spec §2「lint 形式地板：非空 + 含 ≥1 具体名词/路径 + 不含泛词黑名单」——**只做形式层，不判语义"够不够具体"**

- [ ] **Step 1: 写失败测试**：

```python
class AuditWhenToUpdateTest(unittest.TestCase):
    def _doc(self, deck, body_fm):
        (deck / "docs").mkdir(exist_ok=True)
        (deck / "docs" / "a.md").write_text(
            f"---\nstatus: active\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-07\n{body_fm}---\n# t\n",
            encoding="utf-8",
        )
    def test_vague_when_to_update_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            self._doc(deck, "when_to_update: 有任何改动时\n")
            from flightdeck_lint import audit_when_to_update
            self.assertTrue(audit_when_to_update(deck))
    def test_concrete_when_to_update_ok(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            self._doc(deck, "when_to_update: 改了 plugin 加载协议 / 动了 hooks/stop.sh\n")
            from flightdeck_lint import audit_when_to_update
            self.assertEqual(audit_when_to_update(deck), [])
    def test_missing_when_to_update_not_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            self._doc(deck, "")
            from flightdeck_lint import audit_when_to_update
            self.assertEqual(audit_when_to_update(deck), [])
```

- [ ] **Step 2: 跑测试看红**

Run: `uv run pytest scripts/tests/test_flightdeck_lint.py -k when_to_update -v`
Expected: FAIL（`audit_when_to_update` 未定义）

- [ ] **Step 3: 实现 `audit_when_to_update`**（形式地板，仅当字段存在时校验——字段可选）：

```python
VAGUE_TOKENS = ("任何", "所有", "any change", "all changes", "anything", "everything")

def audit_when_to_update(deck):
    """形式地板：when_to_update 若存在，须非空 + 含 ≥1 具体名词/路径 + 不含泛词。
    '够不够具体'是语义判断，不在此（靠 templates 示例 + 作者自律）。"""
    deck = Path(deck)
    findings = []
    for name in KNOWLEDGE_FOLDERS:
        folder = deck / name
        if not folder.is_dir():
            continue
        for f in _artifact_files(folder):
            wtu = parse_frontmatter(f.read_text(encoding="utf-8")).get("when_to_update")
            if wtu is None:
                continue  # 可选字段
            s = str(wtu).strip()
            low = s.lower()
            vague = (not s) or any(t in low or t in s for t in VAGUE_TOKENS)
            concrete = bool(re.search(r"[/.\w]{3,}", s)) and any(ch.isalnum() for ch in s)
            if vague or not concrete:
                findings.append(_finding(
                    "when_to_update", "WARNING", f,
                    f"{name}/{f.name} 的 when_to_update 过泛/空：写成具体改动事件（改了X/新增Y/动了Z文件）",
                ))
    return findings
```

并入 `lint(deck)` 聚合（`findings += audit_status(deck)` 同处加 `findings += audit_when_to_update(deck)`）。

- [ ] **Step 4: 跑测试看绿 + 全 lint 回归**

Run: `uv run pytest scripts/tests/test_flightdeck_lint.py -v`
Expected: 全 PASS

- [ ] **Step 5: commit**

```bash
git add scripts/flightdeck_lint.py scripts/tests/test_flightdeck_lint.py
git commit -F - <<'EOF'
feat(lint): when_to_update 形式地板

非空 + 含具体名词/路径 + 禁泛词黑名单；只做形式层，'够具体'交作者软引导
（实施 spec §2）。字段可选，缺失不报。
EOF
```

---

### Task 6: `stale` 进 INDEX 渲染（带 ⚠ 标记）；`obsolete` 仍排除

**Files:**
- Modify: `scripts/flightdeck_index.py:248,254`（obsolete 排除处）+ `format_row`（stale 标记）
- Test: `scripts/tests/test_flightdeck_index.py`
- 源 §：spec §2「stale 钉进 frontmatter + docs/INDEX + cockpit 浮一行待复核」

- [ ] **Step 1: 先读真实渲染函数名** — 读 `scripts/flightdeck_index.py:238` 起那个把 folder 渲成 `<!-- AUTO:kind -->…` body 的函数（测试要用真名，下方先记作 `<RENDER_FN>`）。

- [ ] **Step 2: 写失败测试** — `stale` 工件出现且带 ⚠；`obsolete` 不出现：

```python
def test_index_marks_stale_and_excludes_obsolete(self):
    with tempfile.TemporaryDirectory() as d:
        deck = Path(d)
        (deck / "docs").mkdir()
        for name, st in (("amber.md", "stale"), ("dead.md", "obsolete"), ("live.md", "active")):
            (deck / "docs" / name).write_text(
                f"---\nstatus: {st}\nwhen_to_read: x\napplies_to: [y]\nlast_updated: 2026-06-07\n---\n# {name}\n",
                encoding="utf-8",
            )
        from flightdeck_index import <RENDER_FN>
        body = <RENDER_FN>(deck / "docs")
        self.assertIn("amber.md", body)
        self.assertIn("⚠", body)            # stale 标记
        self.assertNotIn("dead.md", body)   # obsolete 排除
```

- [ ] **Step 3: 跑测试看红**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py -k marks_stale_and_excludes_obsolete -v`
Expected: FAIL（当前无 ⚠ 标记）

- [ ] **Step 4: 实现** —
  (a) index:248/254 的 obsolete 排除**保留**（obsolete 仍不进路由行），更新注释为：`# obsolete 待排进 archive（archivable_obsolete），不进路由行；stale 进行但带 ⚠`。
  (b) `format_row`：对 `status == "stale"` 的行加 `⚠ ` 前缀（或行尾 ` — ⚠ 待复核`）；其余 status 行不变。

- [ ] **Step 5: 跑测试看绿 + 全 index 回归**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py -v`
Expected: 全 PASS

- [ ] **Step 6: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -F - <<'EOF'
feat(index): stale 进 INDEX 带 ⚠ 标记，obsolete 仍排除路由

stale 是活跃区黄灯须浮现待复核；obsolete 待排 archive、不进路由行
（实施 spec §2）。
EOF
```

---

### Task 7: stale 检测锚点 helper（`last_anchor_ref` + `changed_since_anchor`）

**Files:**
- Modify: `scripts/flightdeck_index.py`（新增 `last_anchor_ref(deck)` + `changed_since_anchor(deck)`；CLI `--changed-since-anchor`；顶部 `import subprocess`）
- Test: `scripts/tests/test_flightdeck_index.py`
- 源 §：spec §2「锚点 = 上次退出仪式记录的 git ref；preflight diff anchor..HEAD + 工作树」

**存储选型（本 plan 定）**：**git trailer**——landing/soft-land commit body 带 `Flightdeck-Sync: <marker>` trailer；`last_anchor_ref` = `git log -1 --grep=Flightdeck-Sync --format=%H`。无新状态文件、用 git 历史当记录、无 chicken-egg。Task 11/12（exit-ritual/landing 散文）负责让 commit 带该 trailer。

- [ ] **Step 1: 写失败测试**（临时 git repo；跨平台 env 用临时 HOME，避免读全局 config）：

```python
import subprocess, os
def _git(deck, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t", HOME=str(deck))
    subprocess.run(["git", *args], cwd=deck, check=True, capture_output=True, env=env)

class AnchorTest(unittest.TestCase):
    def test_anchor_and_changed_since(self):
        with tempfile.TemporaryDirectory() as d:
            deck = Path(d)
            _git(deck, "init", "-q")
            (deck / "a").write_text("1", encoding="utf-8")
            _git(deck, "add", "-A"); _git(deck, "commit", "-qm", "land\n\nFlightdeck-Sync: 1")
            (deck / "b").write_text("2", encoding="utf-8")
            _git(deck, "add", "-A"); _git(deck, "commit", "-qm", "ordinary work")
            from flightdeck_index import last_anchor_ref, changed_since_anchor
            self.assertIsNotNone(last_anchor_ref(deck))
            changed = changed_since_anchor(deck)
            self.assertIn("b", changed)
            self.assertNotIn("a", changed)
```

- [ ] **Step 2: 跑测试看红**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py -k anchor_and_changed -v`
Expected: FAIL（`last_anchor_ref` 未定义）

- [ ] **Step 3: 实现**（`import subprocess` 置文件顶部）：

```python
def last_anchor_ref(deck):
    """最近一个带 Flightdeck-Sync trailer 的 commit SHA（上次退出仪式锚点），无则 None。"""
    try:
        out = subprocess.run(
            ["git", "-C", str(deck), "log", "-1", "--grep=Flightdeck-Sync", "--format=%H"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return out or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def changed_since_anchor(deck):
    """自锚点以来变动的路径（committed + 工作树未提交），相对 repo 根。
    无锚点 → 退化成工作树改动（首跑/无历史仍给信号）。"""
    anchor = last_anchor_ref(deck)
    paths = set()
    try:
        cmds = [["status", "--porcelain"]]
        if anchor:
            cmds.append(["diff", "--name-only", f"{anchor}..HEAD"])
        for cmd in cmds:
            out = subprocess.run(["git", "-C", str(deck), *cmd],
                                 capture_output=True, text=True, check=True).stdout
            for line in out.splitlines():
                p = line[3:].strip() if cmd[0] == "status" else line.strip()
                if p:
                    paths.add(p)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return sorted(paths)
```

加 CLI `--changed-since-anchor` 打印 `changed_since_anchor`，供 preflight 散文调用。

- [ ] **Step 4: 跑测试看绿**

Run: `uv run pytest scripts/tests/test_flightdeck_index.py -k anchor_and_changed -v`
Expected: PASS

- [ ] **Step 5: commit**

```bash
git add scripts/flightdeck_index.py scripts/tests/test_flightdeck_index.py
git commit -F - <<'EOF'
feat(index): stale 检测锚点 helper（trailer 锚点 + changed-since）

last_anchor_ref=最近 Flightdeck-Sync trailer commit；changed_since_anchor
给 preflight 自锚点以来的改动路径，供双仪式 stale 语义检测（实施 spec §2）。
无新状态文件，用 git 历史当锚点记录。
EOF
```

---

### Task 8: 相位 1 全测试绿 + lint 自检

- [ ] **Step 1: 全脚本测试**

Run: `uv run pytest scripts/tests/ -v`
Expected: 全 PASS（含既有 163）

- [ ] **Step 2: 对本 deck 跑 lint**（本 deck 0 个 live obsolete/superseded）

Run: `uv run scripts/flightdeck_lint.py flightdeck`
Expected: 无 `superseded`/`when_to_update` 相关 WARNING（本 deck docs 暂未加 when_to_update，可选字段不报）

---

## 相位 2 — skill 散文（行为层；按 spec § 为内容源，靠阅读 + diff 自检验证）

> 散文任务无单测。每任务：改文件 → 通读改动段 → 对照 spec § 确认覆盖 → commit。保**行为紧致**（不顺手扩写无关段）。改 skills/ 散文加链接前看 incident `skill-prose-links-into-dogfood-deck`。

### Task 9: `templates.md` + `folder-semantics.md`

**Files:** `skills/preflight/templates.md`、`skills/preflight/folder-semantics.md`
**源 §：** spec §1（graduate 字段、两条路、负例）、§2（when_to_update + 好/坏示例）、§3（status 枚举）

- [ ] **Step 1:** `templates.md` knowledge frontmatter 模板加 **`when_to_update`** 字段行 + **好/坏对照示例**（好：「改了 plugin 加载协议 / 动了 hooks/stop.sh」；坏：「有任何改动时」）。workflow（spec）frontmatter 加可选 **`graduate: true`** 说明。
- [ ] **Step 2:** `templates.md` status 取值处改 knowledge = `{active, stale, obsolete}`（删 superseded）；注 `stale`=疑似过期待复核、`obsolete`=已死待归档排水态。
- [ ] **Step 3:** `folder-semantics.md` status 语义/枚举同步（knowledge 三态、obsolete=knowledge 版 done 一句）；docs/ 段补"graduate 落点 + when_to_update 保鲜"一句。
- [ ] **Step 4:** 通读两文件改动段对照 spec §1–3；commit：

```bash
git add skills/preflight/templates.md skills/preflight/folder-semantics.md
git commit -F - <<'EOF'
docs(skill): templates/folder-semantics 加 graduate/when_to_update + 三态枚举

实施 spec §1–3：knowledge frontmatter 加 when_to_update（带好/坏示例）、
spec 加可选 graduate；status 枚举改 {active, stale, obsolete}。
EOF
```

---

### Task 10: `protocol.md`

**Files:** `skills/preflight/protocol.md`
**源 §：** spec §1–4 全部（协议"教科书"，承载模型级真相）

- [ ] **Step 1:** § status：knowledge 枚举改 `{active, stale, obsolete}`，删 superseded 状态值；写明 `supersedes`=纯溯源标注**非钉扣边**、`superseded_by` 字段退役。
- [ ] **Step 2:** § Lifecycle：加 **graduate 接缝**（graduate:true done spec → 本体变身 docs、不留 archive 双胞胎、两条路判据、负例）；加 **obsolete=knowledge 版 done** 排水（obsolete≡done-but-unlanded、仪式排空、退出闸是用户断言）。
- [ ] **Step 3:** 写明**双仪式 stale 检测**（exit-ritual + preflight、锚点定义、幂等键）与 graduate 的 landing=主/preflight=补偿；§ 前提补"单活跃会话 + archive 仍冷存"（spec § 前提与边界）。
- [ ] **Step 4:** 通读对照 spec §1–4 + 前提；commit（heredoc，message 同式）。

---

### Task 11: `exit-ritual.md` + preflight 主流程

**Files:** `skills/preflight/exit-ritual.md`、`skills/preflight/SKILL.md`
**源 §：** spec §1（graduate 收尾）、§2（双仪式检测 + 自动 stale + 锚点）、§3（排空 obsolete）、§4 图

- [ ] **Step 1:** exit-ritual：加「**when_to_update 命中检测**」小节——回合末用 `--changed-since-anchor`（Task 7）比对各 docs `when_to_update`，命中**自动翻 `status: stale`** + cockpit 浮一行；landing commit **带 `Flightdeck-Sync:` trailer**（喂锚点）。
- [ ] **Step 2:** exit-ritual：加「**graduate 收尾**」——见 graduate:true done spec（仍在 specs/）→ 改写搬进 docs/、补 when_to_read/applies_to/when_to_update、源处删；幂等键=源文件仍在 specs/。
- [ ] **Step 3:** exit-ritual：加「**排空 obsolete**」——`--archivable` 现含 obsolete knowledge，与排 done 同一步搬进 archive。
- [ ] **Step 4:** preflight（`SKILL.md` checklist）：加「**回溯安全网**」——进场用 `--changed-since-anchor` 补检 when_to_update→stale；扫 graduate:true done spec 仍在 specs/ → 补做 graduate；扫 obsolete → 提醒排空；跑完推进锚点。明确 preflight 仍 **read-mostly**：stale 翻转 + 锚点推进是它唯一的写。
- [ ] **Step 5:** 通读对照 spec §1–4 + §4 图；commit。

---

### Task 12: `skills/new` + `skills/landing`

**Files:** `skills/new/SKILL.md`、`skills/landing/SKILL.md`
**源 §：** spec §1（graduate 前置问 + hint；landing graduate 改写搬运）、§2（stale 浮现）、§3（排空 obsolete）

- [ ] **Step 1:** `skills/new`：创建 spec 时若命中 graduate 判据（约束后续开发 / 大概率复用，含负例边界）→ **主动问「标记 graduate？」**，点头写 `graduate: true`；说明 flag 窗口=整个 active 期。
- [ ] **Step 2:** `skills/landing`：Land Routine 加 graduate 改写搬运（landing=主路径）；landing commit 带 `Flightdeck-Sync:` trailer；`--archivable` 排空含 obsolete；stale 行浮进 cockpit。
- [ ] **Step 3:** 通读对照 spec §1–3；commit。

---

## 相位 3 — docs/incident 对齐（散文）

### Task 13: `docs/model-architecture.md` + `docs/spec-lifecycle.md`

**Files:** `flightdeck/docs/model-architecture.md`、`flightdeck/docs/spec-lifecycle.md`
**源 §：** spec §1（graduate 两条路）、§3（status 简化 + obsolete=done 对称）、§2（保鲜）

> 这是"实现直接更新既有 docs"那条路（spec § 背景）——本 spec 的耐久知识沉进这两份既有 docs，**不 graduate 成新 doc**。

- [ ] **Step 1:** `model-architecture.md`：status 轴 knowledge 改 `{active, stale, obsolete}`；加「**obsolete = knowledge 版 done**」对称段（drain vs accumulate 框架内）；`supersedes`=溯源非钉扣、`superseded_by` 退役。
- [ ] **Step 2:** `spec-lifecycle.md`：第 6 步 graduate 改写——graduate:true 触发、本体变身 docs **不留 archive 双胞胎**（覆盖旧"历史+真相两份"叙述）、两条路判据、配 when_to_update 保鲜。
- [ ] **Step 3:** 这两份 docs 加 `when_to_update` frontmatter（dogfood 自身吃新字段）：`model-architecture.md` → 「改了 status 枚举 / 文件夹 kind / 归档判据时」；`spec-lifecycle.md` → 「改了 graduate 触发 / archive 搬运 / status 轴时」。**自洽说明**：本次实施正把它们改到当前真相，故实施完它们是 `active`，不需翻 stale（机制是"改动命中且**未同步更新**才 stale"；同步更新即保 active）。
- [ ] **Step 4:** 通读 + `uv run scripts/flightdeck_index.py flightdeck` regen（docs INDEX 摘要变）；commit。

---

### Task 14: 对齐 incident `workflow-has-no-superseded-status`

**Files:** `flightdeck/incidents/2026-06-07-workflow-has-no-superseded-status.md`
**源 §：** spec §3（superseded 状态值删、supersedes 边留）

- [ ] **Step 1:** 原文强调"superseded 是 knowledge 状态、workflow 没有"。现 knowledge 侧也删了 superseded 状态值 → 加一句 Case/注：knowledge status 现为 `{active, stale, obsolete}`，`superseded` 状态值已全局退役，取代关系一律用 `supersedes` 溯源边 + `obsolete` 排水；`lint:43` 引用更新。
- [ ] **Step 2:** commit。

---

## 相位 4 — dogfood 迁移 + 全验证

### Task 15: 迁移扫描 + 全绿验证 + 收尾

- [ ] **Step 1: 扫本 deck live obsolete/superseded**（预期 0，spec 已实测）

```bash
git grep -nE "^status: (obsolete|superseded)" -- 'flightdeck/specs' 'flightdeck/plans' 'flightdeck/incidents' 'flightdeck/checklists' 'flightdeck/docs'
```
Expected: 无命中。若意外 live 命中 → 逐件判断翻 `active`（仍当前）或 `obsolete`（待排空）。

- [ ] **Step 2: 全脚本测试绿**

Run: `uv run pytest scripts/tests/ -v`
Expected: 全 PASS

- [ ] **Step 3: lint + walkaround 自审**

Run: `uv run scripts/flightdeck_lint.py flightdeck`，并跑 `/flightdeck:walkaround`
Expected: 无新 CRITICAL/WARNING（status 合法、INDEX 一致、无悬挂边）

- [ ] **Step 4: 本 spec/plan 收尾** — spec + 本 plan 翻 `done`；本 spec **不 graduate**（耐久知识已进 model-architecture/spec-lifecycle，走"更新既有 docs"路）。跑 landing 归档（入边清空后排进 archive）。

- [ ] **Step 5: final landing commit**（带 `Flightdeck-Sync:` trailer）。

---

## Self-review（写完本 plan 的回看）

- **Spec 覆盖**：§1 graduate→Task 9/10/11/12；§2 when_to_update/stale/双仪式/锚点→Task 5/6/7/10/11；§3 status 枚举/钉扣边/obsolete 排水/match_signature→Task 1/2/3/4/6 + 13/14；§4 图→Task 10/11；前提与边界（单会话/archive 冷存）→Task 10；验收→Task 8/15。**无遗漏 §**。
- **类型/命名一致**：`archivable_obsolete`、`last_anchor_ref`、`changed_since_anchor`、`audit_when_to_update`、`Flightdeck-Sync` trailer、`VAGUE_TOKENS` 全程同名。
- **占位符**：脚本任务均含真实测试+实现代码；散文任务给确切文件+段落要点+源 §（内容真相源=spec，不重复整段散文是刻意 DRY，非占位）。
- **待 executor 就地校正的两处**（已标注）：Task 6 渲染函数真名（读 index:238）；Task 7 git env 跨平台。
