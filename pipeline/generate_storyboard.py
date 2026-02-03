#!/usr/bin/env python3
"""
从 shots.json 生成可视化 storyboard.md

用途：便于创意团队 review 分镜规划、转场、速度调整等配置

Usage:
    python -m pipeline.generate_storyboard ep001
"""

from pathlib import Path
from pipeline.utils import get_episode_dir, load_shots


def generate_storyboard_md(episode_id: str) -> Path:
    """从 shots.json 生成 storyboard.md。

    Returns: storyboard.md 路径
    """
    ep_dir = get_episode_dir(episode_id)
    shots_data = load_shots(episode_id)

    # 收集元数据
    episode_name = shots_data.get("episode", episode_id)
    total_duration = sum(s["duration_s"] for s in shots_data["shots"])
    num_shots = len(shots_data["shots"])
    transitions = shots_data.get("transitions", {})

    # 生成 Markdown 内容
    lines = [
        f"# {episode_name} — 分镜规划",
        "",
        "## 剧集概况",
        "",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| 镜头总数 | {num_shots} 个 |",
        f"| 总时长 | {total_duration:.1f}s ({total_duration/60:.1f}min) |",
        f"| 格式 | 1920×1080 @ 24fps (16:9 横屏) |",
        f"| 生成时间 | {shots_data.get('generated_at', 'N/A')} |",
        "",
        "---",
        "",
        "## 分镜序列",
        "",
    ]

    # 转场摘要
    if transitions:
        lines.extend([
            "### 转场配置",
            "",
        ])
        for key, trans in transitions.items():
            trans_type = trans.get("type", "hard_cut")
            trans_dur = trans.get("dur", 0)
            lines.append(f"- **{key}**: {trans_type} ({trans_dur}s)")
        lines.extend(["", "---", ""])

    # 逐镜头详情
    cumulative_time = 0.0

    for i, shot in enumerate(shots_data["shots"], 1):
        shot_id = shot["shot_id"]
        duration = shot["duration_s"]
        location = shot.get("location", "?")
        camera = shot.get("camera", "?")
        action = shot.get("action", "?")
        dialogue = shot.get("dialogue", "")
        emotion = shot.get("emotion", "")
        speed = shot.get("speed", 1.0)
        trim_start = shot.get("trim_start", 0.0)
        trim_end = shot.get("trim_end")

        # 计算实际时长（考虑速度调整）
        actual_duration = duration / speed if speed != 1.0 else duration

        # 镜头头部
        lines.append(f"### {i}. {shot_id}")
        lines.append("")

        # 时间轴
        lines.append(f"**时间:** {cumulative_time:.1f}s ~ {cumulative_time + actual_duration:.1f}s " +
                    f"({actual_duration:.1f}s)")
        lines.append("")

        # 配置信息表格
        lines.append("| 配置 | 值 |")
        lines.append("|------|------|")
        lines.append(f"| 场景 | `{location}` |")
        lines.append(f"| 景别 | {camera} |")
        lines.append(f"| 情绪 | {emotion} |")

        if speed != 1.0:
            lines.append(f"| 速度 | {speed}x ⚡ |")
        if trim_start > 0 or trim_end is not None:
            trim_info = f"trim={trim_start}"
            if trim_end is not None:
                trim_info += f"-{trim_end}"
            lines.append(f"| 裁剪 | {trim_info} |")

        lines.append("")

        # 动作描述
        lines.append(f"**动作:** {action}")
        lines.append("")

        # 对白
        if dialogue:
            lines.append(f"**对白:** {dialogue}")
            lines.append("")

        # 视觉提示词预览
        prompt_visual = shot.get("prompt_visual", "")
        if prompt_visual:
            prompt_preview = (prompt_visual[:100] + "...") if len(prompt_visual) > 100 else prompt_visual
            lines.append(f"**T2I Prompt:** `{prompt_preview}`")
            lines.append("")

        # 运动提示词预览
        prompt_motion = shot.get("prompt_motion", "")
        if prompt_motion:
            motion_preview = (prompt_motion[:100] + "...") if len(prompt_motion) > 100 else prompt_motion
            lines.append(f"**I2V Prompt:** `{motion_preview}`")
            lines.append("")

        # 转场标注
        if i < num_shots:
            next_shot_id = shots_data["shots"][i]["shot_id"]
            trans_key = f"{shot_id}->{next_shot_id}"
            if trans_key in transitions:
                trans = transitions[trans_key]
                trans_type = trans.get("type", "hard_cut")
                trans_dur = trans.get("dur", 0)
                lines.append(f"**转场→** {trans_type} ({trans_dur}s)")
            else:
                lines.append(f"**转场→** hard_cut (硬切)")
            lines.append("")

        # 分隔线
        lines.append("---")
        lines.append("")

        # 更新累积时间
        cumulative_time += actual_duration

    # 底部摘要
    lines.extend([
        "## 审核清单",
        "",
        "- [ ] 时间轴是否合理？",
        "- [ ] 转场是否流畅？",
        "- [ ] 镜头动作是否清晰？",
        "- [ ] 对白/字幕是否完整？",
        "- [ ] Prompt 是否符合风格？",
        "",
        f"**生成日期:** {shots_data.get('generated_at', 'N/A')}",
        f"**总时长:** {total_duration:.1f}s",
    ])

    content = "\n".join(lines)

    # 写入文件
    storyboard_path = ep_dir / "storyboard.md"
    storyboard_path.write_text(content, encoding="utf-8")

    print(f"✅ Storyboard generated: {storyboard_path}")
    print(f"   {num_shots} shots, {total_duration:.1f}s total")

    return storyboard_path


def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Generate storyboard.md from shots.json")
    parser.add_argument("episode_id", help="Episode ID (e.g., ep001)")
    args = parser.parse_args()

    try:
        generate_storyboard_md(args.episode_id)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
