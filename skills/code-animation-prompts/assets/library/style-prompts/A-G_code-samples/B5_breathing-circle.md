# B5 Breathing Circle

- Category: A–G Code Samples · B Particles
- Looks like: A cloud of particles swells and shrinks with the breath.
- Best for: soothing, slowing down, meditation
- Keywords: breathing, swelling and shrinking, slow

## Style prompt

Use code (Canvas 2D) to draw an animation of "Breathing Circle": A cloud of particles swells and shrinks with the breath.
Good for telling: soothing, slowing down, meditation
Keywords: breathing, swelling and shrinking, slow

Below is our own reference implementation: a drawing function S.B5(c, w, h, t, s), where c is the canvas 2D context, w/h are the width and height, t is in seconds, and s is an empty object for this function to store state in. The shared small utility functions are in _shared-functions.js in the same folder.

```js
S.B5 = (c, w, h, t, s) => {
  if (!s.init) { s.init = 1; const r = rng(17); s.p = Array.from({ length: 750 }, () => [r() * TAU, Math.sqrt(r()), r()]); }
  const b = .5 - .5 * Math.cos(TAU * t / 8), R = Math.min(w, h) * .33 * (.55 + .45 * b);
  c.fillStyle = '#061213'; c.fillRect(0, 0, w, h);
  glowDot(c, w / 2, h / 2, R * 1.3, '#4fb7a8', .12 + .1 * b);
  c.fillStyle = mixHex('#5fbfb0', '#dff3ec', b);
  for (const p of s.p) { const a = p[0] + t * .05 * (p[2] - .5), rr = p[1] * R + Math.sin(t * 1.3 + p[2] * 50) * 2; c.fillRect(w / 2 + Math.cos(a) * rr, h / 2 + Math.sin(a) * rr, 1.4, 1.4); }
  const rising = Math.sin(TAU * t / 8) > 0; c.font = `500 ${Math.min(w, h) / 20}px ${SERIF}`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillStyle = 'rgba(220,240,235,.55)'; c.fillText(rising ? 'Breathe in' : 'Breathe out', w / 2, h / 2 + Math.min(w, h) * .42);
};
```
