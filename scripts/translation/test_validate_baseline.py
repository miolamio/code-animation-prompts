"""Tests for the baseline comparison in scripts/validate_repo.py and for build_manifest.py."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import build_manifest as bm  # noqa: E402
import validate_repo as vr  # noqa: E402

COMMIT = "103ac7e8b3bfb0bac4b0c78b42896f67cb0fe732"
LIB = "skills/code-animation-prompts/assets/library"


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Library(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.library = Path(tmp.name)
        self.content = {"a.md": b"alpha\n", "sub/b.jpg": b"\xff\xd8beta"}
        for name, data in self.content.items():
            path = self.library / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.manifest = {"upstream_commit": COMMIT, "file_count": 2, "algorithm": "sha256",
                         "files": {name: sha(data) for name, data in self.content.items()}}
        self.changes = {"contributions": {"pr-9": {"author": "x"}}, "modified": {}, "added": {}}

    def validate(self):
        return vr.validate_library(self.library, self.manifest, self.changes)

    def test_matching_baseline_with_empty_ledger_passes(self):
        self.assertEqual(self.validate(), (2, 0, 0))

    def test_changed_file_fails(self):
        (self.library / "a.md").write_bytes(b"alpha changed\n")
        with self.assertRaisesRegex(AssertionError, "a.md"):
            self.validate()

    def test_changed_line_ending_fails(self):
        (self.library / "a.md").write_bytes(b"alpha\r\n")
        with self.assertRaisesRegex(AssertionError, "a.md"):
            self.validate()

    def test_stray_file_fails(self):
        (self.library / ".DS_Store").write_bytes(b"x")
        with self.assertRaisesRegex(AssertionError, "DS_Store"):
            self.validate()

    def test_missing_file_fails(self):
        (self.library / "sub/b.jpg").unlink()
        with self.assertRaisesRegex(AssertionError, "b.jpg"):
            self.validate()

    def test_stale_file_count_fails(self):
        self.manifest["file_count"] = 3
        with self.assertRaisesRegex(AssertionError, "count"):
            self.validate()

    def register_modified(self, **overrides):
        new = b"alpha changed\n"
        (self.library / "a.md").write_bytes(new)
        self.changes["modified"]["a.md"] = {"original_sha256": sha(self.content["a.md"]), "sha256": sha(new),
                                            "contribution": "pr-9", "reason": "Fixes a typo.", **overrides}

    def test_registered_modification_passes(self):
        self.register_modified()
        self.assertEqual(self.validate(), (1, 1, 0))

    def test_registered_modification_with_wrong_hash_fails(self):
        self.register_modified(sha256="0" * 64)
        with self.assertRaisesRegex(AssertionError, "a.md"):
            self.validate()

    def test_modification_must_name_the_baseline_hash(self):
        self.register_modified(original_sha256="0" * 64)
        with self.assertRaisesRegex(AssertionError, "a.md"):
            self.validate()

    def test_modification_needs_contribution_and_reason(self):
        self.register_modified(contribution="pr-404")
        with self.assertRaisesRegex(AssertionError, "contribution"):
            self.validate()
        self.register_modified(reason="  ")
        with self.assertRaisesRegex(AssertionError, "reason"):
            self.validate()

    def register_added(self, **overrides):
        (self.library / "new.jpg").write_bytes(b"new")
        self.changes["added"]["new.jpg"] = {"sha256": sha(b"new"), "contribution": "pr-9", "reason": "New still.",
                                            **overrides}

    def test_registered_addition_passes(self):
        self.register_added()
        self.assertEqual(self.validate(), (2, 0, 1))

    def test_addition_that_changed_fails(self):
        self.register_added(sha256="0" * 64)
        with self.assertRaisesRegex(AssertionError, "new.jpg"):
            self.validate()

    def test_addition_overlapping_the_baseline_fails(self):
        self.changes["added"]["a.md"] = {"sha256": sha(b"alpha\n"), "contribution": "pr-9", "reason": "x"}
        with self.assertRaisesRegex(AssertionError, "overlap"):
            self.validate()

    def test_modification_outside_the_baseline_fails(self):
        self.changes["modified"]["other.md"] = {"original_sha256": "0", "sha256": "0", "contribution": "pr-9",
                                                "reason": "x"}
        with self.assertRaisesRegex(AssertionError, "baseline"):
            self.validate()


class Manifest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.library = self.root / LIB
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        for name, data in {"b.md": b"crlf\r\nkept\r\n", "a/c.jpg": b"\xff\xd8"}.items():
            path = self.library / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        (self.root / ".gitattributes").write_bytes(f"{LIB}/** -text\n".encode())
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True)
        (self.root / "docs/translation").mkdir(parents=True)
        (self.root / "docs/translation/path-map.json").write_text(json.dumps({"upstream_commit": COMMIT}),
                                                                  encoding="utf-8")

    def test_schema_and_hashes_of_raw_bytes(self):
        manifest = bm.build(self.root)
        self.assertEqual(manifest["upstream_commit"], COMMIT)
        self.assertEqual(manifest["algorithm"], "sha256")
        self.assertEqual(manifest["file_count"], 2)
        self.assertIn("baseline", manifest["note"])
        self.assertEqual(manifest["files"], {"a/c.jpg": sha(b"\xff\xd8"), "b.md": sha(b"crlf\r\nkept\r\n")})
        self.assertEqual(list(manifest["files"]), sorted(manifest["files"]))

    def test_built_manifest_satisfies_the_validator(self):
        changes = {"contributions": {}, "modified": {}, "added": {}}
        self.assertEqual(vr.validate_library(self.library, bm.build(self.root), changes), (2, 0, 0))

    def test_output_holds_no_chinese(self):
        self.assertIsNone(vr.CHINESE_RE.search(bm.render(bm.build(self.root))))

    def test_untracked_file_in_the_library_is_refused(self):
        (self.library / ".DS_Store").write_bytes(b"x")
        with self.assertRaisesRegex(bm.ManifestError, "DS_Store"):
            bm.build(self.root)

    def test_frozen_manifest_is_not_overwritten_without_force(self):
        path = self.root / bm.MANIFEST
        bm.write(self.root)
        first = path.read_bytes()
        (self.library / "b.md").write_bytes(b"changed\n")
        with self.assertRaisesRegex(bm.ManifestError, "frozen"):
            bm.write(self.root)
        self.assertEqual(path.read_bytes(), first)
        bm.write(self.root, force=True)
        self.assertNotEqual(path.read_bytes(), first)

    def test_old_format_manifest_may_be_replaced_once(self):
        path = self.root / bm.MANIFEST
        path.write_text(json.dumps({"source": "old", "file_count": 0, "algorithm": "sha256", "files": {}}), encoding="utf-8")
        bm.write(self.root)
        self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["upstream_commit"], COMMIT)


class Repository(unittest.TestCase):
    def test_gitattributes_keeps_the_renamed_library_byte_exact(self):
        names = [f"{LIB}/style-picker.html", f"{LIB}/README.md", f"{LIB}/style-prompts/Z_chinese-style/Z5_chinese-paper-cutting.md"]
        out = subprocess.run(["git", "-C", str(bm.ROOT), "check-attr", "text", "--", *names],
                             check=True, capture_output=True, encoding="utf-8").stdout
        self.assertEqual(out.count(": text: unset"), len(names), out)


if __name__ == "__main__":
    unittest.main()
