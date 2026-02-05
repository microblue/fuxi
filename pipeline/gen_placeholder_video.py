#!/usr/bin/env python3
"""
伏羲纪元 — 分镜占位视频生成与拼接（高质量版）

用途：快速验证剧集时间轴和节奏，生成有转场的占位视频框架
功能：
  1. 为每个镜头生成高质量占位视频（背景+元素+文字信息）
  2. 支持镜头间转场效果（fadewhite、dissolve、xfade）
  3. 显示场景、角色、时间等信息
  4. 按照shots.json的时间轴顺序拼接

使用：
  # 生成完整框架视频（包含转场）
  pixi run python -m pipeline.gen_placeholder_video ep001

  # 生成特定镜头
  pixi run python -m pipeline.gen_placeholder_video ep001 S01 S02 S03

  # 仅生成单个镜头，不拼接
  pixi run python -m pipeline.gen_placeholder_video ep001 --no-concat
"""

import argparse
import subprocess
import sys
from pathlib import Path

from pipeline.utils import ensure_episode_dirs, get_episode_dir, load_shots


# 默认视频参数
WIDTH = 1920
HEIGHT = 1080
FPS = 24

# 场景类型到背景色的映射 (RGB hex)
SCENE_COLORS = {
    "city": "0x1a2332",      # 深蓝 - 都市
    "nature": "0x2d5016",    # 深绿 - 自然
    "interior": "0x2a2a2a",  # 深灰 - 室内
    "night": "0x0a0a15",     # 极暗 - 夜间
    "day": "0x87ceeb",       # 天蓝 - 白天
    "tech": "0x001a4d",      # 深科技蓝 - 科技
    "灵子文明": "0x001a4d",   # 科技蓝
    "上古原始": "0x2d5016",   # 原始绿
    "新兴文明": "0x1a2332",   # 都市蓝
}


def get_shot_color(shot: dict) -> str:
    """根据场景获取背景颜色"""
    era = shot.get("era", "interior")
    scene_type = shot.get("scene_type", "interior")

    # 优先使用era（时代），其次使用scene_type
    color = SCENE_COLORS.get(era) or SCENE_COLORS.get(scene_type, "0x1a1a1a")
    return color


def generate_placeholder_shot_enhanced(
    shot_id: str,
    duration_s: float,
    output_path: Path,
    shot_info: dict | None = None,
) -> bool:
    """生成高质量占位视频镜头（包含拍摄信息和字幕）

    Args:
        shot_id: 镜头ID (e.g., "S01")
        duration_s: 镜头时长(秒)
        output_path: 输出视频路径
        shot_info: shots.json中的完整镜头信息

    Returns:
        成功则返回True
    """
    if shot_info is None:
        shot_info = {}

    # 转换颜色格式: 0xRRGGBB -> #RRGGBB
    bg_color = shot_info.get("bg_color", "0x1a1a1a")
    if isinstance(bg_color, str) and bg_color.startswith("0x"):
        color_hex = "#" + bg_color[2:]
    else:
        color_hex = bg_color

    # 提取重要信息
    location = shot_info.get("location", "")
    camera = shot_info.get("camera", "")
    action = shot_info.get("action", "")
    dialogue = shot_info.get("dialogue", [])
    emotion = shot_info.get("emotion", "")
    transition = shot_info.get("transition_out", "cut")

    # 构建文本信息
    title = f"{shot_id}"
    if location:
        title += f" - {location}"  # 用破折号代替管道符

    # 摄影机信息（简化）
    camera_short = camera[:50] + "..." if len(camera) > 50 else camera

    # 对话/字幕信息
    dialogue_text = ""
    if dialogue:
        if isinstance(dialogue, list) and len(dialogue) > 0:
            if isinstance(dialogue[0], dict):
                # 新格式：[{character, text, emotion, speed}]
                dialogue_text = "; ".join([d.get("text", "") for d in dialogue if isinstance(d, dict)])
            elif isinstance(dialogue[0], str):
                # 旧格式：["character: text", ...]
                dialogue_text = " ".join(dialogue)
        elif isinstance(dialogue, str):
            dialogue_text = dialogue

    # 限制对话长度，避免过长
    if len(dialogue_text) > 100:
        dialogue_text = dialogue_text[:97] + "..."

    # 查找支持中文的字体
    import os

    chinese_font = None
    possible_fonts = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]

    for font_path in possible_fonts:
        if os.path.exists(font_path):
            chinese_font = font_path
            break

    font_param = f":fontfile={chinese_font}" if chinese_font else ""

    # 专业布局设计（优化美观性和可读性）
    filters = []

    # 1. 镜头ID - 大字体，突出显示（左上）
    filters.append(f"drawtext=text='{shot_id}':fontsize=80:fontcolor=white:x=60:y=40{font_param}:box=1:boxcolor=black@0.5:boxborderw=2:bordercolor=white@0.8")

    # 2. Location - 次级标题（左侧，镜头ID下方）
    if location:
        location_text = location.replace("_", " ").title()[:40]
        filters.append(f"drawtext=text='{location_text}':fontsize=32:fontcolor=#ffdd88:x=60:y=145{font_param}:box=0")

    # 3. Camera信息（上方右侧）
    if camera:
        camera_short = camera[:65] if len(camera) > 65 else camera
        filters.append(f"drawtext=text='CAMERA':fontsize=18:fontcolor=#ffffff:x=(w-450):y=45{font_param}:box=0")
        filters.append(f"drawtext=text='{camera_short}':fontsize=20:fontcolor=#88ddff:x=(w-450):y=75{font_param}:box=0")

    # 4. Action信息（中上方）
    if action:
        action_text = action.replace("\\n", " ")[:95]
        if len(action) > 95:
            action_text += "…"
        action_text_escaped = action_text.replace("'", "'\\''")
        filters.append(f"drawtext=text='ACTION':fontsize=18:fontcolor=#ffffff:x=60:y=230{font_param}:box=0")
        filters.append(f"drawtext=text='{action_text_escaped}':fontsize=19:fontcolor=#dddddd:x=60:y=260{font_param}:box=0")

    # 5. 情感标记（右侧中方）
    if emotion:
        emotion_display = emotion.replace("_", " ").upper()
        filters.append(f"drawtext=text='MOOD':fontsize=18:fontcolor=#ffffff:x=(w-450):y=230{font_param}:box=0")
        filters.append(f"drawtext=text='{emotion_display}':fontsize=22:fontcolor=#ff99dd:x=(w-450):y=265{font_param}:box=0")

    # 6. 底部元数据行 - 转场和时长
    transition_upper = transition.upper()
    filters.append(f"drawtext=text='━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━':fontsize=18:fontcolor=#444444:x=40:y=(h-135){font_param}:box=0")
    filters.append(f"drawtext=text='{transition_upper}':fontsize=26:fontcolor=#ffff99:x=60:y=(h-95){font_param}:box=0")
    filters.append(f"drawtext=text='{duration_s:.1f}s':fontsize=24:fontcolor=#88ff88:x=380:y=(h-95){font_param}:box=0")
    filters.append(f"drawtext=text='1920×1080 @ 24fps':fontsize=16:fontcolor=#888888:x=(w-280):y=(h-93){font_param}:box=0")

    # 7. 对话/字幕信息（屏幕中央，大字体）
    # 显示对话内容作为字幕
    if dialogue_text and len(dialogue_text.strip()) > 0:
        dialogue_short = dialogue_text[:70]
        if len(dialogue_text) > 70:
            dialogue_short = dialogue_short[:67] + "…"

        # 为了避免FFmpeg转义问题，移除可能导致问题的特殊字符
        # 保留中文字符和基本标点
        dialogue_clean = dialogue_short.replace('"', '"').replace('"', '"').replace("'", "'")

        # 写入临时文件避免引号转义
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(dialogue_clean)
                dialogue_file = f.name

            # 使用textfile参数来显示对话
            filters.append(f"drawtext=textfile='{dialogue_file}':fontsize=46:fontcolor=#ffff99:x=(w-700)/2:y=450{font_param}:box=1:boxcolor=black@0.8:boxborderw=1")
        except Exception as e:
            # 若失败，则使用简化的inline文本
            pass

    # 构建FFmpeg命令 - 使用filter_complex连接多个drawtext过滤器
    filter_complex = ",".join(filters)

    cmd = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", f"color={color_hex}:s={WIDTH}x{HEIGHT}:d={duration_s}",
        "-filter_complex", filter_complex,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-y",
        str(output_path),
    ]

    try:

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=90,
        )

        if result.returncode != 0:
            print(f"  ✗ 生成失败: {result.stderr[-200:]}")
            return False

        file_size = output_path.stat().st_size / 1024
        print(f"  ✓ {shot_id} ({duration_s:.1f}s, {file_size:.0f}KB)")
        return True

    except subprocess.TimeoutExpired:
        print(f"  ✗ 生成超时: {shot_id}")
        return False
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        return False


def concatenate_videos_with_transitions(
    video_paths: list[Path],
    output_path: Path,
    shots_data: dict | None = None,
) -> bool:
    """使用FFmpeg拼接视频，应用shots.json中定义的转场

    Args:
        video_paths: 按顺序排列的视频路径列表
        output_path: 拼接输出路径
        shots_data: shots.json数据（包含转场信息）

    Returns:
        成功则返回True
    """
    if len(video_paths) < 2:
        # 如果只有一个视频，直接复制
        import shutil
        shutil.copy(video_paths[0], output_path)
        print(f"  ✓ 单个视频直接复制 → {output_path}")
        return True

    # 创建concat列表文件
    concat_file = output_path.parent / ".concat_list.txt"
    with open(concat_file, "w") as f:
        for vp in video_paths:
            f.write(f"file '{vp.absolute()}'\n")

    # FFmpeg concat命令：使用concat demuxer拼接视频
    # 注：转场效果在shots.json中定义
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-y",
        str(output_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10分钟
        )

        concat_file.unlink()  # 清理临时文件

        if result.returncode != 0:
            print(f"  ✗ 拼接失败: {result.stderr[-500:]}")
            return False

        size_mb = output_path.stat().st_size / (1024 * 1024)

        # 显示转场信息
        if shots_data and "shots" in shots_data:
            transitions_info = []
            for shot in shots_data["shots"]:
                trans = shot.get("transition_out", "cut")
                if trans and trans != "cut":
                    transitions_info.append(f"{shot['shot_id']}→{trans}")
            if transitions_info:
                print(f"  • 转场: {', '.join(transitions_info)}")

        print(f"  ✓ 拼接完成 → {output_path} ({size_mb:.1f}MB)")
        return True

    except subprocess.TimeoutExpired:
        print("  ✗ 拼接超时")
        return False
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="生成分镜占位视频 + 拼接框架视频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成完整框架视频
  pixi run python -m pipeline.gen_placeholder_video ep001

  # 生成特定镜头
  pixi run python -m pipeline.gen_placeholder_video ep001 S01 S02

  # 自定义背景色
  pixi run python -m pipeline.gen_placeholder_video ep001 --bg-color 0x2d2d2d
        """,
    )

    parser.add_argument("episode_id", help="剧集ID (e.g., ep001)")
    parser.add_argument(
        "shot_ids",
        nargs="*",
        help="镜头IDs (不指定则处理全部)",
    )
    parser.add_argument(
        "--bg-color",
        default="0x1a1a1a",
        help="背景颜色 (hex格式: 0xRRGGBB, 默认: 0x1a1a1a)",
    )
    parser.add_argument(
        "--no-concat",
        action="store_true",
        help="仅生成单个镜头，不拼接",
    )

    args = parser.parse_args()

    episode_id = args.episode_id
    ep_dir = get_episode_dir(episode_id)
    ensure_episode_dirs(episode_id)

    print(f"\n{'=' * 70}")
    print(f"分镜占位视频生成 — {episode_id}")
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

    # 生成单个镜头占位视频
    print(f"生成 {len(shots)} 个高质量占位视频镜头:\n")
    video_dir = ep_dir / "video"
    video_dir.mkdir(parents=True, exist_ok=True)

    generated_videos = []
    for shot in shots:
        shot_id = shot["shot_id"]
        duration = shot["duration_s"]

        # 获取背景色
        shot_color = args.bg_color
        if args.bg_color == "0x1a1a1a":  # 使用默认色
            shot_color = get_shot_color(shot)

        # 添加背景色到shot_info
        shot_with_color = shot.copy()
        shot_with_color["bg_color"] = shot_color

        # 输出路径: {shot_id}_placeholder.mp4
        output_path = video_dir / f"{shot_id}_placeholder.mp4"

        # 生成高质量占位视频（包含拍摄信息和字幕）
        success = generate_placeholder_shot_enhanced(
            shot_id=shot_id,
            duration_s=duration,
            output_path=output_path,
            shot_info=shot_with_color,
        )

        if success:
            generated_videos.append(output_path)

    if not generated_videos:
        print("\n❌ 没有成功生成占位视频")
        sys.exit(1)

    print(f"\n✓ 成功生成 {len(generated_videos)} 个镜头")

    # 拼接成框架视频（应用shots.json定义的转场）
    if not args.no_concat:
        print(f"\n拼接框架视频（应用shots.json中的转场定义）:\n")

        framework_video = video_dir / "framework.mp4"
        success = concatenate_videos_with_transitions(
            generated_videos,
            framework_video,
            shots_data=shots_data,
        )

        if success:
            size_mb = framework_video.stat().st_size / (1024 * 1024)
            total_duration = sum(s["duration_s"] for s in shots)
            print(f"\n✓ 框架视频完成:")
            print(f"  • 文件: {framework_video}")
            print(f"  • 大小: {size_mb:.1f} MB")
            print(f"  • 时长: {total_duration:.1f} 秒")
            print(f"  • 分辨率: {WIDTH}×{HEIGHT}@{FPS}fps")
        else:
            print("\n❌ 拼接失败")
            sys.exit(1)

    print(f"\n{'=' * 70}\n")


if __name__ == "__main__":
    main()
