#!/usr/bin/env python3
"""Extract the lines that contain Chinese from the library files, grouped into translator batches.

Writes .build/translation/segments/<batch>.json:
    {relative_file: {"<line_no>": {"text": str, "code": bool}}}
plus _summary.json, and prints a per-batch table. Lines without Chinese are never touched
by the pipeline, so they stay byte-identical.

Shared helpers (line splitting, Chinese detection, fence tracking) live here and are
imported by apply_segments.py and check_prompts.py.
"""

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = "skills/code-animation-prompts/assets/library"
STYLE = LIB + "/style-prompts/"
SHARED_JS = STYLE + "A-G_code-samples/_shared-functions.js"
BUILD = ".build/translation"

BATCHES = ["ag-z", "k-h", "l", "m", "v-x-r", "o1", "o2", "library-docs"]
FOLDER_BATCH = {"A-G": "ag-z", "Z": "ag-z", "K": "k-h", "H": "k-h", "L": "l", "M": "m",
                "V": "v-x-r", "X": "v-x-r", "R": "v-x-r"}

CHINESE_RE = re.compile("[㐀-鿿豈-﫿]")
FULLWIDTH_RE = re.compile("[　-〿＀-￯]")
_LINE_RE = re.compile(r"[^\r\n]*(?:\r\n|\n|\r)|[^\r\n]+")
_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")


def split_lines(text: str) -> list[tuple[str, str]]:
    """[(content, line_ending)]; only \\n, \\r\\n and \\r count as line breaks."""
    out = []
    for m in _LINE_RE.finditer(text):
        s = m.group(0)
        body = s.rstrip("\r\n")
        out.append((body, s[len(body):]))
    return out


def chinese_count(s: str) -> int:
    return len(CHINESE_RE.findall(s))


def fence_flags(lines: list[str]) -> list[bool]:
    """For each line, True if it is inside (or is a fence line of) a fenced code block."""
    flags, fence = [], None
    for line in lines:
        m = _FENCE_RE.match(line)
        if fence is None:
            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                fence = (m.group(1)[0], len(m.group(1)))
            flags.append(fence is not None)
        else:
            flags.append(True)
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] \
                    and not m.group(2).strip():
                fence = None
    return flags


def count_fences(lines: list[str]) -> int:
    """Number of fenced blocks (opening fences)."""
    n, fence = 0, None
    for line in lines:
        m = _FENCE_RE.match(line)
        if fence is None:
            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                fence = (m.group(1)[0], len(m.group(1)))
                n += 1
        elif m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] \
                and not m.group(2).strip():
            fence = None
    return n


def git_ls_files(root: Path) -> list[str]:
    raw = subprocess.run(["git", "-c", "core.quotepath=off", "-C", str(root), "ls-files", "-z"],
                         check=True, capture_output=True).stdout
    return [p.decode("utf-8") for p in raw.split(b"\0") if p]


def in_scope(path: str) -> bool:
    n = unicodedata.normalize("NFC", path)
    if n == SHARED_JS:
        return True
    return n.startswith(LIB + "/") and n.endswith(".md") and \
        not n.startswith(LIB + "/third-party-licenses/")


def batch_of(path: str) -> str:
    """Batch for a file; O files return 'o' (split later)."""
    n = unicodedata.normalize("NFC", path)
    if n.startswith(STYLE):
        folder = n[len(STYLE):].split("/", 1)
        if len(folder) == 2:
            key = folder[0].split("_", 1)[0]
            if key == "O":
                return "o"
            return FOLDER_BATCH.get(key, "library-docs")
    return "library-docs"


def _o_id(path: str) -> int:
    m = re.match(r"O(\d+)", Path(path).name)
    return int(m.group(1)) if m else 10 ** 9


def file_segments(path: Path, is_js: bool) -> dict:
    text = path.read_bytes().decode("utf-8")
    lines = [b for b, _ in split_lines(text)]
    flags = [True] * len(lines) if is_js else fence_flags(lines)
    return {str(i): {"text": line, "code": flags[i - 1]}
            for i, line in enumerate(lines, 1) if CHINESE_RE.search(line)}


def extract(root: Path) -> dict:
    per_file = {}
    for p in sorted(git_ls_files(root)):
        if not in_scope(p) or not (root / p).is_file():
            continue
        segs = file_segments(root / p, p.endswith(".js"))
        if segs:
            per_file[p] = segs
    chars = {f: sum(chinese_count(s["text"]) for s in segs.values())
             for f, segs in per_file.items()}
    batches = {b: {} for b in BATCHES}
    o_files = []
    for f in per_file:
        b = batch_of(f)
        if b == "o":
            o_files.append(f)
        else:
            batches[b][f] = per_file[f]
    o_files.sort(key=lambda f: (_o_id(f), f))
    total, cum, best, cut = sum(chars[f] for f in o_files), 0, None, 0
    for i in range(len(o_files) + 1):
        d = abs(2 * cum - total)
        if best is None or d < best:
            best, cut = d, i
        if i < len(o_files):
            cum += chars[o_files[i]]
    for i, f in enumerate(o_files):
        batches["o1" if i < cut else "o2"][f] = per_file[f]
    return batches


def summarize(batches: dict) -> dict:
    out = {}
    for b in BATCHES:
        files = batches[b]
        segs = [s for fs in files.values() for s in fs.values()]
        out[b] = {"files": len(files), "segments": len(segs),
                  "chars": sum(chinese_count(s["text"]) for s in segs),
                  "code_segments": sum(1 for s in segs if s["code"])}
    return out


def table(summary: dict) -> str:
    rows = [f"{'batch':<14}{'files':>7}{'segments':>10}{'chars':>9}{'code%':>8}"]
    tot = {"files": 0, "segments": 0, "chars": 0, "code_segments": 0}
    for b in BATCHES:
        s = summary[b]
        for k in tot:
            tot[k] += s[k]
        pct = 100 * s["code_segments"] / s["segments"] if s["segments"] else 0
        rows.append(f"{b:<14}{s['files']:>7}{s['segments']:>10}{s['chars']:>9}{pct:>7.1f}%")
    pct = 100 * tot["code_segments"] / tot["segments"] if tot["segments"] else 0
    rows.append(f"{'TOTAL':<14}{tot['files']:>7}{tot['segments']:>10}{tot['chars']:>9}{pct:>7.1f}%")
    return "\n".join(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    root = args.root.resolve()
    batches = extract(root)
    seg_dir = root / BUILD / "segments"
    seg_dir.mkdir(parents=True, exist_ok=True)
    for b in BATCHES:
        (seg_dir / f"{b}.json").write_text(
            json.dumps(batches[b], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    summary = summarize(batches)
    (seg_dir / "_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(table(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
