#!/usr/bin/env python3
"""
道具参考图生成器 — 根据 props.json 生成每个道具的 T2I 参考图

使用 creative_toolkit 的图片生成 API（支持本地ComfyUI或云端OpenAI）。

用法:
    python -m pipeline.gen_props_refs                           # 生成所有道具
    python -m pipeline.gen_props_refs 灵子 光盘                  # 指定道具
    python -m pipeline.gen_props_refs --backend openai          # 使用OpenAI后端
    python -m pipeline.gen_props_refs --num-candidates 5        # 生成5个候选
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, "/home/dz/creative-toolkit")

from creative_toolkit.image import ComfyUIImageGen, OpenAIImageGen
from pipeline.utils import PROJECT_ROOT


def create_image_gen(backend: str = "comfyui") -> object:
    """工厂函数：创建指定后端的图片生成器"""
    if backend.lower() == "openai":
        return OpenAIImageGen()
    else:  # 默认 comfyui
        return ComfyUIImageGen()


def build_prop_prompt(prop_key: str, prop_info: dict) -> str:
    """从道具信息构建详细的T2I提示词

    Args:
        prop_key: 道具的键（用于ID）
        prop_info: 来自 props.json 的道具数据

    Returns:
        完整的视觉描述提示词
    """
    zh_name = prop_info.get("zh_name", prop_key)
    en_name = prop_info.get("en_name", prop_key)
    brief = prop_info.get("brief", "")
    appearance = prop_info.get("appearance", "")
    materials = prop_info.get("materials", [])
    color = prop_info.get("color", "")
    size = prop_info.get("size", "")
    visual_keywords = prop_info.get("visual_keywords", [])
    era = prop_info.get("era", "")
    tech_level = prop_info.get("tech_level", "")

    # 构建prompt
    prompt_parts = [
        f"Prop: {zh_name} ({en_name})",
        f"Description: {brief}" if brief else None,
        f"Appearance: {appearance}",
        f"Materials: {', '.join(materials)}" if materials else None,
        f"Color: {color}",
        f"Size: {size}",
        f"Era: {era}",
        f"Tech Level: {tech_level}",
        f"Style: {', '.join(visual_keywords)}" if visual_keywords else None,
        "Studio product photography, professional lighting, clean background",
        "Detailed texture, photorealistic, high resolution, 8K",
    ]

    prompt = ". ".join([p for p in prompt_parts if p])
    return prompt


def generate_props_refs(
    prop_names: list[str] | None = None,
    num_candidates: int = 3,
    backend: str = "comfyui",
) -> dict:
    """生成道具参考图

    Args:
        prop_names: 要生成的道具名称或键列表（None表示全部）
        num_candidates: 每个道具生成的候选数
        backend: 图片生成后端 ("comfyui" 或 "seadream")

    Returns:
        {prop_key: [list of generated image paths]}
    """
    # 读取 props.json
    props_path = PROJECT_ROOT / "assets" / "props" / "props.json"
    if not props_path.exists():
        raise FileNotFoundError(f"props.json not found: {props_path}")

    with open(props_path, "r", encoding="utf-8") as f:
        props_data = json.load(f)

    # 获取所有道具键
    all_prop_keys = [k for k in props_data.keys() if k not in ["metadata"]]

    # 确定要处理的道具
    if prop_names:
        # 支持按键或按中文名称匹配
        target_keys = []
        for name in prop_names:
            if name in all_prop_keys:
                target_keys.append(name)
            else:
                # 尝试按中文名称匹配
                for key in all_prop_keys:
                    if props_data[key].get("zh_name") == name:
                        target_keys.append(key)
                        break

        invalid_names = [
            n
            for n in prop_names
            if n not in target_keys
            and not any(props_data[k].get("zh_name") == n for k in all_prop_keys)
        ]
        if invalid_names:
            print(f"⚠️  Unknown props: {invalid_names}")
    else:
        target_keys = all_prop_keys

    print(f"\n{'=' * 60}")
    print(f"🎭 道具参考图生成")
    print(f"{'=' * 60}")
    print(f"后端: {backend}")
    print(f"道具数: {len(target_keys)}")
    print(f"每个道具的候选数: {num_candidates}\n")

    # 创建图片生成器
    image_gen = create_image_gen(backend)

    results = {}

    for prop_key in target_keys:
        prop_info = props_data[prop_key]
        zh_name = prop_info.get("zh_name", prop_key)

        print(f"🎬 生成 {zh_name} ({prop_key}) 的参考图...")

        # 构建输出目录
        prop_dir = PROJECT_ROOT / "assets" / "props" / prop_key
        prop_dir.mkdir(parents=True, exist_ok=True)

        # 生成提示词
        prompt = build_prop_prompt(prop_key, prop_info)

        # 生成多个候选
        generated_paths = []
        for i in range(num_candidates):
            try:
                # 构建输出文件名
                output_filename = f"{prop_key}_ref_{i + 1:03d}.png"
                output_path = prop_dir / output_filename

                # 调用生成API
                print(f"  [{i + 1}/{num_candidates}] Generating {output_filename}...")

                metadata = image_gen.generate(
                    prompt=prompt,
                    output_path=str(output_path),
                    negative_prompt="",
                    size="1536x1024",  # 产品摄影尺寸
                    quality="high",
                )

                generated_paths.append(output_path)
                print(f"  ✓ 保存: {output_path}")

            except Exception as e:
                print(f"  ❌ 生成失败: {e}")
                continue

        results[prop_key] = generated_paths
        print(f"  ✓ {prop_key}: {len(generated_paths)} 个候选\n")

    # 总结
    print(f"{'=' * 60}")
    print(f"✨ 道具参考图生成完成")
    print(f"{'=' * 60}\n")

    total_generated = sum(len(paths) for paths in results.values())
    print(f"📊 总计生成: {total_generated} 张图片")
    for prop_key, paths in results.items():
        if paths:
            zh_name = props_data[prop_key].get("zh_name", prop_key)
            print(f"   {zh_name}: {len(paths)} 张")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="根据 props.json 生成道具参考图"
    )
    parser.add_argument(
        "props",
        nargs="*",
        help="要生成的道具名称或键（留空则生成全部）",
    )
    parser.add_argument(
        "--num-candidates",
        type=int,
        default=3,
        help="每个道具生成的候选数（默认: 3）",
    )
    parser.add_argument(
        "--backend",
        default="comfyui",
        choices=["comfyui", "openai"],
        help="使用的图片生成后端（默认: comfyui）",
    )

    args = parser.parse_args()

    try:
        results = generate_props_refs(
            prop_names=args.props if args.props else None,
            num_candidates=args.num_candidates,
            backend=args.backend,
        )

        # 打印输出位置
        print(f"\n📂 参考图保存位置:")
        for prop_key in results.keys():
            prop_dir = PROJECT_ROOT / "assets" / "props" / prop_key
            print(f"   {prop_dir}/")

    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
