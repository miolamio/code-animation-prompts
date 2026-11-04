# English-only fork design

**Goal:** make `miolamio/code-animation-prompts` fully readable and usable in English, while keeping every style working and every source credited.

**Baseline:** upstream `XiaoyeCodes/code-animation-prompts` at commit `103ac7e`. Work happens on branch `english-translation` and reaches the fork's `main` through a PR. Nothing is sent upstream.

## Decisions

| Topic | Decision |
|---|---|
| Form | English only, in place. Chinese originals remain in git history and upstream. |
| Paths | All Chinese file and folder names become English. Style IDs are kept (`K1_flat-vector.md`). |
| Media | Pixels unchanged, files renamed only. Media showing Chinese is marked as an original reference. |
| Promo GIF | Removed from the tree and README. README shows a gallery of stills checked to contain no Chinese. |
| Chinese as aesthetic | Kept as a literal with an English gloss (calligraphy, paper-cut 囍, the sampled 汉字 in B3). |
| Code depending on Chinese strings | Rewritten for English strings (A2, A3, A4, F2), including counts, coordinates and lookup keys. |
| On-screen Chinese requirements | Become "the user's language" (V, L, M18), including font stacks and subtitle limits. |
| Hosting | Public GitHub fork. |

## Allowlist

`docs/translation/cjk-allowlist.json` is the only place that permits Chinese outside media. Each entry names a file, the permitted literal text, and a reason. Permitted reasons:

- `style-literal`: the characters are the style's visual material.
- `attribution`: the curator's name `俯仰观照`, shown with a romanization.
- `license-quote`: verbatim quotes of the original sharing terms, each with an English translation.
- `media-source`: B6 example HTML, kept unchanged so it matches its mp4 files.
- `translation-record`: `docs/translation/` and `docs/superpowers/`, which record the Chinese originals and this migration.

## Work stages

1. **Glossary and path map.** Translate style names, series labels and recurring terms into `docs/translation/glossary.json`. Build `docs/translation/path-map.json` mapping every Chinese path to its English path.
2. **Rename.** Apply the path map in a commit with no content edits, so git records renames. Update path references in code, docs and picker data in a following commit.
3. **Translate prompts by series.** A script extracts only the lines containing Chinese, translators return a translation or a deletion per line, and a script applies them. Every other line stays byte-identical. Each file keeps its structure, using English labels: `# <ID> <name>`, metadata bullets, `## Style prompt`. Series O uses the existing English prompt and drops the Chinese duplicate; its notes are translated.
4. **Picker.** A one-off migration script writes translated fields into the data blob of the picker. Fields that exist only in the picker are translated directly, and existing `en`, `desc_en` and `prompt_en` values are reused. The blob stays the source of truth afterwards. The UI strings and `lang` attribute become English. Search must keep working over the English fields.
5. **Docs and tooling.** Translate README, CONTRIBUTING, INSTALL, SKILL, attribution, the import prompt, the starter template and script output. Point URLs at the fork. Regenerate `catalog.json`, `STYLES.md` and the docs images.
6. **License.** LICENSE and the pack's notes become English, quoting the original sharing terms verbatim. The notes keep the original count of 193 stills as a historical statement. Third-party MIT license files stay byte-identical. README states this is an unofficial translation, free of charge, with no resale permitted.

## Validator

`validate_repo.py` keeps its role with a new baseline:

- `docs/source-manifest.json` is regenerated from the translated tree and records the upstream commit. The old manifest stays available in git history and is linked by the path map's upstream pin.
- `library-changes.json` restarts empty, because the three contributed stills are part of the new baseline and credited in `references/attribution.md`. It remains the ledger for later changes.
- All count and import-prompt checks move to their English phrases.
- A new check fails on any Chinese character in a tracked text file or path that the allowlist does not cover. CI's `search 水墨` becomes `search ink`.

## Verification

Stage 3 is done when every check below passes:

- **Structure per prompt, against the upstream version:** same number of code fences, same `{{ }}` placeholder names, same URLs, and all numbers in prose preserved.
- **Rewritten code:** A2, A3, A4 and F2 parse and run in Chromium for several frames with no exception. `PARENT` and `SERIF` are undefined upstream, so a temporary harness outside the repo stubs them.
- **Independent review:** a separate agent reads every prompt with a literal or rewritten code, plus a sample of at least 10% of each series, against its Chinese original.
- **Tooling:** `validate_repo.py` passes, `styles.py search ink` returns hits, CI passes on Ubuntu and Windows, and a browser screenshot of the picker shows English UI and working search.

## Accepted limits

- About 20 to 25% of stills, the B6 examples and their mp4 files still show Chinese.
- Stills for A2, A3, A4 and F2 no longer match their rewritten prompts and are marked as original references.
- Upstream updates must be ported by hand using the path map.
- The original terms do not mention translation. The fork stays free, credits its sources and says it is unofficial.
