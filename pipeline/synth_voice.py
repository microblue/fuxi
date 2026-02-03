"""
伏羲纪元 — 语音合成模块

为每个有台词的镜头生成语音音频。
当前使用占位实现（生成静音 WAV），接入 TTS API 后替换 synthesize_line()。
"""

import struct
import wave
from pathlib import Path

from utils import (
    collect_dialogues,
    get_shot_audio_path,
    load_shots,
)

# TTS 配置
SAMPLE_RATE = 44100
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit


def generate_silence_wav(filepath: Path, duration_s: float) -> None:
    """生成指定时长的静音 WAV 文件（占位用）"""
    n_frames = int(SAMPLE_RATE * duration_s)
    with wave.open(str(filepath), "w") as wav:
        wav.setnchannels(CHANNELS)
        wav.setsampwidth(SAMPLE_WIDTH)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(struct.pack(f"<{n_frames}h", *([0] * n_frames)))


def synthesize_line(
    text: str, emotion: str, output_path: Path, duration_s: float
) -> None:
    """
    合成单句台词音频。

    TODO: 接入实际 TTS API（如 Azure TTS / Fish Audio / CosyVoice）
    当前为占位实现，生成对应时长的静音 WAV。

    Args:
        text: 台词文本
        emotion: 情绪标签（用于 TTS 语调控制）
        output_path: 输出 WAV 路径
        duration_s: 目标音频时长
    """
    print(f'  [TTS] {output_path.name}: "{text}" (emotion={emotion}, {duration_s}s)')
    print(f"         -> 占位：生成 {duration_s}s 静音 WAV")
    generate_silence_wav(output_path, duration_s)


def synthesize_narration(text: str, output_path: Path, duration_s: float) -> None:
    """
    合成旁白音频。

    TODO: 使用独立旁白音色
    """
    print(f'  [旁白] {output_path.name}: "{text}" ({duration_s}s)')
    print(f"          -> 占位：生成 {duration_s}s 静音 WAV")
    generate_silence_wav(output_path, duration_s)


def process_episode(episode_id: str) -> list[Path]:
    """为整集生成所有语音音频"""
    print(f"\n{'=' * 60}")
    print(f"语音合成 — {episode_id}")
    print(f"{'=' * 60}")

    shots_data = load_shots(episode_id)
    dialogues = collect_dialogues(shots_data)
    generated = []

    # 为有台词的镜头生成音频
    for d in dialogues:
        audio_path = get_shot_audio_path(episode_id, d["shot_id"])
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        synthesize_line(
            text=d["dialogue"],
            emotion=d["emotion"],
            output_path=audio_path,
            duration_s=d["duration_s"],
        )
        generated.append(audio_path)

    # 处理旁白和机械音（从 sfx_bgm 字段提取）
    for shot in shots_data["shots"]:
        sfx = shot.get("sfx_bgm", "")
        if "旁白" in sfx or "voice" in sfx.lower():
            narration_text = sfx.split("'")[1] if "'" in sfx else sfx
            audio_path = get_shot_audio_path(episode_id, f"{shot['shot_id']}_narration")
            audio_path.parent.mkdir(parents=True, exist_ok=True)
            synthesize_narration(narration_text, audio_path, shot["duration_s"])
            generated.append(audio_path)

    print(f"\n共生成 {len(generated)} 个音频文件")
    return generated


if __name__ == "__main__":
    import sys

    episode = sys.argv[1] if len(sys.argv) > 1 else "ep001"
    process_episode(episode)
