# F3 Split-Screen Comparison

- Category: A–G Code Samples · F Explainer
- Looks like: The past on the left, the present on the right, a line in between.
- Best for: past and present, parents and children
- Keywords: split screen, comparison, left and right

## Style prompt

Use code (Canvas 2D) to draw an animation of "Split-Screen Comparison": The past on the left, the present on the right, a line in between.
Good for telling: past and present, parents and children
Keywords: split screen, comparison, left and right

Below is our own reference implementation: a drawing function S.F3(c, w, h, t, s), where c is the canvas 2D context, w/h are the width and height, t is in seconds, and s is an empty object for this function to store state in. The shared small utility functions are in _shared-functions.js in the same folder.

```js
S.F3 = (c, w, h, t, s) => {
  if (!s.init) { s.init = 1; const r = rng(53); s.rain = Array.from({ length: 90 }, () => [r(), r(), .5 + r()]); s.lit = Array.from({ length: 40 }, () => [r(), r(), r() * TAU, r()]); }
  const dx = w * .5 + Math.sin(t * .6) * w * .04, m = Math.min(w, h), fs = Math.max(11, m / 16);
  c.save(); c.beginPath(); c.rect(0, 0, dx, h); c.clip(); c.fillStyle = vgrad(c, h, '#1a1e26', '#0b0d11'); c.fillRect(0, 0, w, h);
  c.strokeStyle = 'rgba(170,185,205,.35)'; c.lineWidth = 1; for (const [x, y, v] of s.rain) { const yy = ((y * h + t * 220 * v) % (h + 20)) - 10, xx = x * w; c.beginPath(); c.moveTo(xx, yy); c.lineTo(xx - 2, yy + 12 * v); c.stroke(); }
  c.fillStyle = 'rgba(210,218,230,.85)'; c.font = `700 ${fs}px ${SERIF}`; c.textAlign = 'left'; c.textBaseline = 'top'; c.fillText('Before', m * .06, m * .06); c.restore();
  c.save(); c.beginPath(); c.rect(dx, 0, w - dx, h); c.clip(); const g = c.createRadialGradient(w * .75, h * .6, 0, w * .75, h * .6, w * .6); g.addColorStop(0, '#3a2410'); g.addColorStop(1, '#120b05'); c.fillStyle = g; c.fillRect(0, 0, w, h);
  c.globalCompositeOperation = 'lighter'; for (const [x, y, ph, z] of s.lit) { const yy = ((y * h - t * (8 + z * 14)) % h + h) % h; glowDot(c, x * w, yy, 3 + z * 9, '#ffb664', .4 + .3 * Math.sin(t * 2 + ph)); } c.globalCompositeOperation = 'source-over';
  c.fillStyle = 'rgba(255,226,180,.92)'; c.font = `700 ${fs}px ${SERIF}`; c.textAlign = 'right'; c.textBaseline = 'top'; c.fillText('Now', w - m * .06, m * .06); c.restore();
  c.fillStyle = 'rgba(255,255,255,.7)'; c.fillRect(dx - .5, 0, 1, h);
};
```
