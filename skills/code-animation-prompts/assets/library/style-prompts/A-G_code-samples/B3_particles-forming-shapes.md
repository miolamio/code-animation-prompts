# B3 Particles Forming Shapes

- Category: A–G Code Samples · B Particles
- Looks like: Particles gather into a heart, a house, a person, then scatter.
- Best for: concrete things: home, relationships, a person
- Keywords: gathering into, shapes, scattering

## Style prompt

> This prompt is a rewritten, detailed version: the picture rules, colors, and timeline are all fixed, so DeepSeek and Opus 5.5 can both use it directly. What goes inside {{ }} is for you to fill in.

You are a front-end motion engineer. Write **one complete index.html file**: use only native HTML + JavaScript + Canvas 2D, with no external libraries, font files, or images. Make a "Particles Forming Shapes" animation: thousands of tiny glowing particles gather into a shape, hold, scatter, flow along arcs to the next shape and gather again, in a loop.

## Content

- The four shapes, in order: heart → house → person → a Chinese character ({{default: 家 (home)}}).
- When each shape holds, one line of captions appears at the bottom of the picture. The four lines, in order: {{four lines, separated by |. Default: First, a heart|Then, a house|Inside it lives a person|Together they are called home}}.

## Output requirements (mandatory)

1. Output only one html code block, with no explanation. The code must be complete and runnable: no ellipses, and do not write "the rest same as above" or "omitted here".
2. Canvas fixed at 1920×1080; use CSS to scale it proportionally and center it in the window, with any extra area as black bars.
3. The picture is a pure function of time t (seconds), `draw(t)`. Do not use `Math.random`; all randomness uses seeded mulberry32(2026), generated only once at startup. Do not accumulate state in draw (no "ghost image from the previous frame"). This way the same t draws exactly the same picture every time.
4. Loop by default (requestAnimationFrame, t = seconds played); Space pauses/resumes; when the URL has `?t=3.3`, show only the frame at second 3.3 (static).

## Constants

N = 5000 particles; each shape has one cycle PER = 4.8 seconds, 4 shapes in total, full loop 19.2 seconds; shape scale SC = 1080 × 0.36; shape center at (960, 520).

## Shapes (coordinates in the [-1,1] square, y pointing down)

```js
const heart  = (x,y)=>{ y=-y*1.15+.1; x*=1.15; return Math.pow(x*x+y*y-1,3)-x*x*y*y*y<=0; };
const house  = (x,y)=>(Math.abs(x)<=.6&&y>=-.1&&y<=.75&&!(Math.abs(x)<.14&&y>.38))||(y<-.1&&y>-.8&&Math.abs(x)<=.8*(y+.8)/.7);
const person = (x,y)=>(x*x+(y+.55)*(y+.55)<=.05)||(y>=-.28&&y<=.85&&Math.abs(x)<=.25+(y+.28)*.2);
```

- Heart, house, person: in [-1,1]², do "rejection sampling" with seeded random points, keeping those that land inside the shape until you have N.
- Chinese character: on a 400×400 offscreen canvas, draw the glyph in white bold (`bold 340px "Noto Serif SC","Songti SC","SimSun",serif`, horizontally centered, `textBaseline='middle'`, y=210); after `getImageData`, take one point with alpha>128 every 2 pixels and convert it to [-1,1]; after a seeded shuffle, take N (if there are too few, take repeatedly and add ±0.004 jitter).
- Shuffle each of the four target sets once. Particle i goes to the i-th target point in each of the four shapes, so it looks like "the same batch of particles changing shape".

## Fixed parameters per particle (generated once at startup)

Angle `a` (0–2π), amplitude `m` (0–1), phase `ph` (0–2π), flicker frequency `f` (0.6–1.6), size `s` (0–1), whether it has a glow `glow` (true for 20%).

## Position (the core, compute it exactly like this)

Let k = floor(t / PER) % 4 (current shape), n = (k+1) % 4 (next shape), q = t % PER (time within the shape); A = the i-th target point in shape k, B = the i-th target point in shape n.

- Progress e = smoothstep(2.4, 4.2, q). For q in 0–2.4 seconds, e=0 (hold); 2.4–4.2 seconds, morphing; 4.2–4.8 seconds, e=1 (settled).
- Control point C = (A+B)/2 + (cos a, sin a) × (0.35 + 0.9·m).
- Position P = (1−e)²·A + 2(1−e)e·C + e²·B (quadratic Bézier, so particles travel along arcs, bursting apart first and then converging).
- Micro-motion: add (cos(ph + 1.3t), sin(1.7·ph + 1.1t)) × 0.012 × (1 − sin(π·e)) to P.
- Screen coordinates = (960 + P.x × SC, 520 + P.y × SC); then scale everything about the picture center (960, 540) by zoom = 1 + 0.015·sin(0.33t).

## How to draw

1. **Background**: Fill with #07080C; at the center, a radial gradient (radius 800) from `rgba(40,46,66,0.30)` to `rgba(7,8,12,0)`; then draw 220 dim star points at fixed positions (randomized once at startup, opacity 0.15–0.4, flickering slightly with t).
2. **Particles**: Use `globalCompositeOperation = 'lighter'` for additive glow. Colors: heart #F08A8A, house #F1C070, person #A9C6FF, Chinese character #F6EBD0; while morphing, blend linearly by e between "the current shape's color" and "the next shape's color".
3. Each particle's brightness L = 0.75 + 0.25·sin(f·t + ph); radius r = 1.1 + 1.6·s (pixels); base opacity 0.55·L.
4. **Trail**: Draw each particle 3 times, at times t, t−0.045, and t−0.09 (recompute with the same position function, do not store history); opacity ×1, ×0.5, ×0.25 in turn, radius ×1, ×0.8, ×0.6 in turn.
5. **Glow**: Particles with glow=true also draw one more large circle with radius ×3 and opacity 0.05.
6. **Captions**: When each shape holds (fade in for q from 0.3 to 1.0, fade out for q from 2.1 to 2.5), center that shape's line at (960, 960), serif 46px, color #EDE6D6, maximum opacity 0.85.

## Do not

Explosion flashes, lens flares, rainbow colors, a second background, randomness driven by a real-time timer, saving previous-frame state in `draw`.

## Self-check after writing (do not output)

- Refresh the same t twice: is the picture exactly identical?
- At t=1.8, do you see a heart made of particles? At t=3.3, is it bursting apart and flowing toward the house?
- Drawing particles 5000×3 times per frame: will it lag? If it lags, you can draw the glow only for glow particles.
