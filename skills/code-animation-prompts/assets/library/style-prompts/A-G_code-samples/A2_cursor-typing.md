# A2 Cursor Typing

- Category: A–G Code Samples · A Words
- Looks like: On a black background, a cursor types character by character, typing and then deleting.
- Best for: things you can't bring yourself to say, inner monologue
- Keywords: typing, cursor, deleting

## Style prompt

Use code (Canvas 2D) to draw an animation of "Cursor Typing": On a black background, a cursor types character by character, typing and then deleting.
Good for telling: things you can't bring yourself to say, inner monologue
Keywords: typing, cursor, deleting

Below is our own reference implementation: a drawing function S.A2(c, w, h, t, s), where c is the canvas 2D context, w/h are the width and height, t is in seconds, and s is an empty object for this function to store state in. The shared small utility functions are in _shared-functions.js in the same folder.

```js
S.A2 = (c, w, h, t, s) => {
  if (!s.init) {
    s.init = 1; let tt = 0, str = ''; const st = [[0, '']];
    const ops = [['type', 'Actually, I always wanted to tell you'], ['wait', 1.1], ['del', 6], ['wait', .5], ['type', "'m fine."], ['wait', 1.6], ['del', 3], ['wait', .4], ['type', '...'], ['wait', 1.6], ['clear']];
    for (const [k, v] of ops) {
      if (k === 'type') for (const ch of v) { tt += .17; str += ch; st.push([tt, str]); }
      else if (k === 'wait') tt += v;
      else if (k === 'del') for (let i = 0; i < v; i++) { tt += .07; str = str.slice(0, -1); st.push([tt, str]); }
      else { tt += .4; str = ''; st.push([tt, str]); }
    }
    s.st = st; s.len = tt + .8;
  }
  const tm = t % s.len; let i = 0; while (i + 1 < s.st.length && s.st[i + 1][0] <= tm) i++;
  const str = s.st[i][1], since = tm - s.st[i][0];
  c.fillStyle = '#0b0b0c'; c.fillRect(0, 0, w, h);
  const fs = Math.min(w / 10.5, h / 7); c.font = `500 ${fs}px ${SERIF}`; c.textBaseline = 'middle';
  const x0 = w * 0.1, y0 = h * 0.5; c.fillStyle = '#ece8df'; c.fillText(str, x0, y0);
  const cx = x0 + c.measureText(str).width + fs * 0.12;
  const on = since < .45 || Math.floor(tm * 1.8) % 2 === 0;
  if (on) { c.fillStyle = '#f1b25c'; c.fillRect(cx, y0 - fs * 0.55, Math.max(2, fs * 0.07), fs * 1.1); glowDot(c, cx, y0, fs * 0.9, '#f1b25c', .18); }
};
```
