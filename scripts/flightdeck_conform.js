#!/usr/bin/env node
'use strict';
// flightdeck_conform — conform a deck to the canonical schema. Node port of
// flightdeck_conform.py; byte-parity with the reference (LF newlines, codepoint
// sort, deterministic). Built-ins only, zero npm deps.
//
// Mechanical pass: delete non-schema frontmatter fields across every active
// file, stamp rules.md recorded-config, append missing cockpit/rules sections
// (append-only). Prints a missing-required worklist for the /flightdeck:conform
// AI pass. Scope excludes archive/, references/ (IMPORTED_KIND), and stray dirs.

const fs = require('fs');
const path = require('path');
const idx = require('./flightdeck_index');
const { cmpCodepoint } = require('./flightdeck_lib');

const { parseFrontmatter, IMPORTED_KINDS } = idx;
const sortCp = (arr) => [...arr].sort(cmpCodepoint);

// kind → full legal frontmatter set (required + every optional). A field outside
// a file's kind set is deleted. Pinned by test_flightdeck_conform.py.
const LEGAL_FIELDS = {
  spec: new Set(['status', 'summary', 'last_updated', 'note', 'supersedes',
    'related', 'graduate', 'verify']),
  plan: new Set(['status', 'summary', 'last_updated', 'note', 'implements',
    'supersedes', 'related', 'verify']),
  incident: new Set(['status', 'when_to_read', 'applies_to', 'last_updated',
    'summary', 'when_to_update', 'skip_when', 'recurrences', 'resolved_by', 'verify']),
  checklist: new Set(['status', 'when_to_read', 'applies_to', 'last_updated',
    'summary', 'when_to_update', 'skip_when', 'verify', 'synced']),
  reference: new Set(['status', 'when_to_read', 'applies_to', 'last_updated',
    'summary', 'when_to_update', 'verify']),
  doc: new Set(['status', 'when_to_read', 'applies_to', 'last_updated', 'summary',
    'when_to_update', 'verify', 'synced']),
  rules: new Set(['version', 'runtime', 'agents_md']),
};

// kind → fields whose absence is reported on the AI worklist.
const REQUIRED_FIELDS = {
  spec: new Set(['status', 'summary']),
  plan: new Set(['status', 'summary']),
  incident: new Set(['status', 'when_to_read', 'applies_to', 'last_updated']),
  checklist: new Set(['status', 'when_to_read', 'applies_to', 'last_updated']),
  reference: new Set(['status', 'when_to_read', 'applies_to', 'last_updated']),
  doc: new Set(['status', 'when_to_read', 'applies_to', 'last_updated']),
  rules: new Set(['version']),
};

const FOLDER_KIND = {
  specs: 'spec', plans: 'plan', incidents: 'incident',
  checklists: 'checklist', references: 'reference', docs: 'doc',
};
// references/ is an IMPORTED_KIND — never walked (see the .py for the rationale).
const WALK_FOLDERS = Object.keys(FOLDER_KIND).filter((f) => !IMPORTED_KINDS.has(f));

const COCKPIT_SECTIONS = [
  '## Next', '## In Progress', '## Staged (awaiting land)',
  '## Key Context', '## Pending Review', '## Hanging Tasks',
];
const RULES_SECTIONS = ['## House rules', '### Project conventions', '### Rules'];
const INPROGRESS_SKELETON = '<!-- AUTO:inprogress -->\n- (none)\n<!-- /AUTO -->';
const STAGED_SKELETON = '<!-- AUTO:staged -->\n<!-- /AUTO -->';

const RULES_STAMP = ['version', 'runtime', 'agents_md'];
const RULES_DEFAULTS = { version: '3.0', agents_md: 'off' };

const FIELD_RE = /^([A-Za-z_][\w-]*):/;

// Python read_text does universal-newline translation; mirror it so internal
// line logic matches. Writes go out as \n (the parity harness LF-normalizes).
function readText(p) {
  return fs.readFileSync(p, 'utf8').replace(/\r\n?/g, '\n');
}

// Python str.splitlines(keepends=True) over \n-normalized text.
function splitKeepends(text) {
  const out = [];
  let i = 0;
  while (i < text.length) {
    const j = text.indexOf('\n', i);
    if (j === -1) { out.push(text.slice(i)); break; }
    out.push(text.slice(i, j + 1));
    i = j + 1;
  }
  return out;
}

function detectRuntime() {
  const isWin = process.platform === 'win32';
  const exts = isWin ? (process.env.PATHEXT || '.EXE;.CMD;.BAT').split(';') : [''];
  const dirs = (process.env.PATH || '').split(path.delimiter);
  for (const name of ['uv', 'python', 'node']) {
    for (const d of dirs) {
      for (const e of exts) {
        try {
          if (fs.existsSync(path.join(d, name + e)) ||
              fs.existsSync(path.join(d, name + e.toLowerCase()))) return name;
        } catch { /* unreadable dir */ }
      }
    }
  }
  return 'python';
}

function pruneFrontmatter(text, kind) {
  const legal = LEGAL_FIELDS[kind];
  const lines = splitKeepends(text);
  if (!lines.length || lines[0].replace(/\n$/, '') !== '---') return [text, []];
  const out = [lines[0]];
  const removed = [];
  let close = null;
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].replace(/\n$/, '') === '---') { close = i; break; }
    const m = FIELD_RE.exec(lines[i]);
    if (m && !legal.has(m[1])) { removed.push(m[1]); continue; }
    out.push(lines[i]);
  }
  if (close === null) return [text, []];
  out.push(lines[close]);
  out.push(...lines.slice(close + 1));
  return [out.join(''), removed];
}

function stampRules(text, runtime) {
  const defaults = Object.assign({}, RULES_DEFAULTS, { runtime });
  const lines = splitKeepends(text);
  const hasFm = lines.length && lines[0].replace(/\n$/, '') === '---';
  if (!hasFm) {
    const block = '---\n' + RULES_STAMP.map((k) => `${k}: ${defaults[k]}\n`).join('') + '---\n';
    return block + text;
  }
  let close = null;
  const present = new Set();
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].replace(/\n$/, '') === '---') { close = i; break; }
    const m = FIELD_RE.exec(lines[i]);
    if (m) present.add(m[1]);
  }
  if (close === null) return text;
  const additions = RULES_STAMP.filter((k) => !present.has(k)).map((k) => `${k}: ${defaults[k]}\n`);
  return [...lines.slice(0, close), ...additions, ...lines.slice(close)].join('');
}

function sectionBody(section) {
  if (section === '## In Progress') return INPROGRESS_SKELETON;
  if (section === '## Staged (awaiting land)') return STAGED_SKELETON;
  return '- (none)';
}

function addMissingSections(text, which) {
  const sections = which === 'cockpit' ? COCKPIT_SECTIONS : RULES_SECTIONS;
  const present = new Set(text.split('\n').map((ln) => ln.replace(/\n$/, '')));
  const added = [];
  let out = text;
  for (const section of sections) {
    if (present.has(section)) continue;
    if (!out.endsWith('\n')) out += '\n';
    if (!out.endsWith('\n\n')) out += '\n';
    out += `${section}\n\n${sectionBody(section)}\n`;
    added.push(section);
  }
  return [out, added];
}

function makeChanges(p, removed, stamped, added) {
  return {
    path: p,
    removed: removed || [],
    stamped: stamped || [],
    addedSections: added || [],
    get changed() { return !!(this.removed.length || this.stamped.length || this.addedSections.length); },
  };
}

function relPosix(deck, p) {
  return path.relative(deck, p).replace(/\\/g, '/');
}

function kindOf(deck, p) {
  const rel = relPosix(deck, p);
  if (rel.startsWith('..')) return null;
  const parts = rel.split('/');
  if (parts.includes('archive')) return null;
  if (parts.length === 1) return parts[0] === 'rules.md' ? 'rules' : null;
  return FOLDER_KIND[parts[0]] || null;
}

function scopeFiles(deck) {
  const files = [];
  for (const folder of WALK_FOLDERS) {
    const d = path.join(deck, folder);
    let stat;
    try { stat = fs.statSync(d); } catch { continue; }
    if (!stat.isDirectory()) continue;
    const md = idx.walkMd(d).filter((p) => path.basename(p) !== 'INDEX.md');
    md.sort((a, b) => cmpCodepoint(a.replace(/\\/g, '/'), b.replace(/\\/g, '/')));
    for (const p of md) {
      const kind = kindOf(deck, p);
      if (kind !== null) files.push([p, kind]);
    }
  }
  return files;
}

function conformFile(p, kind, apply) {
  const text = readText(p);
  const [newText, removed] = pruneFrontmatter(text, kind);
  const present = new Set(Object.keys(parseFrontmatter(newText)));
  const req = REQUIRED_FIELDS[kind] || new Set();
  const missing = sortCp([...req].filter((f) => !present.has(f)));
  if (apply && newText !== text) fs.writeFileSync(p, newText, 'utf8');
  return { changes: makeChanges(p, removed), missing };
}

function runConform(deck, apply, runtime) {
  const results = [];
  const worklist = [];

  const cockpit = path.join(deck, 'cockpit.md');
  if (fs.existsSync(cockpit) && fs.statSync(cockpit).isFile()) {
    const text = readText(cockpit);
    const [newText, added] = addMissingSections(text, 'cockpit');
    if (apply && newText !== text) fs.writeFileSync(cockpit, newText, 'utf8');
    results.push(makeChanges(cockpit, [], [], added));
  }

  const rules = path.join(deck, 'rules.md');
  if (fs.existsSync(rules) && fs.statSync(rules).isFile()) {
    const text = readText(rules);
    const [pruned, removed] = pruneFrontmatter(text, 'rules');
    const present = new Set(Object.keys(parseFrontmatter(pruned)));
    const stamped = RULES_STAMP.filter((k) => !present.has(k));
    const stampedText = stampRules(pruned, runtime);
    const [newText, added] = addMissingSections(stampedText, 'rules');
    if (apply && newText !== text) fs.writeFileSync(rules, newText, 'utf8');
    results.push(makeChanges(rules, removed, stamped, added));
  }

  for (const [p, kind] of scopeFiles(deck)) {
    const { changes, missing } = conformFile(p, kind, apply);
    results.push(changes);
    const rel = relPosix(deck, p);
    for (const field of missing) worklist.push([rel, field]);
  }

  results.sort((a, b) => cmpCodepoint(relPosix(deck, a.path), relPosix(deck, b.path)));
  worklist.sort((a, b) => cmpCodepoint(a[0], b[0]) || cmpCodepoint(a[1], b[1]));
  return [results, worklist];
}

function changeSegments(ch) {
  const segs = [];
  if (ch.removed.length) segs.push('drop ' + ch.removed.join(','));
  if (ch.stamped.length) segs.push('stamp ' + ch.stamped.join(','));
  if (ch.addedSections.length) segs.push('add ' + ch.addedSections.join(','));
  return segs.join('; ');
}

function main(argv) {
  const a = { deck: null, check: false, runtime: null };
  const pos = [];
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (t === '--check') a.check = true;
    else if (t === '--runtime') a.runtime = argv[++i];
    else pos.push(t);
  }
  a.deck = pos[0];
  const runtime = a.runtime || detectRuntime();
  const apply = !a.check;
  const [results, worklist] = runConform(a.deck, apply, runtime);

  if (a.check) {
    for (const ch of results) {
      if (ch.changed) {
        process.stdout.write(`${relPosix(a.deck, ch.path)}\t${changeSegments(ch)}\n`);
      }
    }
    for (const [rel, field] of worklist) {
      process.stdout.write(`${rel}\t(missing) ${field}\n`);
    }
    const pending = results.some((ch) => ch.changed) || worklist.length > 0;
    return pending ? 1 : 0;
  }

  for (const [rel, field] of worklist) process.stdout.write(`${rel}\t${field}\n`);
  return 0;
}

if (require.main === module) {
  process.exit(main(process.argv.slice(2)));
}

module.exports = {
  LEGAL_FIELDS, REQUIRED_FIELDS, FOLDER_KIND, WALK_FOLDERS,
  COCKPIT_SECTIONS, RULES_SECTIONS,
  pruneFrontmatter, stampRules, addMissingSections, kindOf, detectRuntime,
  runConform, main,
};
