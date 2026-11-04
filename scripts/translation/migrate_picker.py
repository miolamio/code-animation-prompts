#!/usr/bin/env python3
"""Migrate the JSON blob in style-picker.html to English.

The current library .md files are authoritative: name comes from the glossary; cat, desc, fit,
tags, prompt and string `extra` items come from the entry's .md. Anything with no .md source that
still holds Chinese (or is a `desc_en` needing a decision) goes to .build/translation/picker-todo.json.
Answers live in .build/translation/picker-translations.json as {key: value}; a null value removes the field.

Rerunnable: the input may already be migrated, and a second run changes nothing. Any entry that
cannot be mapped raises MigrationError, leaving the page untouched.
"""

import copy
import json
import re
import sys
from pathlib import Path

from extract_segments import BUILD, CHINESE_RE, FULLWIDTH_RE

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = "skills/code-animation-prompts/assets/library"
BLOB_RE = re.compile(r'(<script id="data" type="application/json">)(.*?)(</script>)', re.S)
SECTION_RE = re.compile(r"^## Style prompt[ \t]*$", re.M)
NOTES_RE = re.compile(r"^## Notes[ \t]*$", re.M)
REWRITE_NOTE_RE = re.compile(r"\A> This prompt (?:is|was) [^\n]*\n*")
LABEL_RE = re.compile(r"^- ([^:\n]+): (.*)$", re.M)
FIT_LABELS = ("Best for", "Style")


class MigrationError(Exception):
    pass


def foreign(value, keep=()):
    """True if value still holds Chinese or fullwidth punctuation beyond the permitted literals."""
    text = json.dumps(value, ensure_ascii=False)
    for literal in keep:
        text = text.replace(literal, "")
    return bool(CHINESE_RE.search(text) or FULLWIDTH_RE.search(text))


def parse_md(entry, library):
    """Return (labels, prompt section, {note heading: body}) for an entry's .md."""
    path = library / entry["file"]
    if not path.is_file():
        raise MigrationError(f'{entry["id"]}: missing .md {entry["file"]}')
    text = path.read_text(encoding="utf-8")
    first_line = text.split("\n", 1)[0].split()
    if first_line[:2] != ["#", entry["id"]]:
        raise MigrationError(f'{entry["id"]}: heading of {entry["file"]} names another entry')
    section = SECTION_RE.search(text)
    if not section:
        raise MigrationError(f'{entry["id"]}: no "## Style prompt" section for its prompt')
    notes_match = NOTES_RE.search(text, section.end())
    prompt_end = notes_match.start() if notes_match else len(text)
    notes = {}
    if notes_match:
        parts = re.split(r"^### (.+)$", text[notes_match.end():], flags=re.M)
        notes = {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts), 2)}
    labels = dict(LABEL_RE.findall(text[:section.start()]))
    return labels, text[section.end():prompt_end].strip(), notes


def md_field(entry, field, value, keep):
    if foreign(value, keep):
        raise MigrationError(f'{entry["id"]}: {field} from .md still holds Chinese: {value[:60]!r}')
    return value


def migrate_entry(entry, library, glossary, keep):
    """Rewrite the .md-backed fields of one entry in place."""
    entry_id = entry["id"]
    if entry_id not in glossary["styles"]:
        raise MigrationError(f"{entry_id}: not in glossary styles")
    labels, section, notes = parse_md(entry, library)
    entry["name"] = glossary["styles"][entry_id]
    entry.pop("en", None)  # Identical to the English name; the page treats it as optional.

    category = labels.get("Category", "")
    if " · " not in category:
        raise MigrationError(f"{entry_id}: no usable Category line: {category!r}")
    entry["cat"] = md_field(entry, "cat", category.split(" · ", 1)[1].strip(), keep)

    if "Looks like" in labels:
        entry["desc"] = md_field(entry, "desc", labels["Looks like"].strip(), keep)
    fit = next((labels[label] for label in FIT_LABELS if label in labels), None)
    if fit is not None:
        entry["fit"] = md_field(entry, "fit", fit.strip(), keep)
    if "Keywords" in labels:
        tags = [tag.strip() for tag in labels["Keywords"].split(", ")]
        if not entry.get("tags") or len(tags) == len(entry["tags"]):
            entry["tags"] = md_field(entry, "tags", tags, keep)

    if entry.get("prompt"):
        prompt = REWRITE_NOTE_RE.sub("", section).strip()
        if not prompt:
            raise MigrationError(f"{entry_id}: prompt has no .md section body")
        entry["prompt"] = md_field(entry, "prompt", prompt, keep)
    entry.pop("prompt_en", None)

    hints = {}
    english_labels = set(glossary["labels"].values())
    for index, item in enumerate(entry.get("extra", [])):
        heading = glossary["labels"].get(item["h"], item["h"])
        if heading not in english_labels:
            raise MigrationError(f'{entry_id}: extra heading {item["h"]} is not in glossary labels')
        item["h"] = heading
        if heading in notes:
            hints[f"{entry_id}.extra.{index}.t"] = notes[heading]
            if isinstance(item["t"], str):
                item["t"] = md_field(entry, f"extra {heading}", notes[heading], keep)
    return hints


def apply_translations(data, translations):
    entries = {e["id"]: e for e in data["entries"]}
    meta = {m["id"]: m for m in data["meta"]}
    for key, value in translations.items():
        if foreign(value):
            raise MigrationError(f"{key}: translation still holds Chinese")
        parts = key.split(".")
        target = meta.get(parts[1]) if parts[0] == "meta" else entries.get(parts[0])
        if target is None:
            raise MigrationError(f"{key}: unknown entry in translations")
        path = parts[2:] if parts[0] == "meta" else parts[1:]
        for step in path[:-1]:
            target = target[int(step)] if isinstance(target, list) else target[step]
        if value is None:
            target.pop(path[-1], None)
        else:
            target[path[-1]] = value


def find_todo(data, hints, keep):
    """List every field still needing a translation or a decision."""
    todo = []

    def add(key, source):
        item = {"key": key, "source": source}
        if key in hints:
            item["md"] = hints[key]
        todo.append(item)

    for meta in data["meta"]:
        for field, value in meta.items():
            if foreign(value):
                add(f'meta.{meta["id"]}.{field}', value)
    if foreign(data.get("skills", [])):
        raise MigrationError("skills: unexpected Chinese in the blob's skills list")
    for entry in data["entries"]:
        allowed = keep.get(entry["file"], ())
        for field, value in entry.items():
            if field == "extra":
                for index, item in enumerate(value):
                    if foreign(item["t"], allowed):
                        add(f'{entry["id"]}.extra.{index}.t', item["t"])
            elif field == "desc_en" or foreign(value, allowed):
                add(f'{entry["id"]}.{field}', value)
    return todo


def check_groups(old_entries, new_entries):
    """Within a series, entries must share a category after migration exactly when they did before."""
    new_by_id = {e["id"]: e for e in new_entries}
    forward, backward = {}, {}
    for old in old_entries:
        series, old_cat, new_cat = old["s"], old["cat"], new_by_id[old["id"]]["cat"]
        if forward.setdefault((series, old_cat), new_cat) != new_cat:
            raise MigrationError(f"{series}: category group {old_cat} split into {new_cat} and {forward[series, old_cat]}")
        if backward.setdefault((series, new_cat), old_cat) != old_cat:
            raise MigrationError(f"{series}: category group {new_cat} merges {old_cat} and {backward[series, new_cat]}")


def migrate(data, library, glossary, translations=None, keep=None):
    """Return (migrated blob, todo items). `data` is not modified."""
    keep = keep or {}
    original = data["entries"]
    data = copy.deepcopy(data)
    hints = {}
    for entry in data["entries"]:
        hints.update(migrate_entry(entry, library, glossary, keep.get(entry["file"], ())))
    apply_translations(data, translations or {})
    check_groups(original, data["entries"])
    return data, find_todo(data, hints, keep)


def parse_blob(html):
    match = BLOB_RE.search(html)
    if not match:
        raise MigrationError('no <script id="data"> block in the picker')
    return json.loads(match.group(2))


def dump_blob(data):
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return text.replace("</", "<\\/").replace("<!--", "\\u003c!--")  # Prose must not close the data block.


def read_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default


def run(root=ROOT):
    root = Path(root)
    library = root / LIBRARY
    page = library / "style-picker.html"
    html = page.read_bytes().decode("utf-8")
    glossary = read_json(root / "docs/translation/glossary.json", None)
    keep = {path.removeprefix(LIBRARY + "/"): literals
            for path, literals in read_json(root / BUILD / "keep-literals.json", {}).items()}
    translations = read_json(root / BUILD / "picker-translations.json", {})
    data, todo = migrate(parse_blob(html), library, glossary, translations=translations, keep=keep)
    new_html = BLOB_RE.sub(lambda m: m.group(1) + dump_blob(data) + m.group(3), html, count=1)
    page.write_bytes(new_html.encode("utf-8"))
    todo_path = root / BUILD / "picker-todo.json"
    todo_path.parent.mkdir(parents=True, exist_ok=True)
    todo_path.write_text(json.dumps({"count": len(todo), "items": todo}, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8", newline="\n")
    return data, todo


if __name__ == "__main__":
    try:
        migrated, remaining = run()
        print(f'Migrated {len(migrated["entries"])} entries; {len(remaining)} items in {BUILD}/picker-todo.json.')
    except MigrationError as error:
        sys.exit(f"FAILED: {error}")
