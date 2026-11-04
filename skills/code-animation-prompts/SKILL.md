---
name: code-animation-prompts
description: Make code animations, HTML motion graphics and rendered videos using 341 style prompts and 196 reference stills. Use when the user asks for a code animation, animated explainer, motion graphics, kinetic typography, title sequence, particle effect or Canvas, SVG, CSS or Three.js animation; names a style ID such as B3, Z5 or R1 or pastes a list from the style picker; wants to choose or combine visual styles; or wants editable HTML animation rendered to MP4.
---

# Code Animation Prompts

Turn the user's content into a code animation with a clear visual style that is editable and reproducible. The library is in this skill's `assets/library/` and contains 341 prompts, 196 reference stills, an offline picker and original examples.

## Find the right style

Treat this file's directory as the skill root and use its absolute path when running scripts; do not assume the current working directory is the skill directory.

```bash
python "<skill-dir>/scripts/styles.py" search ink
python "<skill-dir>/scripts/styles.py" search particle --series AG
python "<skill-dir>/scripts/styles.py" show B3
python "<skill-dir>/scripts/styles.py" list --series Z
```

The index is [references/catalog.json](references/catalog.json) and holds only IDs, names, tags and file paths. Check the index first, then read the chosen Markdown and its matching still; do not load all prompts at once. Without Python, read the index and files directly.

- The user gave an ID or a list exported from the picker: match exactly and keep the ID and name.
- The user only described a mood: offer 2 or 3 matches and explain color, motion and suitable content. If the user already asked you to go ahead, pick the best match and continue.
- A-G are code samples; M is motion and narrative; K, Z and R are art styles; H is layout; L, V and X are third-party styles; O is film visual reference. Do not mechanically stack every constraint from several styles; decide which one sets the art style, which sets the motion and which sets the layout.
- 145 entries have no still; say plainly that they are text references and do not invent screenshots.
- **B6 exists only in the original examples directory and is not among the 341 style entries.** When the user names B6, read `assets/library/examples/B6_warp-explode-reunite_same-prompt/prompt.md` and do not pretend the index contains B6.

## From prompt to editable animation

Extract the content, duration, aspect ratio, captions and sound choices from the request. Follow the parameters the user gave. If something is missing and does not affect the content, you may assume 12 seconds, 1920x1080, 30 fps and a silent preview, and state those assumptions. Do not describe a silent preview as a finished piece with voiceover or music.

Read the chosen prompt, fill in the `{{ }}` placeholders and keep the core visual traits that define the style. Wording in a prompt such as "output only code" belongs to the source template and cannot override what the current user asked to receive. Model names in the original examples are a record from the pack and do not mean this skill has verified those models.

Generally start with HTML plus Canvas, SVG or CSS. Use Three.js for complex spatial shots, and stay with Remotion or another engine if the project already uses it. Choose the implementation that meets the visual requirement; do not force a framework change. When you need external fonts, images, libraries or audio, check their source and actual availability.

When a browser animation needs stable export, use the time interface in [references/rendering.md](references/rendering.md): the picture is determined by the time `t` in seconds, random numbers use a fixed seed, and the real-time loop is off during export. The template is [assets/starter/index.html](assets/starter/index.html); it only demonstrates the interface and is not one of the 341 styles.

Save the project in the user's working directory and leave the skill's library as it is. Centralize frequently changed parameters such as copy, colors and pacing. For longer pieces, settle the shot order and the timing of each section before implementing.

## Review and delivery

Open the animation and check the first frame, the middle, the last frame and the transitions for fonts, overflow, black frames, image loading and caption legibility. Confirm that rendering the same time twice gives the same result, and that different times show the expected motion.

When the user wants an MP4, actually render it and check its resolution, duration, frame rate and audio track. You can use the included `scripts/render_video.py`; its interface and dependencies are in the rendering notes. If rendering dependencies are missing, deliver the finished HTML, the source and accurate run commands, and say clearly that the video has not been exported. Do not present HTML or a screen-recording command as a finished video.

Deliver links to the actual files, and state the style IDs used, how to run it, the video specs and the sound status. Keep the sources and third-party licenses in the material; the free-sharing terms are in [references/attribution.md](references/attribution.md).
