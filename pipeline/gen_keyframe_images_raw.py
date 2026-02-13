#!/usr/bin/env python3
"""
关键帧生成（纯Python版，不依赖 ComfyUI HTTP Server）

使用 creative_toolkit.image.flux2_native 直接调用 Flux2 模型生成。

用法（必须在 ComfyUI 的 pixi 环境中运行）:
    cd /home/dz/ComfyUI && pixi run python /home/dz/fuxi/pipeline/gen_keyframe_images_raw.py ep001 S08
    cd /home/dz/ComfyUI && pixi run python /home/dz/fuxi/pipeline/gen_keyframe_images_raw.py ep001 S08 --kf 1
    cd /home/dz/ComfyUI && pixi run python /home/dz/fuxi/pipeline/gen_keyframe_images_raw.py ep001 S08 --steps 20
"""

import json
import logging
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, "/home/dz/fuxi")
sys.path.insert(0, "/home/dz/creative-toolkit")

from pipeline.utils import get_episode_dir, load_shots, PROJECT_ROOT

logger = logging.getLogger(__name__)

OUTPUT_WIDTH = 1920
OUTPUT_HEIGHT = 1080


# 角色别名（与 gen_keyframe_images.py 一致）
_CHARACTER_ALIASES = {
    "young_fuxi": "fuxi",
    "hunter_jia": "hunter",
    "hunter_yi": "hunter",
    "nuwa": "nvwa",
    "observer_ai": None,  # 无视觉形象
}

# 性别 → prompt 前缀
_GENDER_PROMPT_PREFIX = {
    "male": "male figure, masculine features, man, ",
    "female": "female figure, feminine features, woman, ",
}


def load_characters_json() -> dict:
    characters_path = PROJECT_ROOT / "assets" / "characters" / "characters.json"
    if characters_path.exists():
        with open(characters_path, "r", encoding="utf-8") as f:
            return json.load(f).get("characters", {})
    return {}


def resolve_character_name(char_ref: str) -> str | None:
    """解析角色名，返回资产目录名。None表示无视觉形象。"""
    if char_ref in _CHARACTER_ALIASES:
        return _CHARACTER_ALIASES[char_ref]
    return char_ref


def find_location_reference(location_ref: str) -> Path | None:
    """查找 location 参考图。"""
    loc_dir = PROJECT_ROOT / "assets" / "locations" / location_ref
    if loc_dir.exists():
        refs = sorted(loc_dir.glob(f"{location_ref}_ref_*.png"))
        if refs:
            return refs[0]
    # 尝试用 keyframes.json 中的 location_asset 名查找
    locations_dir = PROJECT_ROOT / "assets" / "locations"
    for d in locations_dir.iterdir():
        if d.is_dir():
            refs = sorted(d.glob("*_ref_*.png"))
            if refs and location_ref in d.name:
                return refs[0]
    return None


def find_character_reference(char_ref: str) -> Path | None:
    """查找角色参考图。"""
    resolved = resolve_character_name(char_ref)
    if resolved is None:
        return None
    char_dir = PROJECT_ROOT / "assets" / "characters" / resolved
    if char_dir.exists():
        ref = char_dir / "ref_final.png"
        if ref.exists():
            return ref
        refs = sorted(char_dir.glob("*_ref_*.png"))
        if refs:
            return refs[0]
    return None


def build_gender_prefix(character_refs: list[str], characters_db: dict) -> str:
    for char_ref in character_refs:
        if _CHARACTER_ALIASES.get(char_ref) is None and char_ref in _CHARACTER_ALIASES:
            continue
        char_def = characters_db.get(char_ref, {})
        gender = char_def.get("gender")
        hairstyle = char_def.get("hairstyle", "")
        if gender and gender in _GENDER_PROMPT_PREFIX:
            prefix = _GENDER_PROMPT_PREFIX[gender]
            if hairstyle:
                prefix += f"{hairstyle}, "
            return prefix
    return ""


def generate_keyframes_raw(
    episode_id: str,
    shot_id: str,
    kf_index: int | None = None,
    steps: int = 28,
    guidance: float = 8.0,
    seed: int = 0,
    size: str = "1920x1080",
):
    """用纯 Python Flux2 生成关键帧。"""
    from creative_toolkit.image.flux2_native import Flux2NativeImageGen

    ep_dir = get_episode_dir(episode_id)
    keyframes_path = ep_dir / "keyframes.json"

    with open(keyframes_path, "r", encoding="utf-8") as f:
        keyframes_data = json.load(f)

    shot_keyframes = sorted(
        [kf for kf in keyframes_data["keyframes"] if kf["shot_id"] == shot_id],
        key=lambda x: x["frame_index"],
    )

    if not shot_keyframes:
        print(f"❌ No keyframes for {shot_id}")
        return

    if kf_index is not None:
        shot_keyframes = [kf for kf in shot_keyframes if kf["frame_index"] == kf_index]
        if not shot_keyframes:
            print(f"❌ KF index {kf_index} not found in {shot_id}")
            return

    characters_db = load_characters_json()
    keyframe_dir = ep_dir / "video" / "keyframes"
    keyframe_dir.mkdir(parents=True, exist_ok=True)

    # 初始化生成器
    gen = Flux2NativeImageGen()

    for kf in shot_keyframes:
        keyframe_id = kf["keyframe_id"]
        kf_prompt = kf.get("prompt", "")
        if not kf_prompt:
            print(f"⚠️ [{keyframe_id}] No prompt, skip")
            continue

        # 性别前缀
        kf_assets = kf.get("assets", {})
        kf_character_refs = kf_assets.get("character_refs", [])
        gender_prefix = build_gender_prefix(kf_character_refs, characters_db)
        if gender_prefix:
            kf_prompt = gender_prefix + kf_prompt

        # 构建参考图：最多2张（location + 主角），最少1张（location）
        ref_images = []
        location_ref_key = kf_assets.get("location_ref")

        # 查找 location 参考图（必须）
        if location_ref_key:
            # 尝试直接名
            loc_path = find_location_reference(location_ref_key)
            if not loc_path:
                # 尝试 location_asset 中的 en_name 转换
                loc_asset = kf_assets.get("location_asset", {})
                alt_name = loc_asset.get("en_name", "").lower().replace(" ", "_")
                if alt_name:
                    loc_path = find_location_reference(alt_name)
            if loc_path:
                ref_images.append(loc_path)
                print(f"  🏞️  Location ref: {loc_path.name}")
            else:
                print(f"  ⚠️ Location '{location_ref_key}' not found")

        # 查找主角参考图（可选，最多1张）
        visual_chars = [c for c in kf_character_refs if resolve_character_name(c) is not None]
        if visual_chars:
            main_char = visual_chars[0]
            char_path = find_character_reference(main_char)
            if char_path:
                ref_images.append(char_path)
                print(f"  👤 Character ref: {char_path.name} ({main_char})")

        if not ref_images:
            print(f"  ❌ [{keyframe_id}] No reference images, skip")
            continue

        output_path = keyframe_dir / f"{keyframe_id}.png"
        kf_seed = seed + kf["frame_index"] * 1000

        print(f"\n{'─' * 50}")
        print(f"[Raw] {keyframe_id} ({len(ref_images)} refs, seed={kf_seed})")
        print(f"  📝 {kf_prompt[:100]}...")

        try:
            gen.generate_with_references(
                prompt=kf_prompt,
                ref_images=[str(p) for p in ref_images],
                output_path=str(output_path),
                size=size,
                steps=steps,
                guidance=guidance,
                seed=kf_seed,
            )
            print(f"  ✅ {output_path.name}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    # 清理 GPU
    gen.unload_models()
    print(f"\n{'=' * 50}")
    print("✅ Done")


def main():
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="关键帧生成（纯Python，不依赖ComfyUI Server）")
    parser.add_argument("episode_id", help="剧集编号, e.g. ep001")
    parser.add_argument("shot_id", help="镜头编号, e.g. S08")
    parser.add_argument("--kf", type=int, default=None, help="只生成指定 frame_index (0-based)")
    parser.add_argument("--steps", type=int, default=28, help="采样步数 (default: 28)")
    parser.add_argument("--guidance", type=float, default=8.0, help="Guidance scale (default: 8.0)")
    parser.add_argument("--seed", type=int, default=0, help="基础 seed (default: 0)")
    parser.add_argument("--size", default="1920x1080", help="输出尺寸 (default: 1920x1080)")
    args = parser.parse_args()

    generate_keyframes_raw(
        episode_id=args.episode_id,
        shot_id=args.shot_id,
        kf_index=args.kf,
        steps=args.steps,
        guidance=args.guidance,
        seed=args.seed,
        size=args.size,
    )


if __name__ == "__main__":
    main()
