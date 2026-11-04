# E1 Minimal Geometry

- Category: A–G Code Samples · E Shapes and Paper
- Looks like: Circles, squares, and semicircles roll, drop, and grow on a solid color.
- Best for: making complicated things clear
- Keywords: geometry, flat, color blocks

## Style prompt

Use code (Canvas 2D) to draw an animation of "Minimal Geometry": Circles, squares, and semicircles roll, drop, and grow on a solid color.
Good for telling: making complicated things clear
Keywords: geometry, flat, color blocks

Below is our own reference implementation: a drawing function S.E1(c, w, h, t, s), where c is the canvas 2D context, w/h are the width and height, t is in seconds, and s is an empty object for this function to store state in. The shared small utility functions are in _shared-functions.js in the same folder.

```js
S.E1 = (c, w, h, t, s) => {
  const tm = t % 6.5, m = Math.min(w, h), ly = h * .68, out = eOut(ss(4.6, 5.6, tm)) * w * 1.2;
  c.fillStyle = '#ebe5d6'; c.fillRect(0, 0, w, h);
  c.save(); c.translate(-out * 0, 0);
  c.fillStyle = '#161616'; c.fillRect(w * .06, ly, w * .88 * eOut(tm / .8), Math.max(2, m * .012));
  const cr = m * .14, cx = lerp(-cr, w * .46, eOut((tm - .4) / 1.3)) + out; c.save(); c.translate(cx, ly - cr); c.rotate((cx / cr)); c.fillStyle = '#d9432f'; c.beginPath(); c.arc(0, 0, cr, 0, TAU); c.fill(); c.fillStyle = '#ebe5d6'; c.fillRect(-cr * .08, -cr, cr * .16, cr * .5); c.restore();
  const sq = m * .2, sqx = w * .72 + out, sqy = lerp(-sq, ly - sq / 2, eBack((tm - 1.1) / .9)), rot = eBack((tm - 3) / .7) * Math.PI / 2;
  c.save(); c.translate(sqx, sqy); c.rotate(rot); c.fillStyle = '#2047c9'; c.fillRect(-sq / 2, -sq / 2, sq, sq); c.restore();
  const yr = m * .18 * eBack((tm - 2) / .8); if (yr > 0) { c.fillStyle = '#f2b630'; c.beginPath(); c.arc(w * .24 + out, ly, yr, Math.PI, TAU); c.fill(); }
  c.restore();
};
```
