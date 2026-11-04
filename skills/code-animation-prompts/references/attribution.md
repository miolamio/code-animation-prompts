# Material and licenses

This skill packages the free pack titled "Code Animation: 341 Style Prompts (Free)" that came with the project. The pack's notes, prompts, examples and licenses are kept in `../assets/library/`, with prompts and notes translated into English in this fork. XiaoyeCodes is responsible for the upstream skill packaging, the search, install and render scripts and the display docs, and does not claim all works in the pack as its own original work. This fork is an unofficial, free English translation of [XiaoyeCodes/code-animation-prompts](https://github.com/XiaoyeCodes/code-animation-prompts).

- [Pack notes](../assets/library/README.md): free to use and free to pass on; packaging this content as a course, paid skills or anything else sold for money is prohibited.
- [Pack source notes](../assets/library/licenses-and-sources.md): the curator's notes on the parts they made or rewrote.
- [Lemo-Opuscar](../assets/library/third-party-licenses/Lemo-Opuscar_LICENSE.txt): MIT, Copyright (c) 2026 LemoLab.
- [mg-styles-15](../assets/library/third-party-licenses/mg-styles-15_LICENSE.txt): MIT, Copyright (c) 2026 Vincentwei1021.
- [code-video](../assets/library/third-party-licenses/code-video_LICENSE.txt): MIT, Copyright (c) 2026 Bae-ChangHyun.

Thanks to the original curator, [**俯仰观照 (Fuyang Guanzhao)**](https://space.bilibili.com/3690990015613855/?spm_id_from=333.788.upinfo.detail.click) on Bilibili, for sharing these resources.

## Community additions and the pack baseline

- **Strange Leo (@strangeyu911-tech)**: contributed three 1920x1080 JPEG reference cards through [PR #1](https://github.com/XiaoyeCodes/code-animation-prompts/pull/1): K1 Flat Vector Character, K2 Chibi and K3 Kawaii. These are community additions, not images that shipped with the original pack.
- The author says the images were drawn in SVG and rendered, but the PR only submitted JPEGs with no SVG source files. This repository does not present the JPEGs as editable vector source.
- The original pack has 193 stills; with the community additions, the current catalog has 196. The 193 in the library `README.md` is retained as a historical statement; for current counts, use `catalog.json` and the picker.
- The repository's `docs/source-manifest.json` holds the library's hash baseline; do not overwrite it with current files to make validation pass. The three K images are part of that baseline. [library-changes.json](library-changes.json) records the hashes, sources and reasons for later library changes, and installs with the skill.

Content from different sources keeps its own license. The free-sharing terms do not rewrite the third-party MIT text, and the collection as a whole cannot simply be labelled MIT. Film, art style and example names are descriptive references and do not imply official partnership or endorsement.
