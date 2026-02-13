#!/usr/bin/env python3
"""
关键帧规划生成 — 为每个镜头生成T2I+I2V关键帧序列

策略：
  - 第1帧：I2I生成（场景/角色约束）
  - 第2+帧：I2I参考帧（基于第1帧生成运动）

关键帧数量规则：
  - ≤2s：2帧
  - 2-3s：2-3帧（根据视觉事件复杂度）
  - 3-5s：3帧
  - >5s：4帧

用法:
    python -m pipeline.gen_keyframes ep001
    python -m pipeline.gen_keyframes ep002
"""

import json
import sys
from pathlib import Path

# 添加 creative-toolkit 到路径
sys.path.insert(0, "/home/dz/creative-toolkit")

from pipeline.utils import get_episode_dir, load_shots, PROJECT_ROOT
from creative_toolkit.storyboard import extract_keyframe_specs_for_shot

# ── 名称别名映射 ─────────────────────────────────────────────────
# shots.json 中的 ref 名称 → 实际资产目录名
LOCATION_ALIASES = {
    "ancient_leize_swamp": "primordial_swamp_rainstorm",
    "entropy_descent_site": "primordial_swamp_rainstorm",  # 同一片沼泽区域
}

CHARACTER_ALIASES = {
    "young_fuxi": "fuxi",
    "hunter_jia": "hunter",
    "hunter_yi": "hunter",
    "nuwa": "nvwa",
    "observer_ai": None,  # 无视觉形象，仅画外音
}


def resolve_location_name(location: str) -> str:
    """将 shots.json 中的 location_ref 映射到实际资产目录名。"""
    return LOCATION_ALIASES.get(location, location)


def resolve_character_name(character: str) -> str | None:
    """将 shots.json 中的 character_ref 映射到实际资产目录名。返回 None 表示无视觉形象。"""
    if character in CHARACTER_ALIASES:
        return CHARACTER_ALIASES[character]
    return character


def find_character_reference(character: str) -> Path | None:
    """找到character对应的参考图片。自动应用别名映射。"""
    resolved = resolve_character_name(character)
    if resolved is None:
        return None  # 无视觉形象

    char_ref_dir = PROJECT_ROOT / "assets" / "characters" / resolved

    if char_ref_dir.exists():
        # 查找 {resolved}_ref_*.png 格式
        ref_files = sorted(list(char_ref_dir.glob(f"{resolved}_ref_*.png")))
        if ref_files:
            return ref_files[0]

        # 查找 ref_final.png
        ref_final = char_ref_dir / "ref_final.png"
        if ref_final.exists():
            return ref_final

        # 查找任何 ref_*.png
        ref_files = sorted(list(char_ref_dir.glob("ref_*.png")))
        if ref_files:
            return ref_files[0]

    return None


def find_location_reference(location: str) -> Path | None:
    """找到location对应的参考图片。自动应用别名映射。"""
    resolved = resolve_location_name(location)
    loc_ref_dir = PROJECT_ROOT / "assets" / "locations" / resolved

    if loc_ref_dir.exists():
        ref_files = sorted(list(loc_ref_dir.glob(f"{resolved}_ref_*.png")))
        if ref_files:
            return ref_files[0]

    return None


def load_asset_definitions() -> tuple[dict, dict, dict]:
    """加载资产定义文件。

    Returns:
        (locations_dict, characters_dict, props_dict)
    """
    locations = {}
    characters = {}
    props = {}

    # 加载 locations.json
    locations_path = PROJECT_ROOT / "assets" / "locations" / "locations.json"
    if locations_path.exists():
        with open(locations_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            locations = data.get("locations", {})

    # 加载 characters.json
    characters_path = PROJECT_ROOT / "assets" / "characters" / "characters.json"
    if characters_path.exists():
        with open(characters_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            characters = data.get("characters", {})

    # 加载 props.json
    props_path = PROJECT_ROOT / "assets" / "props" / "props.json"
    if props_path.exists():
        with open(props_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # props.json 中道具直接在顶层（除了 metadata）
            props = {k: v for k, v in data.items() if k != "metadata"}

    return locations, characters, props


def generate_keyframes_md(episode_id: str) -> Path:
    """生成关键帧规划文档 (keyframes.md)。"""
    ep_dir = get_episode_dir(episode_id)
    shots_data = load_shots(episode_id)

    # 计算总时长（兼容 duration 和 duration_s）
    total_duration = sum(s.get('duration_s', s.get('duration', 0)) for s in shots_data['shots'])

    lines = [
        f"# {episode_id} — 关键帧规划",
        "",
        "## 概览",
        "",
        f"**总镜头数:** {len(shots_data['shots'])}",
        f"**总时长:** {total_duration}s",
        "",
        "关键帧策略:",
        "- **第1帧（T2I）**: 文本到图像，设定场景/角色/气氛",
        "- **后续帧（I2V）**: 基于第1帧作为参考，生成镜头内运动",
        "",
        "---",
        "",
    ]

    for shot in shots_data["shots"]:
        shot_id = shot["shot_id"]
        # 兼容 duration 和 duration_s 字段
        duration = shot.get("duration_s", shot.get("duration", 4.0))

        # 从LLM提取完整的关键帧规格，包括所有timing信息
        keyframes = extract_keyframe_specs_for_shot(shot, duration)

        # 使用shot信息作为description
        description = shot.get("action", "")[:40]

        lines.extend(
            [
                f"## {shot_id} — {description}",
                "",
                f"**镜头时长:** {duration}s | **关键帧数:** {len(keyframes)}",
                f"**地点:** {shot.get('location', '?')}",
                f"**情感:** {shot.get('emotion', '?')}",
                "",
                "**视觉事件:**",
                "",
            ]
        )

        for i, keyframe in enumerate(keyframes, 1):
            visual_event = keyframe.get("visual_event", "")
            shot_scale = keyframe.get("shot_scale", "")
            camera_angle = keyframe.get("camera_angle", "")
            lines.append(f"  {i}. {visual_event} ({shot_scale}, {camera_angle})")

        lines.extend(["", "**关键帧详情:**", ""])

        for i, keyframe in enumerate(keyframes, 1):
            frame_type = keyframe.get("type", "i2v")
            timestamp = keyframe.get("timestamp_s", 0.0)
            duration_until = keyframe.get("duration_until_next_s", 0.0)

            lines.extend(
                [
                    f"### {shot_id}-KF{i} ({frame_type})",
                    "",
                    f"- **时间:** {timestamp}s (持续 {duration_until}s)",
                    f"- **类型:** {frame_type}",
                    f"- **景别:** {keyframe.get('shot_scale', '?')}",
                    f"- **相机角度:** {keyframe.get('camera_angle', '?')}",
                ]
            )

            if i == 1:
                # T2I 帧：显示参考图像信息
                ref_image_type = keyframe.get("ref_image_type", "location")
                ref_image_subject = keyframe.get("ref_image_subject", "")
                if ref_image_type and ref_image_subject:
                    lines.append(f"- **参考图像:** {ref_image_type}/{ref_image_subject}")

                # 显示prompt预览
                prompt = keyframe.get("prompt", "")
                preview = prompt[:120] + "..." if len(prompt) > 120 else prompt
                lines.append(f"- **Prompt:** `{preview}`")
            else:
                # I2V 帧：参考前一帧
                ref_frame = keyframe.get("ref_image", "")
                lines.append(f"- **参考帧:** {ref_frame}")

                # 显示prompt预览
                prompt = keyframe.get("prompt", "")
                preview = prompt[:120] + "..." if len(prompt) > 120 else prompt
                lines.append(f"- **Motion Prompt:** `{preview}`")

            lines.append("")

        lines.extend(["---", ""])

    # 保存
    md_path = ep_dir / "keyframes.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Keyframes 文档: {md_path}")

    return md_path


def generate_keyframes_json(episode_id: str) -> Path:
    """生成关键帧配置 JSON。

    extract_keyframe_specs_for_shot 返回完整的keyframe列表，包括所有timing和相机信息。
    同时关联 shots.json 中的资产信息（location_ref, characters, character_refs, prop_refs）
    """
    ep_dir = get_episode_dir(episode_id)
    shots_data = load_shots(episode_id)

    # 加载资产定义
    locations, characters, props = load_asset_definitions()

    keyframes = []

    for shot in shots_data["shots"]:
        shot_id = shot["shot_id"]
        # 兼容 duration 和 duration_s 字段
        duration = shot.get("duration_s", shot.get("duration", 4.0))

        # 从LLM提取完整的关键帧规格，包括timing、camera等所有信息
        shot_keyframes = extract_keyframe_specs_for_shot(shot, duration)

        # 准备 shot 的资产信息
        location_ref = shot.get("location_ref") or shot.get("location")
        location_asset = locations.get(location_ref, {}) if location_ref else {}

        character_refs = shot.get("character_refs", shot.get("characters", []))
        character_assets = {}
        for char_ref in character_refs:
            if char_ref in characters:
                character_assets[char_ref] = characters[char_ref]

        prop_refs = shot.get("prop_refs", [])
        prop_assets = {}
        for prop_ref in prop_refs:
            if prop_ref in props:
                prop_assets[prop_ref] = props[prop_ref]

        for i, kf_spec in enumerate(shot_keyframes, 1):
            keyframe_id = f"{shot_id}-KF{i}"

            # 确定 ref_image：第一帧用角色参考（有角色时）或场景参考，后续帧参考前一帧
            ref_image = None
            if i == 1:
                # 第一帧：如果有角色，优先用角色参考；否则用场景参考
                # 过滤掉无视觉形象的角色（如 observer_ai）
                visual_chars = [c for c in character_refs if resolve_character_name(c) is not None]

                # 1) 有视觉角色 → 用角色参考
                if visual_chars:
                    for char in visual_chars:
                        char_ref_path = find_character_reference(char)
                        if char_ref_path:
                            ref_image = str(char_ref_path)
                            break

                # 2) 无角色或角色参考未找到 → 用场景参考
                if not ref_image and location_ref:
                    loc_ref_path = find_location_reference(location_ref)
                    if loc_ref_path:
                        ref_image = str(loc_ref_path)

                if not ref_image:
                    print(f"  ⚠️ {shot_id}: 未找到任何参考图 (loc={location_ref}, chars={character_refs})")
            else:
                # 后续帧：参考前一帧的keyframe_id
                ref_image = f"{shot_id}-KF{i-1}"

            # keyframe_id added by LLM extractor
            keyframe = {
                "keyframe_id": keyframe_id,
                "shot_id": shot_id,
                "frame_index": i - 1,
                "type": kf_spec.get("type", "i2v"),
                "timestamp_s": kf_spec.get("timestamp_s", 0.0),
                "prompt": kf_spec.get("prompt", ""),
                "camera_state": kf_spec.get("camera_state", ""),
                "ref_image": ref_image,
                "duration_until_next_s": kf_spec.get("duration_until_next_s", 0.0),
                # 新增：资产关联信息
                "assets": {
                    "location_ref": location_ref,
                    "location_asset": location_asset,
                    "character_refs": character_refs,
                    "character_assets": character_assets,
                    "prop_refs": prop_refs,
                    "prop_assets": prop_assets,
                },
            }

            keyframes.append(keyframe)

    output = {
        "episode": episode_id,
        "total_keyframes": len(keyframes),
        "strategy": "I2I(第1帧) + I2I(参考帧)",
        "keyframes": keyframes,
    }

    json_path = ep_dir / "keyframes.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Keyframes JSON: {json_path}")
    print(f"   总帧数: {len(keyframes)}")

    return json_path


def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="生成关键帧规划 (T2I + I2V)")
    parser.add_argument("episode_id", help="剧集编号, e.g. ep001")
    args = parser.parse_args()

    try:
        ep_dir = get_episode_dir(args.episode_id)
        shots_data = load_shots(args.episode_id)
        print(f"\n{'=' * 60}")
        print(f"关键帧生成 — {args.episode_id}")
        print(f"  镜头数: {len(shots_data['shots'])}")
        print(f"{'=' * 60}\n")

        # 生成文档和JSON
        generate_keyframes_md(args.episode_id)
        generate_keyframes_json(args.episode_id)

        print(f"\n✨ 关键帧规划完成")

    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
