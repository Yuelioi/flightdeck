#!/usr/bin/env node
'use strict';
// flightdeck deck initializer — Node port of flightdeck_init.py. Copies the
// full-layout scaffold verbatim into <target>/flightdeck/ and seeds cockpit.md.
// Byte-parity with the Python reference; built-ins only, zero npm deps.

const fs = require('fs');
const path = require('path');

const SCAFFOLD = path.join(__dirname, '..', 'scaffolds', 'full', 'flightdeck');

const ACTIVE = '<FOCUS — one coarse thread label + spec/plan link, filled by preflight first-time-setup>';
const NEXT = '<FIRST_NEXT_ITEM — single concrete action + plan link, filled by preflight first-time-setup>';

function init(target, name, user, date, focus, nextItem) {
  const deck = path.join(target, 'flightdeck');
  if (fs.existsSync(path.join(deck, 'cockpit.md'))) {
    const err = new Error(`deck already exists: ${path.join(deck, 'cockpit.md')}`);
    err.code = 'EEXIST_DECK';
    throw err;
  }
  fs.cpSync(SCAFFOLD, deck, { recursive: true });

  const cockpit = path.join(deck, 'cockpit.md');
  let text = fs.readFileSync(cockpit, 'utf8').replace(/\r\n?/g, '\n');
  text = text.split('[project name]').join(name);
  text = text.split('YYYY-MM-DD · [who] · Stage: `<lifecycle stage>`').join(`${date} · ${user} · Stage: deck initialized`);
  text = text.split(ACTIVE).join(focus);
  text = text.split(NEXT).join(nextItem);
  fs.writeFileSync(cockpit, text, 'utf8');
  return deck;
}

function todayIso() {
  // LOCAL date — must match Python's datetime.date.today().isoformat() for
  // py/js parity. toISOString() is UTC and diverges by a day across the
  // local/UTC midnight window (see incidents/new-default-date-local-vs-utc.md).
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

function main(argv) {
  const a = { target: '.', name: null, user: 'unknown', date: null, focus: '(set me)', nextItem: '(set me)' };
  let sawTarget = false;
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (t === '--name') a.name = argv[++i];
    else if (t === '--user') a.user = argv[++i];
    else if (t === '--date') a.date = argv[++i];
    else if (t === '--focus') a.focus = argv[++i];
    else if (t === '--next') a.nextItem = argv[++i];
    else if (!sawTarget) { a.target = t; sawTarget = true; }
  }
  const name = a.name || path.basename(path.resolve(a.target));
  const date = a.date || todayIso();
  let deck;
  try {
    deck = init(a.target, name, a.user, date, a.focus, a.nextItem);
  } catch (e) {
    if (e.code === 'EEXIST_DECK') {
      process.stdout.write(`refused: ${e.message}\n`);
      return 2;
    }
    throw e;
  }
  process.stdout.write(`created deck at ${deck} (full layout, 2-file contract)\n`);
  return 0;
}

if (require.main === module) {
  process.exit(main(process.argv.slice(2)));
}

module.exports = { init, main };
