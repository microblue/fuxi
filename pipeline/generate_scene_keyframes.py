#!/usr/bin/env python3
"""
场景级关键帧生成 — T2I生成指定场景的所有T2I关键帧

用法:
    python -m pipeline.generate_scene_keyframes ep001 1-1
    python -m pipeline.generate_scene_keyframes ep001 1-2 --output-dir custom_path
"""

import json
from pathlib import Path
from pipeline.utils import get_episode_dir, load_shots
from pipeline.comfyui_api import generate_image


def get_scene_shots(episode_id: str, scene_id: str) -> list[dict]:
    """获取指定场景的所有镜头。"""
    shots_data = load_shots(episode_id)

    scene_shots = []
    for scene in shots_data.get("scenes", []):
        if scene["id"] == scene_id:
            shot_ids = scene["shots"]
            for shot in shots_data["shots"]:
                if shot["shot_id"] in shot_ids:
                    scene_shots.append(shot)
            break

    return scene_shots


def load_keyframes(episode_id: str) -> dict:
    """加载关键帧配置。"""
    ep_dir = get_episode_dir(episode_id)
    keyframes_path = ep_dir / "keyframes.json"
    if not keyframes_path.exists():
        raise FileNotFoundError(f"Missing keyframes.json: {keyframes_path}")

    with open(keyframes_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_t2i_keyframes_for_scene(episode_id: str, scene_id: str) -> list[dict]:
    """获取指定场景的所有T2I关键帧。"""
    scene_shots = get_scene_shots(episode_id, scene_id)
    shot_ids = {shot["shot_id"] for shot in scene_shots}

    keyframes_data = load_keyframes(episode_id)
    t2i_frames = [
        kf for kf in keyframes_data["keyframes"]
        if kf["type"] == "t2i" and kf["shot_id"] in shot_ids
    ]

    return sorted(t2i_frames, key=lambda x: (x["shot_id"], x["frame_index"]))


def generate_scene_keyframes(
    episode_id: str,
    scene_id: str,
    num_candidates: int = 1,
    base_seed: int = 0,
) -> dict:
    """生成场景的T2I关键帧。

    返回: {keyframe_id: Path, ...}
    """
    ep_dir = get_episode_dir(episode_id)

    print(f"\n{'=' * 60}")
    print(f"场景关键帧生成 — {episode_id} Scene {scene_id}")
    print(f"{'=' * 60}\n")

    t2i_frames = get_t2i_keyframes_for_scene(episode_id, scene_id)

    if not t2i_frames:
        print(f"❌ 场景 {scene_id} 未找到T2I关键帧")
        return {}

    print(f"📍 Found {len(t2i_frames)} T2I keyframes for scene {scene_id}")
    print()

    results = {}

    for i, kf in enumerate(t2i_frames, 1):
        keyframe_id = kf["keyframe_id"]
        shot_id = kf["shot_id"]
        prompt = kf["prompt"]

        print(f"[{i}/{len(t2i_frames)}] {keyframe_id}")
        print(f"   Shot: {shot_id}")
        print(f"   Prompt: {prompt[:80]}...")

        try:
            for cand_idx in range(num_candidates):
                seed = base_seed + (i - 1) * 1000 + cand_idx * 100

                # 输出路径
                keyframe_dir = ep_dir / "video" / "keyframes"
                keyframe_dir.mkdir(parents=True, exist_ok=True)

                output_path = keyframe_dir / f"{keyframe_id}_seed{seed:04d}.png"

                print(f"   → Candidate {cand_idx + 1}/{ num_candidates} (seed={seed})")

                # 调用T2I生成
                try:
                    output_path = generate_image(
                        positive_prompt=prompt,
                        dest_path=output_path,
                        seed=seed,
                        width=1344,
                        height=768,
                        steps=20,
                    )
                    print(f"     ✅ {output_path.name}")
                    results[f"{keyframe_id}_c{cand_idx+1}"] = output_path
                except Exception as e:
                    print(f"     ⚠️ Failed: {e}")

        except Exception as e:
            print(f"   ❌ Error: {e}\n")
            continue

    print(f"\n{'=' * 60}")
    print(f"✅ 生成完成")
    print(f"   总数: {len(results)}")
    print(f"{'=' * 60}\n")

    return results


def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="生成场景的T2I关键帧"
    )
    parser.add_argument("episode_id", help="剧集编号, e.g. ep001")
    parser.add_argument("scene_id", help="场景编号, e.g. 1-1")
    parser.add_argument(
        "--num-candidates",
        type=int,
        default=1,
        help="每个关键帧的候选数 (default: 1)"
    )
    parser.add_argument(
        "--base-seed",
        type=int,
        default=0,
        help="基础seed (default: 0)"
    )

    args = parser.parse_args()

    try:
        generate_scene_keyframes(
            episode_id=args.episode_id,
            scene_id=args.scene_id,
            num_candidates=args.num_candidates,
            base_seed=args.base_seed,
        )
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
