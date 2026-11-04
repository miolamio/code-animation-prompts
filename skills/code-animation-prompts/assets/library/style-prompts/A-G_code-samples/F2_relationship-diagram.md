# F2 Relationship Diagram

- Category: A–G Code Samples · F Explainer
- Looks like: Arrows between people are drawn one by one, each with the words that were said written on it.
- Best for: family relationships, cause and effect
- Keywords: nodes, arrows, relationship diagram

## Style prompt

Use code (Canvas 2D) to draw an animation of "Relationship Diagram": Arrows between people are drawn one by one, each with the words that were said written on it.
Good for telling: family relationships, cause and effect
Keywords: nodes, arrows, relationship diagram

Below is our own reference implementation: a drawing function S.F2(c, w, h, t, s), where c is the canvas 2D context, w/h are the width and height, t is in seconds, and s is an empty object for this function to store state in. The shared small utility functions are in _shared-functions.js in the same folder.

```js
S.F2 = (c, w, h, t, s) => {
  const tm = t % 10, fade = 1 - ss(9, 10, tm), m = Math.min(w, h), fs = Math.max(10, m / 20);
  const Nd = { Me: [.5, .55], Dad: [.22, .3], Mom: [.78, .3], Grandma: [.5, .12], School: [.2, .82], Work: [.8, .82] };
  const E = [['Dad', 'Me', 'For your good', 1], ['Mom', 'Me', 'Obey', 1.8], ['Grandma', 'Dad', 'Endure hardship', 2.6], ['Me', 'School', 'Make us proud', 3.4], ['Me', 'Work', 'Never be weak', 4.2], ['Me', 'Mom', 'Cannot say it', 5.2]];
  c.fillStyle = '#0e1116'; c.fillRect(0, 0, w, h); c.globalAlpha = fade;
  const R = m * .075, at = k => [Nd[k][0] * w, Nd[k][1] * h];
  for (const [a, b, lab, t0] of E) {
    const p = eOut((tm - t0) / .7); if (p <= 0) continue; const A = at(a), B = at(b), an = Math.atan2(B[1] - A[1], B[0] - A[0]);
    const sx = A[0] + Math.cos(an) * R, sy = A[1] + Math.sin(an) * R, ex = B[0] - Math.cos(an) * R, ey = B[1] - Math.sin(an) * R, cx = lerp(sx, ex, p), cy = lerp(sy, ey, p);
    const warm = lab === 'Cannot say it'; c.strokeStyle = warm ? '#f1b25c' : '#7c8798'; c.lineWidth = 1.4; if (warm) c.setLineDash([5, 5]); c.beginPath(); c.moveTo(sx, sy); c.lineTo(cx, cy); c.stroke(); c.setLineDash([]);
    c.fillStyle = c.strokeStyle; c.beginPath(); c.moveTo(cx, cy); c.lineTo(cx - Math.cos(an - .4) * 9, cy - Math.sin(an - .4) * 9); c.lineTo(cx - Math.cos(an + .4) * 9, cy - Math.sin(an + .4) * 9); c.fill();
    c.font = `400 ${fs * .8}px ${SANS}`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillStyle = warm ? '#f1b25c' : '#aab3c0'; c.globalAlpha = fade * p; const d = c.measureText(lab).width / 2 * Math.abs(Math.sin(an)) + fs * .4 * Math.abs(Math.cos(an)) + fs * .25; c.fillText(lab, (sx + ex) / 2 - Math.sin(an) * d, (sy + ey) / 2 + Math.cos(an) * d); c.globalAlpha = fade;
  }
  c.font = `500 100px ${SANS}`; const nf = Math.min(fs * .85, R * 170 / Math.max(...Object.keys(Nd).map(k => c.measureText(k).width)));
  Object.keys(Nd).forEach((k, i) => {
    const p = eBack((tm - i * .12) / .5); if (p <= 0) return; const [x, y] = at(k); const me = k === 'Me';
    c.fillStyle = me ? '#f1b25c' : '#161b23'; c.strokeStyle = me ? '#f1b25c' : '#cfd6e0'; c.lineWidth = 1.2; c.beginPath(); c.arc(x, y, R * p, 0, TAU); c.fill(); c.stroke();
    c.fillStyle = me ? '#14100a' : '#e6e9ee'; c.font = `500 ${nf * p}px ${SANS}`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(k, x, y);
  });
  c.globalAlpha = 1;
};
```
