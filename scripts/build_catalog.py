"""Rebuild the lightweight skill catalog and browsable Markdown index."""
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/code-animation-prompts"
LIBRARY = SKILL / "assets/library"
MEDIA_NOTES = ROOT / "docs/translation/media-with-chinese.json"


def main():
    html = (LIBRARY / "style-picker.html").read_text(encoding="utf-8")
    raw = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S).group(1))
    notes = {k: v["note"] for k, v in json.loads(MEDIA_NOTES.read_text(encoding="utf-8"))["stills"].items()}
    entries = []
    for e in raw["entries"]:
        note = notes.pop(e["id"], None)
        if e.get("note") != note:
            raise ValueError(f'{e["id"]}: picker note differs from {MEDIA_NOTES.name}; run scripts/translation/migrate_picker.py')
        for field in ["file", "img"]:
            if e.get(field):
                path = (LIBRARY / e[field]).resolve()
                if LIBRARY.resolve() not in path.parents or not path.is_file():
                    raise ValueError(f"Missing or invalid asset: {e[field]}")
        entries.append(dict(id=e["id"], name=e["name"], series=e["s"], category=e["cat"],
                            description=e.get("desc", ""), fit=e.get("fit", ""), tags=e.get("tags", []),
                            file="assets/library/" + e["file"],
                            image="assets/library/" + e["img"] if e.get("img") else "",
                            **({"reference_note": note} if note else {})))
    if notes:
        raise ValueError(f"Notes for unknown entries in {MEDIA_NOTES.name}: {sorted(notes)}")
    counts = dict(Counter(e["series"] for e in entries))
    stats = json.loads((LIBRARY / "_stats.json").read_text(encoding="utf-8"))
    assert len(entries) == stats["total"] == len({e["id"] for e in entries})
    assert sum(bool(e["image"]) for e in entries) == stats["withStill"]
    assert counts == stats["bySeries"]
    catalog = dict(total=len(entries), with_still=stats["withStill"],
                   series=[dict(id=m["id"], name=m["label"], count=counts[m["id"]]) for m in raw["meta"]], entries=entries)
    (SKILL / "references/catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    lines = [f"# Index of {catalog['total']} styles", "", f"Generated from the offline picker. Click a name to read its prompt; {catalog['with_still']} entries have stills, the rest are text references. A note after a still means it shows Chinese or no longer matches its prompt.", "", "[Back to README](../README.md)", ""]
    for series in catalog["series"]:
        lines += [f'## {series["name"]} · {series["count"]}', "", "| ID | Style | Reference |", "|---|---|---|"]
        for e in entries:
            if e["series"] == series["id"]:
                link = "../skills/code-animation-prompts/"
                name = e["name"].replace("|", "\\|")
                shot = f'[Still]({quote(link + e["image"])})' if e["image"] else "Text reference"
                if e.get("reference_note"):
                    shot += " · Note: " + e["reference_note"].replace("|", "\\|")
                lines.append(f'| {e["id"]} | [{name}]({quote(link + e["file"])}) | {shot} |')
        lines.append("")
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/STYLES.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"Validated {len(entries)} styles and {stats['withStill']} stills.")


if __name__ == "__main__":
    main()
