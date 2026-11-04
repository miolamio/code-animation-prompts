# D4 Daybreak

- Category: A–G Code Samples · D Light and Weather
- Looks like: The sky slowly warms from deep blue, and the sun rises.
- Best for: endings, hope, starting over
- Keywords: sunrise, gradient, daybreak

## Style prompt

Use code (Canvas 2D) to draw an animation of "Daybreak": The sky slowly warms from deep blue, and the sun rises.
Good for telling: endings, hope, starting over
Keywords: sunrise, gradient, daybreak

Below is our own reference implementation: a drawing function S.D4(c, w, h, t, s), where c is the canvas 2D context, w/h are the width and height, t is in seconds, and s is an empty object for this function to store state in. The shared small utility functions are in _shared-functions.js in the same folder.

```js
S.D4 = (c, w, h, t, s) => {
  if (!s.init) { s.init = 1; const r = rng(43); s.st = Array.from({ length: 90 }, () => [r() * w, r() * h * .6, r()]); }
  const K = [['#04060f', '#0d1430'], ['#0c1233', '#3b2e58'], ['#26305e', '#d0766a'], ['#4f79b5', '#f6c27f']];
  const p = (t % 12) / 12, seg = p < .75 ? p / .75 * 3 : 3, i = Math.min(2, Math.floor(seg)), f = ss(0, 1, seg - i), back = ss(.9, 1, p);
  const top = mixHex(mixHex(K[i][0], K[i + 1][0], f), K[0][0], back), bot = mixHex(mixHex(K[i][1], K[i + 1][1], f), K[0][1], back);
  c.fillStyle = vgrad(c, h, top, bot); c.fillRect(0, 0, w, h);
  const dawn = clamp(seg / 3, 0, 1) * (1 - back);
  for (const [x, y, z] of s.st) { c.fillStyle = `rgba(255,255,255,${(1 - dawn * 1.4) * (.3 + z * .6)})`; c.fillRect(x, y, 1.2, 1.2); }
  const m = Math.min(w, h), sy = lerp(h * .86, h * .5, eOut(dawn)); glowDot(c, w * .62, sy, m * .5, '#ffb46a', .35 * dawn); c.fillStyle = mixHex('#ff8a4a', '#fff1c8', dawn); c.beginPath(); c.arc(w * .62, sy, m * .07, 0, TAU); c.fill();
  const hill = (base, amp, col, ph) => { c.fillStyle = col; c.beginPath(); c.moveTo(0, h); for (let x = 0; x <= w; x += 6) c.lineTo(x, base + Math.sin(x / w * 5 + ph) * amp + Math.sin(x / w * 13 + ph) * amp * .3); c.lineTo(w, h); c.fill(); };
  hill(h * .74, h * .04, mixHex('#0a0f20', '#3a3550', dawn * .6), 1); hill(h * .82, h * .03, mixHex('#05070e', '#1d1a28', dawn * .5), 3);
};
```
