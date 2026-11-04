# A3 Big Type Impact

- Category: A–G Code Samples · A Words
- Looks like: Word after word slams into the picture, on the beat.
- Best for: emotional outbursts, key lines, music video choruses
- Keywords: big type, slamming down, on the beat

## Style prompt

Use code (Canvas 2D) to draw an animation of "Big Type Impact": Word after word slams into the picture, on the beat.
Good for telling: emotional outbursts, key lines, music video choruses
Keywords: big type, slamming down, on the beat

Below is our own reference implementation: a drawing function S.A3(c, w, h, t, s), where c is the canvas 2D context, w/h are the width and height, t is in seconds, and s is an empty object for this function to store state in. The shared small utility functions are in _shared-functions.js in the same folder.

```js
S.A3 = (c, w, h, t, s) => {
  const L = [["You", .145, .33, .30, 0, .23], ["know", .435, .30, .22, 0, .29], ["nothing", .785, .33, .17, 0, .36], ["It's", .16, .62, .20, 0, .24], ["all", .41, .62, .14, 0, .18], ["for your own good", .46, .84, .16, 1, .72], ["Obey", .76, .60, .13, 0, .30], ["!", .875, .84, .22, 1, .10]];
  const beat = .4, len = L.length * beat + 1.4, tm = t % len, k = Math.floor(tm / beat), age = tm - k * beat;
  const m = Math.min(w, h), hit = k < L.length ? Math.exp(-age * 9) : 0;
  c.fillStyle = mixHex('#08080a', '#2a2a2e', hit * .5); c.fillRect(0, 0, w, h);
  const sx = (Math.sin(t * 91) * 6) * hit, sy = (Math.cos(t * 77) * 6) * hit;
  c.save(); c.translate(sx, sy); c.textAlign = 'center'; c.textBaseline = 'middle';
  for (let i = 0; i <= Math.min(k, L.length - 1); i++) {
    const [txt, fx0, fy, fz, red, mw] = L[i], newest = i === k, port = h > w, fx = port ? .5 + (fx0 - .5) * .85 : fx0;
    const sc = newest ? 1 + .9 * Math.exp(-age * 16) : 1;
    const size = fz * m * (port ? .95 : 1.45); c.font = `900 ${size}px ${SANS}`;
    c.font = `900 ${size * Math.min(1, mw * w * (port ? .85 : 1) / c.measureText(txt).width) * sc}px ${SANS}`;
    c.fillStyle = red ? (newest ? '#ff4a32' : '#a3392a') : (newest ? '#ffffff' : '#55565c');
    c.fillText(txt, fx * w, fy * h);
  }
  c.restore();
};
```
