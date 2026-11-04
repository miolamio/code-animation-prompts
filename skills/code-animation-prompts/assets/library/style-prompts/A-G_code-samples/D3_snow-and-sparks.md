# D3 Snow and Sparks

- Category: A–G Code Samples · D Light and Weather
- Looks like: Snow falls, and a few sparks drift upward.
- Best for: farewell, endings, a little warmth in the cold
- Keywords: snow, sparks, drifting upward

## Style prompt

Use code (Canvas 2D) to draw an animation of "Snow and Sparks": Snow falls, and a few sparks drift upward.
Good for telling: farewell, endings, a little warmth in the cold
Keywords: snow, sparks, drifting upward

Below is our own reference implementation: a drawing function S.D3(c, w, h, t, s), where c is the canvas 2D context, w/h are the width and height, t is in seconds, and s is an empty object for this function to store state in. The shared small utility functions are in _shared-functions.js in the same folder.

```js
S.D3 = (c, w, h, t, s) => {
  if (!s.init) { s.init = 1; const r = rng(41); s.f = Array.from({ length: 170 }, () => [r() * w, r() * h, r(), r() * TAU]); s.e = Array.from({ length: 14 }, () => [r() * w, r() * h, r(), r() * TAU]); }
  c.fillStyle = vgrad(c, h, '#0e1627', '#04060b'); c.fillRect(0, 0, w, h); const m = Math.min(w, h) / 300;
  for (const [x0, y0, z, ph] of s.f) { const y = (y0 + t * (8 + z * 26) * m) % (h + 10), x = x0 + Math.sin(t * .6 + ph) * 10 * m; c.fillStyle = `rgba(235,242,255,${.35 + z * .55})`; c.beginPath(); c.arc(x, y, (.6 + z * 2.4) * m, 0, TAU); c.fill(); }
  c.globalCompositeOperation = 'lighter';
  for (const [x0, y0, z, ph] of s.e) { const y = h - ((h - y0 + t * (20 + z * 30) * m) % (h + 20)), x = x0 + Math.sin(t * 1.4 + ph) * 14 * m, fl = .5 + .5 * Math.sin(t * 9 + ph * 5); glowDot(c, x, y, 7 * m, '#ff9a3d', .45 * fl * (y / h)); c.fillStyle = `rgba(255,214,150,${fl * (y / h)})`; c.fillRect(x - .8, y - .8, 1.6, 1.6); }
  c.globalCompositeOperation = 'source-over';
};
```
