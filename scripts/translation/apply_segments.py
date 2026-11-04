#!/usr/bin/env python3
"""Apply a translated batch (.build/translation/out/<batch>.json) onto the library files.

Values per "<line_no>": a string (replacement line), null (delete the line), or
{"text": str, "keep": [literal, ...]} (replacement containing permitted Chinese/fullwidth
literals). Everything is validated first; on any problem nothing is written and the exit
code is 1. Bytes of untouched lines, line endings and the final-newline state are kept.
"""

import argparse
import json
import os
import sys
from pathlib import Path

from extract_segments import (BUILD, CHINESE_RE, FULLWIDTH_RE, ROOT, split_lines)


def normalize(value):
    """-> (kind, text, keep) with kind in {'text', 'delete'}, or raises ValueError."""
    if value is None:
        return "delete", None, []
    if isinstance(value, str):
        return "text", value, []
    if isinstance(value, dict) and set(value) <= {"text", "keep"} and isinstance(value.get("text"), str):
        keep = value.get("keep", [])
        if isinstance(keep, list) and all(isinstance(k, str) and k for k in keep):
            return "text", value["text"], keep
    raise ValueError("value must be a string, null, or {\"text\": str, \"keep\": [str, ...]}")


def strip_keep(text: str, keep: list[str]) -> str:
    for k in sorted(keep, key=len, reverse=True):
        text = text.replace(k, "")
    return text


def plan(root: Path, batch: str):
    """Validate; return (problems, new_bytes_by_file, keep_by_file)."""
    seg_path = root / BUILD / "segments" / f"{batch}.json"
    out_path = root / BUILD / "out" / f"{batch}.json"
    problems = []
    if not seg_path.is_file():
        return [f"{seg_path}: segments file not found (run extract_segments.py)"], {}, {}
    if not out_path.is_file():
        return [f"{out_path}: translation output not found"], {}, {}
    segments = json.loads(seg_path.read_text(encoding="utf-8"))
    out = json.loads(out_path.read_text(encoding="utf-8"))

    for f in out:
        if f not in segments:
            problems.append(f"{f}: output refers to a file that is not in the {batch} segments")
    for f, segs in segments.items():
        for ln in segs:
            if f not in out or ln not in out[f]:
                problems.append(f"{f}:{ln}: missing translation")
    for f, lines in out.items():
        if f in segments:
            for ln in lines:
                if ln not in segments[f]:
                    problems.append(f"{f}:{ln}: output refers to a line that is not in the segments")

    new_bytes, keep_by_file = {}, {}
    for f, segs in segments.items():
        path = root / f
        if not path.is_file():
            problems.append(f"{f}: file not found")
            continue
        lines = split_lines(path.read_bytes().decode("utf-8"))
        edits, file_ok = {}, True
        for ln, seg in segs.items():
            i = int(ln)
            if i > len(lines) or lines[i - 1][0] != seg["text"]:
                problems.append(f"{f}:{ln}: file changed since extraction (line no longer matches)")
                file_ok = False
                continue
            if f not in out or ln not in out[f]:
                continue
            try:
                kind, text, keep = normalize(out[f][ln])
            except ValueError as e:
                problems.append(f"{f}:{ln}: {e}")
                continue
            if kind == "delete":
                edits[i] = None
                continue
            bad = False
            if "\n" in text or "\r" in text:
                problems.append(f"{f}:{ln}: replacement contains a line break")
                bad = True
            for k in keep:
                if k not in text:
                    problems.append(f"{f}:{ln}: keep literal {k!r} is not present in the text")
                    bad = True
            rest = strip_keep(text, keep)
            if CHINESE_RE.search(rest):
                problems.append(f"{f}:{ln}: still contains Chinese outside keep: "
                                f"{''.join(CHINESE_RE.findall(rest))!r}")
                bad = True
            if FULLWIDTH_RE.search(rest):
                problems.append(f"{f}:{ln}: contains fullwidth punctuation outside keep: "
                                f"{''.join(FULLWIDTH_RE.findall(rest))!r}")
                bad = True
            if not bad:
                edits[i] = text
                if keep:
                    keep_by_file.setdefault(f, [])
                    keep_by_file[f] += [k for k in keep if k not in keep_by_file[f]]
        if not file_ok:
            continue
        res = []
        for i, (body, eol) in enumerate(lines, 1):
            if i in edits:
                if edits[i] is None:
                    if i == len(lines) and not eol and res:
                        # deleted unterminated last line: keep the "no final newline" state
                        pb, pe = res[-1]
                        res[-1] = (pb, "")
                    continue
                res.append((edits[i], eol))
            else:
                res.append((body, eol))
        new_bytes[f] = "".join(b + e for b, e in res).encode("utf-8")
    return problems, new_bytes, keep_by_file


def atomic_write(path: Path, data: bytes):
    tmp = path.with_name(path.name + ".tmp-apply")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("batch")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    root = args.root.resolve()
    problems, new_bytes, keep = plan(root, args.batch)
    if problems:
        print(f"REFUSED: {len(problems)} problem(s) in batch {args.batch}; nothing written",
              file=sys.stderr)
        for p in problems:
            print(p, file=sys.stderr)
        return 1
    changed = [f for f, b in new_bytes.items() if (root / f).read_bytes() != b]
    for f in changed:
        print(("would update " if args.dry_run else "updated ") + f)
    if args.dry_run:
        print(f"dry run: {len(changed)} file(s) would change, "
              f"{sum(len(v) for v in keep.values())} keep literal(s)")
        return 0
    for f in changed:
        atomic_write(root / f, new_bytes[f])
    if keep:
        kl = root / BUILD / "keep-literals.json"
        data = json.loads(kl.read_text(encoding="utf-8")) if kl.is_file() else {}
        for f, lits in keep.items():
            data.setdefault(f, [])
            data[f] += [x for x in lits if x not in data[f]]
        atomic_write(kl, (json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
                     .encode("utf-8"))
    print(f"applied batch {args.batch}: {len(changed)} file(s) changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
