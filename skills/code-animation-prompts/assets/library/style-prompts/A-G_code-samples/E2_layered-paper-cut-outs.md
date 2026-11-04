# E2 Layered Paper Cut-Outs

- Category: A–G Code Samples · E Shapes and Paper
- Looks like: Layer upon layer of paper pieces with shadows, the front moving fast and the back slow.
- Best for: childhood, stories, tender passages
- Keywords: paper-cut, paper pieces, layering

## Style prompt

Use code (Canvas 2D) to draw an animation of "Layered Paper Cut-Outs": Layer upon layer of paper pieces with shadows, the front moving fast and the back slow.
Good for telling: childhood, stories, tender passages
Keywords: paper-cut, paper pieces, layering

Below is our own reference implementation: a drawing function S.E2(c, w, h, t, s), where c is the canvas 2D context, w/h are the width and height, t is in seconds, and s is an empty object for this function to store state in. The shared small utility functions are in _shared-functions.js in the same folder.

```js
S.E2 = (c, w, h, t, s, dpr) => {
  if (!s.init) { s.init = 1; s.paper = paperTex(w, h, dpr, '#f1e9dc', 47); }
  c.fillStyle = vgrad(c, h, '#f4ecdf', '#dcebe5'); c.fillRect(0, 0, w, h);
  const m = Math.min(w, h); c.save(); c.shadowColor = 'rgba(80,60,30,.25)'; c.shadowBlur = 14; c.fillStyle = '#fff8e7'; c.beginPath(); c.arc(w * .72, h * .26, m * .1, 0, TAU); c.fill(); c.restore();
  const cols = ['#cfe3df', '#9fc7c1', '#6fa59f', '#43807b', '#235a57'];
  cols.forEach((col, i) => {
    const base = h * (.42 + i * .11), amp = h * (.05 + i * .012), off = t * (6 + i * 10) * m / 300;
    c.save(); c.shadowColor = 'rgba(20,40,40,.35)'; c.shadowBlur = 10; c.shadowOffsetY = -3; c.fillStyle = col; c.beginPath(); c.moveTo(0, h);
    for (let x = 0; x <= w + 6; x += 6) { const u = (x + off) / w; c.lineTo(x, base + Math.sin(u * (3 + i) + i * 1.7) * amp + Math.sin(u * 11 + i) * amp * .25); }
    c.lineTo(w, h); c.closePath(); c.fill(); c.restore();
    if (i === 2) { const hx = ((w * .3 - off) % (w * 1.3) + w * 1.3) % (w * 1.3) - w * .15, u = (hx + off) / w, hy = base + Math.sin(u * 5 + i * 1.7) * amp + Math.sin(u * 11 + i) * amp * .25, hs = m * .07; c.fillStyle = '#2f6f69'; c.fillRect(hx - hs / 2, hy - hs * .9, hs, hs); c.beginPath(); c.moveTo(hx - hs * .65, hy - hs * .9); c.lineTo(hx, hy - hs * 1.5); c.lineTo(hx + hs * .65, hy - hs * .9); c.fill(); c.fillStyle = '#ffd98a'; c.fillRect(hx - hs * .12, hy - hs * .55, hs * .24, hs * .3); }
  });
  c.globalAlpha = .5; c.globalCompositeOperation = 'multiply'; c.drawImage(s.paper, 0, 0, w, h); c.globalCompositeOperation = 'source-over'; c.globalAlpha = 1;
};
```
