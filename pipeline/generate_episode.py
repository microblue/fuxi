#!/usr/bin/env python3
"""
伏羲纪元 — 剧集完整流程编排器

协调整个剧集生产流程：
  1. 生成分镜占位视频 (gen_placeholder_video)
  2. 合成音频和效果音 (synth_voice + manage_sfx)
  3. 生成字幕 (build_subtitles)
  4. 生成镜头图像候选 (gen_shot_images)
  5. 生成最终视频 (render_video)

使用：
  # 运行完整流程
  pixi run python -m pipeline.generate_episode ep001

  # 运行特定阶段
  pixi run python -m pipeline.generate_episode ep001 --stage placeholder
  pixi run python -m pipeline.generate_episode ep001 --stage images
  pixi run python -m pipeline.generate_episode ep001 --stage audio
  pixi run python -m pipeline.generate_episode ep001 --stage subtitles
  pixi run python -m pipeline.generate_episode ep001 --stage render

  # 从特定阶段开始（跳过之前的阶段）
  pixi run python -m pipeline.generate_episode ep001 --from-stage images
"""

import argparse
import sys
import subprocess
from pathlib import Path
from enum import Enum

from pipeline.utils import ensure_episode_dirs, get_episode_dir, load_shots


class Stage(Enum):
    """流程阶段定义"""
    PLACEHOLDER = "placeholder"
    AUDIO = "audio"
    SUBTITLES = "subtitles"
    IMAGES = "images"
    RENDER = "render"

    @staticmethod
    def all_stages():
        """返回所有阶段（按顺序）"""
        return [
            Stage.PLACEHOLDER,
            Stage.AUDIO,
            Stage.SUBTITLES,
            Stage.IMAGES,
            Stage.RENDER,
        ]

    @staticmethod
    def stage_index(stage):
        """获取阶段的索引"""
        stages = Stage.all_stages()
        return stages.index(stage)


def run_stage(stage: Stage, episode_id: str, args: argparse.Namespace) -> bool:
    """运行指定的流程阶段"""
    print(f"\n{'=' * 70}")
    print(f"阶段: {stage.value.upper()}")
    print(f"{'=' * 70}\n")

    try:
        if stage == Stage.PLACEHOLDER:
            # 生成占位视频
            cmd = [
                "pixi", "run", "python", "-m",
                "pipeline.gen_placeholder_video", episode_id
            ]
            result = subprocess.run(cmd, check=False)
            return result.returncode == 0

        elif stage == Stage.AUDIO:
            # 合成语音和效果音
            # synth_voice.py
            cmd = [
                "pixi", "run", "python", "-m",
                "pipeline.synth_voice", episode_id
            ]
            result = subprocess.run(cmd, check=False)
            if result.returncode != 0:
                return False

            # manage_sfx.py (可选)
            print("✓ 音频合成完成")
            return True

        elif stage == Stage.SUBTITLES:
            # 生成字幕
            cmd = [
                "pixi", "run", "python", "-m",
                "pipeline.build_subtitles", episode_id
            ]
            result = subprocess.run(cmd, check=False)
            return result.returncode == 0

        elif stage == Stage.IMAGES:
            # 生成T2I候选图像
            cmd = [
                "pixi", "run", "python", "-m",
                "pipeline.gen_shot_images", episode_id,
                "--num-candidates", str(args.num_candidates),
                "--quality", args.image_quality,
            ]
            result = subprocess.run(cmd, check=False)
            return result.returncode == 0

        elif stage == Stage.RENDER:
            # 最终视频合成
            cmd = [
                "pixi", "run", "python", "-m",
                "pipeline.render_video", episode_id
            ]
            result = subprocess.run(cmd, check=False)
            return result.returncode == 0

    except Exception as e:
        print(f"❌ 阶段执行失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="剧集完整流程编排器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
流程阶段（按顺序）:
  1. placeholder - 生成分镜占位视频
  2. audio       - 合成语音和效果音
  3. subtitles   - 生成字幕
  4. images      - 生成镜头T2I候选图像
  5. render      - 最终视频合成

示例:
  # 运行完整流程
  pixi run python -m pipeline.generate_episode ep001

  # 仅生成占位视频
  pixi run python -m pipeline.generate_episode ep001 --stage placeholder

  # 从images阶段开始（跳过之前的）
  pixi run python -m pipeline.generate_episode ep001 --from-stage images

  # 自定义参数
  pixi run python -m pipeline.generate_episode ep001 --num-candidates 5 --image-quality high
        """,
    )

    parser.add_argument("episode_id", help="剧集ID (e.g., ep001)")
    parser.add_argument(
        "--stage",
        type=str,
        choices=[s.value for s in Stage.all_stages()],
        help="运行单个阶段",
    )
    parser.add_argument(
        "--from-stage",
        type=str,
        choices=[s.value for s in Stage.all_stages()],
        help="从指定阶段开始（包括该阶段及之后的所有阶段）",
    )
    parser.add_argument(
        "--num-candidates",
        type=int,
        default=3,
        help="T2I生成的候选图像数 (默认: 3)",
    )
    parser.add_argument(
        "--image-quality",
        choices=["low", "medium", "high"],
        default="high",
        help="T2I生成质量 (默认: high)",
    )

    args = parser.parse_args()

    episode_id = args.episode_id
    ep_dir = get_episode_dir(episode_id)
    ensure_episode_dirs(episode_id)

    print(f"\n{'=' * 70}")
    print(f"伏羲纪元 — 剧集编排流程")
    print(f"剧集: {episode_id}")
    print(f"{'=' * 70}")

    # 检查 shots.json
    try:
        shots_data = load_shots(episode_id)
    except FileNotFoundError:
        print(f"\n❌ 错误: 找不到 {episode_id}/shots.json")
        print("   请先运行: pixi run python -m pipeline.gen_shots {episode_id}")
        sys.exit(1)

    shots = shots_data["shots"]
    print(f"\n✓ 加载 {len(shots)} 个镜头")

    # 确定要运行的阶段
    all_stages = Stage.all_stages()

    if args.stage:
        # 运行单个阶段
        stages_to_run = [Stage(args.stage)]
    elif args.from_stage:
        # 从某个阶段开始
        start_idx = Stage.stage_index(Stage(args.from_stage))
        stages_to_run = all_stages[start_idx:]
    else:
        # 运行所有阶段
        stages_to_run = all_stages

    print(f"\n计划运行阶段: {', '.join(s.value for s in stages_to_run)}\n")

    # 执行每个阶段
    success_count = 0
    for stage in stages_to_run:
        success = run_stage(stage, episode_id, args)
        if success:
            success_count += 1
            print(f"✓ {stage.value}: 完成")
        else:
            print(f"✗ {stage.value}: 失败")
            # 继续执行，即使某个阶段失败
            # 取消注释以在失败时停止:
            # sys.exit(1)

    print(f"\n{'=' * 70}")
    print(f"✓ 完成: {success_count}/{len(stages_to_run)} 个阶段")
    print(f"{'=' * 70}\n")

    if success_count < len(stages_to_run):
        sys.exit(1)


if __name__ == "__main__":
    main()
