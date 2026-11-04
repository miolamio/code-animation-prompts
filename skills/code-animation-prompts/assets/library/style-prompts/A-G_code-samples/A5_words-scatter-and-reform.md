# A5 Words Scatter and Reform

- Category: A–G Code Samples · A Words
- Looks like: A sentence scatters into particles and reforms into a different sentence.
- Best for: a change of heart, a new way of understanding
- Keywords: scatter, reform, transform

## Style prompt

Use code (Canvas 2D) to draw an animation of "Words Scatter and Reform": A sentence scatters into particles and reforms into a different sentence.
Good for telling: a change of heart, a new way of understanding
Keywords: scatter, reform, transform

Below is our own reference implementation: a drawing function S.A5(c, w, h, t, s), where c is the canvas 2D context, w/h are the width and height, t is in seconds, and s is an empty object for this function to store state in. The shared small utility functions are in _shared-functions.js in the same folder.

```js
S.A5 = (c, w, h, t, s, dpr) => {
  if (!s.init) {
    s.init = 1; const P = ["It's all my fault", "It wasn't my fault"], pts = [];
    for (const p of P) {
      const [oc, ox] = offscreen(w, h, 1), lines = (h > w ? [p.slice(0, Math.ceil(p.length / 2)), p.slice(Math.ceil(p.length / 2))] : [p]).map(l => l.trim());
      ox.font = `900 100px ${SERIF}`; const fs = Math.min(w * 82 / Math.max(...lines.map(l => ox.measureText(l).width)), h * 0.34 / lines.length);
      ox.fillStyle = '#fff'; ox.font = `900 ${fs}px ${SERIF}`; ox.textAlign = 'center'; ox.textBaseline = 'middle';
      lines.forEach((l, i) => ox.fillText(l, w / 2, h / 2 + (i - (lines.length - 1) / 2) * fs * 1.15));
      const d = ox.getImageData(0, 0, oc.width, oc.height).data, st = Math.max(2, Math.round(fs / 40)), arr = [];
      for (let y = 0; y < oc.height; y += st) for (let x = 0; x < oc.width; x += st) if (d[(y * oc.width + x) * 4 + 3] > 128) arr.push([x, y]);
      pts.push(arr);
    }
    const r = rng(9), N = Math.min(3200, Math.max(pts[0].length, pts[1].length));
    s.p = []; for (let i = 0; i < N; i++) { const a = pts[0][Math.floor(r() * pts[0].length)], b = pts[1][Math.floor(r() * pts[1].length)], an = r() * TAU, rr = Math.sqrt(r()) * Math.min(w, h) * .55; s.p.push([a[0], a[1], b[0], b[1], w / 2 + Math.cos(an) * rr * 1.4, h / 2 + Math.sin(an) * rr, r()]); }
  }
  const q = t % 9; c.fillStyle = '#07070a'; c.fillRect(0, 0, w, h);
  let col;
  for (const p of s.p) {
    let x, y, k;
    if (q < 2) { x = p[0]; y = p[1]; k = 0; }
    else if (q < 3.3) { const e = eOut((q - 2) / 1.3); x = lerp(p[0], p[4], e); y = lerp(p[1], p[5], e); k = e * .5; }
    else if (q < 4.9) { const e = ss(0, 1, (q - 3.3) / 1.6 - p[6] * .15); x = lerp(p[4], p[2], e); y = lerp(p[5], p[3], e); k = .5 + e * .5; }
    else if (q < 7.4) { x = p[2]; y = p[3]; k = 1; }
    else { const e = ss(7.4, 9, q); x = lerp(p[2], p[0], e); y = lerp(p[3], p[1], e); k = 1 - e; }
    const j = 1.2; x += Math.sin(t * 2 + p[6] * 40) * j; y += Math.cos(t * 1.7 + p[6] * 30) * j;
    col = mixHex('#9aa9c4', '#f6be72', k); c.fillStyle = col; c.fillRect(x, y, 1.6, 1.6);
  }
};
```
