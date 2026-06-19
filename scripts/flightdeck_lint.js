#!/usr/bin/env node
'use strict';
// flightdeck mechanical layer — lint, Node port of flightdeck_lint.py. Runs the
// deterministic audit subset and emits findings as JSON. Byte-parity with the
// Python reference (spec §3.3); gated by scripts/tests/test_parity.py::LintParity.
// Built-ins only, zero npm deps.

const path = require('path');
const idx = require('./flightdeck_index');
const L = require('./flightdeck_lib');

const {
  parseFrontmatter, indexDrift, readText, isDir, isFile, mdNames, walkMd,
  subDirs, relPosix, sortPaths, KNOWLEDGE_KINDS, IMPORTED_KINDS, NESTABLE_KINDS,
} = idx;
const { pyJsonIndent, pyListRepr, sortCp } = L;

const WORKFLOW_STATUSES = new Set(['idea', 'active', 'done']);
const KNOWLEDGE_STATUSES = new Set(['active', 'stale', 'obsolete']);
const LEGAL_SETTINGS = {
  runtime: new Set(['uv', 'python', 'node']),
  agents_md: new Set(['auto', 'off']),
};
const WORKFLOW_FOLDERS = ['specs', 'plans'];
const KNOWLEDGE_FOLDERS = sortCp([...KNOWLEDGE_KINDS]); // deterministic (mirrors the Python sort)
const KNOWN_FOLDERS = new Set(['specs', 'plans', ...KNOWLEDGE_KINDS, ...IMPORTED_KINDS, 'archive']);
const KNOWN_ROOT_FILES = new Set(['cockpit.md', 'INDEX.md', 'rules.md']);
const VAGUE_TOKENS = ['任何', '所有', 'any change', 'all changes', 'anything', 'everything'];

const REQUIRED_SECTIONS = {
  'cockpit.md': [
    ['## In Progress', /^##\s+In Progress\s*$/m],
    ['<!-- AUTO:inprogress -->', /<!--\s*AUTO:inprogress\s*-->/],
    ['<!-- /AUTO -->', /<!--\s*\/AUTO\s*-->/],
    ['## Next', /^##\s+Next\s*$/m],
    ['## Hanging Tasks', /^##\s+Hanging Tasks\s*$/m],
  ],
};

const LINK_RE = /\[[^\]]*\]\(([^)]+)\)/g;
const FENCE_RE = /^[ \t]*(`{3,}|~{3,})[^\n]*\n[\s\S]*?^[ \t]*\1[ \t]*$/gm;
const INLINE_CODE_RE = /`+[^`\n]*`+/g;

const legalRepr = (legalSet) => pyListRepr(sortCp([...legalSet]));

function stripCode(text) {
  return text.replace(FENCE_RE, '').replace(INLINE_CODE_RE, '');
}
function finding(audit, severity, p, message) {
  return { audit, severity, path: String(p), message };
}
function findLinks(text) {
  const out = [];
  let m;
  LINK_RE.lastIndex = 0;
  while ((m = LINK_RE.exec(text)) !== null) out.push(m[1]);
  return out;
}
// top-level *.md absolute paths (no INDEX.md), sorted like Python's sorted(glob)
function artifactFiles(folder) {
  return sortPaths(mdNames(folder).filter((n) => n !== 'INDEX.md').map((n) => path.join(folder, n)));
}

function auditStatus(deck) {
  const findings = [];
  for (const [folders, legal] of [
    [WORKFLOW_FOLDERS, WORKFLOW_STATUSES],
    [KNOWLEDGE_FOLDERS, KNOWLEDGE_STATUSES],
  ]) {
    for (const name of folders) {
      const folder = path.join(deck, name);
      if (!isDir(folder)) continue;
      for (const f of artifactFiles(folder)) {
        const status = parseFrontmatter(readText(f)).status;
        if (!status) {
          findings.push(finding('status', 'CRITICAL', f, `${name}/${path.basename(f)} missing required \`status\``));
        } else if (!legal.has(status)) {
          findings.push(finding('status', 'WARNING', f,
            `${name}/${path.basename(f)} has illegal status \`${status}\` (legal: ${legalRepr(legal)})`));
        }
      }
    }
  }
  return findings;
}

function auditOrphanPlans(deck) {
  const folder = path.join(deck, 'plans');
  if (!isDir(folder)) return [];
  const findings = [];
  for (const f of artifactFiles(folder)) {
    if (!parseFrontmatter(readText(f)).implements) {
      findings.push(finding('orphan-plan', 'INFO', f,
        `plans/${path.basename(f)} has no \`implements:\` — link a spec or confirm standalone`));
    }
  }
  return findings;
}

function driftTargetPath(deck, label) {
  if (label === 'root') return path.join(deck, 'INDEX.md');
  if (label === 'cockpit') return path.join(deck, 'cockpit.md');
  return path.join(deck, label, 'INDEX.md');
}
function auditIndexConsistency(deck) {
  return indexDrift(deck).map((label) =>
    finding('index-consistency', 'WARNING', driftTargetPath(deck, label),
      `INDEX drift: \`${label}\` is stale — regenerate with flightdeck_index.py`));
}

function cleanTarget(target) {
  target = target.trim();
  if (target.startsWith('<') && target.endsWith('>')) target = target.slice(1, -1).trim();
  if (target.startsWith('#')) return null;
  if (target.includes('://') || target.startsWith('mailto:')) return null;
  if (target.startsWith('/')) return null;
  let pathPart = target.split('#')[0].trim();
  if (pathPart.includes(' ')) pathPart = pathPart.split(' ')[0];
  return pathPart || null;
}

function auditDanglingRefs(mdFiles) {
  const findings = [];
  for (const f of mdFiles) {
    let text;
    try { text = readText(f); } catch { continue; }
    for (const raw of findLinks(stripCode(text))) {
      const pathPart = cleanTarget(raw);
      if (pathPart === null) continue;
      if (!isFile(path.join(path.dirname(f), pathPart)) && !isDir(path.join(path.dirname(f), pathPart))) {
        findings.push(finding('dangling-ref', 'CRITICAL', f, `${path.basename(f)} -> ${raw.trim()} (target file missing)`));
      }
    }
  }
  return findings;
}

function auditStray(deck) {
  const linked = new Set();
  for (const name of KNOWN_ROOT_FILES) {
    const entry = path.join(deck, name);
    if (!isFile(entry)) continue;
    for (const raw of findLinks(readText(entry))) {
      const pathPart = cleanTarget(raw);
      if (pathPart) {
        try { linked.add(require('fs').realpathSync(path.join(path.dirname(entry), pathPart))); }
        catch { linked.add(path.resolve(path.dirname(entry), pathPart)); }
      }
    }
  }
  const findings = [];
  const children = sortPaths(
    (() => { try { return require('fs').readdirSync(deck).map((n) => path.join(deck, n)); } catch { return []; } })(),
  );
  for (const child of children) {
    if (isDir(child)) {
      if (!KNOWN_FOLDERS.has(path.basename(child))) {
        findings.push(finding('stray', 'WARNING', child, `unknown directory \`${path.basename(child)}/\` under deck root`));
      }
    } else if (child.endsWith('.md') && !KNOWN_ROOT_FILES.has(path.basename(child))) {
      let resolved;
      try { resolved = require('fs').realpathSync(child); } catch { resolved = path.resolve(child); }
      if (linked.has(resolved)) continue;
      findings.push(finding('stray', 'WARNING', child, `orphan \`${path.basename(child)}\` at deck root — link from an entry or remove`));
    }
  }
  return findings;
}

function auditRequiredStructure(deck) {
  const findings = [];
  for (const [filename, blocks] of Object.entries(REQUIRED_SECTIONS)) {
    const f = path.join(deck, filename);
    if (!isFile(f)) continue;
    const text = readText(f);
    for (const [label, pattern] of blocks) {
      if (!pattern.test(text)) {
        findings.push(finding('required-structure', 'CRITICAL', f,
          `${filename} missing required block \`${label}\` — a multi-line Edit may have dropped it`));
      }
    }
  }
  return findings;
}

function isAlnum(s) {
  return /[\p{L}\p{N}]/u.test(s);
}
function auditWhenToUpdate(deck) {
  const findings = [];
  for (const name of KNOWLEDGE_FOLDERS) {
    const folder = path.join(deck, name);
    if (!isDir(folder)) continue;
    for (const f of artifactFiles(folder)) {
      const wtu = parseFrontmatter(readText(f)).when_to_update;
      if (wtu === undefined) continue;
      const s = String(wtu).trim();
      const low = s.toLowerCase();
      const vague = !s || VAGUE_TOKENS.some((t) => low.includes(t) || s.includes(t));
      const concrete = /[/.\p{L}\p{N}_]{3,}/u.test(s) && isAlnum(s);
      if (vague || !concrete) {
        findings.push(finding('when_to_update', 'WARNING', f,
          `${name}/${path.basename(f)} when_to_update too vague/empty: write a concrete change event (changed X / added Y / touched file Z)`));
      }
    }
  }
  return findings;
}

function auditSettings(deck) {
  const rules = path.join(deck, 'rules.md');
  if (!isFile(rules)) return [];
  const fm = parseFrontmatter(readText(rules));
  const findings = [];
  for (const [key, legal] of Object.entries(LEGAL_SETTINGS)) {
    const val = fm[key];
    if (val !== undefined && !legal.has(val)) {
      findings.push(finding('settings', 'WARNING', rules,
        `rules.md \`${key}: ${val}\` is illegal (legal: ${legalRepr(legal)})`));
    }
  }
  return findings;
}

function collectMd(deck, repoRoot) {
  const files = walkMd(deck).filter((p) => !relPosix(deck, p).split('/').includes('archive'));
  if (repoRoot !== null && repoRoot !== undefined) {
    for (const n of mdNames(repoRoot)) files.push(path.join(repoRoot, n));
  }
  // deterministic by native path string (codepoint) — mirrors the Python sort
  return files.sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));
}

function lint(deck, repoRoot) {
  let findings = [];
  findings = findings.concat(auditStatus(deck));
  findings = findings.concat(auditWhenToUpdate(deck));
  findings = findings.concat(auditSettings(deck));
  findings = findings.concat(auditRequiredStructure(deck));
  findings = findings.concat(auditOrphanPlans(deck));
  if (isFile(path.join(deck, 'INDEX.md'))) findings = findings.concat(auditIndexConsistency(deck));
  findings = findings.concat(auditDanglingRefs(collectMd(deck, repoRoot)));
  findings = findings.concat(auditStray(deck));
  return findings;
}

function main(argv) {
  let deck = null;
  let repoRoot = null;
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--repo-root') repoRoot = argv[++i];
    else if (deck === null) deck = argv[i];
  }
  if (repoRoot === null) repoRoot = path.dirname(deck);
  const findings = lint(deck, repoRoot);
  process.stdout.write(pyJsonIndent({ findings }) + '\n');
  const blocking = findings.some((f) => f.severity === 'CRITICAL' || f.severity === 'WARNING');
  return blocking ? 1 : 0;
}

if (require.main === module) {
  process.exit(main(process.argv.slice(2)));
}

module.exports = { lint, auditStatus, auditSettings, auditDanglingRefs };
