# C2 Single-Stroke Drawing

- Category: A–G Code Samples · C Line and Ink
- Looks like: A single line slowly draws mountains, a sun, and a small figure.
- Best for: the outline of a person or an event
- Keywords: single stroke, line drawing, growth

## Style prompt

Use code (Canvas 2D) to draw an animation of "Single-Stroke Drawing": A single line slowly draws mountains, a sun, and a small figure.
Good for telling: the outline of a person or an event
Keywords: single stroke, line drawing, growth

Below is our own reference implementation: a drawing function S.C2(c, w, h, t, s), where c is the canvas 2D context, w/h are the width and height, t is in seconds, and s is an empty object for this function to store state in. The shared small utility functions are in _shared-functions.js in the same folder.

```js
S.C2 = (c, w, h, t, s) => {
  if (!s.init) {
    s.init = 1; const m = Math.min(w, h), P = (x, y) => [x * w, y * h], circ = (cx, cy, r, n) => Array.from({ length: n + 1 }, (_, i) => [cx * w + Math.cos(-Math.PI / 2 + i / n * TAU) * r * m, cy * h + Math.sin(-Math.PI / 2 + i / n * TAU) * r * m]);
    s.strokes = [
      [[.04, .72], [.96, .72]].map(p => P(...p)),
      [[.06, .72], [.18, .5], [.27, .6], [.42, .36], [.55, .56], [.66, .47], [.79, .61], [.94, .52]].map(p => P(...p)),
      circ(.76, .27, .07, 48),
      circ(.3, .61, .02, 20),
      [[.3, .633], [.3, .68], [.29, .72]].map(p => P(...p)), [[.3, .68], [.31, .72]].map(p => P(...p)), [[.288, .665], [.3, .645], [.312, .665]].map(p => P(...p)),
    ];
    s.total = 0; for (const st of s.strokes) { st.len = 0; for (let i = 1; i < st.length; i++) st.len += Math.hypot(st[i][0] - st[i - 1][0], st[i][1] - st[i - 1][1]); s.total += st.len; }
  }
  const tm = t % 10, p = eOut(clamp(tm / 6.5, 0, 1)) * s.total, fade = 1 - ss(8.8, 10, tm);
  c.fillStyle = '#121722'; c.fillRect(0, 0, w, h);
  c.strokeStyle = `rgba(242,239,232,${fade})`; c.lineWidth = Math.max(1.4, Math.min(w, h) / 220); c.lineCap = 'round'; c.lineJoin = 'round';
  let left = p, tip = null;
  for (const st of s.strokes) {
    if (left <= 0) break; c.beginPath(); c.moveTo(st[0][0], st[0][1]);
    for (let i = 1; i < st.length; i++) { const sl = Math.hypot(st[i][0] - st[i - 1][0], st[i][1] - st[i - 1][1]); if (left >= sl) { c.lineTo(st[i][0], st[i][1]); left -= sl; tip = st[i]; } else { const k = left / sl; tip = [lerp(st[i - 1][0], st[i][0], k), lerp(st[i - 1][1], st[i][1], k)]; c.lineTo(tip[0], tip[1]); left = 0; break; } }
    c.stroke();
  }
  if (tip && tm < 6.6) glowDot(c, tip[0], tip[1], 14, '#f1b25c', .8);
};
```
