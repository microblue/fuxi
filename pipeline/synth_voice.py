"""
伏羲纪元 — 语音合成模块

为每个有台词的镜头生成语音音频。

支持多个 TTS 提供商：
1. Fish Audio (推荐) - 高质量中文 TTS
2. Edge TTS - 免费离线选项
3. 占位符 - 生成静音（开发用）

每个角色可配置不同的音色和情感参数。
"""

import json
import os
import subprocess
from pathlib import Path

from utils import (
    collect_dialogues,
    get_shot_audio_path,
    load_shots,
)

# TTS 配置
SAMPLE_RATE = 44100
CHANNELS = 1

# 角色配置（可在 episodes/{ep}/characters.json 中覆盖）
CHARACTER_VOICES = {
    "fuxi": {
        "provider": "fish_audio",  # 使用 Fish Audio
        "voice_id": "cn_male_youthful",  # 年轻男性音色
        "speed": 1.0,
        "pitch": 0,
    },
    "fuxi_mother": {
        "provider": "fish_audio",
        "voice_id": "cn_female_warm",  # 温暖女性音色
        "speed": 1.0,
        "pitch": 0,
    },
    "elder_woman": {
        "provider": "fish_audio",
        "voice_id": "cn_female_elderly",  # 老年女性音色
        "speed": 0.95,
        "pitch": -5,
    },
    "shaman": {
        "provider": "fish_audio",
        "voice_id": "cn_male_deep",  # 深沉男性音色
        "speed": 0.9,
        "pitch": -10,
    },
    "chief": {
        "provider": "fish_audio",
        "voice_id": "cn_male_authority",  # 权威男性音色
        "speed": 1.0,
        "pitch": -5,
    },
}

# 情感修改参数（影响速度和音高）
EMOTION_PARAMS = {
    "fearful": {"speed_delta": 1.1, "pitch_delta": 10},
    "determined": {"speed_delta": 0.95, "pitch_delta": -5},
    "angry": {"speed_delta": 1.15, "pitch_delta": 15},
    "sad": {"speed_delta": 0.85, "pitch_delta": -10},
    "wonder": {"speed_delta": 1.05, "pitch_delta": 5},
    "confusion": {"speed_delta": 1.0, "pitch_delta": 0},
}


def get_voice_config(character: str, episode_id: str) -> dict:
    """获取角色的声音配置"""
    # 尝试从 episodes/{ep}/characters.json 加载自定义配置
    custom_config_path = Path(f"episodes/{episode_id}/characters.json")
    if custom_config_path.exists():
        with open(custom_config_path) as f:
            custom_config = json.load(f)
            if character in custom_config:
                return {**CHARACTER_VOICES.get(character, {}), **custom_config[character]}

    return CHARACTER_VOICES.get(character, CHARACTER_VOICES["fuxi"])


class FishAudioTTS:
    """Fish Audio TTS 集成"""

    API_KEY = os.getenv("FISH_AUDIO_API_KEY")
    ENDPOINT = "https://api.fish.audio/v1/tts"

    @classmethod
    def synthesize(
        cls,
        text: str,
        voice_id: str,
        output_path: Path,
        speed: float = 1.0,
        pitch: int = 0,
    ) -> bool:
        """使用 Fish Audio 合成语音"""
        if not cls.API_KEY:
            print("  ⚠ FISH_AUDIO_API_KEY not set, falling back to placeholder")
            return False

        try:
            import requests  # 可选依赖

            response = requests.post(
                cls.ENDPOINT,
                json={
                    "text": text,
                    "voice_id": voice_id,
                    "speed": speed,
                    "pitch": pitch,
                },
                headers={"Authorization": f"Bearer {cls.API_KEY}"},
                timeout=30,
            )

            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"    ✓ Generated via Fish Audio")
                return True
            else:
                print(f"    ✗ Fish Audio API error: {response.status_code}")
                return False
        except ImportError:
            print("    ⚠ requests library not installed, skipping Fish Audio")
            return False
        except Exception as e:
            print(f"    ✗ Fish Audio error: {e}")
            return False


class EdgeTTS:
    """Microsoft Edge TTS 集成（免费离线选项）"""

    @staticmethod
    def synthesize(
        text: str,
        output_path: Path,
        lang: str = "zh-CN",
        voice: str = "zh-CN-YunxiNeural",
        speed: float = 1.0,
    ) -> bool:
        """使用 edge-tts 合成"""
        try:
            import edge_tts
            import asyncio

            async def _synthesize():
                communicate = edge_tts.Communicate(
                    text=text, voice=voice, rate=int((speed - 1) * 50)
                )
                await communicate.save(str(output_path))

            asyncio.run(_synthesize())
            print(f"    ✓ Generated via Edge TTS")
            return True

        except ImportError:
            print("    ⚠ edge-tts not installed")
            return False
        except Exception as e:
            print(f"    ✗ Edge TTS error: {e}")
            return False


def generate_silence_wav(filepath: Path, duration_s: float) -> None:
    """生成指定时长的静音 WAV（占位用）"""
    cmd = (
        f'ffmpeg -y -f lavfi -i anullsrc=r={SAMPLE_RATE}:cl=mono '
        f'-t {duration_s} "{filepath}"'
    )
    subprocess.run(cmd, shell=True, capture_output=True)


def synthesize_line(
    text: str,
    character: str,
    emotion: str,
    output_path: Path,
    duration_s: float,
    episode_id: str = "ep001",
) -> None:
    """
    合成单句台词音频。

    Args:
        text: 台词文本
        character: 角色名称
        emotion: 情绪标签
        output_path: 输出 WAV 路径
        duration_s: 目标时长
        episode_id: 剧集 ID（用于加载自定义配置）
    """
    print(f'  [TTS] {output_path.name}: "{text}"')
    print(f'        character={character}, emotion={emotion}, {duration_s}s')

    # 获取声音配置
    voice_config = get_voice_config(character, episode_id)
    provider = voice_config.get("provider", "fish_audio")

    # 应用情感修改
    speed = voice_config.get("speed", 1.0)
    pitch = voice_config.get("pitch", 0)

    if emotion in EMOTION_PARAMS:
        emotion_mod = EMOTION_PARAMS[emotion]
        speed *= emotion_mod.get("speed_delta", 1.0)
        pitch += emotion_mod.get("pitch_delta", 0)

    # 尝试不同的 TTS 提供商
    success = False

    if provider == "fish_audio":
        success = FishAudioTTS.synthesize(
            text,
            voice_id=voice_config.get("voice_id", "cn_male_youthful"),
            output_path=output_path,
            speed=speed,
            pitch=pitch,
        )

    if not success:
        # 降级：尝试 Edge TTS
        success = EdgeTTS.synthesize(
            text,
            output_path=output_path,
            speed=speed,
        )

    if not success:
        # 最终降级：占位符
        print(f"        -> Placeholder: generating {duration_s}s silence")
        generate_silence_wav(output_path, duration_s)


def synthesize_narration(
    text: str, output_path: Path, duration_s: float, episode_id: str = "ep001"
) -> None:
    """
    合成旁白音频（使用独立旁白音色）。
    """
    print(f'  [旁白] {output_path.name}: "{text}" ({duration_s}s)')

    narration_config = {
        "provider": "fish_audio",
        "voice_id": "cn_male_narration",  # 专用旁白音色
        "speed": 1.0,
        "pitch": 0,
    }

    success = False

    if narration_config["provider"] == "fish_audio":
        success = FishAudioTTS.synthesize(
            text,
            voice_id=narration_config.get("voice_id"),
            output_path=output_path,
            speed=narration_config.get("speed", 1.0),
        )

    if not success:
        success = EdgeTTS.synthesize(text, output_path=output_path)

    if not success:
        print(f"        -> Placeholder: generating {duration_s}s silence")
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

        # 从shots中获取角色信息，如果没有则使用第一个角色
        shot = next((s for s in shots_data["shots"] if s["shot_id"] == d["shot_id"]), {})
        character = d.get("characters", [None])[0] or "fuxi"

        synthesize_line(
            text=d["dialogue"],
            character=character,
            emotion=d["emotion"],
            output_path=audio_path,
            duration_s=d["duration_s"],
            episode_id=episode_id,
        )
        generated.append(audio_path)

    # 处理旁白和机械音（从 sfx_bgm 字段提取）
    for shot in shots_data["shots"]:
        sfx = shot.get("sfx_bgm", "")
        if "旁白" in sfx or "voice" in sfx.lower():
            narration_text = sfx.split("'")[1] if "'" in sfx else sfx
            audio_path = get_shot_audio_path(episode_id, f"{shot['shot_id']}_narration")
            audio_path.parent.mkdir(parents=True, exist_ok=True)
            synthesize_narration(narration_text, audio_path, shot["duration_s"], episode_id)
            generated.append(audio_path)

    print(f"\n共生成 {len(generated)} 个音频文件")
    return generated


if __name__ == "__main__":
    import sys

    episode = sys.argv[1] if len(sys.argv) > 1 else "ep001"
    process_episode(episode)
