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
from pathlib import Path
from pipeline.utils import get_episode_dir, load_shots
from creative_toolkit.storyboard import extract_keyframe_specs_for_shot


def generate_keyframes_md(episode_id: str) -> Path:
    """生成关键帧规划文档 (keyframes.md)。"""
    ep_dir = get_episode_dir(episode_id)
    shots_data = load_shots(episode_id)

    lines = [
        f"# {episode_id} — 关键帧规划",
        "",
        "## 概览",
        "",
        f"**总镜头数:** {len(shots_data['shots'])}",
        f"**总时长:** {sum(s['duration_s'] for s in shots_data['shots'])}s",
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
        duration = shot["duration_s"]

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
    """
    ep_dir = get_episode_dir(episode_id)
    shots_data = load_shots(episode_id)

    keyframes = []

    for shot in shots_data["shots"]:
        shot_id = shot["shot_id"]
        duration = shot["duration_s"]

        # 从LLM提取完整的关键帧规格，包括timing、camera等所有信息
        shot_keyframes = extract_keyframe_specs_for_shot(shot, duration)

        for i, kf_spec in enumerate(shot_keyframes, 1):
            keyframe_id = f"{shot_id}-KF{i}"

            # keyframe_id added by LLM extractor
            keyframe = {
                "keyframe_id": keyframe_id,
                "shot_id": shot_id,
                "frame_index": i - 1,
                "type": kf_spec.get("type", "i2v"),
                "timestamp_s": kf_spec.get("timestamp_s", 0.0),
                "prompt": kf_spec.get("prompt", ""),
                "camera_state": kf_spec.get("camera_state", ""),
                "ref_image": kf_spec.get("ref_image", None),
                "duration_until_next_s": kf_spec.get("duration_until_next_s", 0.0),
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
