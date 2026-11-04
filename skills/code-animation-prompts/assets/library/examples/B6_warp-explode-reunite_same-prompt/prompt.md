# B6 Warp Speed · Explosion · Reunion

> The same prompt was given separately to Opus 5.5 (High) and DeepSeek-V4.1-Flash (1017, High), and the results are in this folder. {{ }} marks the content for you to fill in.

You are a front-end motion engineer. Write **one complete index.html file**: use only native HTML + JavaScript + Canvas 2D, with no external libraries, font files or images. Make a 12-second **single continuous take** animation: warp-speed travel → burst through 5 light rings in a row → braking, particles pulled toward the center → explosion → fragments spin and reunite into the title text. The whole thing is one camera flying continuously forward through 3D space, **with no cuts from start to finish**; the same batch of 4000 particles are first starlight streaks, then explosion fragments, and finally form the title.

## Content

- Title: {{Default: 俯仰观照 (Fuyang Guanzhao)}}
- Subtitle: {{Default: In the river's flow, see the instant; in the trees, see eternity}}

## Output requirements (mandatory)

1. Output only one html code block, with no explanation. The code must be complete and runnable: no ellipses, and do not write "the rest as above" or "omitted here".
2. Fix the canvas at 1920×1080; use CSS to scale it proportionally and center it in the window, with any leftover area as black bars.
3. The picture is a pure function of time t (seconds), `draw(t)`. Do not use `Math.random`; all randomness uses seeded mulberry32(7), generated only once at startup. Do not store the previous frame's state in draw. The same t draws exactly the same result every time.
4. Loop by default (requestAnimationFrame, t = seconds played, modulo 12); press Space to pause/resume; when the URL has `?t=5.7`, show only the frame at second 5.7 (static).

## Constants

W=1920, H=1080, screen center (960,540); N=4000 particles; total length 12 seconds; tunnel length L=6000; base focal length F0=900.

## Shot (the camera advances along the z axis. Get these functions right first)

```js
const V0 = 80, V1 = 2600;
const z1 = t => V0*t + (V1-V0)*(3/3.2)*Math.pow(Math.min(t,3)/3, 3.2) + V1*Math.max(0, t-3);
const Z5 = z1(5.0), zB = Z5 + 780, ZC = zB + 900, Z3 = z1(3), ZT = zB - 700;
function camZ(t) {
  if (t <= 5.0) return z1(t);                                              // accelerate to light speed
  if (t <= 5.6) { const u = (t-5.0)/0.6; return Z5 + 2600*0.6*(u - u*u/2); } // hard braking
  if (t <= 8.0) { const v = (t-5.6)/2.4; return zB - 2200*(1-(1-v)*(1-v)); } // sharp pull-back after the explosion
  return zB - 2200 - 120*(t-8.0);                                          // slow pull-back after that
}
```

- **5 light rings**: ring k (k=0..4) is at world coordinate z = Z3 + 2600·(0.3 + 0.42k), and the camera passes through it at time tk = 3.3 + 0.42k; color (125,249,255) when k is even, (255,213,154) when odd; radius R=260.
- **Focal length** f(t) = 900 + 260·exp(−9(t−tk)) added for each ring with tk≤t + (when t≥5.6, also add 520·exp(−6(t−5.6))) - each time a ring is passed, and at the moment of the explosion, the picture gives a sharp "kick".
- **Roll** roll(t) = 0.02·sin(1.7t) + (when t≥5.6, also add 0.12·sin(2π·0.9·(t−5.6))·exp(−2.2(t−5.6))).
- **Jitter**: amp = (t≥5.6 ? 22·exp(−3.2(t−5.6)) : 0), offset = (sin(53t)·amp, cos(47t)·amp).
- Before drawing the particles, light rings, core and shockwave: `ctx.translate(960+jitterX, 540+jitterY); ctx.rotate(roll); ctx.translate(-960, -540)`; after drawing them, `restore`, so that the white flash, captions and so on are not affected by roll and jitter.

## Projection

A point with "camera space" coordinates (X, Y, d) (d is its distance from the camera) is drawn on screen at: `sx = 960 + f·X/d`, `sy = 540 + f·Y/d`.

## Fixed parameters of each particle (generated once at startup)

- `a` (0–2π); `rho` = 220 + 1280·rand^0.8; `zw` = rand·L (world depth in the tunnel); `s` (0–1); `cls` (1 for 15%, 0 for the rest); `ph` (0–2π); `fq` (0.6–1.6);
- Explosion direction `dir`: zz = −0.55 + 1.55·rand, φ = rand·2π, rxy = √(1−zz²), dir = (rxy·cosφ, rxy·sinφ, zz);
- Explosion strength `mag` = 300 + 2600·rand^1.6;
- Rotation amount `sw` = (1.2 + 2·rand)·(random sign);
- Title target point `(tx, ty)`: see below.

## Title target points

Use a 1200×400 offscreen canvas and write the title in white bold text (`bold 280px "Noto Serif SC","Songti SC","SimSun",serif`, horizontally centered, `textBaseline='middle'`, position (600, 205)); sample every 3 pixels, taking the points with alpha>128, and convert their coordinates to ((x−600)·2.093, (y−200)·2.093); after a seeded shuffle, take N of them (if there are not enough, reuse points and add ±3 jitter). Particle i uses point i.

## Camera-space position of each particle at time t (write it as a function `place(p, t)` that returns X, Y, d)

- **t < 5.6 (tunnel)**: k = 1 − 0.92·smoothstep(5.0, 5.6, t) (during 5.0–5.6 seconds the particles converge toward the center of the picture); X = rho·cos(a)·k, Y = rho·sin(a)·k; d = ((zw − camZ(t)) mod L + L) mod L + 60.
- **5.6 ≤ t ≤ 8 (explosion)**: τ = min(1, (t−5.6)/2.4), g = 1 − (1−τ)³; world coordinates X = dir.x·mag·g, Y = dir.y·mag·g, Z = ZC + dir.z·mag·g; d = Z − camZ(t).
- **t > 8 (reunion)**: e = smoothstep(8, 10, t); start point E = (dir.x·mag, dir.y·mag, ZC + dir.z·mag), end point Tg = (tx, ty, ZT); Q = E + (Tg − E)·e; then rotate (Q.x, Q.y) around the origin by θ = sin(π·e)·sw; X, Y = the rotated result, Z = Q.z; d = Z − camZ(t).

## How to draw each frame

1. **Background** #05060A; then draw a radial gradient with center (960,540) and radius 700: from `rgba(30,60,90, 0.28·sf·(t<5.6 ? 1 : 0.4))` to `rgba(5,6,10,0)`. sf = 0.45 + 0.55·clamp(speed/2600, 0, 1), where speed is the current camera speed: 80+2520·(t/3)^2.2 when t<3; 2600 for 3–5 seconds; 2600·(1−(t−5)/0.6) for 5–5.6 seconds; 0 otherwise.
2. Use `globalCompositeOperation='lighter'`, `lineCap='round'` for everything below.
3. **Particles**: draw each one as a line segment from "its screen position at time tp" to "its screen position at time t". tp = max(t − DT, t≥5.6 ? 5.6 : 0), DT = (t<5.6 ? 0.03 : 0.06 − 0.03·smoothstep(8, 9, t)); at time tp, use the focal length for tp. If d<30 at either end, or d differs by more than 500 between the two ends (it has just wrapped back to the start of the tunnel), do not draw that segment.
   - **Color**: t<5.0: (255,213,154) when cls=1, otherwise (191,232,255); 5.0–5.6: blend toward white by smoothstep(5.0, 5.6, t); 5.6–8: while τ<0.4, blend from white to orange (255,176,74), then from orange to magenta (255,61,110); 8–10: blend from magenta to warm white (246,235,208) (by smoothstep(8,10,t)); t≥10: warm white.
   - **Opacity**: t<5.6: (1 − d/L)^1.4·(0.25 + 0.55·s)·sf·1.6, clamped to 0–1; t≥5.6: 0.9·(0.7 + 0.3·sin(fq·t + ph))·(t<8 ? 1−0.4τ : 0.9).
   - **Line weight**: t<5.6: (0.9 + 1.8·s)·clamp(√(900/d), 0.5, 2.2); t≥5.6: (2 + 3·s)·clamp(√(900/d), 0.6, 2.2).
4. **Light rings (draw only when t<5.6!)**: for each ring, d = the ring's z − camZ(t); do not draw if d<40 or d>5200; otherwise draw a 96-segment circle along radius R=260: points = (960 + f·R·cosθ/d, 540 + f·R·sinθ/d); line weight clamp(6·900/d, 1.5, 16), opacity 0.6·clamp(1 − d/5200, 0, 1); after one pass, draw it once more at 3 times the line weight and 1/4 of the opacity as a glow.
5. **Core light**: when t≥4.4 and dc = ZC − camZ(t) > 40, draw a white radial-gradient circle (center (960,540), from `rgba(255,255,255,0.9)` to transparent), radius = 140000/dc·(0.4 + 0.6·smoothstep(4.4, 5.6, t))·(f/900), further multiplied by exp(−3(t−5.6)) when t≥5.6.
6. **Shockwave**: when t≥5.6, ts = clamp((t−5.6)/1.2, 0, 1), world radius Rw = 3600·(1 − (1−ts)³); if ts<1 and dd = ZC − camZ(t) > 40: draw a circle with a white outline, center (960,540), radius f·Rw/dd, opacity 0.8·(1−ts), line weight 1 + 8·(1−ts).
7. Undo the translation/rotation (`restore`), then draw in order:
   - **White flash**: a full-screen white rectangle (lighter), opacity = (t≥5.6 ? 0.95·exp(−9(t−5.6)) : 0.7·smoothstep(5.4, 5.6, t)) + 0.3·exp(−14(t−tk)) added for each ring with t≥tk + (t≥10 ? 0.35·exp(−8(t−10)) : 0), with the total clamped to 1;
   - **Title solidifies** (source-over): opacity 0.9·smoothstep(9.7, 10.3, t)·(1 − smoothstep(11.4, 12, t)), draw the title centered at (960, 545), `bold 300px` in the same typeface, color #F6EBD0;
   - **Subtitle**: opacity 0.85·smoothstep(9.6, 10.4, t)·(1 − smoothstep(11.4, 12, t)), centered at (960, 790), serif 40px, color #EDE6D6;
   - **Vignette**: radial gradient, radius 400→1150, from `rgba(0,0,0,0)` to `rgba(0,0,0,0.55)`;
   - **Fade in at the start and fade out at the end**: a full-screen black rectangle, opacity (1 − smoothstep(0, 0.35, t)) + smoothstep(11.4, 12, t).

smoothstep(a, b, x): t = clamp((x−a)/(b−a), 0, 1), returns t·t·(3 − 2t).

## Do not

`Math.random`; storing the previous frame's state in `draw`; using DOM elements for animation; extra colors; drawing the light rings again after the explosion (as the camera pulls back they would pop up "head-on", so they must not be drawn).

## Self-check after writing (do not output)

- Refresh the same t twice: is the picture exactly identical?
- At t=2.8, do you see starlight streaks stretching outward in all directions, with several cyan/amber rings in the middle?
- At t=5.3, are the particles being pulled toward the center, with a mass of white light at the center? At t=5.7, is there a white radial explosion?
- At t=9.5, are the particles spinning as they converge? At t=10.8, is the title text clear?
- With 4000 lines plus 5 rings drawn per frame, will it stutter?
