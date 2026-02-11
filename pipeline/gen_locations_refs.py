#!/usr/bin/env python3
"""
地点参考图生成 — 根据 locations.json 批量生成所有地点的参考图

从 assets/locations/locations.json 读取地点定义，为每个 location 生成参考图像。
每个地点生成多个候选图（不同seed），存储到 assets/locations/{location_name}/ 目录。

用法:
    pixi run python -m pipeline.gen_locations_refs
    pixi run python -m pipeline.gen_locations_refs lingzi_capital_data_core primordial_swamp_rainstorm
    pixi run python -m pipeline.gen_locations_refs --num-candidates 3
"""

import argparse
import json
import sys
from pathlib import Path

from creative_toolkit.image import ComfyUIImageGen, SeaDreamImageGen
from pipeline.utils import PROJECT_ROOT

# 常量
LOCATIONS_JSON = PROJECT_ROOT / "assets" / "locations" / "locations.json"
LOCATIONS_DIR = PROJECT_ROOT / "assets" / "locations"

# 横屏短剧统一用 16:9 横屏
IMG_W, IMG_H = 1792, 1024  # 16:9 高质量

STYLE_PREFIX = (
    "cinematic film still, photorealistic, 16:9 horizontal aspect ratio, "
    "movie quality lighting, shallow depth of field, epic atmosphere, high detail"
)

DEFAULT_NUM_CANDIDATES = 2
DEFAULT_QUALITY = "high"
DEFAULT_BACKEND = "comfyui"


def load_locations_json() -> dict:
    """加载 locations.json"""
    if not LOCATIONS_JSON.exists():
        raise FileNotFoundError(f"locations.json not found: {LOCATIONS_JSON}")

    with open(LOCATIONS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def create_image_gen(backend: str):
    """创建图像生成器实例

    Args:
        backend: "comfyui" 或 "seadream"

    Returns:
        ComfyUIImageGen 或 SeaDreamImageGen 实例
    """
    if backend == "seadream":
        return SeaDreamImageGen()
    else:  # comfyui is default
        return ComfyUIImageGen()


def build_prompt(location_info: dict) -> str:
    """根据location信息构建T2I生成prompt"""

    # 基础信息
    zh_name = location_info.get("zh_name", "")
    en_name = location_info.get("en_name", "")
    visual_style = location_info.get("visual_style", "")
    atmosphere = location_info.get("atmosphere", "")
    color_palette = location_info.get("color_palette", [])
    architecture = location_info.get("architecture", "")
    lighting = location_info.get("lighting", "")
    key_features = location_info.get("key_features", [])
    era = location_info.get("era", "")

    # 构建prompt
    parts = [STYLE_PREFIX]

    # 位置和时代
    if en_name:
        parts.append(f"{en_name}")
    if era:
        parts.append(f"era: {era}")

    # 氛围和风格
    if atmosphere:
        parts.append(f"atmosphere: {atmosphere}")
    if visual_style:
        parts.append(f"visual style: {visual_style}")

    # 建筑/地形
    if architecture:
        parts.append(architecture)

    # 关键特征
    if key_features:
        # 选择前3个最重要的特征
        features_str = ", ".join(key_features[:3])
        parts.append(f"key features: {features_str}")

    # 配色
    if color_palette:
        colors_str = ", ".join(color_palette[:4])
        parts.append(f"color palette: {colors_str}")

    # 光效
    if lighting:
        parts.append(f"lighting: {lighting}")

    # 添加标准的没有人物的标记
    if "no people" not in " ".join(parts).lower():
        parts.append("no people visible")

    prompt = ", ".join(parts)
    return prompt


def generate_location_refs(
    location_name: str,
    location_info: dict,
    image_gen,
    num_candidates: int = DEFAULT_NUM_CANDIDATES,
    quality: str = DEFAULT_QUALITY,
    base_seed: int = 0,
) -> list[Path]:
    """为单个location生成参考图

    Args:
        location_name: location ID (e.g., "lingzi_capital_data_core")
        location_info: location信息字典
        image_gen: 图像生成器实例 (ComfyUIImageGen 或 SeaDreamImageGen)
        num_candidates: 生成的候选数量
        quality: 生成质量
        base_seed: 基础seed值

    Returns:
        生成的图像路径列表
    """

    # 创建输出目录
    output_dir = LOCATIONS_DIR / location_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # 构建prompt
    prompt = build_prompt(location_info)

    # 标准负面提示词
    negative_prompt = (
        "anatomy error, face distortion, extra limbs, watermark, text artifacts, "
        "oversharpen, uncanny look, blurry, low quality, deformed, distorted, "
        "people, person, human, figure, character"
    )

    generated_paths = []
    zh_name = location_info.get("zh_name", location_name)

    print(f"\n  → {location_name}")
    print(f"     {zh_name}")
    print(f"     生成 {num_candidates} 个候选图像...")

    try:
        for i in range(num_candidates):
            seed_val = base_seed + (i * 1000)
            output_filename = f"{location_name}_ref_{i:02d}_seed{seed_val}.png"
            output_path = output_dir / output_filename

            # 跳过已存在的文件
            if output_path.exists():
                print(f"      • {output_filename} (already exists)")
                generated_paths.append(output_path)
                continue

            # 生成图像
            try:
                print(f"      • {output_filename}...", end="", flush=True)

                image_gen.generate(
                    prompt=prompt,
                    output_path=output_path,
                    negative_prompt=negative_prompt,
                    size=f"{IMG_W}x{IMG_H}",
                    quality=quality,
                )

                if output_path.exists():
                    size_kb = output_path.stat().st_size / 1024
                    print(f" ✓ ({size_kb:.0f}KB)")
                    generated_paths.append(output_path)
                else:
                    print(" ✗ (输出文件未生成)")

            except Exception as e:
                print(f" ✗ ({str(e)[:50]}...)")
                continue

    except Exception as e:
        print(f"    ✗ 错误: {e}")
        return []

    return generated_paths


def main():
    parser = argparse.ArgumentParser(
        description="根据 locations.json 生成地点参考图",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成所有地点的参考图 (默认使用ComfyUI后端)
  pixi run python -m pipeline.gen_locations_refs

  # 使用SeaDream 4.5后端生成特定地点的参考图
  pixi run python -m pipeline.gen_locations_refs --backend seadream lingzi_capital_data_core

  # 自定义候选数量
  pixi run python -m pipeline.gen_locations_refs --num-candidates 3

  # 指定输出质量
  pixi run python -m pipeline.gen_locations_refs --quality high --backend seadream
        """,
    )

    parser.add_argument(
        "location_names",
        nargs="*",
        help="location IDs (不指定则生成全部)",
    )
    parser.add_argument(
        "--num-candidates",
        type=int,
        default=DEFAULT_NUM_CANDIDATES,
        help=f"每个场景生成的候选数量 (默认: {DEFAULT_NUM_CANDIDATES})",
    )
    parser.add_argument(
        "--quality",
        default=DEFAULT_QUALITY,
        help=f"生成质量 (默认: {DEFAULT_QUALITY})",
    )
    parser.add_argument(
        "--base-seed",
        type=int,
        default=0,
        help="基础seed值 (默认: 0)",
    )
    parser.add_argument(
        "--backend",
        choices=["comfyui", "seadream"],
        default=DEFAULT_BACKEND,
        help=f"图像生成后端 (默认: {DEFAULT_BACKEND})",
    )

    args = parser.parse_args()

    print(f"\n{'=' * 70}")
    print(f"地点参考图生成 — 根据 locations.json")
    print(f"后端: {args.backend.upper()}")
    print(f"{'=' * 70}")

    # 创建图像生成器
    try:
        image_gen = create_image_gen(args.backend)
        print(f"\n✓ {args.backend.upper()} 后端已初始化")
    except Exception as e:
        print(f"\n❌ 错误: 无法初始化 {args.backend} 后端: {e}")
        sys.exit(1)

    # 加载 locations.json
    try:
        locations_data = load_locations_json()
    except FileNotFoundError as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)

    locations = locations_data.get("locations", {})
    if not locations:
        print("❌ 错误: locations.json 中未找到 locations 定义")
        sys.exit(1)

    # 过滤location
    if args.location_names:
        location_filter = set(args.location_names)
        locations = {k: v for k, v in locations.items() if k in location_filter}

        # 检查是否有未找到的location
        not_found = location_filter - set(locations.keys())
        if not_found:
            print(f"\n⚠️  未找到的 location: {', '.join(sorted(not_found))}")

        if not locations:
            print(f"❌ 没有找到指定的 location")
            sys.exit(1)

    print(f"\n为 {len(locations)} 个地点生成参考图:\n")

    total_generated = 0
    for location_name, location_info in sorted(locations.items()):
        try:
            generated = generate_location_refs(
                location_name,
                location_info,
                image_gen=image_gen,
                num_candidates=args.num_candidates,
                quality=args.quality,
                base_seed=args.base_seed,
            )
            total_generated += len(generated)
        except Exception as e:
            print(f"  ✗ {location_name}: {e}")

    print(f"\n{'=' * 70}")
    print(f"✅ 生成完成: {total_generated} 个参考图")
    print(f"   输出目录: {LOCATIONS_DIR}")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
