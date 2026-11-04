"""Validate the translated baseline, the change ledger, the Chinese-text allowlist, counts and local links."""
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/code-animation-prompts"
LIBRARY = SKILL / "assets/library"
ALLOWLIST = "docs/translation/cjk-allowlist.json"
IMPORT_PROMPT = ("Install https://github.com/miolamio/code-animation-prompts "
                 "as a skill available to the current coding assistant.")

CHINESE_RE = re.compile("[\u3400-\u9fff\uf900-\ufaff]")
CHINESE_RUN_RE = re.compile("[\u3400-\u9fff\uf900-\ufaff]+")
MEDIA_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".mp4"}
REASONS = {"style-literal", "attribution", "license-quote", "media-source", "translation-record"}
WHOLE_PATH_REASONS = {"media-source", "translation-record"}


def tracked_files(root):
    output = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], check=True, capture_output=True).stdout
    return [name for name in output.decode("utf-8").split("\0") if name]


def glob_regex(pattern):
    """`**` crosses folders, `*` and `?` stay inside one path segment."""
    tokens = {"**": ".*", "*": "[^/]*", "?": "[^/]"}
    return re.compile("".join(tokens.get(part) or re.escape(part) for part in re.split(r"(\*\*|\*|\?)", pattern)))


def entry_problems(entry):
    """Everything wrong with one allowlist entry's own shape."""
    if not isinstance(entry, dict) or set(entry) != {"path", "literals", "reason"}:
        return [f"allowlist entry {entry!r}: expected the keys path, literals and reason"]
    label, literals, reason = f'allowlist entry {entry["path"]}', entry["literals"], entry["reason"]
    if reason not in REASONS:
        return [f"{label}: unknown reason {reason!r}"]
    if literals is None:
        return [] if reason in WHOLE_PATH_REASONS else [f"{label}: literals null is not legal with reason {reason}"]
    if not isinstance(literals, list) or not literals:
        return [f"{label}: literals must be null or a non-empty list"]
    return [f"{label}: literal {literal!r} holds no Chinese" for literal in literals
            if not isinstance(literal, str) or not CHINESE_RE.search(literal)]


def scan_chinese(root, allowlist, tracked=None):
    """Return (problems, stats) for every tracked path and text file against the allowlist."""
    tracked = tracked_files(root) if tracked is None else tracked
    problems = [problem for entry in allowlist for problem in entry_problems(entry)]
    entries = [entry for entry in allowlist if not entry_problems(entry)]
    matches = [(entry, glob_regex(entry["path"])) for entry in entries]
    used, reasons_by_file, text_files = set(), {}, 0

    for name in tracked:
        covering = [entry for entry, regex in matches if regex.fullmatch(name)]
        whole = [entry for entry in covering if entry["literals"] is None]
        if CHINESE_RE.search(name) and not whole:
            problems.append(f"{name}: Chinese in the file path")
        path = Path(root) / name
        if Path(name).suffix.lower() in MEDIA_SUFFIXES or not path.is_file():
            continue
        try:
            text = path.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            problems.append(f"{name}: not UTF-8, so it cannot be checked for Chinese")
            continue
        text_files += 1
        if whole and CHINESE_RE.search(name + text):
            used.update((id(entry), None) for entry in whole)
        if not CHINESE_RE.search(text):
            continue
        if whole:
            reasons_by_file[name] = {entry["reason"] for entry in whole}
            continue
        reasons = reasons_by_file.setdefault(name, set())
        literals = {literal for entry in covering for literal in entry["literals"]}
        for literal in sorted(literals, key=len, reverse=True):  # A longer literal must not read as a shorter one.
            if literal in text:
                text = text.replace(literal, "")
                for entry in covering:
                    if literal in entry["literals"]:
                        used.add((id(entry), literal))
                        reasons.add(entry["reason"])
        for number, line in enumerate(text.split("\n"), 1):
            for run in CHINESE_RUN_RE.findall(line):
                problems.append(f"{name}:{number}: Chinese not covered by the allowlist: {run!r}")

    for entry, regex in matches:
        label = f'allowlist entry {entry["path"]}'
        if not any(regex.fullmatch(name) for name in tracked):
            problems.append(f"{label}: stale, it matches no tracked file")
        elif entry["literals"] is None:
            if (id(entry), None) not in used:
                problems.append(f"{label}: stale, nothing under it holds Chinese any more")
        else:
            problems.extend(f"{label}: stale, literal {literal!r} no longer occurs" for literal in entry["literals"]
                            if (id(entry), literal) not in used)
    counts = collections.Counter(reason for reasons in reasons_by_file.values() for reason in reasons)
    return problems, {"text_files": text_files, "with_chinese": len(reasons_by_file), "by_reason": dict(counts)}


def check_chinese(root, allowlist, tracked=None):
    """Return the list of gate failures; an empty list means the gate passes."""
    return scan_chinese(root, allowlist, tracked)[0]


def validate_library(library, manifest, changes):
    baseline = manifest["files"]
    modified, added = changes["modified"], changes["added"]
    assert manifest["file_count"] == len(baseline), "Baseline manifest count differs"
    assert set(modified) <= set(baseline), "Modified file is not in the baseline"
    assert not set(added) & set(baseline), "Added file overlaps the baseline"
    files = {p.relative_to(library).as_posix(): p for p in library.rglob("*") if p.is_file()}
    expected = set(baseline) | set(added)
    assert set(files) == expected, ("Library file set differs from baseline plus additions: "
                                    f"unexpected {sorted(set(files) - expected)}, missing {sorted(expected - set(files))}")
    for name, record in {**modified, **added}.items():
        assert record["contribution"] in changes["contributions"], f"Missing contribution source: {name}"
        assert record["reason"].strip(), f"Missing change reason: {name}"
    for name, digest in baseline.items():
        if name in modified:
            record = modified[name]
            assert record["original_sha256"] == digest, f"Baseline hash mismatch in the ledger: {name}"
            digest = record["sha256"]
        assert hashlib.sha256(files[name].read_bytes()).hexdigest() == digest, f"Unregistered library change: {name}"
    for name, record in added.items():
        assert hashlib.sha256(files[name].read_bytes()).hexdigest() == record["sha256"], f"Added file changed: {name}"
    return len(baseline) - len(modified), len(modified), len(added)


def check_local_links():
    """Prompt bodies under style-prompts/ keep upstream's dead demo links, so that folder is left out."""
    checked = 0
    for doc in ROOT.rglob("*.md"):
        if any(part in {".git", ".build", ".agents", ".claude"} for part in doc.relative_to(ROOT).parts):
            continue
        if LIBRARY / "style-prompts" in doc.parents:
            continue
        for target in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding="utf-8")):
            if target.startswith(("http:", "https:", "mailto:", "#")):
                continue
            path = unquote(target.split("#")[0])
            assert (doc.parent / path).exists(), f"Broken link: {doc.relative_to(ROOT)} -> {target}"
            checked += 1
    return checked


def main():
    manifest = json.loads((ROOT / "docs/source-manifest.json").read_text(encoding="utf-8"))
    changes = json.loads((SKILL / "references/library-changes.json").read_text(encoding="utf-8"))
    path_map = json.loads((ROOT / "docs/translation/path-map.json").read_text(encoding="utf-8"))
    assert manifest["upstream_commit"] == path_map["upstream_commit"], "Manifest and path map name different upstreams"
    unchanged, modified, added = validate_library(LIBRARY, manifest, changes)

    allowlist = json.loads((ROOT / ALLOWLIST).read_text(encoding="utf-8"))
    problems, chinese = scan_chinese(ROOT, allowlist)
    assert not problems, ("\n".join(problems) + f"\nTranslate the text, or if it truly belongs, add it to {ALLOWLIST}.")

    data = json.loads((SKILL / "references/catalog.json").read_text(encoding="utf-8"))
    assert data["total"] == len(data["entries"]) == 341
    assert len({e["id"] for e in data["entries"]}) == 341
    stills = sum(bool(e["image"]) for e in data["entries"])
    assert stills == data["with_still"]
    stats = json.loads((LIBRARY / "_stats.json").read_text(encoding="utf-8"))
    assert (stats["total"], stats["withStill"]) == (data["total"], stills)
    picker = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>',
                                 (LIBRARY / "style-picker.html").read_text(encoding="utf-8"), re.S).group(1))
    picker_entries = {e["id"]: e for e in picker["entries"]}
    assert len(picker_entries) == len(picker["entries"]) == data["total"]
    for entry in data["entries"]:
        source = picker_entries[entry["id"]]
        assert entry["file"] == "assets/library/" + source["file"]
        assert entry["image"] == ("assets/library/" + source["img"] if source.get("img") else "")
        for key in ["file", "image"]:
            if entry[key]:
                assert (SKILL / entry[key]).is_file(), entry[key]
    checked = check_local_links()

    total, text_only = data["total"], data["total"] - stills
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert f'{total} style prompts | {stills} reference stills' in readme, "README headline counts are stale"
    assert f'reference_stills-{stills}-' in readme, "README badge count is stale"
    assert f'**{stills} have stills, {text_only} are text references**' in readme, "README summary counts are stale"
    assert f'**{stills} stills + {text_only} text references**' in readme, "README table counts are stale"
    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert f'{total} prompts, {stills} reference stills' in skill, "Skill counts are stale"
    assert f'{text_only} entries have no still' in skill, "Skill counts are stale"
    assert f'{stills} entries have stills' in (ROOT / "docs/STYLES.md").read_text(encoding="utf-8"), "Style index count is stale"
    assert IMPORT_PROMPT in readme, "README import prompt is stale"
    assert IMPORT_PROMPT in (ROOT / "prompts/one-click-import.md").read_text(encoding="utf-8"), "Import prompt file is stale"

    by_reason = ", ".join(f"{reason} {count}" for reason, count in sorted(chinese["by_reason"].items()))
    print(f"PASS: {unchanged} library files match the translated baseline; {modified} registered modifications; "
          f"{added} registered additions; {total} styles; {stills} stills; {checked} local links; "
          f"{chinese['text_files']} tracked text files scanned, {chinese['with_chinese']} with allowlisted Chinese "
          f"({by_reason}); counts and import prompt consistent.")


if __name__ == "__main__":
    main()
