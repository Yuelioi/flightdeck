#!/usr/bin/env node
'use strict';
// flightdeck mechanical layer — INDEX regeneration, Node port of
// flightdeck_index.py. Byte-parity with the Python reference (spec §3.3); the
// golden harness (scripts/tests/test_parity.py::IndexParity) is the contract.
// Built-ins only, zero npm deps.

const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');
const L = require('./flightdeck_lib');

const { DASH, sortCp, parseFrontmatter, pyJsonArray, signatureFingerprint } = L;

// ── fs + path helpers (Python read_text universal-newlines; write LF) ─────────
function readText(p) {
  return fs.readFileSync(p, 'utf8').replace(/\r\n?/g, '\n');
}
function writeText(p, s) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, s, 'utf8'); // s carries LF; never inject CRLF
}
function isDir(p) {
  try { return fs.statSync(p).isDirectory(); } catch { return false; }
}
function isFile(p) {
  try { return fs.statSync(p).isFile(); } catch { return false; }
}
function relPosix(base, p) {
  return path.relative(base, p).split(path.sep).join('/');
}
// top-level *.md names in dir (no recursion); [] when dir absent
function mdNames(dir) {
  try {
    return fs.readdirSync(dir).filter(
      (n) => n.endsWith('.md') && isFile(path.join(dir, n)),
    );
  } catch { return []; }
}
// immediate subdirectories of dir (absolute paths)
function subDirs(dir) {
  try {
    return fs.readdirSync(dir)
      .map((n) => path.join(dir, n))
      .filter(isDir);
  } catch { return []; }
}
// recursive *.md absolute paths under root ([] when absent)
function walkMd(root) {
  const out = [];
  function rec(d) {
    let ents;
    try { ents = fs.readdirSync(d, { withFileTypes: true }); } catch { return; }
    for (const e of ents) {
      const full = path.join(d, e.name);
      if (e.isDirectory()) rec(full);
      else if (e.name.endsWith('.md')) out.push(full);
    }
  }
  rec(root);
  return out;
}
// Python `sorted(<Path objects>)` — normcase (lowercase on Windows) part-wise.
// Real decks use lowercase ascii filenames so this rarely diverges from a plain
// name sort, but match_signature's output order depends on it.
function normcaseParts(p) {
  return p.replace(/\\/g, '/').toLowerCase().split('/');
}
function sortPaths(paths) {
  return [...paths].sort((a, b) => {
    const ap = normcaseParts(a);
    const bp = normcaseParts(b);
    const n = Math.min(ap.length, bp.length);
    for (let i = 0; i < n; i++) {
      if (ap[i] < bp[i]) return -1;
      if (ap[i] > bp[i]) return 1;
    }
    return ap.length - bp.length;
  });
}
const fmField = (p, field) => {
  try { return parseFrontmatter(readText(p))[field]; } catch { return undefined; }
};
const fmOf = (p) => parseFrontmatter(readText(p));

// ── kind constants (mirror the Python sets) ──────────────────────────────────
const SUMMARY_KINDS = new Set(['specs', 'plans']);
const KNOWLEDGE_KINDS = new Set(['checklists', 'incidents', 'docs']);
const IMPORTED_KINDS = new Set(['references']);
const NESTABLE_KINDS = new Set(['incidents', 'checklists', 'docs', 'references']);
const FOLDER_ORDER = ['specs', 'plans', 'incidents', 'checklists', 'docs', 'references'];
const REGEN_FOLDERS = FOLDER_ORDER.filter((n) => !IMPORTED_KINDS.has(n));
const AUTO_END = '<!-- /AUTO -->';
const INPROGRESS_SUMMARY_MAX = 80;

// ── signatures ───────────────────────────────────────────────────────────────
function parseSignature(text) {
  const m = text.match(/^##\s+Signature\s*$([\s\S]*?)(?=^##\s|(?![\s\S]))/m);
  if (!m) return {};
  const sig = {};
  for (const line of m[1].split('\n')) {
    const lm = line.match(/^\s*-\s*(symptom|error_type|where|trigger)\s*:\s*(.*)$/);
    if (lm) sig[lm[1]] = lm[2].trim().replace(/^`+/, '').replace(/`+$/, '').trim();
  }
  return sig;
}
function matchSignature(deck, symptom, errorType = '') {
  const fp = signatureFingerprint(symptom, errorType);
  const hits = [];
  const scanRoots = [path.join(deck, 'incidents'), path.join(deck, 'archive', 'incidents')];
  const seen = new Set();
  for (const root of scanRoots) {
    if (!isDir(root)) continue;
    for (const p of sortPaths(walkMd(root))) {
      if (path.basename(p) === 'INDEX.md') continue;
      let resolved;
      try { resolved = fs.realpathSync(p); } catch { resolved = p; }
      if (seen.has(resolved)) continue;
      seen.add(resolved);
      const text = readText(p);
      const sig = parseSignature(text);
      if (!sig.symptom) continue;
      if (signatureFingerprint(sig.symptom, sig.error_type || '') === fp) {
        hits.push({
          path: relPosix(deck, p),
          status: parseFrontmatter(text).status || '',
          where: sig.where || '',
        });
      }
    }
  }
  return hits;
}

// ── row rendering ────────────────────────────────────────────────────────────
function formatRow(kind, filename, fm) {
  const link = `- [${filename}](${filename})`;
  const status = fm.status !== undefined ? fm.status : '?';
  if (SUMMARY_KINDS.has(kind)) {
    let row = `${link} ${DASH} ${status} ${DASH} ${fm.summary !== undefined ? fm.summary : '⚠ summary 缺失'}`;
    if (fm.verify) row = '⚠未验证 ' + row;
    return row;
  }
  if (KNOWLEDGE_KINDS.has(kind)) {
    let row =
      `${link} ${DASH} ${status} ${DASH} ` +
      `when_to_read: ${fm.when_to_read !== undefined ? fm.when_to_read : '⚠ 缺失'} ${DASH} ` +
      `applies_to: ${fm.applies_to !== undefined ? fm.applies_to : '[]'}`;
    if (kind === 'incidents') {
      const raw = fm.recurrences !== undefined ? String(fm.recurrences) : '1';
      const n = /^\s*[+-]?\d+\s*$/.test(raw) ? parseInt(raw, 10) : 1;
      if (n > 1) row += ` ${DASH} recur: ${n}`;
    }
    if (fm.verify) row = '⚠未验证 ' + row;
    else if (status === 'stale') row = '⚠待复核 ' + row;
    return row;
  }
  throw new Error(`unknown folder kind: ${kind}`);
}

function replaceAutoBlock(text, newBlock) {
  const start = text.indexOf('<!-- AUTO:');
  const end = text.indexOf(AUTO_END) + AUTO_END.length;
  return text.slice(0, start) + newBlock + text.slice(end);
}

function areaRow(areaDir) {
  const idx = path.join(areaDir, 'INDEX.md');
  const fm = isFile(idx) ? parseFrontmatter(readText(idx)) : {};
  const purpose = fm.purpose !== undefined ? fm.purpose : '⚠ purpose 缺失';
  const updated = fm.last_updated !== undefined ? fm.last_updated : '—';
  const name = path.basename(areaDir);
  return `- [${name}/](${name}/INDEX.md) ${DASH} ${purpose} ${DASH} last_updated: ${updated}`;
}

function specsGroupedBody(folder, names) {
  const fms = {};
  for (const n of names) fms[n] = fmOf(path.join(folder, n));
  const ideas = sortCp(names.filter((n) => fms[n].status === 'idea'));
  const activeDone = sortCp(
    names.filter((n) => fms[n].status === 'active' || fms[n].status === 'done'),
  ).reverse();
  const groups = [];
  if (ideas.length) {
    groups.push('### Backlog (idea)\n' + ideas.map((n) => formatRow('specs', n, fms[n])).join('\n'));
  }
  if (activeDone.length) {
    groups.push('### Active · Done\n' + activeDone.map((n) => formatRow('specs', n, fms[n])).join('\n'));
  }
  return groups.join('\n\n');
}

function regenFolderIndex(folder) {
  const kind = path.basename(folder);
  if (kind === 'specs') {
    const names = sortCp(mdNames(folder).filter((n) => n !== 'INDEX.md'));
    return `<!-- AUTO:${kind} -->\n${specsGroupedBody(folder, names)}\n${AUTO_END}`;
  }
  const subs = sortPaths(subDirs(folder)); // sorted by name (Path order)
  if (NESTABLE_KINDS.has(kind) && subs.length) {
    const rows = subs.map(areaRow);
    const rowKind = KNOWLEDGE_KINDS.has(kind) ? kind : 'checklists';
    let topFiles = sortCp(mdNames(folder).filter((n) => n !== 'INDEX.md'));
    if (KNOWLEDGE_KINDS.has(kind)) {
      topFiles = topFiles.filter((n) => fmOf(path.join(folder, n)).status !== 'obsolete');
    }
    for (const n of topFiles) rows.push(formatRow(rowKind, n, fmOf(path.join(folder, n))));
    return `<!-- AUTO:${kind} -->\n` + rows.join('\n') + `\n${AUTO_END}`;
  }
  let names = sortCp(mdNames(folder).filter((n) => n !== 'INDEX.md'));
  if (KNOWLEDGE_KINDS.has(kind)) {
    names = names.filter((n) => fmOf(path.join(folder, n)).status !== 'obsolete');
  }
  const rowKind = SUMMARY_KINDS.has(kind) || KNOWLEDGE_KINDS.has(kind) ? kind : 'checklists';
  const rows = names.map((n) => formatRow(rowKind, n, fmOf(path.join(folder, n))));
  return `<!-- AUTO:${kind} -->\n` + rows.join('\n') + `\n${AUTO_END}`;
}

function truncateInprogressSummary(summary) {
  const head = summary ? summary.split('\n')[0] : '';
  const cps = Array.from(head);
  if (cps.length > INPROGRESS_SUMMARY_MAX) {
    return cps.slice(0, INPROGRESS_SUMMARY_MAX).join('').replace(/\s+$/, '') + '…';
  }
  return head;
}

function regenCockpitInprogress(deck) {
  const rows = [];
  for (const kind of ['specs', 'plans']) {
    const folder = path.join(deck, kind);
    if (!isDir(folder)) continue;
    const names = sortCp(mdNames(folder).filter((n) => n !== 'INDEX.md'));
    for (const name of names) {
      const fm = fmOf(path.join(folder, name));
      if (fm.status !== 'active') continue;
      const summary = truncateInprogressSummary(fm.summary !== undefined ? fm.summary : '⚠ summary 缺失');
      let row = `- [${name}](${kind}/${name}) ${DASH} ${summary}`;
      if (fm.note) row += ` ${DASH} [note: ${fm.note}]`;
      rows.push(row);
    }
  }
  return `<!-- AUTO:inprogress -->\n${rows.join('\n')}\n${AUTO_END}`;
}

// ── archivable / advance / verify ────────────────────────────────────────────
function activeInboundTargets(deck) {
  const targets = new Set();
  const kinds = ['specs', 'plans', ...sortCp([...KNOWLEDGE_KINDS])];
  for (const kind of kinds) {
    const folder = path.join(deck, kind);
    if (!isDir(folder)) continue;
    for (const p of walkMd(folder)) {
      if (path.basename(p) === 'INDEX.md') continue;
      const fm = fmOf(p);
      if (fm.status !== 'active') continue;
      if (fm.implements) targets.add(String(fm.implements).trim());
    }
  }
  return targets;
}
function archivableDone(deck) {
  const blocked = activeInboundTargets(deck);
  const result = [];
  for (const kind of ['specs', 'plans']) {
    const folder = path.join(deck, kind);
    if (!isDir(folder)) continue;
    for (const n of sortCp(mdNames(folder).filter((x) => x !== 'INDEX.md'))) {
      const fm = fmOf(path.join(folder, n));
      if (fm.status !== 'done') continue;
      const rel = `${kind}/${n}`;
      if (!blocked.has(rel)) result.push(rel);
    }
  }
  return sortCp(result);
}
function archivableObsolete(deck) {
  const result = [];
  for (const kind of sortCp([...KNOWLEDGE_KINDS])) {
    const folder = path.join(deck, kind);
    if (!isDir(folder)) continue;
    for (const p of walkMd(folder)) {
      if (path.basename(p) === 'INDEX.md') continue;
      if (fmOf(p).status === 'obsolete') result.push(relPosix(deck, p));
    }
  }
  return sortCp(result);
}
function specAdvanceCandidates(deck) {
  const plans = path.join(deck, 'plans');
  if (!isDir(plans)) return [];
  const bySpec = new Map();
  for (const n of sortCp(mdNames(plans).filter((x) => x !== 'INDEX.md'))) {
    const fm = fmOf(path.join(plans, n));
    const target = fm.implements;
    if (target) {
      const key = String(target).trim();
      if (!bySpec.has(key)) bySpec.set(key, new Set());
      bySpec.get(key).add(fm.status || '');
    }
  }
  const result = [];
  for (const [specRel, statuses] of bySpec) {
    const specPath = path.join(deck, specRel);
    if (!isFile(specPath)) continue;
    if (fmOf(specPath).status !== 'active') continue;
    if (statuses.has('done') && [...statuses].every((s) => s === 'done')) result.push(specRel);
  }
  return sortCp(result);
}
function verifyPending(deck) {
  const out = [];
  for (const p of walkMd(deck)) {
    if (path.basename(p) === 'INDEX.md') continue;
    let v;
    try { v = parseFrontmatter(readText(p)).verify; } catch { continue; }
    if (v) out.push([relPosix(deck, p), v]);
  }
  // Python sorts tuples: by path then note. Both are strings.
  return out.sort((a, b) => (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : a[1] < b[1] ? -1 : a[1] > b[1] ? 1 : 0));
}

// ── git ──────────────────────────────────────────────────────────────────────
function git(deck, args) {
  return execFileSync('git', ['-C', deck, ...args], { encoding: 'utf8' });
}
function lastAnchorRef(deck) {
  try {
    const out = git(deck, ['log', '-1', '--grep=Flightdeck-Sync', '--format=%H']).trim();
    return out || null;
  } catch { return null; }
}
function changedSinceAnchor(deck) {
  const anchor = lastAnchorRef(deck);
  const paths = new Set();
  try {
    const cmds = [['status', '--porcelain']];
    if (anchor) cmds.push(['diff', '--name-only', `${anchor}..HEAD`]);
    for (const cmd of cmds) {
      const out = git(deck, cmd);
      for (const line of out.split('\n')) {
        const p = cmd[0] === 'status' ? line.slice(3).trim() : line.trim();
        if (p) paths.add(p);
      }
    }
  } catch { return []; }
  return sortCp([...paths]);
}

// ── shared-knowledge sync / consumers ────────────────────────────────────────
function resolveMasterRoot() {
  const root = path.join(os.homedir(), '.flightdeck');
  return isDir(root) ? root : null;
}
function normDeck(p) {
  let r;
  try { r = fs.realpathSync(p); } catch { r = path.resolve(p); }
  return r.split(path.sep).join('/');
}
function readConsumers(fm) {
  const raw = fm.consumers;
  if (!raw) return [];
  let val;
  try { val = JSON.parse(raw); } catch { return []; }
  return Array.isArray(val) ? val.map((x) => String(x)) : [];
}
function writeConsumersLine(text, consumers) {
  const payload = pyJsonArray(sortCp([...new Set(consumers)]));
  const lines = text.split(/(?<=\n)/); // keepends
  let end = null;
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].trim() === '---') { end = i; break; }
  }
  if (end === null) return text;
  for (let i = 1; i < end; i++) {
    if (lines[i].split(':', 1)[0].trim() === 'consumers') {
      lines[i] = `consumers: ${payload}\n`;
      return lines.join('');
    }
  }
  lines.splice(end, 0, `consumers: ${payload}\n`);
  return lines.join('');
}
function registerConsumer(masterRoot, relpath, deck) {
  const target = path.join(masterRoot, relpath);
  if (!isFile(target)) throw new Error(`not a master file: ${relpath}`);
  const text = readText(target);
  const consumers = readConsumers(parseFrontmatter(text));
  consumers.push(normDeck(deck));
  writeText(target, writeConsumersLine(text, consumers));
  return true;
}
function listConsumers(masterRoot) {
  const seen = new Set();
  for (const p of walkMd(masterRoot)) {
    const rel = relPosix(masterRoot, p);
    if (path.basename(p) === 'INDEX.md' || rel.split('/').includes('archive')) continue;
    let fm;
    try { fm = parseFrontmatter(readText(p)); } catch { continue; }
    for (const c of readConsumers(fm)) seen.add(normDeck(c));
  }
  return sortCp([...seen].filter((c) => isDir(c)));
}
function pruneConsumers(masterRoot) {
  const removed = [];
  for (const p of walkMd(masterRoot)) {
    const relp = relPosix(masterRoot, p);
    if (path.basename(p) === 'INDEX.md' || relp.split('/').includes('archive')) continue;
    let text;
    try { text = readText(p); } catch { continue; }
    const consumers = readConsumers(parseFrontmatter(text));
    if (!consumers.length) continue;
    const kept = [];
    for (const c of consumers) {
      const parentDir = isDir(path.dirname(c));
      let exists = false;
      try { fs.lstatSync(c); exists = true; } catch { exists = false; }
      const confirmedGone = parentDir && !fs.existsSync(c) && !exists;
      if (confirmedGone) removed.push([relPosix(masterRoot, p), c]);
      else kept.push(c);
    }
    if (kept.length !== consumers.length) writeText(p, writeConsumersLine(text, kept));
  }
  return removed;
}
function syncStatus(deck) {
  const masterRoot = resolveMasterRoot();
  const masterOk = masterRoot !== null;
  const out = [];
  for (const p of walkMd(deck)) {
    const rel = relPosix(deck, p);
    if (path.basename(p) === 'INDEX.md' || rel.split('/').includes('archive')) continue;
    let fm;
    try { fm = parseFrontmatter(readText(p)); } catch { continue; }
    if (String(fm.synced || '').trim().toLowerCase() !== 'true') continue;
    if (!masterOk) { out.push(['master-missing', rel]); continue; }
    const masterFile = path.join(masterRoot, rel);
    if (!isFile(masterFile)) { out.push(['dangling', rel]); continue; }
    const projLu = fm.last_updated || '';
    const mastLu = parseFrontmatter(readText(masterFile)).last_updated || '';
    let state;
    if (mastLu > projLu) state = 'upstream-changed';
    else if (mastLu < projLu) state = 'locally-ahead';
    else state = 'in-sync';
    out.push([state, rel]);
  }
  return out.sort((a, b) => (a[1] < b[1] ? -1 : a[1] > b[1] ? 1 : 0));
}

// ── INDEX targets / drift ────────────────────────────────────────────────────
function* indexTargets(deck) {
  for (const name of REGEN_FOLDERS) {
    const folder = path.join(deck, name);
    if (isDir(folder)) {
      yield [name, path.join(folder, 'INDEX.md'), regenFolderIndex(folder)];
      if (NESTABLE_KINDS.has(name)) {
        for (const area of sortPaths(subDirs(folder))) {
          if (isFile(path.join(area, 'INDEX.md')) || mdNames(area).length) {
            yield [`${name}/${path.basename(area)}`, path.join(area, 'INDEX.md'), regenFolderIndex(area)];
          }
        }
      }
    }
  }
  const cockpit = path.join(deck, 'cockpit.md');
  if (isFile(cockpit) && readText(cockpit).includes('<!-- AUTO:inprogress -->')) {
    yield ['cockpit', cockpit, regenCockpitInprogress(deck)];
  }
}
function indexDrift(deck) {
  const labels = [];
  for (const [label, p, newBlock] of indexTargets(deck)) {
    let curBlock;
    try {
      const current = readText(p);
      const s = current.indexOf('<!-- AUTO:');
      const e = current.indexOf(AUTO_END);
      if (s === -1 || e === -1) throw new Error('no auto');
      curBlock = current.slice(s, e + AUTO_END.length);
    } catch { labels.push(label); continue; }
    if (curBlock !== newBlock) labels.push(label);
  }
  return labels;
}

// ── CLI ──────────────────────────────────────────────────────────────────────
function parseArgs(argv) {
  const a = {
    deck: null, check: false, archivable: false, advanceCandidates: false,
    matchSignature: null, sigErrorType: '', changedSinceAnchor: false,
    verifyPending: false, syncStatus: false, registerConsumer: null,
    listConsumers: false, pruneConsumers: false,
  };
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (t === '--check') a.check = true;
    else if (t === '--archivable') a.archivable = true;
    else if (t === '--advance-candidates') a.advanceCandidates = true;
    else if (t === '--match-signature') a.matchSignature = argv[++i];
    else if (t === '--sig-error-type') a.sigErrorType = argv[++i];
    else if (t === '--changed-since-anchor') a.changedSinceAnchor = true;
    else if (t === '--verify-pending') a.verifyPending = true;
    else if (t === '--sync-status') a.syncStatus = true;
    else if (t === '--register-consumer') a.registerConsumer = [argv[++i], argv[++i]];
    else if (t === '--list-consumers') a.listConsumers = true;
    else if (t === '--prune-consumers') a.pruneConsumers = true;
    else if (a.deck === null) a.deck = t;
  }
  return a;
}

function main(argv) {
  const args = parseArgs(argv);
  const out = [];
  const deck = args.deck;

  if (args.archivable) {
    for (const rel of sortCp([...new Set([...archivableDone(deck), ...archivableObsolete(deck)])])) out.push(rel);
    process.stdout.write(out.length ? out.join('\n') + '\n' : '');
    return 0;
  }
  if (args.advanceCandidates) {
    for (const rel of specAdvanceCandidates(deck)) out.push(rel);
    process.stdout.write(out.length ? out.join('\n') + '\n' : '');
    return 0;
  }
  if (args.matchSignature !== null) {
    for (const h of matchSignature(deck, args.matchSignature, args.sigErrorType)) {
      out.push(`${h.status}\t${h.path}`);
    }
    process.stdout.write(out.length ? out.join('\n') + '\n' : '');
    return 0;
  }
  if (args.changedSinceAnchor) {
    for (const p of changedSinceAnchor(deck)) out.push(p);
    process.stdout.write(out.length ? out.join('\n') + '\n' : '');
    return 0;
  }
  if (args.verifyPending) {
    for (const [p, note] of verifyPending(deck)) out.push(`${p}\t${note}`);
    process.stdout.write(out.length ? out.join('\n') + '\n' : '');
    return 0;
  }
  if (args.syncStatus) {
    for (const [state, p] of syncStatus(deck)) out.push(`${state}\t${p}`);
    process.stdout.write(out.length ? out.join('\n') + '\n' : '');
    return 0;
  }
  if (args.registerConsumer !== null) {
    const [deckArg, rel] = args.registerConsumer;
    try {
      registerConsumer(deck, rel, deckArg);
      process.stdout.write(`registered\t${normDeck(deckArg)}\t${rel}\n`);
      return 0;
    } catch (e) {
      process.stderr.write(`register failed: ${e.message}\n`);
      return 1;
    }
  }
  if (args.listConsumers) {
    for (const c of listConsumers(deck)) out.push(c);
    process.stdout.write(out.length ? out.join('\n') + '\n' : '');
    return 0;
  }
  if (args.pruneConsumers) {
    for (const [rel, c] of pruneConsumers(deck)) out.push(`pruned\t${rel}\t${c}`);
    process.stdout.write(out.length ? out.join('\n') + '\n' : '');
    return 0;
  }

  const drift = [];
  for (const [label, p, newBlock] of indexTargets(deck)) {
    let current = null;
    let curBlock = null;
    try {
      current = readText(p);
      const s = current.indexOf('<!-- AUTO:');
      const e = current.indexOf(AUTO_END);
      if (s === -1 || e === -1) throw new Error('no auto');
      curBlock = current.slice(s, e + AUTO_END.length);
    } catch {
      drift.push(label);
      if (!args.check) writeText(p, `# ${label} — INDEX\n\n${newBlock}\n`);
      continue;
    }
    if (curBlock === newBlock) continue;
    drift.push(label);
    if (!args.check) writeText(p, replaceAutoBlock(current, newBlock));
  }

  if (args.check) {
    process.stdout.write((drift.length ? 'DRIFT: ' + drift.join(', ') : 'clean') + '\n');
    return drift.length ? 1 : 0;
  }
  process.stdout.write((drift.length ? 'regenerated: ' + drift.join(', ') : 'already clean') + '\n');
  return 0;
}

if (require.main === module) {
  process.exit(main(process.argv.slice(2)));
}

module.exports = {
  main,
  parseFrontmatter, formatRow, regenFolderIndex, regenCockpitInprogress,
  indexDrift, indexTargets, matchSignature, archivableDone, archivableObsolete,
  specAdvanceCandidates, verifyPending, syncStatus, listConsumers, pruneConsumers,
  KNOWLEDGE_KINDS, IMPORTED_KINDS, NESTABLE_KINDS, SUMMARY_KINDS,
  readText, writeText, relPosix, isDir, isFile, mdNames, walkMd, subDirs, sortPaths,
};
