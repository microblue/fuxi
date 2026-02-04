#!/usr/bin/env python3
"""
关键帧规划生成 — 为每个镜头生成T2I+I2V关键帧序列

策略：
  - 第1帧：T2I生成（文本到图像，场景/角色约束）
  - 第2+帧：I2V参考帧（基于第1帧生成运动）

关键帧数量规则：
  - ≤2s：2帧
  - 2-3s：2-3帧（根据视觉事件复杂度）
  - 3-5s：3帧
  - >5s：4帧

用法:
    python -m pipeline.generate_keyframes ep001
    python -m pipeline.generate_keyframes ep002
"""

import json
from pathlib import Path
from pipeline.utils import get_episode_dir, load_shots


def get_camera_position_for_keyframe(
    shot: dict, kf_index: int, total_kfs: int
) -> str:
    """根据shot的camera信息和关键帧位置，生成该帧的相机位置描述。

    时间进度：0 = 开始, 0.5 = 中间, 1.0 = 结束
    """
    camera = shot.get("camera", "").lower()

    # 关键帧的相对位置
    frame_progress = kf_index / (total_kfs - 1) if total_kfs > 1 else 0

    position_desc = ""

    # 处理距离变化
    if "crane down" in camera:
        if frame_progress < 0.4:
            position_desc = "camera positioned high, wide aerial view"
        elif frame_progress < 0.7:
            position_desc = "camera descending, mid-level perspective"
        else:
            position_desc = "camera descended low, detailed street-level view"

    elif "crane up" in camera:
        if frame_progress < 0.4:
            position_desc = "camera positioned low, street-level view"
        elif frame_progress < 0.7:
            position_desc = "camera ascending, expanding perspective"
        else:
            position_desc = "camera high, revealing wide panoramic view"

    elif "pulling back" in camera or "pull back" in camera:
        if frame_progress < 0.4:
            position_desc = "camera close-in, detailed view"
        elif frame_progress < 0.7:
            position_desc = "camera stepping back, widening perspective"
        else:
            position_desc = "camera pulled back far, epic wide scale view"

    elif "push in" in camera:
        if frame_progress < 0.4:
            position_desc = "camera at medium distance"
        elif frame_progress < 0.7:
            position_desc = "camera pushing in, tightening focus"
        else:
            position_desc = "camera close intimate detail view"

    # 处理旋转/倾斜
    if "tilt up" in camera:
        if frame_progress < 0.5:
            position_desc = (position_desc or "") + ", tilting upward"
        else:
            position_desc = (position_desc or "") + ", looking up at sky"

    elif "tilt down" in camera:
        if frame_progress < 0.5:
            position_desc = (position_desc or "") + ", tilting downward"
        else:
            position_desc = (position_desc or "") + ", looking down at ground"

    # 处理焦点变化 (rack focus)
    if "rack focus" in camera:
        if frame_progress < 0.5:
            position_desc = (position_desc or "") + ", focus on foreground"
        else:
            position_desc = (position_desc or "") + ", focus shifted to background"

    # 默认描述
    if not position_desc:
        if "close_up" in camera or "close-up" in camera:
            position_desc = "close-up shot, intimate framing"
        elif "medium" in camera:
            position_desc = "medium shot, balanced composition"
        elif "wide" in camera:
            position_desc = "wide shot, expansive view"
        elif "full_shot" in camera:
            position_desc = "full shot, complete scene in frame"
        else:
            position_desc = "static camera position"

    # 添加镜头特性
    if "handheld" in camera:
        position_desc += ", handheld camera with subtle movement"
    elif "steady" in camera or "static" in camera:
        position_desc += ", steady camera, minimal movement"

    return position_desc


# ─────────────────────────────────────────────────────────────
# 关键帧策略配置
# ─────────────────────────────────────────────────────────────

KEYFRAME_STRATEGIES = {
    # 场景 1-1: 灵子文明首都
    "S01": {
        "num_frames": 3,
        "description": "城市开场 → 危机",
        "visual_events": ["城市全景", "灯光故障", "警报闪烁"],
    },
    "S02": {
        "num_frames": 2,
        "description": "羲和登场",
        "visual_events": ["中枢塔顶", "数据流舞蹈"],
    },
    "S03": {
        "num_frames": 2,
        "description": "特写决断",
        "visual_events": ["脸部特写", "微笑→决心"],
    },
    "S04": {
        "num_frames": 3,
        "description": "能量爆发",
        "visual_events": ["数据提取", "光柱升起", "光点散射"],
    },
    "S05": {
        "num_frames": 3,
        "description": "温柔消散",
        "visual_events": ["身体透明", "微笑保持", "化作光粒"],
    },
    # 场景 1-2: 原始世界
    "S06": {
        "num_frames": 2,
        "description": "时空硬切",
        "visual_events": ["沼泽猎人", "向上惊呼"],
    },
    "S07": {
        "num_frames": 3,
        "description": "火种降临",
        "visual_events": ["天空撕裂", "蓝光坠落", "伏羲痛楚"],
    },
    "S08": {
        "num_frames": 2,
        "description": "漩涡吸引",
        "visual_events": ["发光漩涡", "伏羲靠近"],
    },
    # 场景 1-3: 漩涡边缘
    "S09": {
        "num_frames": 3,
        "description": "觉醒触发",
        "visual_events": ["手触晶体", "能量涌入", "跪地爆光"],
    },
    "S10": {
        "num_frames": 3,
        "description": "代码视觉三层",
        "visual_events": ["眼睛变色", "树木代码绿", "水面分子蓝"],
    },
    "S11": {
        "num_frames": 2,
        "description": "存在危机",
        "visual_events": ["看手", "看世界"],
    },
    "S12": {
        "num_frames": 2,
        "description": "氛围反转",
        "visual_events": ["天色变暗", "威胁降临"],
    },
    # 场景 1-4: 熵单位降临
    "S13": {
        "num_frames": 2,
        "description": "敌人登场",
        "visual_events": ["三个几何体", "无声下降"],
    },
    "S14": {
        "num_frames": 3,
        "description": "恐怖杀戮",
        "visual_events": ["黑色触手", "像素化上升", "彻底分解"],
    },
    "S15": {
        "num_frames": 3,
        "description": "本能反击",
        "visual_events": ["怒吼", "代码视觉", "能量爆发"],
    },
    "S16": {
        "num_frames": 3,
        "description": "地面变幻",
        "visual_events": ["触手延伸", "手按地面", "流沙困敌"],
    },
    "S17": {
        "num_frames": 2,
        "description": "女娲救场",
        "visual_events": ["绿光骨箭", "女娲现身"],
    },
    "S18": {
        "num_frames": 2,
        "description": "敌人汇合",
        "visual_events": ["聚集成阵", "红光脉动"],
    },
    "S19": {
        "num_frames": 2,
        "description": "逃离回头",
        "visual_events": ["回身看", "眼光微亮"],
    },
    # 场景 end
    "S20": {
        "num_frames": 1,
        "description": "本集终",
        "visual_events": ["黑屏", "字幕"],
    },
}


def calculate_keyframe_timings(
    shot_duration_s: float, num_frames: int
) -> list[dict]:
    """计算关键帧的时间戳和时长。

    返回: [{timestamp_s, duration_until_next_s}, ...]
    """
    if num_frames <= 1:
        return [{"timestamp_s": 0.0, "duration_until_next_s": shot_duration_s}]

    # 均匀分布关键帧
    frame_interval = shot_duration_s / (num_frames - 1)
    timings = []

    for i in range(num_frames):
        timestamp = i * frame_interval
        # 最后一帧到shot结束
        duration_until_next = shot_duration_s - timestamp
        timings.append(
            {
                "timestamp_s": round(timestamp, 3),
                "duration_until_next_s": round(duration_until_next, 3),
            }
        )

    return timings


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
        strategy = KEYFRAME_STRATEGIES.get(shot_id, {})
        num_frames = strategy.get("num_frames", 2)
        description = strategy.get("description", "")
        visual_events = strategy.get("visual_events", [])

        timings = calculate_keyframe_timings(duration, num_frames)

        lines.extend(
            [
                f"## {shot_id} — {description}",
                "",
                f"**镜头时长:** {duration}s | **关键帧数:** {num_frames}",
                f"**地点:** {shot.get('location', '?')}",
                f"**情感:** {shot.get('emotion', '?')}",
                "",
                "**视觉事件:**",
                "",
            ]
        )

        for i, event in enumerate(visual_events, 1):
            lines.append(f"  {i}. {event}")

        lines.extend(["", "**关键帧详情:**", ""])

        for i, timing in enumerate(timings, 1):
            frame_type = "T2I (场景设置)" if i == 1 else "I2V (参考帧)"
            timestamp = timing["timestamp_s"]
            duration_until = timing["duration_until_next_s"]

            lines.extend(
                [
                    f"### {shot_id}-KF{i} ({frame_type})",
                    "",
                    f"- **时间:** {timestamp}s (持续 {duration_until}s)",
                    f"- **类型:** {frame_type}",
                ]
            )

            if i == 1:
                # T2I 帧：显示 prompt
                prompt = shot.get("prompt_visual", "")
                preview = prompt[:120] + "..." if len(prompt) > 120 else prompt
                lines.append(f"- **Prompt:** `{preview}`")
            else:
                # I2V 帧：作为参考
                lines.append(f"- **参考帧:** {shot_id}-KF1 (本镜头第1帧)")

            lines.append("")

        lines.extend(["---", ""])

    # 保存
    md_path = ep_dir / "keyframes.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Keyframes 文档: {md_path}")

    return md_path


def generate_keyframes_json(episode_id: str) -> Path:
    """生成关键帧配置 JSON。

    返回结构:
    {
      "episode": "ep001",
      "keyframes": [
        {
          "keyframe_id": "S01-KF1",
          "shot_id": "S01",
          "frame_index": 0,
          "type": "t2i",
          "timestamp_s": 0.0,
          "prompt": "...",
          "reference_frame": null,
          "duration_until_next_s": 1.5
        },
        {
          "keyframe_id": "S01-KF2",
          "shot_id": "S01",
          "frame_index": 1,
          "type": "i2v",
          "timestamp_s": 1.5,
          "prompt": null,
          "reference_frame": "S01-KF1",
          "duration_until_next_s": 1.5
        }
      ]
    }
    """
    ep_dir = get_episode_dir(episode_id)
    shots_data = load_shots(episode_id)

    keyframes = []

    for shot in shots_data["shots"]:
        shot_id = shot["shot_id"]
        duration = shot["duration_s"]
        strategy = KEYFRAME_STRATEGIES.get(shot_id, {})
        num_frames = strategy.get("num_frames", 2)

        timings = calculate_keyframe_timings(duration, num_frames)

        for i, timing in enumerate(timings, 1):
            keyframe_id = f"{shot_id}-KF{i}"

            # 生成相机位置描述
            camera_position = get_camera_position_for_keyframe(shot, i - 1, num_frames)

            if i == 1:
                # T2I 帧
                visual_prompt = shot.get("prompt_visual", "")
                # 如果prompt非空，则在前面加上相机位置信息
                if visual_prompt:
                    prompt_with_camera = f"[Camera: {camera_position}] {visual_prompt}"
                else:
                    prompt_with_camera = f"[Camera: {camera_position}]"

                keyframe = {
                    "keyframe_id": keyframe_id,
                    "shot_id": shot_id,
                    "frame_index": i - 1,
                    "type": "t2i",
                    "timestamp_s": timing["timestamp_s"],
                    "prompt": prompt_with_camera,
                    "reference_frame": None,
                    "duration_until_next_s": timing["duration_until_next_s"],
                }
            else:
                # I2V 帧（基于第1帧）
                # I2V帧使用motion prompt，同样加上相机位置信息
                motion_prompt = shot.get("prompt_motion", "")
                if motion_prompt:
                    prompt_with_camera = f"[Camera: {camera_position}] {motion_prompt}"
                else:
                    prompt_with_camera = f"[Camera: {camera_position}]"

                keyframe = {
                    "keyframe_id": keyframe_id,
                    "shot_id": shot_id,
                    "frame_index": i - 1,
                    "type": "i2v",
                    "timestamp_s": timing["timestamp_s"],
                    "prompt": prompt_with_camera,
                    "reference_frame": f"{shot_id}-KF1",
                    "duration_until_next_s": timing["duration_until_next_s"],
                }

            keyframes.append(keyframe)

    output = {
        "episode": episode_id,
        "total_keyframes": len(keyframes),
        "strategy": "T2I(第1帧) + I2V(参考帧)",
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
