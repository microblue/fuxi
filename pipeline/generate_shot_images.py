#!/usr/bin/env python3
"""
Generate T2I (Text-to-Image) candidate images for shots using Flux.

Reads prompts from shots.json's `prompt_visual` field or from prompt files.
Uses creative_toolkit's ComfyUIImageGen to generate multiple candidates per shot.

Usage:
    python -m pipeline.generate_shot_images ep001
    python -m pipeline.generate_shot_images ep001 S03 S04
    python -m pipeline.generate_shot_images ep001 --num-candidates 5
"""

import argparse
import random
import sys
from pathlib import Path

from creative_toolkit.image import ComfyUIImageGen

from pipeline.utils import (
    ensure_episode_dirs,
    get_episode_dir,
    load_shots,
    parse_prompt_file,
)

# Target resolution for T2I: 16:9 horizontal
IMG_SIZE = "1344x768"
NUM_CANDIDATES_DEFAULT = 3


def generate_shot_images(
    episode_id: str,
    shot_ids: list[str] | None = None,
    num_candidates: int = NUM_CANDIDATES_DEFAULT,
    quality: str = "high",
) -> dict[str, list[Path]]:
    """Generate T2I candidate images for shots.

    Args:
        episode_id: Episode ID (e.g., "ep001")
        shot_ids: Specific shots to generate. If None, generate all.
        num_candidates: Number of candidate images per shot
        quality: Generation quality ("low", "medium", "high")

    Returns:
        Dict mapping shot_id → list of generated image paths
    """
    ep_dir = ensure_episode_dirs(episode_id)
    shots_data = load_shots(episode_id)

    # Filter shots
    all_shots = shots_data["shots"]
    if shot_ids:
        shots_to_gen = [s for s in all_shots if s["shot_id"] in shot_ids]
    else:
        shots_to_gen = all_shots

    print(f"\n{'=' * 60}")
    print(f"T2I Generation — {episode_id}")
    print(f"  Shots: {len(shots_to_gen)}/{len(all_shots)}")
    print(f"  Candidates per shot: {num_candidates}")
    print(f"  Quality: {quality}")
    print(f"  Size: {IMG_SIZE}")
    print(f"{'=' * 60}\n")

    gen = ComfyUIImageGen()
    results: dict[str, list[Path]] = {}

    for shot in shots_to_gen:
        shot_id = shot["shot_id"]
        print(f"[{shot_id}]")

        # Extract prompt
        positive_prompt = shot.get("prompt_visual", "")

        # If prompt_visual is empty, try to load from prompt file
        if not positive_prompt:
            prompt_file = ep_dir / "prompts" / f"{shot_id}.txt"
            if prompt_file.exists():
                positive_prompt, _ = parse_prompt_file(prompt_file)
                print(f"  Loaded prompt from {prompt_file.name}")
            else:
                print(f"  ⚠ No prompt found for {shot_id}, skipping")
                continue

        if not positive_prompt:
            print(f"  ⚠ Empty prompt for {shot_id}, skipping")
            continue

        # Truncate prompt display
        prompt_display = (
            (positive_prompt[:70] + "…")
            if len(positive_prompt) > 70
            else positive_prompt
        )
        print(f"  Prompt: {prompt_display}")

        gen_paths = []
        output_dir = ep_dir / "video"
        output_dir.mkdir(parents=True, exist_ok=True)

        for i in range(num_candidates):
            seed = random.randint(0, 2**31 - 1)
            output_name = f"{shot_id}_gen_{i + 1:03d}_seed{seed}.png"
            output_path = output_dir / output_name

            try:
                print(f"    Generating candidate {i + 1}/{num_candidates}  seed={seed}")
                gen.generate(
                    prompt=positive_prompt,
                    output_path=output_path,
                    negative_prompt="",  # Flux2 doesn't need negative
                    size=IMG_SIZE,
                    quality=quality,
                )
                gen_paths.append(output_path)
                print(f"    ✓ {output_name}")
            except Exception as e:
                print(f"    ✗ Generation failed: {e}")
                continue

        if gen_paths:
            results[shot_id] = gen_paths
            print(f"  Generated {len(gen_paths)}/{num_candidates} candidates")
        else:
            print(f"  ⚠ No candidates generated for {shot_id}")
        print()

    # Summary
    total_generated = sum(len(paths) for paths in results.values())
    print(f"{'=' * 60}")
    print(f"✅ Generation complete")
    print(f"   Total: {total_generated} images from {len(results)} shots")
    print(f"{'=' * 60}\n")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate T2I candidate images for episode shots"
    )
    parser.add_argument("episode_id", help="Episode ID (e.g., ep001)")
    parser.add_argument(
        "shot_ids",
        nargs="*",
        help="Specific shot IDs to generate (e.g., S01 S02). If not specified, generate all.",
    )
    parser.add_argument(
        "--num-candidates",
        type=int,
        default=NUM_CANDIDATES_DEFAULT,
        help=f"Number of candidates per shot (default: {NUM_CANDIDATES_DEFAULT})",
    )
    parser.add_argument(
        "--quality",
        choices=["low", "medium", "high"],
        default="high",
        help="Generation quality (default: high)",
    )

    args = parser.parse_args()

    try:
        generate_shot_images(
            episode_id=args.episode_id,
            shot_ids=args.shot_ids if args.shot_ids else None,
            num_candidates=args.num_candidates,
            quality=args.quality,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
