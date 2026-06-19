#!/usr/bin/env node
'use strict';
// flightdeck_new — create a deck artifact with correct frontmatter + naming +
// INDEX/cockpit regen. Node port of flightdeck_new.py; byte-parity with the
// reference. Built-ins only, zero npm deps.

const fs = require('fs');
const path = require('path');
const idx = require('./flightdeck_index');

const KIND_FOLDER = {
  spec: 'specs', plan: 'plans', incident: 'incidents',
  checklist: 'checklists', reference: 'references', doc: 'docs',
};
const WORKFLOW = new Set(['spec', 'plan']);
const KNOWLEDGE = new Set(['incident', 'checklist', 'reference', 'doc']);
const DATELESS = KNOWLEDGE; // knowledge is always <slug>.md (standing reference, not a log)
const SLUG_RE = /^[a-z0-9-]+$/;
const DEFAULT_STATUS = {
  spec: 'idea', plan: 'idea',
  incident: 'active', checklist: 'active', reference: 'active', doc: 'active',
};

const INCIDENT_BODY = (title) =>
  `# ${title}

## Signature
- symptom: \`<error text / observable symptom>\`
- error_type: <exception type/error code or —>
- where: <function/file/subsystem>
- trigger: <what action/scenario triggers it>

## Symptom / repro

## Root cause

## Fix

## Cases
- YYYY-MM-DD first seen
`;

function todayIso() {
  // LOCAL date — must match Python's datetime.date.today().isoformat() for
  // py/js parity. toISOString() is UTC and diverges by a day across the
  // local/UTC midnight window (see incidents/new-default-date-local-vs-utc.md).
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

function frontmatter(kind, status, date, summary, implementsField, whenToRead, appliesTo) {
  const lines = ['---', `status: ${status}`];
  if (WORKFLOW.has(kind)) {
    if (summary) lines.push(`summary: ${summary}`);
    if (status !== 'idea') lines.push(`last_updated: ${date}`);
    if (implementsField) lines.push(`implements: ${implementsField}`);
  } else {
    if (summary) lines.push(`summary: ${summary}`);
    lines.push(`when_to_read: ${whenToRead}`);
    lines.push(`applies_to: [${appliesTo.join(', ')}]`);
    lines.push(`last_updated: ${date}`);
    if (kind === 'incident') lines.push('resolved_by:');
  }
  lines.push('---');
  return lines.join('\n');
}

function bodyScaffold(kind, title) {
  if (kind === 'incident') return INCIDENT_BODY(title);
  return `# ${title}\n`;
}

function vErr(msg) {
  const e = new Error(msg);
  e.code = 'REFUSE';
  return e;
}

function newArtifact(deck, kind, slug, title, opts = {}) {
  const { status = null, summary = '', implements: implementsField = null,
    whenToRead = null, appliesTo = null, date = null, regen = true } = opts;
  if (!(kind in KIND_FOLDER)) {
    throw vErr(`unknown kind: '${kind}' (one of: ${Object.keys(KIND_FOLDER).sort().join(', ')})`);
  }
  if (!slug || !SLUG_RE.test(slug)) {
    throw vErr(`illegal slug: '${slug}' — must match ^[a-z0-9-]+$ ` +
      '(lowercase ascii / digits / hyphens, e.g. new-artifact-entrypoint)');
  }
  if (!title) throw vErr('title is required');
  if (WORKFLOW.has(kind) && !summary) {
    throw vErr(`${kind} requires --summary (drives the INDEX row; required by flightdeck_index)`);
  }
  if (KNOWLEDGE.has(kind) && (!whenToRead || !appliesTo)) {
    throw vErr(`${kind} requires --when-to-read and --applies-to (required routing fields)`);
  }
  if (implementsField && !WORKFLOW.has(kind)) {
    throw vErr(`--implements is workflow-only; not valid for kind '${kind}'`);
  }

  const theDate = date || todayIso();
  const theStatus = status || DEFAULT_STATUS[kind];

  const folder = path.join(deck, KIND_FOLDER[kind]);
  const filename = theStatus === 'idea' || DATELESS.has(kind) ? `${slug}.md` : `${theDate}-${slug}.md`;
  const filePath = path.join(folder, filename);
  if (fs.existsSync(filePath)) throw vErr(`artifact already exists: ${filePath}`);

  const fm = frontmatter(kind, theStatus, theDate, summary, implementsField, whenToRead, appliesTo);
  const body = bodyScaffold(kind, title);
  fs.mkdirSync(folder, { recursive: true });
  fs.writeFileSync(filePath, `${fm}\n\n${body}`, 'utf8');

  if (regen) idx.main([deck]);
  return filePath;
}

function main(argv) {
  const a = { deck: null, kind: null, slug: null, title: null, status: null,
    summary: '', implements: null, whenToRead: null, appliesTo: null, date: null };
  const pos = [];
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (t === '--slug') a.slug = argv[++i];
    else if (t === '--title') a.title = argv[++i];
    else if (t === '--status') a.status = argv[++i];
    else if (t === '--summary') a.summary = argv[++i];
    else if (t === '--implements') a.implements = argv[++i];
    else if (t === '--when-to-read') a.whenToRead = argv[++i];
    else if (t === '--applies-to') a.appliesTo = argv[++i];
    else if (t === '--date') a.date = argv[++i];
    else pos.push(t);
  }
  a.deck = pos[0];
  a.kind = pos[1];
  const applies = a.appliesTo ? a.appliesTo.split(',').map((s) => s.trim()) : null;
  let filePath;
  try {
    filePath = newArtifact(a.deck, a.kind, a.slug, a.title, {
      status: a.status, summary: a.summary, implements: a.implements,
      whenToRead: a.whenToRead, appliesTo: applies, date: a.date,
    });
  } catch (e) {
    if (e.code === 'REFUSE') { process.stdout.write(`refused: ${e.message}\n`); return 2; }
    throw e;
  }
  const status = a.status || DEFAULT_STATUS[a.kind];
  process.stdout.write(`created ${a.kind} at ${filePath}\n`);
  if (WORKFLOW.has(a.kind) && status === 'idea') {
    process.stdout.write('INDEX updated; cockpit unchanged (status=idea)\n');
  } else if (WORKFLOW.has(a.kind)) {
    process.stdout.write('INDEX + cockpit (## In Progress) updated\n');
  } else {
    process.stdout.write('folder INDEX updated\n');
  }
  return 0;
}

if (require.main === module) {
  process.exit(main(process.argv.slice(2)));
}

module.exports = { newArtifact, main };
