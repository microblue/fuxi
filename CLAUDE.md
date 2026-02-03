# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI短剧创作项目（AI Short Drama Production System） — an automated pipeline for producing publish-ready horizontal short dramas (网络剧/电视台). The system covers the full workflow: topic selection → script → storyboard → asset creation → prompt engineering → audio/subtitles → video rendering.

Reference material: `《伏羲纪元》1-30集完整分集剧本.pdf` in project root.

## Build & Dev Commands (Pixi)

```bash
pixi run dev        # uvicorn app.main:app --reload
pixi run test       # pytest
pixi run lint       # ruff check .
pixi run format     # ruff format .
```

## Target Directory Structure

```
fuxi/
├─ style_bible/           # Reusable creative assets
│  ├─ world.md            # World-building rules
│  ├─ tone.md             # Tone & style guide
│  ├─ camera_language.md  # Shot/camera conventions
│  ├─ character_templates.md
│  └─ prompt_templates.md # Modular prompt structure
├─ pipeline/              # Automation scripts (Python)
│  ├─ generate_episode.py # Orchestrator: runs full pipeline
│  ├─ synth_voice.py      # TTS per shot/dialogue block
│  ├─ build_subtitles.py  # Subtitle generation & alignment
│  ├─ render_video.py     # Final composition → mp4
│  └─ utils.py
└─ episodes/
   └─ epNNN/
      ├─ script.md        # Full screenplay
      ├─ shots.json       # Storyboard (structured shot list)
      ├─ prompts/         # Generated image/video prompts
      ├─ assets/          # characters/, locations/, props/
      ├─ audio/
      ├─ video/
      └─ report.md        # Quality self-check
```

## Complete Workflow Architecture

**See [WORKFLOW.md](WORKFLOW.md) for comprehensive pipeline documentation:**
- Complete data flow from script → script.md → shots.json → prompts → T2I (Flux) → keyframes → I2V (LTX-2) → video composition → final.mp4
- Configuration schemas and parameter tuning
- Execution commands and workflow orchestration
- Quality checkpoints and troubleshooting

## Production Pipeline (Phases A–G, sequential)

A. **Topic selection** — generate ≥10 candidates, pick strongest conflict/twist
B. **Script** (`script.md`) — characters, scenes, dialogue, emotion arc; dialogue must be colloquial and concise
C. **Storyboard** (`shots.json`) — each shot: `shot_id, duration_s, location, characters, camera, action, dialogue, emotion, prompt_visual, prompt_motion, sfx_bgm, notes`
D. **Asset cards** — character cards (appearance, outfit, trait keywords, unique identifier) and location cards (space, lighting, palette, compatible shots)
E. **Prompt engineering** — modular structure: `[STYLE][CHARACTER][LOCATION][ACTION][CAMERA][LIGHTING][MOOD]`; negative prompts always include: anatomy error, face distortion, extra limbs, watermark, text artifacts, oversharpen, uncanny look
F. **Audio & subtitles** — audio split per shot; subtitles ≤16 Chinese chars/line, time-aligned
G. **Render & output** — sequential shot assembly → `final.mp4`; rhythm over effects

## Default Specs (no need to ask)

- Format: 1920×1080 horizontal, 24/30fps
- Duration: ~60s per episode, 8–12 shots
- Cast: 2–3 characters, 1–2 locations
- Default genre: 都市现实主义 · 轻悬疑/爽点反转 · 双主角

## Key Constraints

- Pipeline scripts must be runnable end-to-end (`generate_episode.py` → `final.mp4`), placeholder assets are acceptable
- Every episode requires `report.md` answering: hook within 3s? characters memorable? emotion arc clear? shots serve narrative? which assets are reusable?
- All characters/scenes/styles must be asset-ized for cross-episode reuse
- Hook in first 3 seconds; information change every 10–15 seconds; memorable ending required
