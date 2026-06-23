# Promo Video

This folder contains a vertical short-video source for promoting AI Delivery Spec.

## Output

- Format: 9:16 vertical
- Resolution: 1080x1920
- Duration: 45 seconds
- Main output: `dist/ai-delivery-spec-promo-vertical.mp4`

## Render

```bash
npx --yes --package playwright --package ffmpeg-static node media/promo-video/render-video.js
```

Optional lower-quality quick render:

```bash
PROMO_FPS=8 npx --yes --package playwright --package ffmpeg-static node media/promo-video/render-video.js
```

## Suggested Caption

Most PRDs are not build-ready.

AI Delivery Spec turns product ideas, PRDs, prototypes, role paths, and
acceptance gates into build-ready specs for AI-era product teams.

Open-source: https://github.com/franklinxkk/ai-delivery-spec
