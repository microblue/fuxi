#!/usr/bin/env python3
"""Generate videos for Fuxi EP001 using creative-toolkit.

Queues all shots to ComfyUI at once, then monitors completion.
Uses creative_toolkit.comfyui for workflow building and queue management.
"""

import os
import random
import shutil
import sys
import time
from pathlib import Path

# Add creative-toolkit to path
sys.path.insert(0, "/home/dz/creative-toolkit")

from creative_toolkit.comfyui import ComfyUIClient, ComfyUIError, build_ltx2_i2v_workflow

# ── Config ──────────────────────────────────────────────────────────────
VIDEO_DIR = Path("/home/dz/fuxi/episodes/ep001/video")
OUTPUT_DIR = Path("/home/dz/ComfyUI/output")

# Fuxi is 9:16 vertical short drama
WIDTH = 512
HEIGHT = 896
LENGTH = 49  # ~2 seconds at 24fps (8*6+1)
FPS = 24
STEPS = 25
CFG = 3.0
STRENGTH = 0.85

# Shot descriptions for video motion prompts
SHOT_PROMPTS = {
    "S03": "A woman with flowing light robes smiles serenely, her expression calm and decisive, golden data patterns shimmer around her, subtle head movement, cinematic lighting, sci-fi mythology style",
    "S04": "A woman presses both hands on a control console, golden data streams being extracted from her body upward, a massive pillar of light rises from the city center splitting into countless light particles scattering into the cosmos, epic scale, camera slowly zooms out",
    "S05": "A woman's body gradually becomes transparent and dissolves into golden light particles, she smiles peacefully as she fades away, emotional cinematic moment, soft golden glow",
    "S06": "Stormy night in a primordial swamp, heavy rain, lightning flashes illuminate a young man (16yo) and hunters tracking through mud and water, dark atmospheric, camera pans slowly",
    "S07": "The sky tears open with silver-blue geometric light streams crashing down into the swamp center, not lightning but structured data-like energy, dramatic upward camera angle, the young man clutches his left eye in pain",
    "S08": "Silver-blue light dissolves into a glowing vortex in swamp water, a translucent crystal floats at the center, a young man cautiously approaches, eerie glow, slow movement",
    "S09": "A young man reaches out and touches a crystal, golden data streams surge up his arm, he collapses to his knees in pain, his left eye erupts with intense golden light, dramatic energy burst",
    "S10": "Extreme close-up of an eye transforming - pupil turns dark gold with a tiny rotating bagua/octagram pattern deep within, code-like green text overlays the surrounding forest view, digital augmented reality vision",
    "S11": "A young man stares at his own hands in shock, looking around at a world now overlaid with digital code patterns, trees show green growth algorithms, water shows molecular grids, bewildered expression",
    "S12": "The sky darkens dramatically and suddenly, ominous atmosphere, environmental wide shot of swamp landscape plunging into darkness",
    "S13": "Three pale geometric octahedrons silently descend from the dark sky, menacing and alien, low angle looking up, threatening sci-fi atmosphere",
    "S14": "Black data streams attack a hunter, his body begins to pixelate and dissolve, horror element, dark energy tendrils wrapping around victim",
    "S15": "A young man roars and extends his hand, in his code-vision he sees the jagged structure of black data streams and instinctively grabs and tears them apart, dynamic action shot, energy burst",
    "S16": "More data tentacles extend outward, the young man manipulates ground code turning mud into quicksand to trap the geometric entities briefly, wide shot showing the battle, dynamic camera",
    "S17": "From a distant cliff, a bone arrow wrapped in green light streaks through the air, a young woman (17yo) appears shouting from the cliff edge, the young man stumbles away, dynamic action wide shot",
    "S18": "Three geometric octahedrons converge and merge, emitting a final transmission pulse, ominous wide shot",
    "S19": "A young man looks back in the rain, his left eye glowing faintly gold in the darkness, expression of fear confusion and survival, emotional medium shot, rain atmosphere",
}


def get_existing_videos() -> set[str]:
    """Check which shots already have generated videos (>100KB = real)."""
    existing = set()
    for f in OUTPUT_DIR.iterdir():
        if f.name.startswith("fuxi_ep001_") and "_vid" in f.name and f.suffix == ".mp4":
            parts = f.name.split("_")
            if len(parts) >= 3:
                sid = parts[2]
                if f.stat().st_size > 100_000:
                    existing.add(sid)
    return existing


def main():
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    client = ComfyUIClient()

    if not client.health_check():
        print("ERROR: ComfyUI is not reachable!")
        sys.exit(1)
    print("✓ ComfyUI is online")

    existing = get_existing_videos()
    print(f"Already done ({len(existing)}): {sorted(existing)}")

    shots = sorted(SHOT_PROMPTS.keys(), key=lambda x: int(x[1:]))

    # ── Phase 1: Upload images & queue all workflows ───────────────────
    queued: list[tuple[str, str]] = []  # (shot_id, prompt_id)
    skipped = []

    for sid in shots:
        if sid in existing:
            skipped.append(sid)
            continue

        final_img = VIDEO_DIR / f"{sid}_final.png"
        if not final_img.exists():
            print(f"[{sid}] No final image, skipping")
            skipped.append(sid)
            continue

        prompt = SHOT_PROMPTS[sid]
        seed = random.randint(1, 2**31)
        prefix = f"fuxi_ep001_{sid}_vid"

        print(f"[{sid}] Uploading image...")
        upload_result = client.upload_image(final_img)
        image_name = upload_result.get("name", final_img.name)

        workflow = build_ltx2_i2v_workflow(
            image_name=image_name,
            prompt=prompt,
            seed=seed,
            filename_prefix=prefix,
            width=WIDTH,
            height=HEIGHT,
            length=LENGTH,
            steps=STEPS,
            cfg=CFG,
            strength=STRENGTH,
            fps=FPS,
        )

        try:
            prompt_id = client.queue_prompt(workflow)
            queued.append((sid, prompt_id))
            print(f"[{sid}] ✓ Queued (prompt_id: {prompt_id[:8]}..., seed={seed})")
        except ComfyUIError as e:
            print(f"[{sid}] ✗ Failed to queue: {e}")

    if skipped:
        print(f"\nSkipped {len(skipped)}: {sorted(skipped)}")

    if not queued:
        print("\nNothing to generate!")
        return

    print(f"\n{'='*60}")
    print(f"Queued {len(queued)} videos. Waiting for completion...")
    print(f"{'='*60}\n")

    # ── Phase 2: Monitor completion ────────────────────────────────────
    completed = 0
    failed = 0
    total = len(queued)

    for sid, prompt_id in queued:
        print(f"[{sid}] Waiting... ({completed + failed + 1}/{total})")
        try:
            history = client.wait_for_completion(prompt_id)

            outputs = history.get("outputs", {})
            video_found = False
            for _node_id, node_out in outputs.items():
                for g in node_out.get("gifs", []):
                    fname = g.get("filename", "")
                    if fname.endswith(".mp4"):
                        src = OUTPUT_DIR / fname
                        dst = VIDEO_DIR / f"{sid}_video.mp4"
                        if src.exists():
                            shutil.copy2(src, dst)
                            size_mb = src.stat().st_size / (1024 * 1024)
                            print(f"[{sid}] ✓ Done! {fname} ({size_mb:.1f}MB) → {dst.name}")
                            video_found = True

            if video_found:
                completed += 1
            else:
                print(f"[{sid}] ⚠ Completed but no video file found")
                failed += 1

        except ComfyUIError as e:
            print(f"[{sid}] ✗ Failed: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Video generation complete!")
    print(f"  ✓ Completed: {completed}/{total}")
    if failed:
        print(f"  ✗ Failed: {failed}/{total}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
