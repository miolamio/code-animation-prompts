import json
import subprocess
import tempfile
import unicodedata
import unittest
from pathlib import Path

import apply_path_map as apm


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout


class ApplyPathMapTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.email", "t@example.com")
        git(self.root, "config", "user.name", "t")
        self.files = {"库/说明.md": "a", "库/子/图.txt": "b", "plain.txt": "c"}
        for rel, text in self.files.items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "init")

    def write_map(self, paths):
        map_path = self.root.parent / (self.root.name + "-map.json")
        map_path.write_text(json.dumps({"paths": paths}, ensure_ascii=False), encoding="utf-8")
        self.addCleanup(map_path.unlink)
        return map_path

    def run_tool(self, paths, *flags):
        return apm.main(["--root", str(self.root), "--map", str(self.write_map(paths)), *flags])

    def test_moves_chinese_files_and_removes_empty_dirs(self):
        code = self.run_tool({"库/说明.md": "lib/readme.md", "库/子/图.txt": "lib/sub/pic.txt"})
        self.assertEqual(code, 0)
        status = git(self.root, "-c", "core.quotepath=off", "diff", "--cached", "--name-status", "-M100%")
        self.assertEqual(sorted(status.splitlines()), sorted([
            "R100\t库/说明.md\tlib/readme.md", "R100\t库/子/图.txt\tlib/sub/pic.txt"]))
        self.assertFalse((self.root / "库").exists())

    def test_dry_run_changes_nothing(self):
        self.assertEqual(self.run_tool({"库/说明.md": "lib/readme.md"}, "--dry-run"), 0)
        self.assertEqual(git(self.root, "diff", "--cached", "--name-status"), "")
        self.assertFalse((self.root / "lib").exists())

    def test_dry_run_reports_all_problems(self):
        code = self.run_tool({
            "missing.txt": "x.txt",
            "库/说明.md": "plain.txt",
            "库/子/图.txt": "plain.txt/inside.txt",
        }, "--dry-run")
        self.assertNotEqual(code, 0)
        problems = apm.validate(self.root, {
            "missing.txt": "x.txt", "库/说明.md": "plain.txt", "库/子/图.txt": "plain.txt/inside.txt"})
        text = "\n".join(problems)
        self.assertIn("missing.txt", text)
        self.assertGreaterEqual(len(problems), 3)
        self.assertEqual(git(self.root, "diff", "--cached", "--name-status"), "")

    def test_nfd_source_matches_tracked_nfc(self):
        nfd = unicodedata.normalize("NFD", "café.txt")
        nfc = unicodedata.normalize("NFC", "café.txt")
        (self.root / nfc).write_text("x", encoding="utf-8")
        git(self.root, "add", "-A")
        self.assertEqual(self.run_tool({nfd: "cafe.txt"}, "--dry-run"), 0)


if __name__ == "__main__":
    unittest.main()
