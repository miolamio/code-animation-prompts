# M1 Hand-Drawn Whiteboard Explainer

- Category: M Motion Styles · Explainers
- Looks like: White background; a hand (or a pen) draws as it explains, with lines drawn first and then colored.
- Best for: Passages explaining concepts and principles. For example, "the large language model is the brain, the Harness is the hands and feet".

## Style prompt

> This prompt is a rewritten, detailed version: the rendering rules, colors and timeline are all fixed, so both DeepSeek and Opus 5.5 can use it directly. Content inside {{ }} is for you to fill in.

You are a front-end motion engineer. Write **one complete index.html file**: plain HTML + JavaScript + Canvas only, with no external libraries, font files or images. Make a hand-drawn whiteboard explainer animation.

## What to explain

- Topic: {{topic, e.g. the large language model is the brain, the Harness is the hands and feet}}
- Total duration: {{seconds, default 20}}
- Text on screen: {{3-6 short phrases. E.g. title "How AI Gets Work Done"; left "Large Language Model", subtitle "thinks, speaks"; right "Harness", subtitle "hands and feet: really does things"; on the arrow "Command"}}

## Output requirements (mandatory)

1. Output only one html code block, with no explanation. The code must be complete and runnable: no ellipses, and do not write "rest same as above" or "omitted here".
2. The canvas is fixed at 1920×1080; use CSS to scale it proportionally and center it in the window, with black bars for the extra window space.
3. Everything on screen is determined by the function `draw(t)`, where `t` is in seconds. Do not use `Math.random`; if you need randomness, use a seeded mulberry32(seed), so the same `t` draws exactly the same picture every time.
4. Loop by default; Space pauses/resumes; when the URL has `?t=8.5`, show only the frame at second 8.5 (still), for easy screenshots.

## How to draw

- Base color #FBFAF7; on top, a few very faint gray smudges (40-90px wide, opacity 0.03-0.06).
- Lines are black marker #1B1B1B, 10px wide, with `lineCap` and `lineJoin` both round. Draw every stroke twice: the first pass at opacity 0.93; the second pass 5.5px wide, opacity 0.55, offset by ±1.5px.
- Only black and **one** accent color #E5432B (used for the title underline, arrow, subtitles and pen cap). No third color.
- Typeface: `font-family: "Segoe Print", "Bradley Hand", "Marker Felt", "Comic Sans MS", "Noto Sans", sans-serif` (a casual handwriting face, with a general Noto fallback for the user's script; for a CJK film put a brush or handwriting face such as KaiTi or STKaiti first), bold; title 110px, labels 90px, subtitles 56px. Draw text with `strokeText` plus `fillText`, with a stroke width of about 3.5% of the font size.
- Hand-drawn feel: add ±2.5px jitter to every point, taking the jitter from seeded randomness indexed by the point's number, not re-randomized every frame.
- Things to draw:
  - A cloud-shaped "brain": polar coordinates r = R·(1 + 0.11·|sin(3.5θ)|), with a few wavy lines inside;
  - A stick figure: round head, a single-line body, two arms (each ending in a circle as the hand), two legs;
  - A curved accent-color arrow, with the arrowhead following the direction of the line's tail;
  - A marker: black barrel, red cap, about 330px long, tilted 55 degrees, with the tip always resting at the end of "the stroke currently being drawn"; after everything is drawn, it slides out of the frame.

## Motion rules

- Each stroke is a list of points. Use progress (0→1) to decide how many points have been drawn, with progress eased in-out; one stroke takes 0.4-1.2 seconds.
- Order: title → title underline (red) → left brain → right figure → red arrow → the word "Command" → the two label texts. Only one stroke is drawn at a time.
- After everything is drawn, hold still for 1.5 seconds, then loop.

## Do not

Gradients, shadows, glow, 3D, particles, complex color schemes, screens full of text, camera shake.

## Self-check after writing (do not output)

- At `t=0`, is it an almost blank whiteboard?
- At `t=total duration-0.1`, are all elements present?
- Is any text covered by a line or the pen?
- Refreshing twice at the same `t`, is the picture exactly identical?
