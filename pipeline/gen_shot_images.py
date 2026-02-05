#!/usr/bin/env python3
"""
伏羲纪元 — 镜头图像生成（T2I - Text to Image）

从 shots.json 中的 prompt_visual 生成高质量T2I候选图像
使用 creative_toolkit 的 ComfyUIImageGen（Flux模型）

使用：
  # 生成整集的所有镜头图像
  pixi run python -m pipeline.gen_shot_images ep001

  # 生成特定镜头的图像
  pixi run python -m pipeline.gen_shot_images ep001 S01 S02 S03

  # 自定义候选数量
  pixi run python -m pipeline.gen_shot_images ep001 --num-candidates 5

  # 指定输出质量
  pixi run python -m pipeline.gen_shot_images ep001 --quality high
"""

import argparse
import sys
from pathlib import Path

from creative_toolkit.image import ComfyUIImageGen
from pipeline.utils import ensure_episode_dirs, get_episode_dir, load_shots

# 默认参数
DEFAULT_NUM_CANDIDATES = 3
DEFAULT_SIZE = "1792x1024"  # 16:9 aspect ratio for cinematic look
DEFAULT_QUALITY = "high"
DEFAULT_BASE_SEED = 42


def get_shot_image_dir(episode_dir: Path, shot_id: str) -> Path:
    """获取镜头图像输出目录"""
    return episode_dir / "video"


def generate_shot_images(
    episode_id: str,
    shot_id: str,
    prompt_visual: str,
    num_candidates: int = DEFAULT_NUM_CANDIDATES,
    size: str = DEFAULT_SIZE,
    quality: str = DEFAULT_QUALITY,
    base_seed: int = DEFAULT_BASE_SEED,
) -> list[Path]:
    """生成单个镜头的多个T2I候选图像

    Args:
        episode_id: 剧集ID (e.g., "ep001")
        shot_id: 镜头ID (e.g., "S01")
        prompt_visual: 图像生成的正向prompt
        num_candidates: 生成的候选数量 (default: 3)
        size: 输出尺寸 (default: "1792x1024")
        quality: 生成质量 (default: "high")
        base_seed: 基础seed值用于生成变化

    Returns:
        生成的图像路径列表
    """
    ep_dir = get_episode_dir(episode_id)
    output_dir = get_shot_image_dir(ep_dir, shot_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 标准的负面提示词（防止常见问题）
    negative_prompt = (
        "anatomy error, face distortion, extra limbs, watermark, text artifacts, "
        "oversharpen, uncanny look, blurry, low quality, deformed, distorted"
    )

    generated_paths = []

    print(f"  → {shot_id}: 生成 {num_candidates} 个候选图像...", end="", flush=True)

    try:
        image_gen = ComfyUIImageGen()

        for i in range(num_candidates):
            # 构建输出文件名
            seed_val = base_seed + (i * 1000)
            output_filename = f"{shot_id}_gen_{i:03d}_seed{seed_val}.png"
            output_path = output_dir / output_filename

            # 跳过已存在的文件
            if output_path.exists():
                print(f"\n      • {output_filename} (already exists)")
                generated_paths.append(output_path)
                continue

            # 生成图像
            try:
                metadata = image_gen.generate(
                    prompt=prompt_visual,
                    output_path=output_path,
                    negative_prompt=negative_prompt,
                    size=size,
                    quality=quality,
                )

                if output_path.exists():
                    file_size = output_path.stat().st_size / 1024
                    print(f"\n      ✓ {output_filename} ({file_size:.0f}KB)")
                    generated_paths.append(output_path)
                else:
                    print(f"\n      ✗ {output_filename} (generation failed)")

            except Exception as e:
                print(f"\n      ✗ {output_filename}: {str(e)[:50]}")
                continue

        if generated_paths:
            print(f"    ✓ {shot_id}: {len(generated_paths)} 个成功生成", end="")
        else:
            print(f"    ✗ {shot_id}: 生成失败", end="")

    except Exception as e:
        print(f"\n    ✗ 初始化ComfyUIImageGen失败: {e}", file=sys.stderr)
        return []

    return generated_paths


def main():
    parser = argparse.ArgumentParser(
        description="生成镜头的T2I候选图像（基于prompt_visual）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成整集的所有镜头图像
  pixi run python -m pipeline.gen_shot_images ep001

  # 生成特定镜头
  pixi run python -m pipeline.gen_shot_images ep001 S01 S02 S03

  # 自定义候选数量和质量
  pixi run python -m pipeline.gen_shot_images ep001 --num-candidates 5 --quality high

  # 使用自定义尺寸
  pixi run python -m pipeline.gen_shot_images ep001 --size 1920x1080
        """,
    )

    parser.add_argument("episode_id", help="剧集ID (e.g., ep001)")
    parser.add_argument(
        "shot_ids",
        nargs="*",
        help="镜头IDs (不指定则处理全部)",
    )
    parser.add_argument(
        "--num-candidates",
        type=int,
        default=DEFAULT_NUM_CANDIDATES,
        help=f"每个镜头生成的候选数量 (默认: {DEFAULT_NUM_CANDIDATES})",
    )
    parser.add_argument(
        "--size",
        default=DEFAULT_SIZE,
        help=f"输出尺寸 (默认: {DEFAULT_SIZE})",
    )
    parser.add_argument(
        "--quality",
        choices=["low", "medium", "high"],
        default=DEFAULT_QUALITY,
        help=f"生成质量 (默认: {DEFAULT_QUALITY})",
    )
    parser.add_argument(
        "--base-seed",
        type=int,
        default=DEFAULT_BASE_SEED,
        help=f"基础seed值 (默认: {DEFAULT_BASE_SEED})",
    )

    args = parser.parse_args()

    episode_id = args.episode_id
    ep_dir = get_episode_dir(episode_id)
    ensure_episode_dirs(episode_id)

    print(f"\n{'=' * 70}")
    print(f"镜头图像生成（T2I） — {episode_id}")
    print(f"模型: Flux | 尺寸: {args.size} | 质量: {args.quality.upper()}")
    print(f"{'=' * 70}\n")

    # 加载shots.json
    try:
        shots_data = load_shots(episode_id)
    except FileNotFoundError:
        print(f"❌ 错误: 找不到 {episode_id}/shots.json")
        print("   请先运行: pixi run python -m pipeline.gen_shots {episode_id}")
        sys.exit(1)

    shots = shots_data["shots"]

    # 过滤镜头
    if args.shot_ids:
        shot_filter = set(args.shot_ids)
        shots = [s for s in shots if s["shot_id"] in shot_filter]
        if not shots:
            print(f"❌ 未找到指定的镜头: {args.shot_ids}")
            sys.exit(1)

    # 检查prompt_visual是否存在
    shots_with_prompt = [
        s for s in shots if s.get("prompt_visual") and s["prompt_visual"].strip()
    ]

    if not shots_with_prompt:
        print(f"❌ 没有找到包含 prompt_visual 的镜头")
        print("   请确保 shots.json 中所有镜头都有 prompt_visual 字段")
        sys.exit(1)

    print(f"处理 {len(shots_with_prompt)} 个镜头 (每个生成 {args.num_candidates} 个候选图像):\n")

    total_generated = 0
    success_count = 0

    for shot in shots_with_prompt:
        shot_id = shot["shot_id"]
        prompt_visual = shot.get("prompt_visual", "")

        if not prompt_visual.strip():
            print(f"  ✗ {shot_id}: 缺少 prompt_visual")
            continue

        generated = generate_shot_images(
            episode_id=episode_id,
            shot_id=shot_id,
            prompt_visual=prompt_visual,
            num_candidates=args.num_candidates,
            size=args.size,
            quality=args.quality,
            base_seed=args.base_seed,
        )

        if generated:
            success_count += 1
            total_generated += len(generated)
            print()

    print(f"\n{'=' * 70}")
    print(f"✓ 完成: {success_count}/{len(shots_with_prompt)} 个镜头")
    print(f"✓ 总计生成: {total_generated} 个候选图像")
    print(f"{'=' * 70}\n")

    if success_count < len(shots_with_prompt):
        sys.exit(1)


if __name__ == "__main__":
    main()
