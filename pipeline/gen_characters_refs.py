#!/usr/bin/env python3
"""
角色参考图生成器 — 根据 characters.json 生成每个角色的 T2I 参考图

使用 creative_toolkit 的图片生成 API（支持本地ComfyUI或云端OpenAI）。

用法:
    python -m pipeline.gen_characters_refs                        # 生成所有角色
    python -m pipeline.gen_characters_refs Xihe Nuwa              # 指定角色
    python -m pipeline.gen_characters_refs --backend openai       # 使用OpenAI后端
    python -m pipeline.gen_characters_refs --num-candidates 5     # 生成5个候选
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


def build_character_prompt(character_info: dict) -> str:
    """从角色信息构建详细的T2I提示词

    Args:
        character_info: 来自 characters.json 的角色数据

    Returns:
        完整的视觉描述提示词
    """
    zh_name = character_info.get("zh_name", "Unknown")
    en_name = character_info.get("en_name", "Unknown")
    appearance = character_info.get("appearance", "")
    clothing = character_info.get("clothing", "")
    accessories = character_info.get("accessories", "")
    personality_keywords = character_info.get("personality_keywords", [])
    visual_keywords = character_info.get("visual_keywords", [])
    era = character_info.get("era", "")
    role_description = character_info.get("role_description", "")

    # 构建prompt
    prompt_parts = [
        f"Character: {zh_name} ({en_name})",
        f"Role: {role_description}",
        f"Appearance: {appearance}",
        f"Clothing: {clothing}",
        f"Accessories: {accessories}" if accessories else None,
        f"Era: {era}",
        f"Personality: {', '.join(personality_keywords)}" if personality_keywords else None,
        f"Visual Style: {', '.join(visual_keywords)}" if visual_keywords else None,
        "Cinematic portrait, professional lighting, photorealistic, detailed features, 8K resolution",
        "Clean background (neutral gray), studio lighting",
    ]

    prompt = ". ".join([p for p in prompt_parts if p])
    return prompt


def generate_character_refs(
    character_ids: list[str] | None = None,
    num_candidates: int = 3,
    backend: str = "comfyui",
) -> dict:
    """生成角色参考图

    Args:
        character_ids: 要生成的角色ID列表（None表示全部）
        num_candidates: 每个角色生成的候选数
        backend: 图片生成后端 ("comfyui" 或 "seadream")

    Returns:
        {character_id: [list of generated image paths]}
    """
    # 读取 characters.json
    characters_path = PROJECT_ROOT / "assets" / "characters" / "characters.json"
    if not characters_path.exists():
        raise FileNotFoundError(f"characters.json not found: {characters_path}")

    with open(characters_path, "r", encoding="utf-8") as f:
        characters_data = json.load(f)

    # 确定要处理的角色
    all_character_ids = list(characters_data.get("characters", {}).keys())
    if character_ids:
        target_ids = [cid for cid in character_ids if cid in all_character_ids]
        invalid_ids = [cid for cid in character_ids if cid not in all_character_ids]
        if invalid_ids:
            print(f"⚠️  Unknown characters: {invalid_ids}")
    else:
        target_ids = all_character_ids

    print(f"\n{'=' * 60}")
    print(f"🎬 角色参考图生成")
    print(f"{'=' * 60}")
    print(f"后端: {backend}")
    print(f"角色数: {len(target_ids)}")
    print(f"每个角色的候选数: {num_candidates}\n")

    # 创建图片生成器
    image_gen = create_image_gen(backend)

    results = {}

    for character_id in target_ids:
        character_info = characters_data["characters"][character_id]
        zh_name = character_info.get("zh_name", character_id)

        print(f"📸 生成 {zh_name} ({character_id}) 的参考图...")

        # 构建输出目录
        char_dir = PROJECT_ROOT / "assets" / "characters" / character_id
        char_dir.mkdir(parents=True, exist_ok=True)

        # 生成提示词
        prompt = build_character_prompt(character_info)

        # 生成多个候选
        generated_paths = []
        for i in range(num_candidates):
            try:
                # 构建输出文件名
                output_filename = f"{character_id}_ref_{i + 1:03d}.png"
                output_path = char_dir / output_filename

                # 调用生成API
                print(f"  [{i + 1}/{num_candidates}] Generating {output_filename}...")

                # ComfyUIImageGen.generate() 不支持 seed 参数
                # SeaDreamImageGen 可能支持，但为了兼容性，我们不使用seed
                metadata = image_gen.generate(
                    prompt=prompt,
                    output_path=str(output_path),
                    negative_prompt="",
                    size="1536x1024",  # 人物肖像尺寸
                    quality="high",
                )

                generated_paths.append(output_path)
                print(f"  ✓ 保存: {output_path}")

            except Exception as e:
                print(f"  ❌ 生成失败: {e}")
                continue

        results[character_id] = generated_paths
        print(f"  ✓ {character_id}: {len(generated_paths)} 个候选\n")

    # 总结
    print(f"{'=' * 60}")
    print(f"✨ 角色参考图生成完成")
    print(f"{'=' * 60}\n")

    total_generated = sum(len(paths) for paths in results.values())
    print(f"📊 总计生成: {total_generated} 张图片")
    for character_id, paths in results.items():
        if paths:
            print(f"   {character_id}: {len(paths)} 张")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="根据 characters.json 生成角色参考图"
    )
    parser.add_argument(
        "characters",
        nargs="*",
        help="要生成的角色ID或名称（留空则生成全部）",
    )
    parser.add_argument(
        "--num-candidates",
        type=int,
        default=3,
        help="每个角色生成的候选数（默认: 3）",
    )
    parser.add_argument(
        "--backend",
        default="comfyui",
        choices=["comfyui", "openai"],
        help="使用的图片生成后端（默认: comfyui）",
    )

    args = parser.parse_args()

    try:
        results = generate_character_refs(
            character_ids=args.characters if args.characters else None,
            num_candidates=args.num_candidates,
            backend=args.backend,
        )

        # 打印输出位置
        print(f"\n📂 参考图保存位置:")
        for char_id, paths in results.items():
            if paths:
                char_dir = PROJECT_ROOT / "assets" / "characters" / char_id
                print(f"   {char_dir}/")

    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
