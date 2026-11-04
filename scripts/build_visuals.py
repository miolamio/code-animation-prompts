"""Render README artwork from the real bundled stills and picker with Playwright."""
import argparse
import html
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/code-animation-prompts"
OUT = ROOT / "docs/images"
BUILD = ROOT / ".build"
MEDIA_NOTES = ROOT / "docs/translation/media-with-chinese.json"
GALLERY_SIZE = 12
GALLERY_CANDIDATES = ["E2", "G1", "C3", "L18", "L26", "L32", "L36", "L49", "L51", "O17", "O77", "O91",
                      "E1", "D4", "L31", "L47", "O30", "O85"]
PICKER_SEARCH = "blueprint"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser-channel", help="Use an installed browser, e.g. chrome or msedge")
    parser.add_argument("--skip-video", action="store_true", help="Refresh PNGs without regenerating the unchanged GIF")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(exist_ok=True)
    catalog = json.loads((SKILL / "references/catalog.json").read_text(encoding="utf-8"))
    entries = catalog["entries"]
    total = len(entries)
    with_still = sum(bool(e["image"]) for e in entries)
    text_only = total - with_still
    series_count = len(catalog["series"])
    by_id = {e["id"]: e for e in entries}

    listed = set(json.loads(MEDIA_NOTES.read_text(encoding="utf-8"))["stills"])
    gallery_ids = [id for id in GALLERY_CANDIDATES if id not in listed][:GALLERY_SIZE]
    if len(gallery_ids) < GALLERY_SIZE:
        raise SystemExit(f"Only {len(gallery_ids)} gallery candidates are free of Chinese; add more to GALLERY_CANDIDATES.")

    def card(id):
        e = by_id[id]
        src = (SKILL / e["image"]).as_uri()
        return f'<article><img src="{src}"><div><b>{id}</b><span>{html.escape(e["name"])}</span></div></article>'

    css = '''*{box-sizing:border-box}body{margin:0;font-family:"Segoe UI",sans-serif;background:#0d111a;color:#f4f6fa} .topline{font-size:14px;letter-spacing:3px;color:#b7f47b}h1,p{margin:0}article{overflow:hidden;border:1px solid #29313e;border-radius:14px;background:#141c28}article img{width:100%;aspect-ratio:16/9;object-fit:contain;display:block;background:#0a0c13}article div{display:flex;align-items:center;gap:14px;padding:16px 18px}article b{color:#b7f47b;font-family:Consolas,monospace;font-size:15px}article span{color:#dce2ed;font-size:16px}.foot{font-size:13px;letter-spacing:1px;color:#8591a6;display:flex;justify-content:space-between}'''
    gallery = f'''<!doctype html><meta charset="utf-8"><style>{css}body{{width:1600px;padding:52px 56px}}h1{{font-size:40px;margin:14px 0}}p{{color:#94a0b4;font-size:18px;margin-bottom:30px}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}}.foot{{margin-top:28px}}</style><div class="topline">A SMALL WINDOW INTO {total} STYLES</div><h1>One idea, many ways to show it.</h1><p>These are real reference stills from the library. Every ID leads to its prompt.</p><div class="grid">{''.join(card(x) for x in gallery_ids)}</div><div class="foot"><span>REFERENCE STILLS FROM THE INCLUDED LIBRARY</span><span>{with_still} WITH STILLS / {text_only} TEXT REFERENCES</span></div>'''
    # The picker screenshots show live cards, so hide the ones whose stills show Chinese.
    hide_listed = ",".join(f"#c-{id}" for id in sorted(listed)) + "{display:none!important}"
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, channel=args.browser_channel)
        page = browser.new_page(viewport={"width":1600,"height":1000}, device_scale_factor=1)
        path = BUILD / "style-gallery.html"
        path.write_text(gallery, encoding="utf-8", newline="\n")
        page.goto(path.as_uri())
        page.evaluate("document.fonts.ready")
        page.locator("img").evaluate_all("imgs => Promise.all(imgs.map(i => i.decode()))")
        page.locator("body").screenshot(path=str(OUT / "style-gallery.png"))
        page.goto((SKILL / "assets/library/style-picker.html").as_uri())
        page.add_style_tag(content=hide_listed)
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT / "style-picker.png"))
        page.locator('#q').fill(PICKER_SEARCH)
        page.wait_for_timeout(500)
        page.screenshot(path=str(OUT / "picker-search.png"))
        browser.close()
    if args.skip_video:
        print(f"README PNGs rendered: {total} styles, {with_still} stills, {text_only} text references.")
        return
    subprocess.run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", "3", "-t", "4",
        "-i", str(SKILL / "assets/library/examples/B6_warp-explode-reunite_same-prompt/Opus5.5_High.mp4"),
        "-filter_complex", "fps=10,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=none",
        "-loop", "0", str(OUT / "b6-preview.gif")
    ], check=True)
    print("README visuals rendered from original assets.")


if __name__ == "__main__":
    main()
