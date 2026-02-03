"""
伏羲纪元 — 短剧生产管线工具函数
"""

import json
import os
import re
import subprocess
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
EPISODES_DIR = PROJECT_ROOT / "episodes"
STYLE_BIBLE_DIR = PROJECT_ROOT / "style_bible"


def get_episode_dir(episode_id: str) -> Path:
    """获取指定剧集的目录路径"""
    ep_dir = EPISODES_DIR / episode_id
    return ep_dir


def ensure_episode_dirs(episode_id: str) -> Path:
    """确保剧集目录结构完整"""
    ep_dir = get_episode_dir(episode_id)
    subdirs = [
        "prompts",
        "assets/characters",
        "assets/locations",
        "assets/props",
        "audio",
        "video",
    ]
    for sub in subdirs:
        (ep_dir / sub).mkdir(parents=True, exist_ok=True)
    return ep_dir


def load_shots(episode_id: str) -> dict:
    """加载 shots.json"""
    shots_file = get_episode_dir(episode_id) / "shots.json"
    if not shots_file.exists():
        raise FileNotFoundError(f"shots.json not found for {episode_id}: {shots_file}")
    with open(shots_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_prompt(episode_id: str, shot_id: str) -> str:
    """加载指定镜头的 prompt 文件"""
    prompt_file = get_episode_dir(episode_id) / "prompts" / f"{shot_id}.txt"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    with open(prompt_file, "r", encoding="utf-8") as f:
        return f.read()


def get_shot_audio_path(episode_id: str, shot_id: str) -> Path:
    """获取指定镜头的音频文件路径"""
    return get_episode_dir(episode_id) / "audio" / f"{shot_id}.wav"


def get_shot_video_path(episode_id: str, shot_id: str) -> Path:
    """获取指定镜头的视频文件路径"""
    return get_episode_dir(episode_id) / "video" / f"{shot_id}.mp4"


def get_final_video_path(episode_id: str) -> Path:
    """获取最终输出视频路径"""
    return get_episode_dir(episode_id) / "video" / "final.mp4"


def collect_dialogues(shots_data: dict) -> list[dict]:
    """从 shots.json 提取所有有台词的镜头"""
    dialogues = []
    for shot in shots_data["shots"]:
        if shot.get("dialogue"):
            dialogues.append(
                {
                    "shot_id": shot["shot_id"],
                    "dialogue": shot["dialogue"],
                    "emotion": shot.get("emotion", ""),
                    "duration_s": shot["duration_s"],
                    "characters": shot.get("characters", []),
                }
            )
    return dialogues


def collect_subtitles(shots_data: dict) -> list[dict]:
    """从 shots.json 提取所有需要字幕的镜头"""
    subtitles = []
    cumulative_time = 0.0
    for shot in shots_data["shots"]:
        if shot.get("subtitle") or shot.get("dialogue"):
            text = shot.get("subtitle") or shot.get("dialogue", "")
            subtitles.append(
                {
                    "shot_id": shot["shot_id"],
                    "text": text,
                    "start_s": cumulative_time,
                    "end_s": cumulative_time + shot["duration_s"],
                }
            )
        cumulative_time += shot["duration_s"]
    return subtitles


def format_timecode(seconds: float) -> str:
    """秒数转 SRT 时间码格式 HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# ─────────────────────────────────────────────────────────────
# Prompt parsing and asset discovery utilities
# ─────────────────────────────────────────────────────────────


def parse_prompt_file(filepath: Path) -> tuple[str, str]:
    """Extract positive and negative prompts from a prompt file.

    Supports multiple formats:
    1. [POSITIVE PROMPT] ... [NEGATIVE PROMPT] ...
    2. [IMAGE PROMPT] ... [NEGATIVE] ...

    Falls back to treating entire file as positive prompt if no markers found.

    Returns: (positive_prompt, negative_prompt)
    """
    text = filepath.read_text(encoding="utf-8")

    # Default negative prompt
    negative = (
        "anatomy error, face distortion, extra limbs, extra fingers, watermark, text artifacts, "
        "oversharpen, uncanny look, blurry, low quality, cartoon, anime, illustration style, "
        "deformed face, asymmetric eyes, bad proportions, cropped, out of frame"
    )

    # Format 1: [POSITIVE PROMPT] ... [NEGATIVE PROMPT] ...
    pos_match = re.search(
        r"\[POSITIVE PROMPT\]\s*\n(.*?)(?:\[NEGATIVE|$)", text, re.DOTALL
    )
    if pos_match:
        positive = pos_match.group(1).strip()
        neg_match = re.search(r"\[NEGATIVE PROMPT\]\s*\n(.*?)(?:\[|$)", text, re.DOTALL)
        if neg_match:
            negative = neg_match.group(1).strip()
        return positive, negative

    # Format 2: [IMAGE PROMPT] ...
    img_match = re.search(r"\[IMAGE PROMPT\]\s*\n(.*?)(?:\[VIDEO|$)", text, re.DOTALL)
    if img_match:
        positive = img_match.group(1).strip()
        neg_match = re.search(r"\[NEGATIVE\]\s*(.*?)(?:\[|$)", text, re.DOTALL)
        if neg_match:
            negative = neg_match.group(1).strip()
        return positive, negative

    # Fallback: use whole text as positive
    positive = text.strip()
    return positive, negative


def find_shot_video(episode_dir: Path, shot_id: str) -> Path | None:
    """Find video source file for a shot.

    Prefers {shot_id}_video.mp4 (from img2vid), falls back to {shot_id}.mp4.

    Returns: Path to video file, or None if not found.
    """
    video_dir = episode_dir / "video"
    for name in [f"{shot_id}_video.mp4", f"{shot_id}.mp4"]:
        path = video_dir / name
        if path.exists():
            return path
    return None


def find_shot_audio(episode_dir: Path, shot_id: str) -> list[Path]:
    """Find audio files for a shot.

    Returns: List of audio file paths (may be empty).
    """
    audio_dir = episode_dir / "audio"
    audio_files = []
    for name in [f"{shot_id}.wav", f"{shot_id}_narration.wav"]:
        path = audio_dir / name
        if path.exists():
            audio_files.append(path)
    return audio_files


def get_video_duration(video_path: Path) -> float:
    """Get duration of a video file in seconds using ffprobe.

    Returns: Duration in seconds, or 0.0 if unable to determine.
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-show_entries",
                "format=duration",
                "-of",
                "csv=p=0",
                str(video_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except Exception:
        pass
    return 0.0
