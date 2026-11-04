# H1 Biennale Yellow

- Category: H Ready-Made Layouts · Ready-Made Layouts
- Looks like: Warm parchment base, sun-yellow glow, large serif headline, indigo ink, thin lines

## Style prompt

> This prompt was rewritten in a detailed version: the picture rules, colors and timeline are all fixed, so both DeepSeek and Opus 5.5 can use it directly. The content inside {{ }} is for you to fill in.

You are a front-end motion engineer. Write **one complete index.html file**: only native HTML + JavaScript + Canvas, with no external libraries, font files or images. Make an animated title card in the style of an "art biennale magazine cover".

Warm parchment base, sun-yellow glow, large serif headline, indigo ink, thin lines

- Headline (two lines): {{line 1, e.g. Biennale}} / {{line 2, e.g. Yellow}} (line 2 in italics)
- Header left: {{e.g. THE TWELFTH BIENNALE · EDITORIAL SERIES}}; header right: {{e.g. N° 01}}
- Footer left (in the user's language): {{one-line description}}; footer right: {{issue number}}
- Total duration: {{seconds, default 6}}

## Output requirements (mandatory)

1. Output only one html code block, with no explanation. The code must be complete and runnable: no ellipses, and do not write "the rest is the same as above" or "omitted here".
2. The canvas is fixed at 1920×1080, scaled proportionally and centered with CSS; any leftover area is black bars.
3. Everything on screen is determined by the function `draw(t)` (`t` is in seconds). Do not use `Math.random`; for the paper grain use a seeded mulberry32(seed).
4. Loop by default; space bar pauses/resumes; when the URL carries `?t=3`, show only the frame at second 3.

## Colors and lines (use only these)

- Base color paper = #F2E9D2; add paper grain: 5000 small square dots of 1–3px, half #8C7A55 and half #FFFAF0, at opacity 0.045–0.095. Draw the paper grain only once and cache it on an offscreen canvas.
- The only accent color is sun = #F6C23E.
- Text and all lines use ink = #1D2A68, with line weight 1.6–1.8px.

## Typeface

`font-family: Georgia, "Times New Roman", "Noto Serif", serif` (for a non-Latin script, add a serif face for that script before the generic `serif`). Use serif type only throughout the film. Headline about 214px, `letterSpacing = '-4px'`; header 26px, uppercase, `letterSpacing = '6px'`; footer text 34px. (Canvas `ctx.letterSpacing` works in recent browsers; if unsupported, draw character by character.)

## Layout (coordinates for 1920×1080)

1. Outer frame: `strokeRect(64, 64, 1792, 952)`; then draw two horizontal lines: y=148 and y=932, from x=64 to x=1856.
2. The sun, centered at (1380, 470):
   - Glow: radial gradient, radius 20→560, from `rgba(246,194,62,1)` to `rgba(246,194,62,0.92)` (at 38%), then to `rgba(246,214,120,0.35)` (at 70%), to `rgba(246,214,120,0)` (at 100%);
   - Solid circle: radius 250, color sun;
   - Three concentric thin rings: radius 250, 330, 410 (ink, opacity 0.9, 0.45, 0.45);
   - Tick ring: radius 410 to 421 (every 5th tick is a long one, reaching 432), 120 ticks in total, ink, opacity 0.85.
3. Headline: left edge x=100, first line baseline y=560, second line (italic) baseline y=770. Make sure the right end of the headline does not touch the tick ring (its leftmost point is about x=948).
4. The two small header lines have baseline y=118 (left x=104, right x=1650); the footer text has baseline y=980 (left x=104), and the issue number is right-aligned to x=1816.

## Motion

- 0–0.8 s: the outer frame and the two horizontal lines are "drawn out" from the four corners toward the middle (use `setLineDash` or truncate by progress);
- 0.4–1.8 s: the sun rises into place from 300px below (ease-out), glow opacity 0→1;
- 1.0–2.4 s: the two headline lines fade in one after the other from 24px below, with letter spacing tightening from +20px to −4px;
- 2.0–2.8 s: header and footer fade in; the tick ring rotates slowly clockwise at 1° per second;
- Final 0.5 s: everything fades out to the paper color, then loops.

## Do not

Gradient color blocks, shadows, rounded cards, a second accent color, sans-serif headlines, glow, particles.

## Self-check after writing (do not output)

- Does the whole film use only sun as its accent color?
- Does the headline touch the tick ring?
- If the same `t` is refreshed twice, is the picture exactly identical?
