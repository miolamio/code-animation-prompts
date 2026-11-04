#!/usr/bin/env python3
"""One-off: write docs/source-manifest.json from the translated library, as the fork's frozen baseline.

Hashes the working-tree bytes of the files git tracks under the library, and refuses a tree with
stray files. Once the file holds a translated baseline it is frozen, and this refuses to overwrite it
unless --force is given. Record later library changes in references/library-changes.json instead.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = "skills/code-animation-prompts/assets/library"
MANIFEST = "docs/source-manifest.json"
PATH_MAP = "docs/translation/path-map.json"
SOURCE = "Code Animation: 341 Style Prompts (Free), translated to English in this fork"
NOTE = ("Translated baseline of the English fork, generated once by scripts/translation/build_manifest.py and then "
        "frozen. The upstream Chinese baseline remains in git history at upstream_commit.")


class ManifestError(Exception):
    pass


def build(root):
    root = Path(root)
    library = root / LIBRARY
    output = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--", LIBRARY],
                            check=True, capture_output=True).stdout.decode("utf-8")
    tracked = {name[len(LIBRARY) + 1:] for name in output.split("\0") if name}
    on_disk = {path.relative_to(library).as_posix() for path in library.rglob("*") if path.is_file()}
    if tracked != on_disk:
        raise ManifestError(f"Library differs from git: untracked {sorted(on_disk - tracked)}, "
                            f"missing {sorted(tracked - on_disk)}")
    upstream = json.loads((root / PATH_MAP).read_text(encoding="utf-8"))["upstream_commit"]
    files = {name: hashlib.sha256((library / name).read_bytes()).hexdigest() for name in sorted(tracked)}
    return {"source": SOURCE, "note": NOTE, "upstream_commit": upstream, "file_count": len(files),
            "algorithm": "sha256", "files": files}


def render(manifest):
    return json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"


def write(root, force=False):
    path = Path(root) / MANIFEST
    if not force and path.is_file() and "upstream_commit" in json.loads(path.read_text(encoding="utf-8")):
        raise ManifestError(f"{MANIFEST} is frozen; pass --force only to replace the baseline on purpose")
    manifest = build(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(manifest), encoding="utf-8", newline="\n")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="replace an existing translated baseline")
    try:
        written = write(ROOT, parser.parse_args().force)
    except ManifestError as error:
        sys.exit(f"FAILED: {error}")
    print(f"Wrote {written['file_count']} files to {MANIFEST}")
