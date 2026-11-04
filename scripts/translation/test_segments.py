"""Tests for the line-level translation pipeline (extract / apply / check)."""

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import apply_segments
import check_prompts
import extract_segments

LIB = "skills/code-animation-prompts/assets/library"
SP = LIB + "/style-prompts"
AG = SP + "/A-G_code-samples"


def git(root, *args):
    return subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.quotepath=off",
         "-C", str(root), *args],
        check=True, capture_output=True, encoding="utf-8").stdout


class Repo:
    """Temporary git repo; files are written as bytes and tracked."""

    def __init__(self, test):
        self._td = tempfile.TemporaryDirectory()
        test.addCleanup(self._td.cleanup)
        self.root = Path(self._td.name)
        git(self.root, "init", "-q")

    def write(self, rel, data, track=True):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
        if track:
            git(self.root, "add", "-f", rel)
        return p

    def read(self, rel):
        return (self.root / rel).read_bytes()

    def commit(self):
        git(self.root, "commit", "-q", "-m", "x")
        return git(self.root, "rev-parse", "HEAD").strip()

    def segments(self, batch):
        p = self.root / ".build/translation/segments" / (batch + ".json")
        return json.loads(p.read_text(encoding="utf-8"))

    def put_out(self, batch, obj):
        p = self.root / ".build/translation/out" / (batch + ".json")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def run(main, argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


def extract(repo):
    return run(extract_segments.main, ["--root", str(repo.root)])


def apply(repo, batch, *extra):
    return run(apply_segments.main, [batch, "--root", str(repo.root), *extra])


class ExtractTests(unittest.TestCase):
    def test_segments_lines_codes_and_endings(self):
        r = Repo(self)
        text = ("# 标题\r\nplain\r\n```js\r\n// 注释\r\nlet a = 1;\r\n```\r\n"
                "~~~\nx 中\n~~~\nlast 文")
        r.write(AG + "/A1_x.md", text)
        code, out, _ = extract(r)
        self.assertEqual(code, 0)
        seg = r.segments("ag-z")[AG + "/A1_x.md"]
        self.assertEqual(
            seg,
            {"1": {"text": "# 标题", "code": False},
             "4": {"text": "// 注释", "code": True},
             "8": {"text": "x 中", "code": True},
             "10": {"text": "last 文", "code": False}})

    def test_longer_fence_not_closed_by_shorter(self):
        r = Repo(self)
        r.write(AG + "/A1_x.md", "````\n```\n中\n````\n外 中\n")
        extract(r)
        seg = r.segments("ag-z")[AG + "/A1_x.md"]
        self.assertTrue(seg["3"]["code"])
        self.assertFalse(seg["5"]["code"])

    def test_js_file_is_code(self):
        r = Repo(self)
        r.write(AG + "/_shared-functions.js", "// 共享\nlet a;\n")
        extract(r)
        self.assertEqual(r.segments("ag-z")[AG + "/_shared-functions.js"]["1"],
                         {"text": "// 共享", "code": True})

    def test_scope_and_batches(self):
        r = Repo(self)
        files = {
            AG + "/A1_a.md": "中", SP + "/Z_chinese-style/Z1_a.md": "中",
            SP + "/K_cartoon-styles/K1_a.md": "中", SP + "/H_ready-made-layouts/H1_a.md": "中",
            SP + "/L_Lemo-Opuscar/L1_a.md": "中", SP + "/M_motion-styles/M1_a.md": "中",
            SP + "/V_mg-styles-15/V1_a.md": "中", SP + "/X_code-video/X1_a.md": "中",
            SP + "/R_learned-from-references/R1_a.md": "中",
            LIB + "/README.md": "中", LIB + "/examples/B6/prompt.md": "中",
            LIB + "/licenses-and-sources.md": "中",
        }
        for k, v in files.items():
            r.write(k, v)
        # out of scope
        r.write(LIB + "/style-picker.html", "中")
        r.write(LIB + "/third-party-licenses/MIT.md", "中")
        r.write(LIB + "/examples/B6/a.html", "中")
        r.write(LIB + "/_stats.json", "中")
        r.write(AG + "/untracked.md", "中", track=False)
        r.write(AG + "/A9_nochinese.md", "plain English only\n")
        extract(r)
        got = {}
        for b in ["ag-z", "k-h", "l", "m", "v-x-r", "o1", "o2", "library-docs"]:
            for f in r.segments(b):
                self.assertNotIn(f, got, "file in two batches")
                got[f] = b
        self.assertEqual(set(got), set(files))
        self.assertEqual(got[AG + "/A1_a.md"], "ag-z")
        self.assertEqual(got[SP + "/Z_chinese-style/Z1_a.md"], "ag-z")
        self.assertEqual(got[SP + "/K_cartoon-styles/K1_a.md"], "k-h")
        self.assertEqual(got[SP + "/H_ready-made-layouts/H1_a.md"], "k-h")
        self.assertEqual(got[SP + "/L_Lemo-Opuscar/L1_a.md"], "l")
        self.assertEqual(got[SP + "/M_motion-styles/M1_a.md"], "m")
        for f in ("V_mg-styles-15/V1", "X_code-video/X1", "R_learned-from-references/R1"):
            self.assertEqual(got[SP + "/" + f + "_a.md"], "v-x-r")
        self.assertEqual(got[LIB + "/README.md"], "library-docs")
        self.assertEqual(got[LIB + "/examples/B6/prompt.md"], "library-docs")

    def test_o_split_numeric_order_and_even_chars(self):
        r = Repo(self)
        o = SP + "/O_98-best-picture-winners/"
        sizes = {2: 10, 10: 10, 1: 10, 3: 10}   # numeric order 1,2,3,10
        for n, c in sizes.items():
            r.write(o + "O%d_x.md" % n, "中" * c + "\n")
        extract(r)
        o1 = [Path(f).name for f in r.segments("o1")]
        o2 = [Path(f).name for f in r.segments("o2")]
        self.assertEqual(o1, ["O1_x.md", "O2_x.md"])
        self.assertEqual(o2, ["O3_x.md", "O10_x.md"])

    def test_summary_and_table(self):
        r = Repo(self)
        r.write(AG + "/A1_a.md", "中文\n```\n码\n```\nok\n")
        code, out, _ = extract(r)
        s = json.loads((r.root / ".build/translation/segments/_summary.json").read_text())
        self.assertEqual(s["ag-z"]["files"], 1)
        self.assertEqual(s["ag-z"]["segments"], 2)
        self.assertEqual(s["ag-z"]["chars"], 3)
        self.assertEqual(s["ag-z"]["code_segments"], 1)
        self.assertEqual(s["o1"]["files"], 0)
        self.assertIn("ag-z", out)
        self.assertIn("library-docs", out)


class ApplyTests(unittest.TestCase):
    F = AG + "/A1_a.md"

    def setUp(self):
        self.r = Repo(self)

    def prep(self, data):
        self.r.write(self.F, data)
        extract(self.r)

    def test_roundtrip_crlf_lf_no_final_newline(self):
        data = "keep\r\n中一\r\nmid\n中二\nend 中三".encode()
        self.prep(data)
        self.r.put_out("ag-z", {self.F: {"2": "one", "4": "two", "5": "three"}})
        code, out, err = apply(self.r, "ag-z")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.r.read(self.F), b"keep\r\none\r\nmid\ntwo\nthree")

    def test_final_newline_kept(self):
        self.prep("a\n中\n")
        self.r.put_out("ag-z", {self.F: {"2": "b"}})
        self.assertEqual(apply(self.r, "ag-z")[0], 0)
        self.assertEqual(self.r.read(self.F), b"a\nb\n")

    def test_delete_lines(self):
        self.prep("a\r\n中\r\nb\r\n中2")
        self.r.put_out("ag-z", {self.F: {"2": None, "4": None}})
        self.assertEqual(apply(self.r, "ag-z")[0], 0)
        # deleted last line had no newline: no-final-newline state is preserved
        self.assertEqual(self.r.read(self.F), b"a\r\nb")

    def test_dry_run_writes_nothing(self):
        self.prep("a\n中\n")
        self.r.put_out("ag-z", {self.F: {"2": {"text": "中 ok", "keep": ["中"]}}})
        code, out, _ = apply(self.r, "ag-z", "--dry-run")
        self.assertEqual(code, 0)
        self.assertEqual(self.r.read(self.F), "a\n中\n".encode())
        self.assertFalse((self.r.root / ".build/translation/keep-literals.json").exists())

    def test_keep_literals_recorded_and_merged(self):
        self.prep("a\n中\n文\n")
        self.r.put_out("ag-z", {self.F: {"2": {"text": "say 中", "keep": ["中"]}, "3": "x"}})
        self.assertEqual(apply(self.r, "ag-z")[0], 0)
        kl = self.r.root / ".build/translation/keep-literals.json"
        self.assertEqual(json.loads(kl.read_text(encoding="utf-8")), {self.F: ["中"]})
        self.assertEqual(self.r.read(self.F), "a\nsay 中\nx\n".encode())
        # a second batch appends to, not replaces, the file
        kl.write_text(json.dumps({"other.md": ["字"]}, ensure_ascii=False), encoding="utf-8")
        self.r.write(self.F, "a\n中\n")
        extract(self.r)
        self.r.put_out("ag-z", {self.F: {"2": {"text": "中", "keep": ["中"]}}})
        self.assertEqual(apply(self.r, "ag-z")[0], 0)
        self.assertEqual(json.loads(kl.read_text(encoding="utf-8")),
                         {"other.md": ["字"], self.F: ["中"]})

    def test_refusals_list_every_problem_and_write_nothing(self):
        g = AG + "/A2_b.md"
        self.r.write(self.F, "中1\n中2\n中3\n中4\n中5\n")
        self.r.write(g, "中\n")
        extract(self.r)
        self.r.write(self.F, "中1\n中2 changed\n中3\n中4\n中5\n")  # drift after extraction
        self.r.put_out("ag-z", {
            self.F: {
                "1": "ok",                                    # fine
                "2": "fine but drifted",                      # file changed
                # "3" missing
                "4": "left 中 over",                          # residual Chinese
                "5": {"text": "abc", "keep": ["中"]},         # keep not in text
                "9": "ghost",                                 # unknown line
            },
            g: {"1": "full，width"},                      # fullwidth comma
            "nope.md": {"1": "x"},                            # unknown file
        })
        code, out, err = apply(self.r, "ag-z")
        self.assertNotEqual(code, 0)
        text = out + err
        for needle in ("A1_a.md:3", "missing", "A1_a.md:9", "A1_a.md:2", "changed",
                       "A1_a.md:4", "A1_a.md:5", "keep", "A2_b.md:1", "fullwidth", "nope.md"):
            self.assertIn(needle, text)
        self.assertEqual(self.r.read(self.F), "中1\n中2 changed\n中3\n中4\n中5\n".encode())
        self.assertEqual(self.r.read(g), "中\n".encode())

    def test_fullwidth_allowed_in_keep(self):
        self.prep("a\n中\n")
        self.r.put_out("ag-z", {self.F: {"2": {"text": "x，y", "keep": ["，"]}}})
        self.assertEqual(apply(self.r, "ag-z")[0], 0)

    def test_line_break_in_replacement_refused(self):
        self.prep("a\n中\n")
        self.r.put_out("ag-z", {self.F: {"2": "two\nlines"}})
        self.assertNotEqual(apply(self.r, "ag-z")[0], 0)

    def test_missing_out_file(self):
        self.prep("a\n中\n")
        self.assertNotEqual(apply(self.r, "ag-z")[0], 0)


class CheckTests(unittest.TestCase):
    """check_prompts compares against the upstream commit via path-map.json."""

    CN = SP + "/A-G_代码样片/A1_词雨.md"
    EN = AG + "/A1_word-rain.md"

    def build(self, upstream, current, cn=None, en=None):
        r = Repo(self)
        cn, en = cn or self.CN, en or self.EN
        r.write(cn, upstream)
        commit = r.commit()
        git(r.root, "rm", "-q", "--cached", cn)
        (r.root / cn).unlink()
        r.write(en, current)
        r.write("docs/translation/path-map.json",
                json.dumps({"upstream_commit": commit, "paths": {cn: en}}, ensure_ascii=False))
        return r

    def check(self, r, *files):
        return run(check_prompts.main, ["--root", str(r.root), *(files or (self.EN,))])

    def test_clean(self):
        up = "# 词\n宽 1920 高 0.5 {{ name }} https://a.com/x #FF00aa 12px\n```js\nx\n```\n"
        cur = "# Word\nwidth 1920 height 0.5 {{name}} https://a.com/x #ff00AA 12px\n```js\nx\n```\n"
        code, out, _ = self.check(self.build(up, cur))
        self.assertEqual(code, 0, out)

    def test_each_kind(self):
        up = ("词\n1920 0.5 12px #ff0000 {{a}} {{b}} https://a.com/x\n"
              "```\nx\n```\n```\ny\n```\n")
        cur = ("w\n0.5 14px {{a}} {{c}} https://b.com/y\n```\nx\n```\n")
        code, out, _ = self.check(self.build(up, cur))
        self.assertNotEqual(code, 0)
        lines = [l for l in out.splitlines() if l.startswith(self.EN)]
        kinds = {l.split(": ")[1] for l in lines}
        self.assertEqual(kinds, {"code-fences", "placeholders", "urls", "numbers"})
        joined = out
        for needle in ("1920", "12px", "#ff0000", "{{b}}","a.com/x", "b.com/y"):
            self.assertIn(needle, joined)

    def test_chinese_numeral_unit_leniency(self):
        up = "第 2 拍 1.05 倍 0.9s 30%\n"
        cur = "beat 2, 1.05x, 0.9 s, 30 percent\n"
        code, out, _ = self.check(self.build(up, cur))
        self.assertEqual(code, 0, out)

    def test_prose_placeholders_compare_by_count(self):
        up = "词 {{默认：家}} {{ x_1 }}\n"
        code, out, _ = self.check(self.build(up, "w {{default: home}} {{x_1}}\n"))
        self.assertEqual(code, 0, out)
        code, out, _ = self.check(self.build(up, "w {{x_1}}\n"))
        self.assertNotEqual(code, 0)
        self.assertIn("count upstream 2, now 1", out)

    def test_deleted_lines_excluded_from_upstream(self):
        cn = SP + "/O_奥斯卡98部/O1_x.md"
        en = SP + "/O_98-best-picture-winners/O1_x.md"
        up = "## 风格提示词\n红色 #ff0000\nEnglish:\nred 2s\n"
        cur = "## Style prompt\nEnglish:\nred 2s\n"      # upstream line 2 deleted
        r = self.build(up, cur, cn, en)
        code, out, _ = self.check(r, en)
        self.assertNotEqual(code, 0)                     # no deletion record: #ff0000 missing
        r.put_out("o1", {en: {"2": None}})
        code, out, _ = self.check(r, en)
        self.assertEqual(code, 0, out)

    def test_batch_option_and_rewrite_section(self):
        cn = SP + "/A-G_代码样片/A2_光标.md"
        en = AG + "/A2_cursor-typing.md"
        r = self.build("词 100px\n```\n```\n", "词 100px\n```\n```\n", cn, en)
        extract(r)                                       # segments exist for ag-z
        r.write(en, "w 50px\n```\n```\n")             # then it gets translated
        code, out, _ = run(check_prompts.main, ["--root", str(r.root), "--batch", "ag-z"])
        self.assertEqual(code, 0, out)
        self.assertIn("expected-rewrite", out)
        self.assertIn("A2_cursor-typing.md: expected-rewrite: numbers", out)

    def test_unmapped_file_is_a_finding(self):
        r = self.build("词\n", "w\n")
        r.write(AG + "/A7_new.md", "x\n")
        code, out, _ = self.check(r, AG + "/A7_new.md")
        self.assertNotEqual(code, 0)
        self.assertIn("A7_new.md: no-upstream", out)


if __name__ == "__main__":
    unittest.main()
