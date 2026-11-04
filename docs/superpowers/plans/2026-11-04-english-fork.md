# English-only Fork Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the fork into an English-only library with every style working and every source credited, as specified in `docs/superpowers/specs/2026-11-04-english-fork-design.md`.

**Architecture:** Paths are renamed first from a reviewed map. Chinese text is then translated line by line through an extract, translate, apply pipeline, so non-Chinese lines stay byte-identical. Picker data is rebuilt from translated files plus a separate pass over picker-only fields. The validator moves to a new baseline with a Chinese-text gate.

**Tech Stack:** Python 3.10+ standard library, `unittest` for tool tests, Playwright with Chromium for rendering checks.

**Working rules for every task:**
- Work on branch `english-translation` in `/Users/codegeek/src/code-animation-prompts`.
- Upstream baseline is commit `103ac7e`; read originals with `git -c core.quotepath=off show 103ac7e:<path>`.
- Only the coordinator commits and pushes. Subagents leave changes in the working tree and report the files they touched.
- Intermediate data goes in `.build/translation/`, which the validator skips. Task 1 adds it to `.gitignore` if it is not already ignored.
- Migration tools live in `scripts/translation/` with tests in `scripts/translation/test_*.py`, run by `python3 -m unittest discover -s scripts/translation`.

---

### Task 1: Glossary and path map

**Files:**
- Create: `docs/translation/glossary.json`, `docs/translation/path-map.json`, `scripts/translation/build_path_map.py`, `scripts/translation/test_build_path_map.py`

- [ ] **Step 1:** Write `glossary.json` with `series` (series ID to English label), `styles` (style ID to English name, using the picker's `en` field where it exists), `terms` (recurring Chinese terms to one English rendering) and `labels` (metadata labels: 分类 Category, 长什么样 Looks like, 适合 Best for, 关键词 Keywords, 风格 Style, 年份 Year, 风格提示词 Style prompt).
- [ ] **Step 2:** Write failing tests for `build_path_map.py`: every tracked path with Chinese gets an entry; targets contain no Chinese; targets are unique on a case-insensitive filesystem; `.md` and `.jpg` stems stay paired; style IDs stay as the filename prefix; slugs are lowercase ASCII with hyphens, with folder form `<series>_<label>`.
- [ ] **Step 3:** Implement the script so it emits `{"upstream_commit": "103ac7e...", "paths": {zh: en}}`. Hand-named non-style paths go in a dict in the script: the picker becomes `style-picker.html`, the shared helper becomes `_shared-functions.js`, the stats file becomes `_stats.json`.
- [ ] **Step 4:** Run the tests and confirm they pass. Report the map's entry count, which must equal the count of tracked paths containing Chinese, and any collisions.

### Task 2: Rename paths

**Files:**
- Create: `scripts/translation/apply_path_map.py`
- Modify: all paths in `docs/translation/path-map.json`

- [ ] **Step 1:** Implement `apply_path_map.py` using `git mv` only, creating parent folders and removing emptied ones. It takes `--dry-run`.
- [ ] **Step 2:** Run `--dry-run`, then for real. `git status` must show renames only, and `git diff --cached -M --stat` must show 0 line changes for renamed files.
- [ ] **Step 3:** Coordinator commits as `refactor: rename Chinese paths to English`.

### Task 3: Fix references to renamed paths

**Files:**
- Modify: `scripts/validate_repo.py`, `scripts/build_catalog.py`, `scripts/build_visuals.py`, `.github/workflows/validate.yml`, `.gitattributes`, `README.md`, `CONTRIBUTING.md`, `LICENSE.md`, `docs/INSTALL.md`, `skills/code-animation-prompts/SKILL.md`, `skills/code-animation-prompts/references/*`, `skills/code-animation-prompts/assets/library/style-picker.html`, prompts that name `_公共函数.js`

- [ ] **Step 1:** Replace every old path in text with its mapped path, including `file` and `img` in the picker blob and paths in `library-changes.json`. Update the picker's own folder references at its lines 104 and 109. Leave prose translation to later tasks.
- [ ] **Step 2:** Run `python3 scripts/build_catalog.py`. Run `python3 skills/code-animation-prompts/scripts/styles.py show B3` and confirm the path it prints exists. Temporarily loosen only the manifest comparison so link checks can run, then run `python3 scripts/validate_repo.py`: every local link must resolve. Task 8 replaces this loosening.
- [ ] **Step 3:** Coordinator commits as `refactor: update references to renamed paths`.

### Task 4: Translation pipeline

**Files:**
- Create: `scripts/translation/extract_segments.py`, `scripts/translation/apply_segments.py`, `scripts/translation/check_prompts.py`, `scripts/translation/test_segments.py`

- [ ] **Step 1:** Write failing tests:
  - Extract emits `{file: {line_no: text}}` for lines with Chinese only, tagging lines inside code fences with `"code": true`.
  - Apply replaces the line, deletes on `null`, leaves all other bytes unchanged including line endings, and exits non-zero if a segment has no translation or an output still has Chinese that isn't marked `"keep": ["literal"]`.
  - `check_prompts` compares a translated file with its upstream version and reports differences in code-fence count, `{{ }}` placeholder names, URLs and numbers. For O files, content from the deleted Chinese prompt section is excluded.
- [ ] **Step 2:** Implement all three and run the tests until they pass.
- [ ] **Step 3:** Run extract into `.build/translation/segments/<batch>.json`, one file per batch below, and report the Chinese-character count per batch.

### Task 5: Translate prompts (parallel batches)

**Batches:** `A-G` with `Z`; `K` with `H`; `L`; `M`; `V` with `X` and `R`; `O` part 1; `O` part 2; library docs and examples, excluding B6 HTML.

Output for each batch: `.build/translation/out/<batch>.json`, one entry per segment.

- [ ] **Step 1:** Each translator reads `docs/translation/glossary.json` and the design spec's decisions, then translates every segment. Rules:
  - Use glossary terms exactly.
  - Prompt text keeps its role as instructions to an AI, in natural English rather than word-for-word, with every number, unit, colour value, technical parameter and placeholder name preserved.
  - Literals named in the spec stay as Chinese with an English gloss, marked `keep`.
  - Requirements for Chinese on screen, Chinese fonts or Chinese speech become the user's language.
  - Series O: delete the Chinese prompt lines that duplicate the English prompt, and translate the notes.
- [ ] **Step 2:** A2, A3, A4 and F2 are in the first batch and rewrite their code for English strings: character counts in `['del', n]`, per-word coordinates, tunnel strings and lookup keys all follow the new strings.
- [ ] **Step 3:** Apply each batch, then run `check_prompts.py` over it. The bar for a batch is every segment applied and every report line explained or fixed.
- [ ] **Step 4:** Coordinator commits each batch as `feat(library): translate <batch> prompts to English`.

### Task 6: Verify rewritten code and review translation quality

**Files:**
- Modify: translated prompts, only where review finds an error

- [ ] **Step 1:** A fresh agent extracts the code from A2, A3, A4 and F2, runs each in Chromium through a harness in the scratchpad that stubs `PARENT` and `SERIF`, and renders at least 5 frames at different times. Pass: no exception, and a screenshot showing readable English.
- [ ] **Step 2:** Independent reviewers, who did not translate the batch, compare against upstream every prompt with a `keep` literal or rewritten code, plus at least 10% of each batch chosen by a fixed random seed. They report meaning changes, dropped constraints, and glossary drift.
- [ ] **Step 3:** Fix confirmed findings, re-run `check_prompts.py`. Coordinator commits as `fix(library): apply translation review findings`.

### Task 7: Picker and generated catalog

**Files:**
- Create: `scripts/translation/migrate_picker.py`, `scripts/translation/test_migrate_picker.py`
- Modify: `skills/code-animation-prompts/assets/library/style-picker.html`, `skills/code-animation-prompts/scripts/styles.py`, `scripts/build_catalog.py`, `references/catalog.json`, `docs/STYLES.md`

- [ ] **Step 1:** Write failing tests, then implement `migrate_picker.py`: `name`, `cat`, `desc`, `fit`, `tags` come from the translated `.md` and the glossary; `prompt` is rebuilt line by line from the same segment outputs; `en`, `desc_en` and `prompt_en` are reused; O's `extra` and any remaining fields are listed for translation.
- [ ] **Step 2:** A translator handles the listed fields plus about 60 UI strings. Set `lang="en"` and make the search index cover the English fields.
- [ ] **Step 3:** Translate the labels in `styles.py` and the generated text in `build_catalog.py`, then run `python3 scripts/build_catalog.py`. `styles.py search ink` must return hits. Coordinator commits as `feat(picker): migrate picker and catalog to English`.

### Task 8: Docs, license, validator and media

**Files:**
- Create: `docs/translation/cjk-allowlist.json`, `docs/translation/media-with-chinese.json`
- Modify: `README.md`, `CONTRIBUTING.md`, `LICENSE.md`, `docs/INSTALL.md`, `prompts/one-click-import.md`, `skills/code-animation-prompts/SKILL.md`, `skills/code-animation-prompts/references/*`, `skills/code-animation-prompts/agents/openai.yaml`, `skills/code-animation-prompts/assets/starter/index.html`, `scripts/*.py`, `.github/workflows/validate.yml`, `docs/source-manifest.json`, `CLAUDE.md`
- Delete: `docs/images/promo-hq.gif`

- [ ] **Step 1:** Translate docs and point URLs at `miolamio/code-animation-prompts`. README states the fork is an unofficial free translation, credits upstream and bans resale. LICENSE and the pack's notes quote the original terms verbatim with translations and keep the 193 historical count. Third-party license files stay byte-identical.
- [ ] **Step 2:** Build `media-with-chinese.json` from the OCR set plus a visual pass over candidates OCR missed, including Z5, R3 and A5, and add A2, A3, A4 and F2 as no longer matching their prompts. Surface this as a `reference_note` in `catalog.json`, in `styles.py show` output, and in the picker.
- [ ] **Step 3:** Replace the README hero with `docs/images/style-gallery.png` after confirming by eye that it has no Chinese. If it does, change `build_visuals.py` to draw from stills outside `media-with-chinese.json`. Update `build_visuals.py` display text, run it with `--skip-video`, and delete the GIF.
- [ ] **Step 4:** Write failing tests first for the Chinese gate, then update `validate_repo.py`: regenerate the manifest with the upstream commit recorded, reset the ledger to the 3 contributed stills, move count and import-prompt checks to the English phrases, and fail on Chinese in any tracked text file or path unless allowlisted. Change CI's search to `search ink`. Remove the loosening from Task 3.
- [ ] **Step 5:** Rewrite `CLAUDE.md` to describe the English fork: new paths, the new baseline, and the allowlist.
- [ ] **Step 6:** Run `python3 scripts/validate_repo.py`. Pass: it reports PASS with 341 styles and 196 stills. Coordinator commits as `feat: complete English docs, license and validator`.

### Task 9: Final verification and PR

- [ ] **Step 1:** A fresh agent confirms each spec requirement against the tree, runs the CI commands, and takes a browser screenshot of the picker showing English UI and working search for `ink`.
- [ ] **Step 2:** Coordinator pushes the branch, confirms CI passes on Ubuntu and Windows, and opens a PR against `miolamio/code-animation-prompts` `main`, never upstream. The merge stays with the user.
