#!/usr/bin/env python3
"""
生成关键帧规划markdown文档 — 基于新的I2I序列架构

架构：
  - i2i_first (20帧): location参考 + visual prompt → 初始场景
  - i2i_seq (28帧): 前一帧结果 + motion prompt → 运动变化

用法:
    python -m pipeline.generate_keyframes_md ep001
"""

import json
from pathlib import Path
from pipeline.utils import get_episode_dir, load_shots


def generate_keyframes_md(episode_id: str) -> Path:
    """生成关键帧规划markdown文档。"""
    ep_dir = get_episode_dir(episode_id)
    shots_data = load_shots(episode_id)

    # 加载keyframes.json
    keyframes_path = ep_dir / "keyframes.json"
    with open(keyframes_path, "r", encoding="utf-8") as f:
        keyframes_data = json.load(f)

    # 按shot_id分组关键帧
    keyframes_by_shot = {}
    for kf in keyframes_data["keyframes"]:
        shot_id = kf["shot_id"]
        if shot_id not in keyframes_by_shot:
            keyframes_by_shot[shot_id] = []
        keyframes_by_shot[shot_id].append(kf)

    # 生成markdown
    lines = [
        f"# {episode_id} — 关键帧规划详细表",
        "",
        "## 📊 概览",
        "",
        f"**总镜头数:** {len(shots_data['shots'])}",
        f"**总时长:** {sum(s['duration_s'] for s in shots_data['shots'])}s",
        f"**总关键帧:** {keyframes_data['total_keyframes']}",
        "",
        "| 类型 | 数量 | 说明 |",
        "|------|------|------|",
        "| i2i_first | 20 | 第一帧：location参考 + visual prompt (denoise=0.7) |",
        "| i2i_seq | 28 | 后续帧：前一帧参考 + motion prompt (denoise=0.5) |",
        "",
        "---",
        "",
    ]

    # 按镜头生成详细信息
    for shot in shots_data["shots"]:
        shot_id = shot["shot_id"]
        duration = shot["duration_s"]
        location = shot.get("location", "?")
        emotion = shot.get("emotion", "?")

        kfs = sorted(keyframes_by_shot.get(shot_id, []), key=lambda x: x["frame_index"])

        lines.extend([
            f"## {shot_id} — {duration}s | {location}",
            "",
            f"**情感:** {emotion}",
            f"**关键帧数:** {len(kfs)}",
            "",
            "| KF ID | 类型 | 时间(s) | 提示词摘要 |",
            "|-------|------|--------|----------|",
        ])

        for kf in kfs:
            kf_id = kf["keyframe_id"]
            kf_type = kf["type"]
            timestamp = kf["timestamp_s"]
            prompt = kf.get("prompt", "")

            # 生成提示词摘要
            if prompt:
                preview = prompt[:60] + "..." if len(prompt) > 60 else prompt
            else:
                preview = "(无提示词)"

            # 标记denoise强度
            if kf_type == "i2i_first":
                denoise_note = " (0.7)"
            else:
                denoise_note = " (0.5)"

            lines.append(
                f"| {kf_id} | {kf_type}{denoise_note} | {timestamp} | {preview} |"
            )

        lines.extend(["", "**完整提示词：**", ""])

        for kf in kfs:
            prompt = kf.get("prompt", "")
            if prompt:
                lines.extend([
                    f"### {kf['keyframe_id']} ({kf['type']})",
                    "",
                    "```",
                    prompt,
                    "```",
                    "",
                ])

        lines.extend(["---", ""])

    # 统计信息
    lines.extend([
        "## 📈 统计",
        "",
        "### 按类型分布",
        "",
    ])

    type_counts = {"i2i_first": 0, "i2i_seq": 0}
    for kf in keyframes_data["keyframes"]:
        type_counts[kf["type"]] = type_counts.get(kf["type"], 0) + 1

    for kf_type, count in sorted(type_counts.items()):
        lines.append(f"- **{kf_type}**: {count}")

    # 保存
    md_path = ep_dir / "keyframes.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ 关键帧markdown: {md_path}")

    return md_path


def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="生成关键帧规划markdown")
    parser.add_argument("episode_id", help="剧集编号, e.g. ep001")
    args = parser.parse_args()

    try:
        generate_keyframes_md(args.episode_id)
        print(f"✨ 关键帧md生成完成")

    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
