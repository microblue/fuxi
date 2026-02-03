#!/usr/bin/env python3
"""
Batch I2V (Image-to-Video) generation for all shots in an episode.

Orchestrates generate_shot_video.py for multiple shots, reading prompts from shots.json.

Usage:
    python -m pipeline.generate_episode_videos ep001
    python -m pipeline.generate_episode_videos ep001 S03 S04 S05
    python -m pipeline.generate_episode_videos ep001 --frames 121 --quality high
"""

import argparse
import sys
from pathlib import Path

from pipeline.generate_shot_video import generate_shot_video
from pipeline.utils import get_episode_dir, load_shots


def generate_episode_videos(
    episode_id: str,
    shot_ids: list[str] | None = None,
    frames: int = 121,
    seed1: int = 42,
    seed2: int = 420,
) -> dict[str, Path]:
    """Generate I2V videos for shots in an episode.

    Args:
        episode_id: Episode ID (e.g., "ep001")
        shot_ids: Specific shots to generate. If None, generate all.
        frames: Number of frames per video
        seed1: Stage 1 seed
        seed2: Stage 2 seed

    Returns:
        Dict mapping shot_id → output video path
    """
    ep_dir = get_episode_dir(episode_id)
    shots_data = load_shots(episode_id)

    # Filter shots
    all_shots = shots_data["shots"]
    if shot_ids:
        shots_to_gen = [s for s in all_shots if s["shot_id"] in shot_ids]
    else:
        shots_to_gen = all_shots

    print(f"\n{'=' * 60}")
    print(f"I2V Generation — {episode_id}")
    print(f"  Shots: {len(shots_to_gen)}/{len(all_shots)}")
    print(f"  Frames: {frames} @ 25fps = {frames / 25:.1f}s")
    print(f"{'=' * 60}\n")

    results: dict[str, Path] = {}
    failed: list[str] = []

    for i, shot in enumerate(shots_to_gen, 1):
        shot_id = shot["shot_id"]
        print(f"[{i}/{len(shots_to_gen)}] {shot_id}")

        try:
            # Try to load input image from shot data or assets
            input_image = shot.get("input_image")
            if not input_image:
                # Try common naming patterns
                for pattern in [
                    f"assets/characters/{shot.get('character_id', 'unknown')}_ref.png",
                    f"assets/locations/{shot.get('location', 'unknown')}_ref.png",
                    f"video/{shot_id}_gen_001.png",  # From T2I generation
                ]:
                    candidate = ep_dir / pattern
                    if candidate.exists():
                        input_image = str(candidate.relative_to(ep_dir))
                        break

            if not input_image:
                print(f"  ⚠ No input image found, skipping {shot_id}")
                failed.append(shot_id)
                continue

            # Generate video
            output_path = generate_shot_video(
                episode_id,
                shot_id,
                video_prompt=shot.get("prompt_motion"),
                input_image=input_image,
                frames=frames,
                seed1=seed1,
                seed2=seed2,
            )
            results[shot_id] = output_path
        except Exception as e:
            print(f"  ✗ Generation failed: {e}")
            failed.append(shot_id)
            continue

    # Summary
    print(f"\n{'=' * 60}")
    print(f"✅ Generation complete")
    print(f"   Generated: {len(results)}")
    if failed:
        print(f"   Failed: {len(failed)} ({', '.join(failed)})")
    print(f"{'=' * 60}\n")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate I2V videos for all shots in an episode"
    )
    parser.add_argument("episode_id", help="Episode ID (e.g., ep001)")
    parser.add_argument(
        "shot_ids",
        nargs="*",
        help="Specific shot IDs to generate (e.g., S01 S02). If not specified, generate all.",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=121,
        help="Number of frames per video (default: 121, ~4.8s @ 25fps)",
    )
    parser.add_argument(
        "--seed1",
        type=int,
        default=42,
        help="Stage 1 seed (default: 42)",
    )
    parser.add_argument(
        "--seed2",
        type=int,
        default=420,
        help="Stage 2 seed (default: 420)",
    )

    args = parser.parse_args()

    try:
        generate_episode_videos(
            episode_id=args.episode_id,
            shot_ids=args.shot_ids if args.shot_ids else None,
            frames=args.frames,
            seed1=args.seed1,
            seed2=args.seed2,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
