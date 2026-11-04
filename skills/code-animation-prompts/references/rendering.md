# Exporting browser animations

## Time interface

The included renderer works with HTML that provides this interface (it does not render arbitrary web pages):

```js
window.renderAt = async function (t) {
  // t is in seconds; move all animation, particles, camera and captions to this moment.
  draw(t);
};
```

When the page receives `?export=1`, it does not start a requestAnimationFrame or timer loop and stops self-playing CSS animations, so `renderAt(t)` alone advances the picture. Generate random particles at startup with a fixed seed, or compute them directly from index and time. Have async resources ready before `renderAt` returns. The canvas pixel size, CSS viewport and output size must match, with no player controls in the frame.

`../assets/starter/index.html` is a minimal example you can copy. HTML in the source material is not guaranteed to provide this interface; when adapting it, save a copy and leave the library unmodified. Existing projects such as Remotion use their own export tools.

## Dependencies

Search and install only need the Python 3.10+ standard library. Only browser rendering needs extra installs:

```bash
python -m pip install playwright
python -m playwright install chromium
ffmpeg -version
```

FFmpeg must be installed and on your PATH; for installation, see the [official FFmpeg downloads](https://ffmpeg.org/download.html).

## Export

```bash
python "<skill-dir>/scripts/render_video.py" ./index.html \
  --output ./output/video.mp4 --duration 12 --fps 30 --width 1920 --height 1080
```

If you have prepared music or voiceover, add `--audio ./narration.wav`. The script does not generate sound or loop short audio; it pads with silence or trims to the video length. The default is silent. If the output file already exists, it stops, so pick another filename.

The script loads the HTML through a local HTTP server bound to a random port on `127.0.0.1`, so keep dependent resources in the HTML file's directory and its subdirectories. It captures one frame at each `t = frame / fps` and encodes with FFmpeg as H.264 / yuv420p. Dimensions must be positive even numbers; the frame count is `ceil(duration * fps)`, so the actual length may round up by one frame. By default it captures the whole output viewport.

Frame-by-frame rendering of long or high-resolution pieces is slow. Export a short section first to check visuals and dependencies, then render the full piece. If the output fails, report the specific missing item or interface error and do not claim it finished.
