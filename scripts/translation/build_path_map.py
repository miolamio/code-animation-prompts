#!/usr/bin/env python3
"""Build docs/translation/path-map.json, mapping each Chinese upstream path to its English path.

Paths are read from the upstream commit's tree, not the working tree, so the map can
still be rebuilt after the rename. Style names come from docs/translation/glossary.json.
"""

import json
import re
import subprocess
import unicodedata
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
GLOSSARY_PATH = ROOT / "docs/translation/glossary.json"
OUTPUT_PATH = ROOT / "docs/translation/path-map.json"

UPSTREAM_COMMIT = "103ac7e8b3bfb0bac4b0c78b42896f67cb0fe732"
LIBRARY = "skills/code-animation-prompts/assets/library/"
ZH_STYLE_ROOT = "风格提示词"
EN_STYLE_ROOT = "style-prompts"
HAN = re.compile(r"[㐀-鿿豈-﫿]")
STYLE_FILE = re.compile(r"^([A-Z]\d+)_.*\.(md|jpg)$")
SERIES_FOLDER = re.compile(r"^(A-G|[A-Z])_(.+)$")

_B6 = "示例/B6_光速穿梭·爆炸·重聚_同一份提示词/"
_B6_EN = "examples/B6_warp-explode-reunite_same-prompt/"
_X7 = "示例/X7_英雄漫画_只给一句话/"
_X7_EN = "examples/X7_hero-comic_one-line-brief/"

# Every non-style path, relative to the library. Files with ASCII names keep them.
NON_STYLE = {
    "风格挑选.html": "style-picker.html",
    "_统计.json": "_stats.json",
    "说明.md": "README.md",
    "许可与来源.md": "licenses-and-sources.md",
    "风格提示词/A-G_代码样片/_公共函数.js": "style-prompts/A-G_code-samples/_shared-functions.js",
    "第三方许可/Lemo-Opuscar_LICENSE.txt": "third-party-licenses/Lemo-Opuscar_LICENSE.txt",
    "第三方许可/code-video_LICENSE.txt": "third-party-licenses/code-video_LICENSE.txt",
    "第三方许可/mg-styles-15_LICENSE.txt": "third-party-licenses/mg-styles-15_LICENSE.txt",
    _B6 + "提示词.md": _B6_EN + "prompt.md",
    _B6 + "DeepSeek-V4.1-Flash_High.html": _B6_EN + "DeepSeek-V4.1-Flash_High.html",
    _B6 + "DeepSeek-V4.1-Flash_High.mp4": _B6_EN + "DeepSeek-V4.1-Flash_High.mp4",
    _B6 + "Opus5.5_High.html": _B6_EN + "Opus5.5_High.html",
    _B6 + "Opus5.5_High.mp4": _B6_EN + "Opus5.5_High.mp4",
    _B6 + "截图_DeepSeek做出的B6.png": _B6_EN + "screenshot_deepseek-b6-result.png",
    _B6 + "截图_Opus5.5的出图文件夹.png": _B6_EN + "screenshot_opus5.5-output-folder.png",
    _X7 + "提示词.md": _X7_EN + "prompt.md",
    _X7 + "DeepSeek写的说明.md": _X7_EN + "deepseek-notes.md",
    _X7 + "截图_DeepSeek做漫画的对话.png": _X7_EN + "screenshot_deepseek-comic-chat.png",
    _X7 + "hero-pd.svg": _X7_EN + "hero-pd.svg",
    _X7 + "index.html": _X7_EN + "index.html",
    _X7 + "ink-and-thunder.mp4": _X7_EN + "ink-and-thunder.mp4",
}


def slugify(name: str) -> str:
    """Turn an English name into a lowercase ASCII slug with hyphens."""
    text = unicodedata.normalize("NFKD", name).replace("&", " and ")
    text = re.sub(r"['’]", "", text).lower()
    ascii_only = text.encode("ascii", "ignore").decode("ascii") if not HAN.search(text) else ""
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only).strip("-")
    if not slug:
        raise ValueError(f"no slug for name: {name!r}")
    return slug


def upstream_paths() -> list[str]:
    output = subprocess.run(
        ["git", "ls-tree", "-r", "-z", "--name-only", UPSTREAM_COMMIT],
        cwd=ROOT,
        check=True,
        capture_output=True,
        encoding="utf-8",
    ).stdout
    return [path for path in output.split("\0") if path]


def series_folder(folder: str, series_labels: dict[str, str]) -> str:
    """Translate a `<series>_<label>` folder. Folders with ASCII labels stay as they are."""
    if folder.isascii():
        return folder
    match = SERIES_FOLDER.match(folder)
    if match is None:
        raise ValueError(f"unexpected series folder: {folder}")
    series = match.group(1)
    return f"{series}_{slugify(series_labels[series.replace('-', '')])}"


def map_path(source: str, glossary: dict) -> str:
    """Return the English path for one Chinese upstream path."""
    if not source.startswith(LIBRARY):
        raise ValueError(f"no mapping for path outside the library: {source}")
    relative = source[len(LIBRARY):]
    if relative in NON_STYLE:
        return LIBRARY + NON_STYLE[relative]
    parts = PurePosixPath(relative).parts
    match = STYLE_FILE.match(parts[-1])
    if len(parts) != 3 or parts[0] != ZH_STYLE_ROOT or match is None:
        raise ValueError(f"no mapping for path: {source}")
    style_id, suffix = match.group(1), match.group(2)
    name = f"{style_id}_{slugify(glossary['styles'][style_id])}.{suffix}"
    return f"{LIBRARY}{EN_STYLE_ROOT}/{series_folder(parts[1], glossary['series'])}/{name}"


def build() -> dict:
    glossary = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))
    sources = sorted(path for path in upstream_paths() if HAN.search(path))
    return {
        "upstream_commit": UPSTREAM_COMMIT,
        "paths": {source: map_path(source, glossary) for source in sources},
    }


def render(document: dict) -> str:
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    document = build()
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(render(document))
    print(f"Wrote {len(document['paths'])} paths to {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
