# Z5 Chinese Paper Cutting

- Category: Z Chinese Style · Chinese Style
- Looks like: Red paper cut into openwork, folk patterns / Chinese paper cutting

## Style prompt

> This prompt is a rewritten, detailed version: the picture rules, colors, and timeline are all fixed, so DeepSeek and Opus 5.5 can both use it directly. What goes inside {{ }} is for you to fill in.

You are a front-end motion engineer. Write **one complete index.html file**: use only native HTML + JavaScript + Canvas, with no external libraries, font files, or images. Make an animation in the "Chinese Paper Cutting" style: circular openwork window paper-cuts, cut from folded red paper, stacked layer by layer on window paper, with drop shadows.

## Content

- Topic: {{topic, e.g.: opening titles for newlyweds}}
- Total duration: {{seconds, default 12}}
- Character to cut out at the center: {{default "囍" (double happiness)}}

## Output requirements (mandatory)

1. Output only one html code block, with no explanation. The code must be complete and runnable: no ellipses, and do not write "the rest same as above" or "omitted here".
2. Canvas fixed at 1920×1080, scaled proportionally and centered with CSS, with any extra area as black bars.
3. Everything in the picture is determined by the function `draw(t)` (`t` is in seconds). Do not use `Math.random`; if randomness is needed, use seeded mulberry32(seed), so the same `t` draws the same picture every time.
4. Loop by default; Space pauses/resumes; when the URL has `?t=5`, show only the frame at second 5.

## Color

Window paper #F1E8D4; main red #C8102E; deep red #8F0B22. No colors other than these three: no gold, gradients, or highlights.

## How to draw (follow these steps)

1. **Window paper**: Fill with #F1E8D4, then use seeded randomness to draw 2000 thin short lines 8–34px long (half #B9A98A, half #FFFAF0, opacity 0.05–0.11) as paper fibers. Draw this layer only once and cache it in an offscreen canvas.
2. **Make two sheets of red paper** (each on its own offscreen canvas, size 1920×1080, with the origin moved to the center of the picture):
   - `layerBase`: a deep red #8F0B22 disc, radius 452; use `destination-out` to cut 48 small holes of radius 10 around the outer edge (placed at radius 428), then cut away the whole circle within radius 400 (leaving only a ring of deep red edge).
   - `layerTop`: a bright red #C8102E disc, radius 404; use `destination-out` to cut the following, and **every ring is "draw 1/N, rotate-copy N times"**:
     - 48 small holes at the outer edge: radius 9, placed at r=378;
     - 24 small teardrops: from r=342 to r=274, width 22;
     - 12 large petals: from r=244 to r=74, width 50;
     - 12 small diamonds: each first rotated by π/12, centered at r=226, width 32, height 48;
     - 12 small dots: each first rotated by π/12, radius 12, placed at r=170;
     - 12 inner petals: from r=78 to r=148, width 26;
     - then cut away the center circle of radius 66; then fill in a small disc of radius 46 at the center with bright red; finally use `destination-out` to write the center character on the small disc (bold 66px, centered).
   - Red "bridges" must remain between the petals; do not cut the red paper apart.
3. **Four corner pieces**: On another offscreen canvas, draw a bright red "quarter circle" (radius 250, its center at the corner of the picture), and cut: 9 small holes along the arc edge (radius 7), 4 teardrops, and a round window of radius 58. Copy it to the four corners (flipped).
4. **Composite**: Draw the window paper first; then draw `layerBase`, `layerTop`, and the four corner pieces in order, setting the drop shadow before each layer: `shadowColor='rgba(70,12,12,0.38)'`, `shadowBlur=16`, `shadowOffsetX=5`, `shadowOffsetY=9`.

The teardrop path can use this function directly (origin at the center of the window paper-cut, negative y is upward):

```js
function drop(g, y0, y1, w) {
  const d = y0 - y1;
  g.beginPath(); g.moveTo(0, y0);
  g.bezierCurveTo(w, y0 - d * .25, w * .9, y1 + d * .35, 0, y1);
  g.bezierCurveTo(-w * .9, y1 + d * .35, -w, y0 - d * .25, 0, y0);
  g.fill();
}
function ring(g, n, fn) { for (let i = 0; i < n; i++) { g.save(); g.rotate(i * Math.PI * 2 / n); fn(g, i); g.restore(); } }
```

## Motion

- 0–0.8 seconds: the deep red base disc unfolds from radius 0 to full (ease-out); 0.25 seconds later, the bright red main disc unfolds the same way.
- 1.2–4 seconds: the openwork "opens" ring by ring from the outside in (each hole's radius grows from 0 to its target, each ring 0.18 seconds later, each hole 0.35 seconds); because the holes are cut out, implement this by passing "hole radius × progress" to the hole-cutting steps above and regenerating `layerTop` every frame (finished rings can be cached).
- 4–4.4 seconds: the center character "stamps" in: scale 1.15 → 1.0.
- After that, the whole window paper-cut sways slowly by ±0.6° (period 6 seconds), and the shadow offset shifts with it by ±2px.
- Hold still for the last second, then loop.

## Do not

Gold, gradients, plastic highlights, 3D, particles, glow, overly heavy shadows, writing the character on the paper (it must be cut out).

## Self-check after writing (do not output)

- Are the cut-outs cut with `destination-out`, not covered with the base color?
- Are the 12 copies perfectly symmetrical?
- Do all shadows fall toward the lower right?
- Refresh the same `t` twice: is the picture exactly identical?
