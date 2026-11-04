# C1 Spreading Ink Wash

- Category: A–G Code Samples · C Line and Ink
- Looks like: Ink bleeds outward across rice paper, bloom after bloom.
- Best for: a Chinese sensibility, memories, grief
- Keywords: ink wash, bleed outward, rice paper

## Style prompt

Use code (Canvas 2D) to draw an animation of "Spreading Ink Wash": Ink bleeds outward across rice paper, bloom after bloom.
Good for telling: a Chinese sensibility, memories, grief
Keywords: ink wash, bleed outward, rice paper

Below is our own reference implementation: a drawing function S.C1(c, w, h, t, s), where c is the canvas 2D context, w/h are the width and height, t is in seconds, and s is an empty object for this function to store state in. The shared small utility functions are in _shared-functions.js in the same folder.

```js
S.C1 = (c, w, h, t, s, dpr) => {
  if (!s.init) {
    s.init = 1; s.paper = paperTex(w, h, dpr, '#e9e2d2', 21); const r = rng(23);
    s.blobs = [[.3, .45, .26, .2], [.62, .38, .2, 1.5], [.48, .66, .16, 3.0], [.78, .62, .12, 4.2]].map(([x, y, R, t0]) => ({ x, y, R, t0, k: Array.from({ length: 16 }, () => [(r() - .5) * .5, (r() - .5) * .5, .4 + r() * .6]) }));
  }
  const tm = t % 10; c.drawImage(s.paper, 0, 0, w, h); const m = Math.min(w, h);
  c.globalCompositeOperation = 'multiply';
  for (const b of s.blobs) {
    const age = tm - b.t0; if (age <= 0) continue; const g = 1 - Math.exp(-age * .9), R = b.R * m * g;
    for (const [dx, dy, kk] of b.k) { const gr = c.createRadialGradient(b.x * w + dx * R, b.y * h + dy * R, 0, b.x * w + dx * R, b.y * h + dy * R, R * kk); gr.addColorStop(0, 'rgba(28,28,32,.22)'); gr.addColorStop(.7, 'rgba(28,28,32,.08)'); gr.addColorStop(1, 'rgba(28,28,32,0)'); c.fillStyle = gr; c.beginPath(); c.arc(b.x * w + dx * R, b.y * h + dy * R, R * kk, 0, TAU); c.fill(); }
  }
  c.globalCompositeOperation = 'source-over';
  const sz = m * .085, sx = w * .06, sy = h - sz - h * .07; c.fillStyle = '#b3352a'; c.fillRect(sx, sy, sz, sz);
  c.fillStyle = '#f3e6d6'; c.font = `700 ${sz * .38}px ${SERIF}`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('俯仰', sx + sz / 2, sy + sz / 2); // seal characters 俯仰 ("looking up and down")
  const f = ss(8.6, 10, tm); if (f > 0) { c.globalAlpha = f; c.drawImage(s.paper, 0, 0, w, h); c.globalAlpha = 1; }
};
```
