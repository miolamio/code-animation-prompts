# A4 Word Tunnel

- Category: A–G Code Samples · A Words
- Looks like: Words form ring after ring, and the shot burrows inward.
- Best for: being unable to make sense of something, thoughts spiraling deeper
- Keywords: tunnel, rotation, burrowing inward

## Style prompt

Use code (Canvas 2D) to draw an animation of "Word Tunnel": Words form ring after ring, and the shot burrows inward.
Good for telling: being unable to make sense of something, thoughts spiraling deeper
Keywords: tunnel, rotation, burrowing inward

Below is our own reference implementation: a drawing function S.A4(c, w, h, t, s), where c is the canvas 2D context, w/h are the width and height, t is in seconds, and s is an empty object for this function to store state in. The shared small utility functions are in _shared-functions.js in the same folder.

```js
S.A4 = (c, w, h, t, s) => {
  c.fillStyle = '#04050a'; c.fillRect(0, 0, w, h);
  const N = 14, R = Math.hypot(w, h) * 0.5, txt = 'Why me? Why can I not say it? Why?';
  c.textAlign = 'center'; c.textBaseline = 'middle';
  for (let i = 0; i < N; i++) {
    const p = ((i / N) + t * 0.08) % 1, r = R * (0.03 + Math.pow(p, 2.6) * 1.6), a = Math.sin(Math.PI * p) * .9;
    if (r < 3) continue;
    const n = 20, rot = i * .37 + t * .18 * (i % 2 ? 1 : -1), fs = r * 0.15;
    c.font = `500 ${fs}px ${SERIF}`; c.fillStyle = `rgba(${lerp(120, 230, p)},${lerp(140, 225, p)},${lerp(200, 240, p)},${a})`;
    for (let j = 0; j < n; j++) { const an = rot + j / n * TAU; c.save(); c.translate(w / 2 + Math.cos(an) * r, h / 2 + Math.sin(an) * r); c.rotate(an + Math.PI / 2); c.fillText(txt[(i * 3 + j) % txt.length], 0, 0); c.restore(); }
  }
  glowDot(c, w / 2, h / 2, Math.min(w, h) * .12, '#7f8fd6', .25);
};
```
