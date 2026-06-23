#!/usr/bin/env python3
"""Build-stamp anchor: detect whether the loaded plugin cache matches the working tree.

The dogfood problem: the live build Claude Code loads is the *plugin cache*, not this
repo. After editing a skill/script you can't tell, from inside a session, whether the
cache still reflects your edits or is stale and needs a re-sync.

This computes a short content hash over the **plugin build inputs** (the source set that
`local-plugin-testing.md`'s robocopy mirrors into the cache — skills/scripts/adapters/
manifests/context files; NOT the `flightdeck/` deck, docs/, or tmp/). The hash
is stored in `.current` at repo root.

Wiring (see flightdeck/knowledge/local-plugin-testing.md):
  --write   recompute the hash and write it to .current. Run this **as the first step of
            the sync**, right before robocopy /MIR — so the mirror carries the fresh stamp
            into the cache too. Never run --write without then syncing, or .current will
            claim "current" while the cache is actually old.
  --check   recompute the live hash and compare to .current.
            prints/exits: current -> 0 ; stale -> 1 ; no .current -> 2.

Because --write only fires at sync time, any edit afterwards makes the live hash diverge
from the stored stamp, and --check reports `stale` with zero manual bookkeeping.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAMP = ROOT / ".current"

# Plugin build inputs — what actually determines loaded behavior. Missing entries are
# skipped (e.g. an adapter dir that doesn't exist). `.current` itself is never hashed.
INCLUDE = [
    "skills",
    "scripts",
    "adapters",
    ".claude-plugin",
    ".codex-plugin",
    ".cursor-plugin",
    "gemini-extension.json",
    "GEMINI.md",
    "CLAUDE.md",
]
SKIP_PARTS = {"__pycache__"}
SKIP_SUFFIX = {".pyc", ".pyo"}


def _iter_files():
    for rel in INCLUDE:
        p = ROOT / rel
        if not p.exists():
            continue
        if p.is_file():
            yield p
            continue
        for f in p.rglob("*"):
            if not f.is_file():
                continue
            if SKIP_PARTS & set(f.parts) or f.suffix in SKIP_SUFFIX:
                continue
            yield f


def compute() -> str:
    h = hashlib.sha256()
    files = sorted(_iter_files(), key=lambda f: f.relative_to(ROOT).as_posix())
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(f.read_bytes())
        h.update(b"\0")
    return h.hexdigest()[:12]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="plugin build-stamp anchor (.current)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true", help="recompute and write .current (sync step)")
    g.add_argument("--check", action="store_true", help="compare live hash to .current")
    args = ap.parse_args(argv)

    live = compute()

    if args.write:
        STAMP.write_text(live + "\n", encoding="utf-8")
        print(f"build stamp written: {live}")
        return 0

    if not STAMP.exists():
        print("unknown — no .current (run --write during sync)")
        return 2
    stored = STAMP.read_text(encoding="utf-8").strip()
    if stored == live:
        print(f"current ({live})")
        return 0
    print(
        f"stale - working tree {live} != synced {stored}; "
        f"reload cache (see flightdeck/knowledge/local-plugin-testing.md)"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
