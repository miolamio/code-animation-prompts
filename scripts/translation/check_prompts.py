#!/usr/bin/env python3
"""Compare translated library files with their upstream (Chinese) versions.

Upstream = `git show <upstream_commit>:<chinese path>` using docs/translation/path-map.json.
Findings, one per line: `file: kind: detail` with kind in code-fences, placeholders, urls,
numbers, no-upstream. A2/A3/A4/F2 (code intentionally rewritten) are reported as
`file: expected-rewrite: <kind>: detail` in their own section and do not fail the run.
Exit code 1 if any unexplained finding exists.
Lines translators deleted (null in .build/translation/out/*.json) are dropped from the
upstream side first.
"""

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

from extract_segments import BUILD, CHINESE_RE, FULLWIDTH_RE, ROOT, count_fences, split_lines

REWRITE_IDS = ("A2", "A3", "A4", "F2")
PLACEHOLDER_RE = re.compile(r"\{\{\s*([^{}]*?)\s*\}\}")
URL_RE = re.compile(r"https?://[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+")
HEX_RE = re.compile(r"(?<![A-Za-z0-9_&])#(?:[0-9A-Fa-f]{8}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{4}|[0-9A-Fa-f]{3})(?![A-Za-z0-9])")
NUM_RE = re.compile(
    r"(?:(?<![A-Za-z0-9_.#])|(?<=\dx))(\d+(?:\.\d+)?)"
    r"(?:(px|ms|fps|deg|rem|em|vh|vw|pt|%|s|k|K)(?![A-Za-z]))?")


def nfc(s):
    return unicodedata.normalize("NFC", s)


def git_out(root, *args):
    return subprocess.run(["git", "-c", "core.quotepath=off", "-C", str(root), *args],
                          check=True, capture_output=True).stdout


def clean_url(u):
    u = u.rstrip(".,;:!?'*")
    while u.endswith(")") and u.count(")") > u.count("("):
        u = u[:-1].rstrip(".,;:!?'*")
    return u


def facts(text: str) -> dict:
    lines = [b for b, _ in split_lines(text)]
    urls = {clean_url(u) for u in URL_RE.findall(text)}
    stripped = URL_RE.sub(" ", text)
    hexes = {h.lower() for h in HEX_RE.findall(stripped)}
    stripped = HEX_RE.sub(" ", stripped)
    nums = set((m.group(1), m.group(2) or "") for m in NUM_RE.finditer(stripped))
    phs = PLACEHOLDER_RE.findall(text)
    # Placeholders whose "name" is Chinese prose (e.g. {{默认：家}}) are translated by design,
    # so only identifier-like names are compared by name; all placeholders are compared by count.
    named = {re.sub(r"\s+", "", p) for p in phs
             if p and not CHINESE_RE.search(p) and not FULLWIDTH_RE.search(p)}
    return {"fences": count_fences(lines), "ph_count": len(phs), "placeholders": named,
            "urls": urls, "hex": hexes, "nums": nums}


def num_missing(up, now):
    """Upstream (value, unit) tokens that have no counterpart now. Units are matched
    strictly only when both sides carry one ('12px' vs '12pt'); a bare number on either
    side counts as a match ('0.9s' vs '0.9 s', '1.05倍' vs '1.05x')."""
    missing = []
    for v, u in sorted(up, key=lambda t: (float(t[0]), t[1])):
        if not any(v == v2 and (u == u2 or not u or not u2) for v2, u2 in now):
            missing.append(v + u)
    return missing


def diff(up_text, now_text):
    up, now = facts(up_text), facts(now_text)
    out = []
    if up["fences"] != now["fences"]:
        out.append(("code-fences", f"upstream {up['fences']}, now {now['fences']}"))
    if up["ph_count"] != now["ph_count"]:
        out.append(("placeholders", f"count upstream {up['ph_count']}, now {now['ph_count']}"))
    for kind, key in (("placeholders", "placeholders"), ("urls", "urls")):
        lost, added = sorted(up[key] - now[key]), sorted(now[key] - up[key])
        if key == "placeholders":
            added = []   # translated prose placeholders legitimately add new ASCII names
        if lost or added:
            fmt = (lambda xs: ", ".join("{{%s}}" % x for x in xs)) if key == "placeholders" \
                else (lambda xs: ", ".join(xs))
            parts = ([f"missing {fmt(lost)}"] if lost else []) + ([f"added {fmt(added)}"] if added else [])
            out.append((kind, "; ".join(parts)))
    lost = sorted(up["hex"] - now["hex"]) + num_missing(up["nums"], now["nums"])
    if lost:
        out.append(("numbers", "missing " + ", ".join(lost)))
    return out


def load_deletions(root):
    dele = {}
    out_dir = root / BUILD / "out"
    if out_dir.is_dir():
        for p in sorted(out_dir.glob("*.json")):
            for f, lines in json.loads(p.read_text(encoding="utf-8")).items():
                for ln, v in lines.items():
                    if v is None:
                        dele.setdefault(f, set()).add(int(ln))
    return dele


class Upstream:
    def __init__(self, root):
        m = json.loads((root / "docs/translation/path-map.json").read_text(encoding="utf-8"))
        self.root, self.commit = root, m["upstream_commit"]
        self.rev = {nfc(en): cn for cn, en in m["paths"].items()}
        self.tree = None

    def text(self, en_path):
        cn = self.rev.get(nfc(en_path))
        if cn is None:
            return None
        if self.tree is None:
            raw = git_out(self.root, "ls-tree", "-r", "-z", "--name-only", self.commit)
            self.tree = {nfc(p.decode("utf-8")): p.decode("utf-8") for p in raw.split(b"\0") if p}
        real = self.tree.get(nfc(cn))
        if real is None:
            return None
        return git_out(self.root, "show", f"{self.commit}:{real}").decode("utf-8")


def is_rewrite(path):
    name = Path(path).name
    return any(name.startswith(i + "_") for i in REWRITE_IDS)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--batch")
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    root = args.root.resolve()
    if args.batch:
        sp = root / BUILD / "segments" / f"{args.batch}.json"
        if not sp.is_file():
            print(f"{sp}: segments file not found", file=sys.stderr)
            return 2
        files = list(json.loads(sp.read_text(encoding="utf-8")))
    else:
        files = [Path(f).resolve().relative_to(root).as_posix() if Path(f).is_absolute() else f
                 for f in args.files]
    if not files:
        ap.error("give --batch or at least one file")
    up, dele = Upstream(root), load_deletions(root)
    fails, rewrites = [], []
    for f in files:
        text = up.text(f)
        if text is None:
            fails.append(f"{f}: no-upstream: not in path-map.json or missing at {up.commit[:7]}")
            continue
        drop = dele.get(f, set())
        if drop:
            text = "".join(b + e for i, (b, e) in enumerate(split_lines(text), 1) if i not in drop)
        now = (root / f).read_bytes().decode("utf-8")
        for kind, detail in diff(text, now):
            if is_rewrite(f):
                rewrites.append(f"{f}: expected-rewrite: {kind}: {detail}")
            else:
                fails.append(f"{f}: {kind}: {detail}")
    for line in fails:
        print(line)
    if rewrites:
        print("# expected-rewrite (code intentionally rewritten, not failures)")
        for line in rewrites:
            print(line)
    print(f"# {len(files)} file(s) checked, {len(fails)} unexplained, {len(rewrites)} expected-rewrite",
          file=sys.stderr)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
