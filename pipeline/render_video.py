"""
伏羲纪元 — 最终视频合成模块

将镜头素材按顺序拼接，应用转场，混合音频，输出 final.mp4。

功能：
- 规格化镜头：缩放、填充到 1920×1080，标准化帧率
- 转场系统：支持 fadewhite、dissolve、xfade、hard_cut
- 时间轴计算：考虑转场重叠时间
- 音频混合：多轨音频延迟混合

配置从 shots.json 读取：
- transitions: 镜头间转场定义 (可选，默认 hard_cut)
- speed: 慢动作倍数 (可选，默认 1.0)
- trim_start / trim_end: 裁剪秒数 (可选)

依赖：ffmpeg（系统安装）、ffprobe（系统安装）
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

from pipeline.utils import (
    ensure_episode_dirs,
    find_shot_audio,
    find_shot_video,
    get_episode_dir,
    get_final_video_path,
    get_video_duration,
    load_shots,
)

# 视频参数
WIDTH = 1920
HEIGHT = 1080
FPS = 24


def run_ff(cmd: str, desc: str = "") -> subprocess.CompletedProcess:
    """运行 ffmpeg 命令，记录日志"""
    tag = f"[{desc}] " if desc else ""
    print(f"  {tag}{cmd[:130]}…")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ FAILED:\n{result.stderr[-600:]}")
        sys.exit(1)
    return result


def normalize_shot(
    src_path: Path,
    output_path: Path,
    target_duration: float,
    shot_id: str,
    speed: float = 1.0,
    trim_start: float = 0.0,
    trim_end: float | None = None,
) -> float:
    """规格化单个镜头到 1920×1080。

    Args:
        src_path: 源视频路径
        output_path: 输出视频路径
        target_duration: 目标时长（秒）
        shot_id: 镜头ID
        speed: 速度倍数 (1.0=正常，0.5=2x慢放)
        trim_start: 从开头裁剪秒数
        trim_end: 从结尾裁剪秒数（None=不裁剪）

    Returns:
        实际输出时长
    """
    vf = []

    # 1. 裁剪
    if trim_start > 0 or trim_end is not None:
        if trim_end is not None:
            duration = trim_end - trim_start
        else:
            duration = f"{target_duration - trim_start}"
        vf.append(f"trim={trim_start}:{trim_start + duration},setpts=PTS-STARTPTS")

    # 2. 速度调整 (实现慢动作)
    if speed != 1.0:
        vf.append(f"setpts={1/speed}*PTS")

    # 3. 缩放 + 填充到目标分辨率
    vf += [
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease",
        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:black",
        f"fps={FPS}",
        "setsar=1",
    ]

    cmd = (
        f'ffmpeg -y -i "{src_path}" '
        f'-vf "{",".join(vf)}" '
        f"-c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p "
        f'-an "{output_path}"'
    )
    run_ff(cmd, f"Normalize {shot_id}")

    actual_duration = get_video_duration(output_path)
    print(f"  ✓ {shot_id}: {actual_duration:.2f}s (target {target_duration}s)")
    return actual_duration


def concat_shots(
    group_idx: int,
    shot_videos: list[Path],
    output_path: Path,
    temp_dir: Path,
) -> float:
    """使用 ffmpeg concat demuxer 拼接硬切镜头。

    Returns: 拼接后的总时长
    """
    if len(shot_videos) == 1:
        # 单个镜头，直接复制
        shutil.copy2(shot_videos[0], output_path)
        return get_video_duration(shot_videos[0])

    # 创建 concat 列表文件
    concat_list = temp_dir / f"concat_{group_idx}.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for vpath in shot_videos:
            f.write(f"file '{vpath}'\n")

    cmd = (
        f'ffmpeg -y -f concat -safe 0 -i "{concat_list}" '
        f'-c copy "{output_path}"'
    )
    run_ff(cmd, f"Concat group {group_idx}")

    duration = get_video_duration(output_path)
    print(f"  Group {group_idx}: {len(shot_videos)} shots → {duration:.2f}s")
    return duration


def apply_transitions(
    group_videos: list[Path],
    group_durations: list[float],
    transitions: list[dict],
    output_path: Path,
) -> float:
    """使用 xfade 在组之间应用转场。

    Args:
        group_videos: 各组视频路径
        group_durations: 各组时长
        transitions: 转场列表 (每个 dict 有 'type' 和 'dur')
        output_path: 输出路径

    Returns: 最终视频时长
    """
    if len(group_videos) == 1:
        # 无转场，直接返回
        return group_durations[0]

    # 构建 xfade 滤镜链
    inputs = " ".join(f'-i "{f}"' for f in group_videos)

    filter_parts = []
    accum = group_durations[0]
    prev = "[0:v]"

    for i, transition in enumerate(transitions):
        td = transition.get("dur", 0)
        offset = max(0, accum - td)
        is_last = i == len(transitions) - 1
        out = "[vout]" if is_last else f"[v{i}]"

        trans_type = transition.get("type", "hard_cut")

        if trans_type == "hard_cut":
            # Hard cut: concat without xfade
            filter_parts.append(f"{prev}[{i + 1}:v]concat=n=2:v=1:a=0[v{i}]")
            prev = f"[v{i}]"
        else:
            # Xfade transition
            filter_parts.append(
                f"{prev}[{i + 1}:v]xfade=transition={trans_type}:"
                f"duration={td}:offset={offset:.3f}{out}"
            )
            prev = out

        accum = accum + group_durations[i + 1] - td

    filter_chain = ";".join(filter_parts)

    cmd = (
        f"ffmpeg -y {inputs} "
        f'-filter_complex "{filter_chain}" '
        f'-map "[vout]" -c:v libx264 -preset fast -crf 18 '
        f'-pix_fmt yuv420p "{output_path}"'
    )
    run_ff(cmd, "Apply transitions")

    duration = get_video_duration(output_path)
    print(f"  Video with transitions: {duration:.2f}s")
    return duration


def mix_audio(
    video_path: Path,
    episode_dir: Path,
    shot_timeline: list[dict],
    output_path: Path,
) -> None:
    """混合多轨音频。

    Args:
        video_path: 视频文件路径
        episode_dir: 剧集目录
        shot_timeline: 镜头时间轴 (每个元素: {shot_id, start, dur})
        output_path: 最终输出路径
    """
    # 收集音频输入
    audio_inputs = []
    audio_filters = []
    audio_idx = 1  # 0 = 视频

    for entry in shot_timeline:
        shot_id = entry["shot_id"]
        start_s = entry["start"]

        for audio_path in find_shot_audio(episode_dir, shot_id):
            delay_ms = max(0, int(start_s * 1000))
            audio_inputs.append(f'-i "{audio_path}"')
            audio_filters.append(
                f"[{audio_idx}:a]adelay={delay_ms}|{delay_ms},apad[a{audio_idx}]"
            )
            audio_idx += 1
            print(f"  🔊 {audio_path.name} → {start_s:.2f}s")

    if audio_inputs:
        # 混合所有音频轨道
        labels = "".join(f"[a{i}]" for i in range(1, audio_idx))
        n = audio_idx - 1
        audio_filters.append(f"{labels}amix=inputs={n}:duration=first:normalize=0[aout]")

        filter_complex = ";".join(audio_filters)
        audio_input_str = " ".join(audio_inputs)

        cmd = (
            f'ffmpeg -y -i "{video_path}" {audio_input_str} '
            f'-filter_complex "{filter_complex}" '
            f'-map 0:v -map "[aout]" '
            f"-c:v copy -c:a aac -b:a 192k "
            f'-shortest "{output_path}"'
        )
        run_ff(cmd, "Mix audio")
    else:
        # 无音频，直接复制视频
        shutil.copy2(video_path, output_path)
        print("  (no audio files found)")


def render_episode(episode_id: str) -> Path:
    """渲染整集视频。

    Returns: 最终输出视频路径
    """
    print(f"\n{'=' * 60}")
    print(f"视频合成 — {episode_id}")
    print(f"{'=' * 60}")

    # 初始化目录
    ep_dir = ensure_episode_dirs(episode_id)
    shots_data = load_shots(episode_id)

    video_dir = ep_dir / "video"
    video_dir.mkdir(parents=True, exist_ok=True)

    temp_dir = video_dir / "temp_compose"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)

    # ─────────────────────────────────────────────────────────
    # Phase 1: 规格化每个镜头
    # ─────────────────────────────────────────────────────────
    print(f"\n{'═' * 60}")
    print("Phase 1: 规格化镜头 → 1920×1080")
    print(f"{'═' * 60}")

    shots = shots_data["shots"]
    all_shot_ids = [s["shot_id"] for s in shots]
    target_durations = {s["shot_id"]: s["duration_s"] for s in shots}

    normalized_videos = {}  # shot_id → normalized_path
    actual_durations = {}   # shot_id → actual_duration

    for shot in shots:
        shot_id = shot["shot_id"]
        src = find_shot_video(ep_dir, shot_id)

        if not src:
            print(f"  ⚠ {shot_id}: 源视频不存在，跳过")
            continue

        output = temp_dir / f"{shot_id}.mp4"
        speed = shot.get("speed", 1.0)
        trim_start = shot.get("trim_start", 0.0)
        trim_end = shot.get("trim_end")

        actual_dur = normalize_shot(
            src,
            output,
            target_durations[shot_id],
            shot_id,
            speed=speed,
            trim_start=trim_start,
            trim_end=trim_end,
        )

        normalized_videos[shot_id] = output
        actual_durations[shot_id] = actual_dur

    available_ids = [sid for sid in all_shot_ids if sid in normalized_videos]
    print(f"\n  可用镜头: {len(available_ids)}/{len(all_shot_ids)}")

    if not available_ids:
        raise RuntimeError("没有可用的源视频")

    # ─────────────────────────────────────────────────────────
    # Phase 2: 转场规划
    # ─────────────────────────────────────────────────────────
    print(f"\n{'═' * 60}")
    print("Phase 2: 转场规划")
    print(f"{'═' * 60}")

    transitions_config = shots_data.get("transitions", {})

    def get_transition(from_id: str, to_id: str) -> dict:
        """获取两个镜头间的转场配置。"""
        key = f"{from_id}->{to_id}"
        if key in transitions_config:
            return transitions_config[key]
        # 默认: 硬切
        return {"type": "hard_cut", "dur": 0}

    # 按镜头索引建立转场映射
    shot_transitions = {}  # index → transition_dict
    for i in range(len(available_ids) - 1):
        trans = get_transition(available_ids[i], available_ids[i + 1])
        shot_transitions[i] = trans
        if trans["type"] != "hard_cut":
            print(f"  {available_ids[i]}->{available_ids[i + 1]}: "
                  f"{trans['type']} ({trans.get('dur', 0)}s)")

    # ─────────────────────────────────────────────────────────
    # Phase 3: 在组内硬切拼接
    # ─────────────────────────────────────────────────────────
    print(f"\n{'═' * 60}")
    print("Phase 3: 硬切拼接（组内）")
    print(f"{'═' * 60}")

    # 将连续的硬切镜头分组
    groups = []  # 每组: [shot_id, ...]
    group_transitions = []  # 每组后的转场
    current_group = [available_ids[0]]

    for i in range(1, len(available_ids)):
        trans = shot_transitions.get(i - 1, {"type": "hard_cut"})
        if trans["type"] == "hard_cut":
            current_group.append(available_ids[i])
        else:
            groups.append(current_group)
            group_transitions.append(trans)
            current_group = [available_ids[i]]
    groups.append(current_group)

    group_videos = []
    group_durations = []

    for group_idx, group in enumerate(groups):
        if len(group) == 1:
            # 单镜头组
            video_path = str(normalized_videos[group[0]])
            group_videos.append(Path(video_path))
            dur = actual_durations[group[0]]
            group_durations.append(dur)
            print(f"  Group {group_idx}: {group[0]} (单个)")
        else:
            # 多镜头拼接
            shot_paths = [normalized_videos[sid] for sid in group]
            output = temp_dir / f"group_{group_idx}.mp4"
            dur = concat_shots(group_idx, shot_paths, output, temp_dir)
            group_videos.append(output)
            group_durations.append(dur)

    # ─────────────────────────────────────────────────────────
    # Phase 4: 组间转场
    # ─────────────────────────────────────────────────────────
    print(f"\n{'═' * 60}")
    print("Phase 4: 组间转场（xfade）")
    print(f"{'═' * 60}")

    if len(group_videos) == 1:
        video_only = str(group_videos[0])
    else:
        video_only = str(temp_dir / "video_with_transitions.mp4")
        apply_transitions(
            group_videos,
            group_durations,
            group_transitions,
            Path(video_only),
        )

    # ─────────────────────────────────────────────────────────
    # Phase 5: 音频混合
    # ─────────────────────────────────────────────────────────
    print(f"\n{'═' * 60}")
    print("Phase 5: 音频混合")
    print(f"{'═' * 60}")

    # 构建时间轴
    shot_timeline = []
    timeline_offset = 0.0

    for shot_idx, shot_id in enumerate(available_ids):
        shot_dur = actual_durations[shot_id]

        # 应用转场时间调整
        if shot_idx > 0:
            trans = shot_transitions.get(shot_idx - 1, {"type": "hard_cut"})
            if trans["type"] != "hard_cut":
                timeline_offset -= trans.get("dur", 0)

        shot_timeline.append({
            "shot_id": shot_id,
            "start": timeline_offset,
            "dur": shot_dur,
        })
        timeline_offset += shot_dur

    # 最终输出路径
    final_output = get_final_video_path(episode_id)

    mix_audio(Path(video_only), ep_dir, shot_timeline, final_output)

    # ─────────────────────────────────────────────────────────
    # 报告
    # ─────────────────────────────────────────────────────────
    final_duration = get_video_duration(final_output)
    final_size = final_output.stat().st_size

    print(f"\n{'═' * 60}")
    print(f"✅ 合成完毕")
    print(f"   输出: {final_output}")
    print(f"   时长: {final_duration:.1f}s ({final_duration / 60:.1f} min)")
    print(f"   大小: {final_size / 1024 / 1024:.1f} MB")
    print(f"   镜头: {len(available_ids)}")
    print(f"{'═' * 60}")

    print("\n  时间轴:")
    for entry in shot_timeline:
        has_audio = "🔊" if find_shot_audio(ep_dir, entry["shot_id"]) else "  "
        print(f"    {entry['start']:7.2f}s  {has_audio}  {entry['shot_id']:4s}  "
              f"({entry['dur']:.2f}s)")

    # 清理临时文件
    shutil.rmtree(temp_dir)

    return final_output


if __name__ == "__main__":
    import sys

    episode = sys.argv[1] if len(sys.argv) > 1 else "ep001"
    render_episode(episode)
