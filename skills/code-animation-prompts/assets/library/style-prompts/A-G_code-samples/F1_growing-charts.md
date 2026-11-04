# F1 Growing Charts

- Category: A–G Code Samples · F Explainer
- Looks like: Bars grow one by one, numbers tick up, then they connect into a line.
- Best for: data, research findings
- Keywords: charts, numbers, growth

## Style prompt

Use code (Canvas 2D) to draw an animation of "Growing Charts": Bars grow one by one, numbers tick up, then they connect into a line.
Good for telling: data, research findings
Keywords: charts, numbers, growth

Below is our own reference implementation: a drawing function S.F1(c, w, h, t, s), where c is the canvas 2D context, w/h are the width and height, t is in seconds, and s is an empty object for this function to store state in. The shared small utility functions are in _shared-functions.js in the same folder.

```js
S.F1 = (c, w, h, t, s) => {
  const tm = t % 8.5, V = [12, 19, 27, 33, 41, 58], N = ['Primary', 'Middle', 'High', 'College', 'Work', 'Now'], fade = 1 - ss(7.6, 8.5, tm);
  c.fillStyle = '#0f1418'; c.fillRect(0, 0, w, h); c.globalAlpha = fade;
  const l = w * .1, r = w * .94, top = h * .2, bot = h * .8, fs = Math.max(9, Math.min(w, h) / 24);
  c.fillStyle = '#8f9aa5'; c.font = `500 ${fs}px ${SANS}`; c.textBaseline = 'alphabetic'; c.textAlign = 'left'; c.fillText('Sample data: times I almost said it', l, h * .11);
  c.strokeStyle = '#2c3640'; c.lineWidth = 1; for (let k = 0; k <= 3; k++) { const y = lerp(bot, top, k / 3); c.beginPath(); c.moveTo(l, y); c.lineTo(r, y); c.stroke(); }
  const bw = (r - l) / V.length, pts = [];
  V.forEach((v, i) => {
    const e = eOut((tm - .2 - i * .25) / .8), bh = (bot - top) * v / 60 * e, x = l + bw * i + bw * .22, ww = bw * .56;
    c.fillStyle = i === V.length - 1 ? '#f1b25c' : '#5d7fa3'; c.fillRect(x, bot - bh, ww, bh);
    c.fillStyle = '#e8ecef'; c.textAlign = 'center'; c.font = `500 ${fs}px ${MONO}`; if (e > 0) c.fillText(Math.round(v * e), x + ww / 2, bot - bh - fs * .5);
    c.fillStyle = '#8f9aa5'; c.font = `400 ${fs * .9}px ${SANS}`; c.fillText(N[i], x + ww / 2, bot + fs * 1.4);
    pts.push([x + ww / 2, bot - (bot - top) * v / 60]);
  });
  const lp = clamp((tm - 2.6) / 1.4, 0, 1); if (lp > 0) { c.strokeStyle = '#f1b25c'; c.lineWidth = 2; c.beginPath(); const n = lp * (pts.length - 1); c.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i <= Math.floor(n); i++) c.lineTo(pts[i][0], pts[i][1]); const fi = Math.floor(n); if (fi < pts.length - 1) c.lineTo(lerp(pts[fi][0], pts[fi + 1][0], n - fi), lerp(pts[fi][1], pts[fi + 1][1], n - fi)); c.stroke(); }
  c.globalAlpha = 1;
};
```
