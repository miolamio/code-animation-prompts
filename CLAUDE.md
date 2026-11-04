# CLAUDE.md

English-only fork of a Chinese library of code-animation style prompts, packaged as a Claude Code and Codex skill. Upstream is `XiaoyeCodes/code-animation-prompts`; the fork is unofficial and free. Design decisions and accepted limits: `docs/superpowers/specs/2026-11-04-english-fork-design.md`.

## Commands

```bash
python3 scripts/validate_repo.py                     # The repo gate. No flags; stops at the first failed check.
python3 -m unittest discover -s scripts/translation  # Needs git and full history (upstream commit 103ac7e).
python3 scripts/build_catalog.py
python3 scripts/build_visuals.py
python3 scripts/install_skill.py
python3 skills/code-animation-prompts/scripts/styles.py
python3 skills/code-animation-prompts/scripts/render_video.py
```

Search and install need only the standard library (Python 3.10+). `build_visuals.py` needs Playwright and Chromium; video output needs FFmpeg. CI runs on Ubuntu and Windows, so tools decode git output and files as UTF-8 explicitly.

## Source and generated files

- **Source:** the JSON blob in `<script id="data">` of `skills/code-animation-prompts/assets/library/style-picker.html`. Edit it directly.
- **Generated:** `references/catalog.json` and `docs/STYLES.md` by `build_catalog.py`; `docs/images/` by `build_visuals.py`. The README hero is `docs/images/style-gallery.png`.
- **Finished records:** the migration tools in `scripts/translation/` did their one-off job, and `.build/` is local scratch. `migrate_picker.py` would rewrite the blob from the `.md` files, so leave them out of normal edits. Their tests still run in CI.

## Frozen baseline and ledger

`docs/source-manifest.json` holds the SHA-256 of every file in the translated library, including the K1-K3 stills. It stays frozen: when the check fails, fix the change or register it. `scripts/translation/build_manifest.py` refuses to overwrite it without `--force`, and `--force` is for replacing the baseline on purpose, at the owner's request.

`skills/code-animation-prompts/references/library-changes.json` is the ledger, and starts empty. Each changed library file needs an entry under `modified` or `added`, keyed by path relative to the library, with `sha256`, `reason` and a `contribution` key defined under `contributions`; `modified` entries add `original_sha256`. Any byte counts: a picker blob edit, a stray `.DS_Store`, a line ending. `.gitattributes` sets `-text` on the library so hashes hold on Windows.

A prompt lives twice: its `.md` and the blob's `prompt` field. Edit both and register both.

## Chinese-text gate

The validator fails on any Chinese character (U+3400-U+9FFF, U+F900-U+FAFF) in a tracked path or text file that `docs/translation/cjk-allowlist.json` does not cover. It also fails on stale entries, so the list only holds what is still there.

On a failure at `file:line`, translate the text. Add an entry only if the characters truly belong, using one of the five reasons: `style-literal`, `attribution`, `license-quote`, `media-source`, `translation-record`. `literals: null` is legal only with the last two. A style literal keeps an English gloss beside it, and the curator's name keeps its romanization. For a "stale" failure, remove the literal or entry. In code outside `scripts/translation/`, write Chinese ranges as `\u` escapes.

## Media showing Chinese

Media pixels stay unchanged. `docs/translation/media-with-chinese.json` lists stills and files that show Chinese or no longer match their rewritten prompts. Each entry under `stills` must equal that style's `note` in the picker blob, and `build_catalog.py` errors if they differ, so change both together.

## Upstream sync

Sync is by hand. Add the upstream remote, diff from `upstream_commit` in `docs/translation/path-map.json`, find each file's English path in the map's `paths`, then port and translate the change and register it in the ledger. The map stays pinned to that commit, because its tests compare against it.

## Library quirks

- **Empty stubs:** M14, M15, M16, M17, M26, M35, M39 and M40 (`*_untitled.md`) are empty upstream and count toward the 341 styles. They stay empty.
- **B6:** an example under `examples/` with no index entry, unrelated to the `B3` style.
- **193 stills:** the library `README.md` keeps this original count as a historical statement; current counts are 196 stills across the picker, `_stats.json`, README and `SKILL.md`.
- **Dead links:** `DEMO.md` links in prompt bodies are upstream's, so the link checker skips `style-prompts/`. It checks every other `.md`, this file included, so link here with backticks.
- **Adding a still:** follow `CONTRIBUTING.md`. Adding a style has no documented procedure; at minimum it touches the picker, `_stats.json`, the README series table and the total hard-coded in `validate_repo.py`.
- **Prompt format:** `# <ID> <name>`, then bullets such as `- Category:` and `- Looks like:`, then `## Style prompt`. Names are `<ID>_<slug>.md` with a same-stem `.jpg` for a still.

## Licence

`LICENSE.md` is a per-source provenance note, because the sources carry different terms. Keep the collection described as mixed-source, and label only the third-party parts MIT; their licence files stay byte-identical. The fork stays free and states that it is unofficial and not for resale. Put credit in `references/attribution.md` so installed copies keep it, and say plainly when a contribution is JPEG-only, with no editable source.
