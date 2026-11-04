# Code Animation Style Prompts

A total of **341 styles**, one prompt each. They work with Opus 5.5 and also with DeepSeek. Of these, 193 come with stills.

Some were collected from the web; many I organized, made and summarized myself.

## What's inside

| Folder / file | What it is |
|---|---|
| `style-picker.html` | The picker page. Double-click to open it directly in Chrome or Edge; no internet connection needed. You can filter by category, search, enlarge stills, read prompts, tick styles and export a list. Do not separate it from the "style-prompts" folder. |
| `style-prompts/` | 341 styles, each with one `.md` prompt; those with a still have a `.jpg` of the same name beside them |
| `examples/` | Two real tests: the same detailed prompt given to Opus 5.5 and to DeepSeek, compared; and the result of giving DeepSeek just one sentence |
| `licenses-and-sources.md`, `third-party-licenses/` | Where each category of styles comes from and which license it uses |

### How the 341 are divided

| Category | Count | What it is |
|---|---|---|
| A–G Code Samples | 26 | Type, particles, line and ink, light and weather, shapes and paper, explainers, material feel; each comes with reference implementation code |
| M Motion Styles | 40 | How a whole video moves, cuts and tells its story |
| K Cartoon Styles | 38 | What the characters and the picture look like |
| Z Chinese Style | 15 | Ink wash, gongbi, paper-cut, shadow puppets, Dunhuang... |
| H Ready-Made Layouts | 12 | Complete pairings of color palette and typeface |
| L Lemo-Opuscar | 59 | Styles from the open-source project Lemo-Opuscar, each with a complete method |
| V mg-styles-15 | 15 | Motion styles from the open-source project mg-styles-15 |
| X code-video | 31 | Styles from the open-source project code-video |
| R Learned from References | 7 | Cyberpunk drawn in code, learned by following references |
| O 98 Best Picture Winners | 98 | 98 Oscar Best Picture winners, one art style each |

## How to use

**With DeepSeek Harness (or Claude Code):**

1. Put this folder somewhere it can read, and tell it: "Read this folder. I want to use the styles in it to make code animations."
2. Pick your styles in `style-picker.html`, click "Selected list" to copy, and send it over.
3. Be clear about what you want to express: what the content is, how long it runs, landscape or vertical format, how the shots move, and how several styles join together.
4. **Remember to say whether you want music and sound effects.** If you don't say, it will most likely come out silent.
5. Have it output an html file that opens in a browser, then have it render that to video.

**Using one style directly:** Open that style's `.md`, copy the "Style prompt" section to the model, and add your content. Some prompts contain `{{ }}`, which marks the places for you to fill in.

**Tip:** The more detailed the prompt (colors, timing and shots all fixed), the closer the results from different models; a single sentence also works, but the result differs every time and it is slower. `examples/` has both.

## Terms

- 全部免费，不用私信，不用买课。 All of it is free: no private message needed, no course to buy.
- 你可以免费用、免费转给别人；转的时候也请免费分享。 You may use this for free and pass it on to others for free; when you pass it on, please also share it for free.
- **禁止把这些内容包装成课程、付费 skills 或任何收费的东西拿去卖。** **Packaging this content as a course, a paid skill or anything else that charges money, and selling it, is prohibited.**
- The parts that come from open-source projects keep their original licenses and attribution; see `licenses-and-sources.md`.

If you find this useful, a like, a coin and a favorite are welcome as support. Thank you all, and I will keep open-sourcing more useful material.
