#!/usr/bin/env python3
"""Apply docs/translation/path-map.json with `git mv` (renames are staged, nothing is committed).

--dry-run prints the planned moves and validates only. Paths are matched against
`git ls-files -z` (never the filesystem) after Unicode NFC normalisation, so macOS
NFD/NFC differences do not matter; the tracked spelling is what gets passed to git.
"""

import argparse
import json
import os
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MAP = ROOT / "docs/translation/path-map.json"


def nfc(path: str) -> str:
    return unicodedata.normalize("NFC", path)


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", "core.quotepath=off", "-C", str(root), *args],
        check=True, capture_output=True, encoding="utf-8",
    ).stdout


def tracked(root: Path) -> dict[str, str]:
    """Map NFC-normalised path -> path exactly as git spells it."""
    out = git(root, "ls-files", "-z")
    return {nfc(p): p for p in out.split("\0") if p}


def validate(root: Path, paths: dict[str, str]) -> list[str]:
    files = tracked(root)
    problems: list[str] = []
    seen: dict[str, str] = {}
    sources = {nfc(s) for s in paths}
    for source, target in paths.items():
        if nfc(source) not in files:
            problems.append(f"source not tracked: {source}")
        t = nfc(target)
        if t in files:
            problems.append(f"target already tracked: {target}")
        elif os.path.lexists(root / target):
            problems.append(f"target exists on disk: {target}")
        if t in seen:
            problems.append(f"duplicate target {target} (from {seen[t]} and {source})")
        seen[t] = source
        # A target nested under a tracked file path (file used as a directory).
        parts = t.split("/")
        for i in range(1, len(parts)):
            parent = "/".join(parts[:i])
            if parent in files:
                kind = "moving source" if parent in sources else "tracked file"
                problems.append(f"target {target} is inside {kind} {parent}")
    # A target that is also the directory of another target (file/dir clash).
    for t in list(seen):
        parts = t.split("/")
        for i in range(1, len(parts)):
            if "/".join(parts[:i]) in seen:
                problems.append(f"target {seen['/'.join(parts[:i])]} -> file also used as directory by {seen[t]}")
    return problems


def remove_empty_dirs(root: Path, sources: list[str]) -> None:
    for source in sources:
        parent = (root / source).parent
        while parent != root and parent.is_dir():
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--map", type=Path, default=DEFAULT_MAP)
    args = ap.parse_args(argv)
    root = args.root.resolve()
    paths: dict[str, str] = json.loads(args.map.read_text(encoding="utf-8"))["paths"]

    problems = validate(root, paths)
    if args.dry_run:
        for source, target in paths.items():
            print(f"{source} -> {target}")
    if problems:
        print(f"{len(problems)} problem(s):", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1
    if args.dry_run:
        print(f"OK: {len(paths)} moves validated")
        return 0

    files = tracked(root)
    for source, target in paths.items():
        (root / target).parent.mkdir(parents=True, exist_ok=True)
        git(root, "mv", "--", files[nfc(source)], target)
    remove_empty_dirs(root, [files[nfc(s)] for s in paths])
    print(f"Moved {len(paths)} paths")
    return 0


if __name__ == "__main__":
    sys.exit(main())
