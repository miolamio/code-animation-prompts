# B2 Firefly Dust

- Category: A–G Code Samples · B Particles
- Looks like: Warm-colored points of light drift slowly upward, some far, some near.
- Best for: warmth, memories, finding the light again
- Keywords: firefly, light dust, warm

## Style prompt

Use code (Canvas 2D) to draw an animation of "Firefly Dust": Warm-colored points of light drift slowly upward, some far, some near.
Good for telling: warmth, memories, finding the light again
Keywords: firefly, light dust, warm

Below is our own reference implementation: a drawing function S.B2(c, w, h, t, s), where c is the canvas 2D context, w/h are the width and height, t is in seconds, and s is an empty object for this function to store state in. The shared small utility functions are in _shared-functions.js in the same folder.

```js
S.B2 = (c, w, h, t, s) => {
  if (!s.init) { s.init = 1; const r = rng(7); s.p = []; for (let i = 0; i < 70; i++) s.p.push({ x: r() * w, y: r() * h, z: r(), ph: r() * TAU, f: .5 + r() * 1.5 }); }
  const g = c.createRadialGradient(w * .5, h * .7, 0, w * .5, h * .7, Math.hypot(w, h) * .7); g.addColorStop(0, '#231409'); g.addColorStop(1, '#060403'); c.fillStyle = g; c.fillRect(0, 0, w, h);
  c.globalCompositeOperation = 'lighter'; const m = Math.min(w, h) / 300;
  for (const p of s.p) {
    const z = p.z, size = (1.2 + z * z * 24) * m, vy = (5 + z * 16) * m;
    const y = ((p.y - t * vy) % (h + 60) + h + 60) % (h + 60) - 30, x = p.x + Math.sin(t * .4 * p.f + p.ph) * 18 * m;
    const fl = .55 + .45 * Math.sin(t * p.f * 2.2 + p.ph), a = (z > .8 ? .13 : .55) * fl;
    glowDot(c, x, y, size * (z > .8 ? 1.6 : 1), z > .5 ? '#ffb664' : '#ffd79a', a);
    if (z < .8) { c.fillStyle = `rgba(255,236,200,${.8 * fl})`; c.beginPath(); c.arc(x, y, Math.max(.6, size * .12), 0, TAU); c.fill(); }
  }
  c.globalCompositeOperation = 'source-over';
};
```
