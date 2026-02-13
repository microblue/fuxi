#!/usr/bin/env python3
"""批量生成所有镜头的关键帧。"""

import json
import sys
from pathlib import Path
from pipeline.utils import get_episode_dir, load_shots
from pipeline.gen_keyframe_images import generate_shot_keyframes


def batch_generate_keyframes(episode_id: str) -> dict:
    """为整个episode生成所有镜头的关键帧。

    Returns:
        {
            "total_shots": int,
            "generated": int,
            "skipped": int,
            "failed": int,
            "errors": [...]
        }
    """
    ep_dir = get_episode_dir(episode_id)
    shots_data = load_shots(episode_id)

    total_shots = len(shots_data["shots"])
    generated = 0
    skipped = 0
    failed = 0
    errors = []

    keyframe_dir = ep_dir / "video" / "keyframes"
    keyframe_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 70}")
    print(f"批量关键帧生成 — {episode_id}")
    print(f"总镜头数: {total_shots}")
    print(f"{'=' * 70}\n")

    for i, shot in enumerate(shots_data["shots"], 1):
        shot_id = shot["shot_id"]

        # 检查该shot的关键帧是否已全部生成
        keyframes_path = ep_dir / "keyframes.json"
        with open(keyframes_path, "r", encoding="utf-8") as f:
            keyframes_data = json.load(f)

        shot_keyframes = [
            kf for kf in keyframes_data["keyframes"]
            if kf["shot_id"] == shot_id
        ]

        # 检查是否所有关键帧都已生成
        all_exist = True
        for kf in shot_keyframes:
            # 支持新旧两种文件名格式：S01-KF1.png 或 S01-KF1_seed*.png
            kf_id = kf['keyframe_id']
            matching = list(keyframe_dir.glob(f"{kf_id}.png")) + list(keyframe_dir.glob(f"{kf_id}_*.png"))
            if not matching:
                all_exist = False
                break

        if all_exist and shot_keyframes:
            print(f"[{i:2d}/{total_shots}] ⏭️  {shot_id} - 已生成（跳过）")
            skipped += 1
            continue

        # 生成该shot的关键帧
        try:
            print(f"[{i:2d}/{total_shots}] 🎬 {shot_id} - 生成中...", end=" ", flush=True)
            results = generate_shot_keyframes(
                episode_id=episode_id,
                shot_id=shot_id,
                num_candidates=1,
                base_seed=0,
            )

            if results:
                print(f"✅ {len(results)} 帧")
                generated += 1
            else:
                print(f"⚠️  无输出")
                skipped += 1

        except Exception as e:
            print(f"❌ 错误: {str(e)[:50]}")
            failed += 1
            errors.append({
                "shot_id": shot_id,
                "error": str(e)
            })

    print(f"\n{'=' * 70}")
    print(f"生成完成")
    print(f"  总镜头数: {total_shots}")
    print(f"  成功生成: {generated}")
    print(f"  已跳过: {skipped}")
    print(f"  失败: {failed}")
    print(f"{'=' * 70}\n")

    if errors:
        print("❌ 失败的镜头:")
        for err in errors:
            print(f"  - {err['shot_id']}: {err['error']}")

    return {
        "total_shots": total_shots,
        "generated": generated,
        "skipped": skipped,
        "failed": failed,
        "errors": errors
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="批量生成episode的所有关键帧")
    parser.add_argument("episode_id", help="剧集编号, e.g. ep001")

    args = parser.parse_args()

    try:
        batch_generate_keyframes(args.episode_id)
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
