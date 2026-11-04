"""Tests for the Chinese-text gate in scripts/validate_repo.py."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import validate_repo as vr  # noqa: E402


def rule(path, literals=None, reason="translation-record"):
    return {"path": path, "literals": literals, "reason": reason}


class Fixture(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.files = []

    def write(self, rel, data):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
        self.files.append(rel)

    def problems(self, allowlist=()):
        return vr.check_chinese(self.root, list(allowlist), self.files)

    def assert_fails(self, allowlist, needle):
        problems = self.problems(allowlist)
        self.assertTrue(any(needle in problem for problem in problems), problems)


class TrackedText(Fixture):
    def test_clean_file_passes(self):
        self.write("a.md", "plain English\n")
        self.assertEqual(self.problems(), [])

    def test_chinese_in_text_file_fails_with_path_and_line(self):
        self.write("a.py", "x = 1\n# 注释\n")
        self.assert_fails([], "a.py:2")

    def test_range_boundaries(self):
        for char in ["\u3400", "\u4e00", "\u9fff", "\uf900", "\ufaff"]:
            self.files = []
            self.write("a.md", char)
            self.assertTrue(self.problems(), hex(ord(char)))
        for char in ["\u33ff", "\ua000", "\uf8ff", "\ufb00", "\u3001", "\uff0c", "\u00e9", "\u3072"]:
            self.files = []
            self.write("a.md", char)
            self.assertEqual(self.problems(), [], hex(ord(char)))

    def test_text_file_that_is_not_utf8_fails(self):
        self.write("a.txt", "注释".encode("gbk"))
        self.assert_fails([], "a.txt")

    def test_tracked_file_missing_from_disk_is_skipped(self):
        self.files.append("gone.md")
        self.assertEqual(self.problems(), [])


class Paths(Fixture):
    def test_chinese_in_path_fails(self):
        self.write("库/a.md", "plain\n")
        self.assert_fails([], "库/a.md")

    def test_literal_rule_does_not_excuse_the_path(self):
        self.write("库/a.md", "库\n")
        self.assert_fails([rule("库/a.md", ["库"], "style-literal")], "库/a.md")

    def test_whole_path_rule_excuses_the_path(self):
        self.write("docs/translation/库.md", "库\n")
        self.assertEqual(self.problems([rule("docs/translation/**")]), [])


class Literals(Fixture):
    def test_allowlisted_literal_passes(self):
        self.write("z5.md", "Cut the character 囍 from red paper.\n")
        self.assertEqual(self.problems([rule("z5.md", ["囍"], "style-literal")]), [])

    def test_same_file_with_other_chinese_fails(self):
        self.write("z5.md", "Cut 囍 from 红纸.\n")
        problems = self.problems([rule("z5.md", ["囍"], "style-literal")])
        self.assertTrue(any("红纸" in problem for problem in problems), problems)
        self.assertFalse(any("囍" in problem for problem in problems), problems)

    def test_literal_for_another_file_does_not_apply(self):
        self.write("a.md", "囍\n")
        self.write("b.md", "囍\n")
        self.assert_fails([rule("a.md", ["囍"], "style-literal")], "b.md")

    def test_entries_for_one_file_combine(self):
        self.write("l.md", "全部免费 and 俯仰观照\n")
        self.assertEqual(self.problems([rule("l.md", ["全部免费"], "license-quote"),
                                        rule("l.md", ["俯仰观照"], "attribution")]), [])

    def test_literal_that_contains_a_shorter_literal_wins(self):
        self.write("a.md", "俯仰观照 and 俯仰\n")
        self.assertEqual(self.problems([rule("a.md", ["俯仰"], "style-literal"),
                                        rule("a.md", ["俯仰观照"], "attribution")]), [])

    def test_literal_may_contain_ascii(self):
        self.write("l.md", "禁止付费 skills 卖。\n")
        self.assertEqual(self.problems([rule("l.md", ["禁止付费 skills 卖。"], "license-quote")]), [])


class WholePathRules(Fixture):
    def test_directory_rule_passes(self):
        self.write("docs/translation/a/b.md", "中文\n")
        self.write("docs/translation/c.json", "中文\n")
        self.assertEqual(self.problems([rule("docs/translation/**")]), [])

    def test_directory_rule_stops_at_the_directory(self):
        self.write("docs/translation/a.md", "中文\n")
        self.write("docs/translation-old/a.md", "中文\n")
        self.assert_fails([rule("docs/translation/**")], "docs/translation-old/a.md")

    def test_single_star_does_not_cross_a_slash(self):
        self.write("docs/a.md", "中文\n")
        self.write("docs/sub/b.md", "中文\n")
        problems = self.problems([rule("docs/*.md")])
        self.assertTrue(any("docs/sub/b.md" in problem for problem in problems), problems)
        self.assertFalse(any("docs/a.md" in problem for problem in problems), problems)

    def test_media_source_file_rule_passes(self):
        self.write("b6.html", "中文\n")
        self.assertEqual(self.problems([rule("b6.html", None, "media-source")]), [])

    def test_whole_path_with_any_other_reason_is_rejected(self):
        self.write("a.md", "中文\n")
        for reason in ["style-literal", "attribution", "license-quote"]:
            self.assert_fails([rule("a.md", None, reason)], reason)


class MalformedEntries(Fixture):
    def setUp(self):
        super().setUp()
        self.write("a.md", "中\n")

    def test_unknown_reason_is_rejected(self):
        self.assert_fails([rule("a.md", ["中"], "looks-nice")], "looks-nice")

    def test_empty_literals_are_rejected(self):
        self.assert_fails([rule("a.md", [], "attribution")], "literals")

    def test_literal_without_chinese_is_rejected(self):
        self.assert_fails([rule("a.md", ["中", "plain"], "attribution")], "plain")

    def test_unexpected_or_missing_keys_are_rejected(self):
        self.assert_fails([{"path": "a.md", "reason": "media-source"}], "keys")
        self.assert_fails([dict(rule("a.md"), note="x")], "keys")


class BinaryMedia(Fixture):
    def test_media_files_are_skipped_even_with_chinese_bytes(self):
        for name in ["a.png", "b.JPG", "c.jpeg", "d.gif", "e.mp4"]:
            self.write(name, b"\x00\xff" + "中文".encode("utf-8"))
        self.assertEqual(self.problems(), [])

    def test_chinese_named_media_still_fails_on_its_path(self):
        self.write("图.png", b"\x00\xff")
        self.assert_fails([], "图.png")

    def test_svg_is_text(self):
        self.write("a.svg", "<text>中文</text>")
        self.assert_fails([], "a.svg")


class Staleness(Fixture):
    def test_literal_no_longer_in_file_fails(self):
        self.write("a.md", "囍\n")
        self.assert_fails([rule("a.md", ["囍", "酒家"], "style-literal")], "酒家")

    def test_shorter_literal_only_found_inside_a_longer_one_is_stale(self):
        self.write("a.md", "酒家\n")
        self.assert_fails([rule("a.md", ["家", "酒家"], "style-literal")], "'家'")

    def test_path_matching_no_tracked_file_fails(self):
        self.write("a.md", "plain\n")
        self.assert_fails([rule("gone.md", ["囍"], "style-literal")], "gone.md")
        self.assert_fails([rule("gone/**")], "gone/**")

    def test_whole_path_rule_with_no_chinese_left_fails(self):
        self.write("docs/translation/a.md", "plain\n")
        self.assert_fails([rule("docs/translation/**")], "docs/translation/**")


class TrackedFiles(unittest.TestCase):
    def test_lists_tracked_paths_unquoted_and_ignores_untracked(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            for rel in ["库.md", "plain.md", "untracked.md"]:
                (root / rel).write_text("x\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "库.md", "plain.md"], check=True)
            self.assertEqual(sorted(vr.tracked_files(root)), sorted(["库.md", "plain.md"]))


if __name__ == "__main__":
    unittest.main()
