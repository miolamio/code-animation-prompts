# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

A Chinese-language library of code-animation style prompts, packaged as an installable Claude Code and Codex skill. The skill lives in `skills/code-animation-prompts/`, with an offline HTML picker, a search script and an HTML-to-MP4 renderer. Root `scripts/` holds maintainer tooling.

## Commands

There is no package manager, linter or test suite. `validate_repo.py` is the only gate: it is one flat pass with no flags and no way to run a single check. CI (`.github/workflows/validate.yml`) runs the validator plus a `styles.py` search and show smoke test on Ubuntu and Windows.

```bash
python3 scripts/validate_repo.py
python3 scripts/build_catalog.py
python3 scripts/build_visuals.py --browser-channel chrome --skip-video
python3 scripts/install_skill.py --target codex|claude|both --dry-run

python3 skills/code-animation-prompts/scripts/styles.py search 水墨 --limit 3
python3 skills/code-animation-prompts/scripts/styles.py show B3
python3 skills/code-animation-prompts/scripts/styles.py list --series Z
python3 skills/code-animation-prompts/scripts/render_video.py skills/code-animation-prompts/assets/starter/index.html --output output/demo.mp4 --duration 12 --fps 30 --width 1920 --height 1080
```

Search and install use only the standard library (Python 3.10+). `build_visuals.py` needs Playwright and Chromium; `render_video.py`, and `build_visuals.py` without `--skip-video`, also need FFmpeg.

## How the data fits together

- **Source of truth:** the JSON blob in `<script id="data">` inside `style-picker.html`, in `skills/code-animation-prompts/assets/library/`. `build_catalog.py` reads it.
- **Generated, so regenerate them:** `references/catalog.json` and `docs/STYLES.md` come from `build_catalog.py`. `docs/images/{hero,style-gallery,style-picker,picker-search}.png` and `b6-preview.gif` come from `build_visuals.py`.
- **Frozen baseline:** `docs/source-manifest.json` records the upstream pack. When validation fails, fix the change or its ledger entry and leave the manifest as it is.
- **Change ledger:** `references/library-changes.json` records every library file added or modified since the baseline, with `sha256`, `reason` and `contribution`; modified files also carry `original_sha256`. The validator hashes the library against manifest plus ledger, so an unregistered change fails, including a stray `.DS_Store`.
- **Counts pinned by the validator:** README headline, badge and count phrases; the still counts in `SKILL.md`; `_stats.json`, including `bySeries`. The total style count is hard-coded in `validate_repo.py`.
- **Import prompt:** the prompt in README must appear verbatim in `prompts/one-click-import.md`.

The validator also link-checks every `.md` outside the library, this file included, so relative links must resolve.

## Changing the library

- **Adding a still:** follow `CONTRIBUTING.md`. The steps span the picker, stats, ledger, attribution, generated files and counts. Commit `eef26f4` is a worked example of the correct shape.
- **Upstream records stay as shipped:** `README.md` keeps its original count of 193 stills on purpose (see `references/attribution.md`), so record changes in the ledger. Commit `b8e5453` edited that file and the manifest, and `eef26f4` reverted both.
- **Editing a prompt `.md`:** this needs a ledger entry. Picker entries have their own `prompt` field, so check that copy as well.
- **Adding a style:** there is no documented procedure. At minimum it touches the picker, `_stats.json`, the README series table and the hard-coded total.
- **B6 is not a style:** it is an example under `examples/` and has no index entry. The `B3` style is unrelated.

## Conventions

- **Names:** prompts are `<ID>_<name>.md`, with a same-stem `.jpg` if there is a still. Folders are `<series>_<label>`.
- **Prompt format:** `# <ID> <name>`, then bullets such as `- 分类：` and `- 长什么样：`, then `## 风格提示词` with the body. Bodies may be in English or bilingual under Chinese headers.
- **Language:** docs, README and `SKILL.md` are in Chinese. Script docstrings and assert messages are in English.
- **Byte preservation:** `.gitattributes` sets `-text` on the library so hashes hold across platforms.

## Licensing and attribution

`LICENSE.md` is a per-source provenance note, because the sources carry different terms. Keep the collection described as mixed-source, and never label it MIT as a whole.

- Put credit in `references/attribution.md`, so installed copies keep it.
- A JPEG-only contribution must not claim editable source.
- `docs/images/promo-hq.gif`, the README hero, has no source or script in this repo. `build_visuals.py` does not produce it.
