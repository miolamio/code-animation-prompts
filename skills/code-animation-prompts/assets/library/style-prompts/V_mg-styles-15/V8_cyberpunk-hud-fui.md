# V8 Cyberpunk HUD / FUI

- Category: V mg-styles-15 · mg-styles-15
- Best for: sci-fi interfaces

## Style prompt

# Cyberpunk HUD / FUI (Fictional UI)

**Original video**: KESTREL-9 · TARGET ACQUIRED · 1920×1080 · 30 fps · 10 s · final AI review score 7.93 / 10

**Source code**: [demos/22-hud/](../demos/22-hud/)

## How to use

1. Create a new empty folder and open an AI assistant in it that can write code and run commands (for example Claude Code). Your machine needs to be able to render web pages (Node + Chrome) and run ffmpeg.
2. Copy the entire "Prompt" below into it and send.
3. To use your own content: change the story, brand name, copy and color palette in `Creative seed`, or the dimensions in `Output` (for example vertical format 1080×1920). Do not delete the `Signature features` section; it is what makes this style instantly recognizable.
4. To improve further: once the final video is out, open a separate AI to review it with [rubric.md](../rubric.md), then paste the review back to the AI that made it for another round. The original video went through two such rounds.

## Prompt

```text
You are the director, motion designer, engineer and sound designer of ONE 10-second motion-design film.
The goal is the most classic, yet most stunning form of this style — award-shortlist / high-end commercial quality. A clean,
template-looking result is a fail. Benchmarks: Buck, ManvsMachine, Ordinary Folk, Giant Ant, Territory Studio, Apple keynote
motion, Pentagram motion identities, top Behance/Motionographer features, top Douyin/Bilibili designer accounts.

# Style
Cyberpunk HUD / FUI (Fictional UI)

# Output (fixed)
- 1920×1080, 30 fps, exactly 10.000 s (300 frames), H.264 MP4 with stereo AAC audio (48 kHz), mastered to −14 LUFS
  integrated, true peak ≤ −1 dBTP. Final file: video.mp4.

# Suggested technical route
HTML: SVG/Canvas FUI layers + Three.js wireframe hologram; seeded random data; glow/scanline post pass
(You may choose a better route if it clearly raises quality; say why.)

# Creative seed
"TARGET ACQUIRED": Cyberpunk HUD / FUI, film-UI grade (Territory Studio-level density & restraint).
- Deep teal-black; cyan #00E5FF linework with orange/red #FF6A00 alert state; hex grid, concentric rotating rings with ticks, radar sweep (conic) with blips, data columns (monospace numbers rolling 3–5 frames then settling), typewriter status lines with cursor, sparkline graphs, a central Three.js wireframe hologram (globe or drone) with scanlines.
- Layered build-up: lines draw on in hierarchical staggered order → data comes alive → a target is found → lock brackets snap 1.4 → 1.0 (fast-out slow-in) → everything flips to alert orange with 'TARGET LOCKED', coordinates "N31°14′ E121°29′".
- Glow, slight chromatic aberration, scanlines, restrained micro-glitches.
Sound: darksynth pulse + HUD beeps, scan sweeps, ascending lock-on tone, alarm on lock.

You are the director: you may change the concept, copy, story beats and brand names if you find a stronger idea, but the result must remain the CANONICAL, instantly-recognisable form of this style and must hit its signature features below.

# Signature features and key techniques (the result is judged against these)
Packaging that simulates the heads-up displays of sci-fi film/game interfaces: cyan-orange neon wireframes, target-lock frames, radar sweeps, tiny data-stream text. It serves as the default 'tech' skin in tech product reviews, game edits (Cyberpunk 2077, EVA fan remixes), military and aerospace science explainers and AI product demos; AE HUD tutorials on Bilibili reach 200,000 views.
Visual features: cyan/orange neon wireframes, target-lock frames and crosshairs, radar/ring scan loop, small monospace data streams and typewriter text, hexagonal grids and bloom
Key techniques: wireframe growth: SVG stroke-dasharray/dashoffset stroke animation, with elements unfolding in hierarchical staggered frames
Ring radar: conic-gradient scan sector rotating in a loop + target points flickering
Number rolling: random numbers jump quickly for 3~5 frames, then settle on the true value; text typewriter + blinking cursor
Lock frame: corner brackets shrink from large to small and snap to the target (scale 1.4→1.0 + fast-out slow-in)
Global outer glow + slight chromatic aberration + scanline overlay for a unified material feel

# How to work
1. Treatment. Write down one clear idea: a hook in the first 0.5 s (never open on more than 0.3 s of empty or black), an
   escalation, one unmistakable hero moment at ~60–75 % of the runtime, and a composed end frame held ~0.8–1.2 s with living
   micro-motion. Map every signature feature above to a moment. Keep one cue sheet (beats and hit times) that both the
   picture and the sound read from.
2. Key frames before motion. Build the look, render stills at 6–10 key times and actually look at them. Each still should be
   poster-worthy: composition, hierarchy, negative space, type set properly (kerning, line-height, weight contrast, language-appropriate
   punctuation, ~5 % safe margins). Iterate until nothing looks default, generic, cramped or "AI-template".
3. Motion. Build the choreography and preview at low resolution. Step through the fastest moves frame by frame: spacing,
   easing, arcs, overlap, anticipation and follow-through, motion blur. No unintended dead spans; the energy follows the music.
4. Sound. Write genre-correct music and sound design locked to the cue sheet. Check that visual hits land on audio onsets.
   Master to the output spec.
5. Final. Render at full resolution (motion blur where apt), then check: exactly 10.00 s, resolution, fps, audio present and at
   the right loudness, no black frames, no fallback fonts or tofu, no clipped elements at the frame edges, no shimmer on thin
   lines, no gradient banding. Fix and repeat until you would submit it to a festival.
6. Write an honest self-critique: what is strongest, what is weakest, what you would do with more time.

# Rules
- Rendering must be deterministic: every frame is a pure function of time t. Seeded randomness only; physics and particles
  precomputed or closed-form; no real-time clocks; no state-triggered CSS transitions. A reliable route: a web page that can
  draw any time t on request, captured frame by frame with a headless browser and encoded with ffmpeg (or a Blender script
  that renders a PNG sequence).
- Assets: only CC0 / public domain / OFL / Apache / free-for-commercial-use. Record each source and licence in CREDITS.md.
  No real brand trademarks; invent brand names.
- On-screen text must be correct and natural: idiomatic in the user's language, with that language's proper punctuation, no typos.

# Craft checklist (what a jury looks for)
- Style authenticity: an expert names the style in one second; every signature technique is present and executed correctly.
- Motion craft: purposeful easing (no linear unless mechanical by design), overlap and stagger, anticipation and
  follow-through, arcs, squash and stretch where the style allows, consistent physics, motion blur where apt; transitions
  carried by elements, not crossfades.
- Rhythm: hits locked to the music; contrast between busy and calm; no monotony.
- Design: strong composition, grid, typographic hierarchy, controlled palette; texture and finishing (grain, glow, vignette)
  only where the style wants it; nothing looks accidental.
- Technical polish: no jitter (unless intended), no popping, no aliasing, no banding, no fallback fonts, no half-loaded images.
- Sound: genre-correct, musical, synced, mastered.

# Before you deliver, score yourself honestly
1–10 on style fidelity, concept wow, motion craft, design & typography, finish & texture, sound & sync, technical
(6 = template-level, 8 = high-end agency, 9 = award shortlist). Aim for 9; fix whatever scores lowest first.

# Deliver
video.mp4, plus a short report: the concept in two sentences; a beat sheet with timecodes; how each signature feature is
realised; the tech route; check numbers (duration, resolution, fps, loudness, true peak); your honest top-3 weaknesses.
```
