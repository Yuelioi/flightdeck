'use strict';
// flightdeck Node port — shared helpers, byte-parity with the Python reference.
// These are the landmine helpers (spec §3.3): code-point sort vs UTF-16, the two
// JSON escaping regimes Python uses, sha1-over-UTF-8, frontmatter parse. Every
// export is unit-parity-tested against its Python twin in
// scripts/tests/test_flightdeck_lib_parity.py. Built-ins only, zero npm deps.

const crypto = require('crypto');

const DASH = '—'; // em dash —, the INDEX row delimiter

// ── sorting ────────────────────────────────────────────────────────────────
// Python sorted() compares by Unicode CODE POINT. JS default Array.sort and the
// `<` operator compare by UTF-16 code UNIT, which diverges on non-BMP. Iterate
// code points (Array.from splits on them) to match Python exactly.
function cmpCodepoint(a, b) {
  const ai = Array.from(a);
  const bi = Array.from(b);
  const n = Math.min(ai.length, bi.length);
  for (let i = 0; i < n; i++) {
    const x = ai[i].codePointAt(0);
    const y = bi[i].codePointAt(0);
    if (x !== y) return x < y ? -1 : 1;
  }
  return ai.length - bi.length;
}
const sortCp = (arr) => [...arr].sort(cmpCodepoint);

// ── JSON, the two Python regimes ─────────────────────────────────────────────
// (1) Python `json.dumps(str)` default = ensure_ascii=True → non-ASCII escaped
// to \uXXXX (surrogate pairs for astral). Used by the consumers: line. Iterate
// code UNITS (charCodeAt) so an astral char emits its two \uXXXX halves exactly
// like Python.
function pyStr(s) {
  const base = JSON.stringify(s); // double-quoted, escapes control + " + backslash
  let out = '';
  for (let i = 0; i < base.length; i++) {
    const code = base.charCodeAt(i);
    out += code >= 0x80 ? '\\u' + code.toString(16).padStart(4, '0') : base[i];
  }
  return out;
}
// json.dumps(list_of_str) with default separators (", ", ": ") → ["a", "b"]
function pyJsonArray(items) {
  return '[' + items.map(pyStr).join(', ') + ']';
}

// (2) Python `json.dumps(obj, ensure_ascii=False, indent=2)` — non-ASCII literal,
// 2-space indent, item sep ",", key sep ": ", empty containers compact. JS
// JSON.stringify(v, null, 2) matches this byte-for-byte for the lint findings
// shape (insertion key order preserved on both sides). Verified by the lib
// parity suite; kept as a named export so callers state intent.
function pyJsonIndent(value) {
  return JSON.stringify(value, null, 2);
}

// Python list repr — `str(sorted(set))` → ['a', 'b'] with SINGLE quotes. Used in
// lint messages (e.g. "legal: ['node', 'python', 'uv']"), NOT json double quotes.
function pyListRepr(items) {
  return '[' + items.map((s) => "'" + s + "'").join(', ') + ']';
}

// ── fingerprint ──────────────────────────────────────────────────────────────
function fingerprint(key) {
  return crypto.createHash('sha1').update(key, 'utf8').digest('hex').slice(0, 12);
}

// Volatile-token scrubbing for incident signatures (mirrors flightdeck_index._VOLATILE).
// JS \w/\d are ASCII (Python's are Unicode); error strings are ASCII in practice.
const VOLATILE = [
  [/\b[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}\b/g, '_UUID_'],
  [/0x[0-9a-fA-F]+/g, '_HEX_'],
  [/\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}:\d{2}\S*)?/g, '_TIME_'],
  [/[A-Za-z]:\\[^\s:]+|(?:\/[\w.\-]+){2,}/g, '_PATH_'],
  [/\bline\s+\d+\b/gi, 'line _N_'],
  [/\b\d{4,}\b/g, '_N_'],
];
function normalizeSymptom(s) {
  let out = (s || '').trim();
  for (const [pat, repl] of VOLATILE) out = out.replace(pat, repl);
  return out.replace(/\s+/g, ' ').trim();
}
function signatureFingerprint(symptom, errorType = '') {
  const key = `${(errorType || '').trim()}\n${normalizeSymptom(symptom)}`;
  return fingerprint(key);
}

// ── frontmatter ──────────────────────────────────────────────────────────────
// Mirrors flightdeck_index.parse_frontmatter: leading ---fenced block, one
// `key: value` per line (first colon splits, both sides trimmed), {} when absent.
// Python uses str.splitlines() which splits on \n AND \r; we strip \r first so
// CRLF files behave identically.
function parseFrontmatter(text) {
  const lines = text.replace(/\r\n?/g, '\n').split('\n');
  if (!lines.length || lines[0].trim() !== '---') return {};
  const fm = {};
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].trim() === '---') break;
    const idx = lines[i].indexOf(':');
    if (idx !== -1) fm[lines[i].slice(0, idx).trim()] = lines[i].slice(idx + 1).trim();
  }
  return fm;
}

module.exports = {
  DASH,
  cmpCodepoint,
  sortCp,
  pyStr,
  pyJsonArray,
  pyJsonIndent,
  pyListRepr,
  fingerprint,
  normalizeSymptom,
  signatureFingerprint,
  parseFrontmatter,
};
