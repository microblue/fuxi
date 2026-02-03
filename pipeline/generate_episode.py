#!/usr/bin/env python3
"""
伏羲纪元 — 全流程剧集生成管线

用法:
    python generate_episode.py [episode_id]
    python generate_episode.py ep001

流程:
    1. 验证目录结构与 shots.json
    2. 分镜可视化 (生成 storyboard.md 供人工 review)
    3. 图片生成 (T2I, generate_shot_images)
    4. 语音合成（synth_voice）
    5. 字幕生成（build_subtitles）
    6. 视频生成 (I2V, generate_episode_videos) - 可选
    7. 视频渲染与合成（render_video）
    8. 输出 final.mp4 + 渲染日志
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

from utils import ensure_episode_dirs, get_episode_dir, get_final_video_path, load_shots
from generate_storyboard import generate_storyboard_md
from generate_keyframes import generate_keyframes_json, generate_keyframes_md
from generate_shot_images import generate_shot_images
from synth_voice import process_episode as synth_voice
from build_subtitles import generate_srt
from generate_episode_videos import generate_episode_videos
from render_video import render_episode as render_video


def validate_episode(episode_id: str) -> bool:
    """验证剧集必要文件是否存在"""
    ep_dir = get_episode_dir(episode_id)

    required = [
        ep_dir / "script.md",
        ep_dir / "shots.json",
    ]

    all_ok = True
    for f in required:
        if f.exists():
            print(f"  [OK] {f.relative_to(ep_dir)}")
        else:
            print(f"  [缺失] {f.relative_to(ep_dir)}")
            all_ok = False

    # 验证 shots.json 格式
    if (ep_dir / "shots.json").exists():
        shots_data = load_shots(episode_id)
        n_shots = len(shots_data.get("shots", []))
        total_dur = sum(s["duration_s"] for s in shots_data.get("shots", []))
        print(f"  [信息] {n_shots} 个镜头, 总时长 {total_dur}s")

        # 检查必填字段
        required_fields = [
            "shot_id",
            "duration_s",
            "location",
            "camera",
            "action",
            "emotion",
            "prompt_visual",
        ]
        for shot in shots_data["shots"]:
            missing = [f for f in required_fields if f not in shot]
            if missing:
                print(f"  [警告] {shot.get('shot_id', '?')}: 缺少字段 {missing}")

    return all_ok


def run_pipeline(episode_id: str) -> None:
    """执行完整生产管线"""
    start_time = time.time()
    log_lines = []

    def log(msg: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {msg}"
        print(line)
        log_lines.append(line)

    log(f"{'=' * 60}")
    log(f"伏羲纪元 · 全流程生产管线")
    log(f"剧集: {episode_id}")
    log(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"{'=' * 60}")

    # 阶段 0: 目录验证
    log("\n[阶段 0] 目录结构验证")
    ep_dir = ensure_episode_dirs(episode_id)
    log(f"  目录已就绪: {ep_dir}")

    # 阶段 1: 文件验证
    log("\n[阶段 1] 文件验证")
    if not validate_episode(episode_id):
        log("  [错误] 必要文件缺失，终止管线")
        return

    # 阶段 2: 分镜可视化
    log("\n[阶段 2] 分镜可视化")
    try:
        storyboard_path = generate_storyboard_md(episode_id)
        log(f"  完成: {storyboard_path}")
        log("  💡 请review storyboard.md，确认镜头规划、转场、速度调整等配置无误")
    except Exception as e:
        log(f"  [警告] 分镜生成失败: {e}")
        log("  继续执行后续步骤...")

    # 阶段 2.5: 关键帧规划
    log("\n[阶段 2.5] 关键帧规划 (T2I + I2V)")
    try:
        keyframes_md = generate_keyframes_md(episode_id)
        keyframes_json = generate_keyframes_json(episode_id)
        log(f"  完成: {keyframes_json}")
        log(f"         {keyframes_md}")
    except Exception as e:
        log(f"  [警告] 关键帧规划失败: {e}")
        log("  继续执行后续步骤...")

    # 阶段 3: 图片生成 (T2I)
    log("\n[阶段 3] 图片生成 (T2I)")
    try:
        image_results = generate_shot_images(episode_id)
        total_images = sum(len(paths) for paths in image_results.values())
        log(f"  完成: {total_images} 张候选图 ({len(image_results)} 个镜头)")
    except Exception as e:
        log(f"  [警告] 图片生成失败: {e}")
        log("  继续执行后续步骤...")

    # 阶段 4: 语音合成
    log("\n[阶段 4] 语音合成")
    try:
        audio_files = synth_voice(episode_id)
        log(f"  完成: {len(audio_files)} 个音频文件")
    except Exception as e:
        log(f"  [错误] 语音合成失败: {e}")
        log("  继续执行后续步骤...")

    # 阶段 5: 字幕生成
    log("\n[阶段 5] 字幕生成")
    try:
        srt_path = generate_srt(episode_id)
        log(f"  完成: {srt_path}")
    except Exception as e:
        log(f"  [错误] 字幕生成失败: {e}")
        log("  继续执行后续步骤...")

    # 阶段 6: 视频生成 (I2V, 可选)
    log("\n[阶段 6] 视频生成 (I2V)")
    log("  [跳过] I2V 生成是可选阶段，可手动运行:")
    log("    python -m pipeline.generate_episode_videos %s" % episode_id)

    # 阶段 7: 视频渲染与合成
    log("\n[阶段 7] 视频渲染与合成")
    try:
        final_path = render_video(episode_id)
        log(f"  完成: {final_path}")
    except Exception as e:
        log(f"  [错误] 视频渲染失败: {e}")
        final_path = None

    # 阶段 7: 输出日志
    elapsed = time.time() - start_time
    log(f"\n{'=' * 60}")
    log(f"管线完成")
    log(f"耗时: {elapsed:.1f}s")
    if final_path and final_path.exists():
        size_mb = final_path.stat().st_size / (1024 * 1024)
        log(f"输出: {final_path} ({size_mb:.1f} MB)")
    else:
        log("输出: 未生成最终视频")
    log(f"{'=' * 60}")

    # 保存渲染日志
    render_log_path = ep_dir / "video" / "render_log.txt"
    with open(render_log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))
    print(f"\n渲染日志已保存: {render_log_path}")


if __name__ == "__main__":
    episode = sys.argv[1] if len(sys.argv) > 1 else "ep001"
    run_pipeline(episode)
