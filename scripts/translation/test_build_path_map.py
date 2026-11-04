"""Tests for the Chinese-to-English path map and the glossary it is built from."""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_path_map as bpm  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
GLOSSARY = json.loads((ROOT / "docs/translation/glossary.json").read_text(encoding="utf-8"))
HAN = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
UPSTREAM_PICKER = "skills/code-animation-prompts/assets/library/风格挑选.html"
STYLE_ROOT = "skills/code-animation-prompts/assets/library/style-prompts/"
SERIES_FOLDERS = {"A-G", "M", "K", "Z", "H", "L", "V", "X", "R", "O"}
WINDOWS_RESERVED = re.compile(r'[<>:"\\|?*\x00-\x1f]')
WINDOWS_DEVICE = re.compile(r"^(con|prn|aux|nul|com\d|lpt\d)(\.|$)", re.I)
STYLE_FILE = re.compile(r"^([A-Z]\d+)_(.+)\.(md|jpg)$")
# Eight upstream stubs have an empty name, such as M14_.md, so a source slug may be empty.
SOURCE_STYLE_FILE = re.compile(r"^([A-Z]\d+)_(.*)\.(md|jpg)$")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-c", "core.quotepath=off", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        encoding="utf-8",
    ).stdout


def tracked() -> list[str]:
    return [p for p in git("ls-files", "-z").split("\0") if p]


def upstream_tracked() -> list[str]:
    return [p for p in git("ls-tree", "-r", "-z", "--name-only", bpm.UPSTREAM_COMMIT).split("\0") if p]


def is_style(source: str) -> bool:
    return "/风格提示词/" in source and SOURCE_STYLE_FILE.match(PurePosixPath(source).name) is not None


# Reviewed glossary corrections that deliberately differ from the picker's `en`.
STYLE_OVERRIDES = {"K20": "Paper Cut", "L10": "Engineering Comparison Board"}


class SlugifyTests(unittest.TestCase):
    def test_slugs(self) -> None:
        cases = {
            "Flat Vector": "flat-vector",
            "Oliver!": "oliver",
            "You Can't Take It with You": "you-cant-take-it-with-you",
            "Urban Sketch · Pen & Wash": "urban-sketch-pen-and-wash",
            "Cyberpunk HUD / FUI": "cyberpunk-hud-fui",
            "Kramer vs. Kramer": "kramer-vs-kramer",
            "The Lord of the Rings: The Return of the King": "the-lord-of-the-rings-the-return-of-the-king",
            "HD-2D": "hd-2d",
        }
        for name, slug in cases.items():
            self.assertEqual(bpm.slugify(name), slug)

    def test_rejects_name_without_slug(self) -> None:
        with self.assertRaises(ValueError):
            bpm.slugify("水墨")


class PathMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = bpm.build()
        cls.paths = cls.document["paths"]

    def test_upstream_commit_is_full_sha_of_baseline(self) -> None:
        self.assertEqual(self.document["upstream_commit"], git("rev-parse", "103ac7e").strip())

    def test_every_chinese_path_has_an_entry(self) -> None:
        sources = {p for p in upstream_tracked() + tracked() if HAN.search(p)}
        self.assertTrue(sources)
        self.assertEqual(sources - set(self.paths), set())

    def test_no_entry_for_ascii_or_unknown_paths(self) -> None:
        upstream = set(upstream_tracked())
        for source in self.paths:
            self.assertTrue(HAN.search(source), source)
            self.assertIn(source, upstream)

    def test_targets_are_ascii_without_chinese(self) -> None:
        for target in self.paths.values():
            self.assertIsNone(HAN.search(target), target)
            self.assertTrue(target.isascii(), target)

    def test_targets_unique_case_insensitively_including_untouched_paths(self) -> None:
        targets = list(self.paths.values()) + [p for p in upstream_tracked() if p not in self.paths]
        folded = [t.casefold() for t in targets]
        self.assertEqual(len(folded), len(set(folded)))

    def test_folders_map_one_to_one(self) -> None:
        forward: dict[str, str] = {}
        for source, target in self.paths.items():
            src, dst = PurePosixPath(source).parent, PurePosixPath(target).parent
            self.assertEqual(forward.setdefault(str(src), str(dst)), str(dst))
        folded = [v.casefold() for v in forward.values()]
        self.assertEqual(len(folded), len(set(folded)))

    def test_windows_safe_and_short(self) -> None:
        for target in self.paths.values():
            self.assertLess(len(target), 200, target)
            for part in PurePosixPath(target).parts:
                self.assertIsNone(WINDOWS_RESERVED.search(part), target)
                self.assertIsNone(WINDOWS_DEVICE.match(part), target)
                self.assertFalse(part.endswith((".", " ")), target)
                self.assertNotIn(" ", part, target)

    def test_md_and_jpg_stems_stay_paired(self) -> None:
        by_stem: dict[str, dict[str, str]] = {}
        for source, target in self.paths.items():
            suffix = PurePosixPath(source).suffix
            if suffix in {".md", ".jpg"} and is_style(source):
                by_stem.setdefault(source[: -len(suffix)], {})[suffix] = target
        paired = [t for t in by_stem.values() if len(t) == 2]
        self.assertEqual(len(paired), 196)
        for pair in paired:
            self.assertEqual(pair[".md"][:-3], pair[".jpg"][:-4])

    def test_style_ids_stay_as_filename_prefix(self) -> None:
        seen = set()
        for source, target in self.paths.items():
            if not is_style(source):
                continue
            source_id = SOURCE_STYLE_FILE.match(PurePosixPath(source).name).group(1)
            match = STYLE_FILE.match(PurePosixPath(target).name)
            self.assertIsNotNone(match, target)
            self.assertEqual(match.group(1), source_id)
            self.assertEqual(PurePosixPath(source).suffix, PurePosixPath(target).suffix)
            seen.add(source_id)
        self.assertEqual(seen, set(GLOSSARY["styles"]))

    def test_style_slugs_are_lowercase_ascii_hyphenated(self) -> None:
        for source, target in self.paths.items():
            if is_style(source):
                slug = STYLE_FILE.match(PurePosixPath(target).name).group(2)
                self.assertRegex(slug, r"^[a-z0-9]+(-[a-z0-9]+)*$", target)
                self.assertEqual(slug, bpm.slugify(GLOSSARY["styles"][PurePosixPath(target).name.split("_")[0]]))

    def test_series_folder_form(self) -> None:
        folders = set()
        for source, target in self.paths.items():
            if not is_style(source):
                continue
            self.assertTrue(target.startswith(STYLE_ROOT), target)
            folder = PurePosixPath(target).parent.name
            match = re.fullmatch(r"([A-Z](?:-[A-Z])?)_([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)", folder)
            self.assertIsNotNone(match, folder)
            self.assertIn(match.group(1), SERIES_FOLDERS)
            letter = PurePosixPath(target).name[0]
            self.assertTrue(match.group(1)[0] <= letter <= match.group(1)[-1], target)
            folders.add(match.group(1))
        self.assertEqual(folders, SERIES_FOLDERS)

    def test_required_non_style_names(self) -> None:
        library = "skills/code-animation-prompts/assets/library/"
        self.assertEqual(self.paths[library + "风格挑选.html"], library + "style-picker.html")
        self.assertEqual(self.paths[library + "_统计.json"], library + "_stats.json")
        self.assertEqual(
            self.paths[library + "风格提示词/A-G_代码样片/_公共函数.js"],
            library + "style-prompts/A-G_code-samples/_shared-functions.js",
        )

    def test_ascii_names_kept_under_renamed_parents(self) -> None:
        checked = 0
        for source, target in self.paths.items():
            name = PurePosixPath(source).name
            if name.isascii() and not is_style(source):
                self.assertEqual(PurePosixPath(target).name, name, source)
                checked += 1
        self.assertEqual(checked, 10)
        for folder in ("L_Lemo-Opuscar", "V_mg-styles-15", "X_code-video"):
            self.assertTrue(any(f"/{folder}/" in t for t in self.paths.values()), folder)

    def test_written_file_matches_build_and_is_sorted(self) -> None:
        text = (ROOT / "docs/translation/path-map.json").read_text(encoding="utf-8")
        self.assertEqual(text, bpm.render(self.document))
        written = json.loads(text)
        self.assertEqual(list(written["paths"]), sorted(written["paths"]))


class GlossaryTests(unittest.TestCase):
    def test_series_and_style_coverage(self) -> None:
        self.assertEqual(set(GLOSSARY["series"]), {"AG", "M", "K", "Z", "H", "L", "V", "X", "R", "O"})
        ids = {
            SOURCE_STYLE_FILE.match(PurePosixPath(p).name).group(1)
            for p in upstream_tracked()
            if is_style(p) and p.endswith(".md")
        }
        self.assertEqual(len(ids), 341)
        self.assertEqual(set(GLOSSARY["styles"]), ids)

    def test_values_are_english(self) -> None:
        for section in ("series", "styles", "terms", "labels"):
            for key, value in GLOSSARY[section].items():
                self.assertTrue(value.strip(), key)
                self.assertIsNone(HAN.search(value), f"{key}: {value}")

    def test_picker_english_names_are_reused(self) -> None:
        html = git("show", f"{bpm.UPSTREAM_COMMIT}:{UPSTREAM_PICKER}")
        blob = re.search(r'<script id="data"[^>]*>(.*?)</script>', html, re.S).group(1)
        entries = json.loads(blob)["entries"]
        with_en = [e for e in entries if e.get("en")]
        self.assertEqual(len(with_en), 202)
        for entry in with_en:
            expected = STYLE_OVERRIDES.get(entry["id"], entry["en"])
            self.assertEqual(GLOSSARY["styles"][entry["id"]], expected)

    def test_terms_and_labels(self) -> None:
        self.assertGreaterEqual(len(GLOSSARY["terms"]), 60)
        required = {
            "分类": "Category",
            "长什么样": "Looks like",
            "适合": "Best for",
            "关键词": "Keywords",
            "风格": "Style",
            "年份": "Year",
            "风格提示词": "Style prompt",
        }
        for key, value in required.items():
            self.assertEqual(GLOSSARY["labels"][key], value)


if __name__ == "__main__":
    unittest.main()
