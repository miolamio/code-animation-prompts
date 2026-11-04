# D2 Window Light and Dust

- Category: A–G Code Samples · D Light and Weather
- Looks like: A beam of light comes through a window, with dust drifting in the light.
- Best for: quiet, time, old houses
- Keywords: window light, dust, light beam

## Style prompt

Use code (Canvas 2D) to draw an animation of "Window Light and Dust": A beam of light comes through a window, with dust drifting in the light.
Good for telling: quiet, time, old houses
Keywords: window light, dust, light beam

Below is our own reference implementation: a drawing function S.D2(c, w, h, t, s), where c is the canvas 2D context, w/h are the width and height, t is in seconds, and s is an empty object for this function to store state in. The shared small utility functions are in _shared-functions.js in the same folder.

```js
S.D2 = (c, w, h, t, s) => {
  if (!s.init) { s.init = 1; const r = rng(37); s.p = Array.from({ length: 170 }, () => [r() * w, r() * h, r() * TAU, .4 + r() * 1.4]); }
  c.fillStyle = '#0b0806'; c.fillRect(0, 0, w, h);
  const wx = w * .08, wy = h * .08, ww = w * .2, wh = h * .36;
  const beam = new Path2D(); beam.moveTo(wx + ww, wy); beam.lineTo(wx, wy + wh); beam.lineTo(w * .52, h * 1.02); beam.lineTo(w * 1.02, h * .66); beam.closePath();
  const g = c.createLinearGradient(wx, wy, w * .8, h); g.addColorStop(0, 'rgba(255,222,165,.34)'); g.addColorStop(1, 'rgba(255,200,140,.03)');
  c.globalCompositeOperation = 'lighter'; c.fillStyle = g; c.fill(beam);
  c.fillStyle = 'rgba(255,214,160,.12)'; c.beginPath(); c.moveTo(w * .52, h); c.lineTo(w * .7, h * .86); c.lineTo(w, h * .7); c.lineTo(w, h); c.fill();
  c.globalCompositeOperation = 'source-over';
  c.fillStyle = '#f4e2c2'; c.fillRect(wx, wy, ww, wh); c.fillStyle = '#0b0806'; c.fillRect(wx + ww / 2 - 2, wy, 4, wh); c.fillRect(wx, wy + wh / 2 - 2, ww, 4);
  for (const p of s.p) {
    const x = (p[0] + Math.sin(t * .2 + p[2]) * 20 + t * 4) % w, y = (p[1] + Math.cos(t * .17 + p[2]) * 16 - t * 2 + h * 10) % h;
    const lit = c.isPointInPath(beam, x * (c.getTransform().a), y * (c.getTransform().d));
    c.fillStyle = lit ? `rgba(255,236,200,${.5 + .4 * Math.sin(t * 2 + p[2])})` : 'rgba(255,220,170,.05)'; c.beginPath(); c.arc(x, y, p[3] * (lit ? 1 : .7), 0, TAU); c.fill();
  }
};
```
