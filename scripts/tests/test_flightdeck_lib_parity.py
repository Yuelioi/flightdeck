"""Unit parity for flightdeck_lib.js helpers vs their Python twins.

Shells `node -e` to call each helper and compares to the Python reference. The
landmine helpers (code-point sort, the two json escaping regimes, sha1, the
signature fingerprint, frontmatter parse) are locked here before any script
leans on them. Skips when node is absent.
"""
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from flightdeck_index import signature_fingerprint, parse_frontmatter

LIB = Path(__file__).resolve().parent.parent / "flightdeck_lib.js"
HAVE_NODE = shutil.which("node") is not None


def node_eval(expr):
    js = f"const L=require({json.dumps(str(LIB))});process.stdout.write(String({expr}));"
    p = subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0:
        raise AssertionError(p.stderr)
    return p.stdout


@unittest.skipUnless(HAVE_NODE, "node not on PATH")
class LibParity(unittest.TestCase):
    def test_sort_codepoint(self):
        items = ["b", "a", "Z", "é", "\U0001F600x", "ab", "aa", "中", "0"]
        py = sorted(items)
        js = json.loads(node_eval(f"JSON.stringify(L.sortCp({json.dumps(items)}))"))
        self.assertEqual(py, js)

    def test_py_json_array_ascii(self):
        items = sorted({"/x", "/a", "/a"})
        py = json.dumps(items)  # ensure_ascii=True default
        js = node_eval(f"L.pyJsonArray({json.dumps(items)})")
        self.assertEqual(py, js)

    def test_py_json_array_non_ascii_escaped(self):
        # the consumers: line uses json.dumps default (ensure_ascii=True): escape
        items = ["/路径/a", "/b\U0001F600"]
        py = json.dumps(items)
        js = node_eval(f"L.pyJsonArray({json.dumps(items)})")
        self.assertEqual(py, js)

    def test_fingerprint(self):
        py = signature_fingerprint("boom\nbang  x", "KeyError")
        js = node_eval('L.signatureFingerprint("boom\\nbang  x", "KeyError")')
        self.assertEqual(py, js)

    def test_fingerprint_empty_error_type(self):
        py = signature_fingerprint("boom", "")
        js = node_eval('L.signatureFingerprint("boom", "")')
        self.assertEqual(py, js)

    def test_frontmatter(self):
        txt = "---\nversion: 3.0\nruntime: uv\nconsumers: [\"/a\", \"/b\"]\n---\nbody\n"
        py = parse_frontmatter(txt)
        js = json.loads(node_eval(f"JSON.stringify(L.parseFrontmatter({json.dumps(txt)}))"))
        self.assertEqual(py, js)

    def test_frontmatter_absent(self):
        txt = "no frontmatter here\n"
        py = parse_frontmatter(txt)
        js = json.loads(node_eval(f"JSON.stringify(L.parseFrontmatter({json.dumps(txt)}))"))
        self.assertEqual(py, js)

    def test_py_json_indent(self):
        obj = {"findings": [{"audit": "status", "severity": "CRITICAL",
                             "path": "x/y.md", "message": "缺 status 字段"}]}
        py = json.dumps(obj, ensure_ascii=False, indent=2)
        js = node_eval(f"L.pyJsonIndent({json.dumps(obj)})")
        self.assertEqual(py, js)

    def test_py_json_indent_empty(self):
        obj = {"findings": []}
        py = json.dumps(obj, ensure_ascii=False, indent=2)
        js = node_eval(f"L.pyJsonIndent({json.dumps(obj)})")
        self.assertEqual(py, js)

    def test_py_list_repr(self):
        items = sorted({"uv", "python", "node"})
        py = str(items)  # Python list repr: ['node', 'python', 'uv']
        js = node_eval(f"L.pyListRepr({json.dumps(items)})")
        self.assertEqual(py, js)


if __name__ == "__main__":
    unittest.main()
