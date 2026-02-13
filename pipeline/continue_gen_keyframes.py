#!/usr/bin/env python3
"""继续生成ep001剩余镜头的关键帧（跳过已完成的）。"""

import json
import sys
from pathlib import Path
from pipeline.utils import get_episode_dir, load_shots
from pipeline.gen_keyframe_images import generate_shot_keyframes


def continue_generate_keyframes(episode_id: str, start_shot: str = "S02", skip_errors: bool = True) -> dict:
    """继续为episode生成剩余镜头的关键帧。

    Args:
        episode_id: 剧集编号
        start_shot: 开始的shot_id（跳过之前完成的）
        skip_errors: 出错时是否继续处理下一个shot

    Returns:
        生成统计信息
    """
    ep_dir = get_episode_dir(episode_id)
    shots_data = load_shots(episode_id)

    # 找到开始索引
    all_shot_ids = [shot["shot_id"] for shot in shots_data["shots"]]
    try:
        start_idx = all_shot_ids.index(start_shot)
    except ValueError:
        print(f"❌ 错误: shot_id '{start_shot}' 未找到")
        return {"error": f"shot_id {start_shot} not found"}

    shots_to_process = shots_data["shots"][start_idx:]
    total_shots = len(shots_to_process)
    generated = 0
    skipped = 0
    failed = 0
    errors = []

    keyframe_dir = ep_dir / "video" / "keyframes"

    print(f"\n{'=' * 70}")
    print(f"继续生成关键帧 — {episode_id}")
    print(f"开始位置: {start_shot}")
    print(f"待处理镜头数: {total_shots}")
    print(f"{'=' * 70}\n")

    for i, shot in enumerate(shots_to_process, 1):
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
            output_path = keyframe_dir / f"{kf['keyframe_id']}_seed0000.png"
            if not output_path.exists():
                all_exist = False
                break

        if all_exist and shot_keyframes:
            print(f"[{i:2d}/{total_shots}] ⏭️  {shot_id} - 已生成（跳过）")
            skipped += 1
            continue

        # 生成该shot的关键帧
        try:
            print(f"[{i:2d}/{total_shots}] 🎬 {shot_id} - 生成中...", flush=True)
            results = generate_shot_keyframes(
                episode_id=episode_id,
                shot_id=shot_id,
                num_candidates=1,
                base_seed=0,
            )

            if results:
                print(f"      ✅ {len(results)} 帧\n", flush=True)
                generated += 1
            else:
                print(f"      ⚠️  无输出\n", flush=True)
                skipped += 1

        except KeyboardInterrupt:
            print(f"\n\n⚠️ 用户中断")
            break
        except Exception as e:
            error_msg = str(e)[:100]
            print(f"      ❌ 错误: {error_msg}\n", flush=True)
            failed += 1
            errors.append({
                "shot_id": shot_id,
                "error": error_msg
            })
            if not skip_errors:
                raise

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
        print()

    # 最终统计所有已生成的关键帧
    all_keyframes = list(keyframe_dir.glob("*.png"))
    print(f"总关键帧文件数: {len(all_keyframes)}")

    return {
        "total_shots": total_shots,
        "generated": generated,
        "skipped": skipped,
        "failed": failed,
        "errors": errors
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="继续生成episode的关键帧")
    parser.add_argument("episode_id", help="剧集编号, e.g. ep001")
    parser.add_argument("--start", default="S02", help="开始的shot_id (default: S02)")
    parser.add_argument("--no-skip-errors", action="store_true", help="出错时停止")

    args = parser.parse_args()

    try:
        continue_generate_keyframes(
            episode_id=args.episode_id,
            start_shot=args.start,
            skip_errors=not args.no_skip_errors
        )
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
