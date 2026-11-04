# D1 Rainy Window

- Category: A–G Code Samples · D Light and Weather
- Looks like: Raindrops on glass, with blurred night lights behind.
- Best for: waiting, nighttime, longing
- Keywords: rainy window, night, blurred lights

## Style prompt

Use code (Canvas 2D) to draw an animation of "Rainy Window": Raindrops on glass, with blurred night lights behind.
Good for telling: waiting, nighttime, longing
Keywords: rainy window, night, blurred lights

Below is our own reference implementation: a drawing function S.D1(c, w, h, t, s), where c is the canvas 2D context, w/h are the width and height, t is in seconds, and s is an empty object for this function to store state in. The shared small utility functions are in _shared-functions.js in the same folder.

```js
S.D1 = (c, w, h, t, s, dpr) => {
  if (!s.init) {
    s.init = 1; const r = rng(31); [s.bg, s.bx] = offscreen(w, h, dpr); const b = s.bx; b.fillStyle = vgrad(b, h, '#0b1020', '#05060b'); b.fillRect(0, 0, w, h);
    const cols = ['#ffb35c', '#ff6a4d', '#6fd1e0', '#fff1cf', '#ffd27a'];
    for (let i = 0; i < 46; i++) glowDot(b, r() * w, h * (.25 + r() * .7), (8 + r() * 36) * Math.min(w, h) / 300, cols[Math.floor(r() * cols.length)], .28 + r() * .25);
    s.dots = Array.from({ length: Math.round(w * h / 500) }, () => [r() * w, r() * h, .6 + r() * 2.2]);
    s.sl = Array.from({ length: 9 }, () => ({ x: r() * w, y: r() * h, v: 0, r: 2 + r() * 2.2, ph: r() * 10, tr: [] }));
  }
  const dt = clamp(t - (s.lt ?? t), 0, .05); s.lt = t;
  c.drawImage(s.bg, 0, 0, w, h);
  for (const [x, y, r] of s.dots) { c.fillStyle = 'rgba(190,210,235,.12)'; c.beginPath(); c.arc(x, y, r, 0, TAU); c.fill(); c.fillStyle = 'rgba(255,255,255,.35)'; c.fillRect(x - r * .3, y - r * .4, Math.max(.6, r * .35), Math.max(.6, r * .35)); }
  for (const d of s.sl) {
    const go = Math.sin(t * 1.3 + d.ph) > .2; d.v = lerp(d.v, go ? 60 * h / 300 : 2, .1); d.y += d.v * dt; d.x += Math.sin(t * 3 + d.ph) * .15;
    d.tr.push([d.x, d.y]); if (d.tr.length > 60) d.tr.shift();
    if (d.y > h + 10) { d.y = -10; d.x = Math.random() * w; d.tr = []; }
    c.strokeStyle = 'rgba(200,220,240,.12)'; c.lineWidth = d.r * .6; c.beginPath(); d.tr.forEach((p, i) => i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.stroke();
    const g = c.createLinearGradient(d.x, d.y - d.r, d.x, d.y + d.r); g.addColorStop(0, 'rgba(255,255,255,.5)'); g.addColorStop(1, 'rgba(120,140,170,.2)'); c.fillStyle = g; c.beginPath(); c.ellipse(d.x, d.y, d.r, d.r * 1.25, 0, 0, TAU); c.fill();
  }
};
```
