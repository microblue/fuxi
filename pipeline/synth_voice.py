"""
伏羲纪元 — 语音合成模块

使用 creative_toolkit 的 TTS 引擎生成配音。

支持:
- Fish Audio (推荐) - 高质量中文 TTS
- Edge TTS - 免费离线选项
- 本地或远程部署
"""

import asyncio
import json
import subprocess
from pathlib import Path

from creative_toolkit.voice import EdgeTTS, FishTTS, TTSEngine

from pipeline.utils import collect_dialogues, get_shot_audio_path, load_shots


# 英文角色名到中文名称的映射
CHARACTER_CHINESE_NAMES = {
    "xihe": "羲和",
    "observer_ai": "观测者AI",
    "fuxi_mother": "羲和母亲",
    "elder_woman": "老妇人",
    "shaman": "萨满",
    "chief": "族长",
    "hunter_a": "猎人甲",
    "hunter_b": "猎人乙",
    "hunter_c": "猎人丙",
    "young_fuxi": "年轻伏羲",
    "nüwa": "女娲",
}


def extract_dialogue_for_character(
    dialogue_data: str | list,
    character: str = None,
) -> tuple[str, str, float]:
    """从对话数据中提取指定角色的对白、语气和语速。

    支持两种格式：
    1. 字符串: "角色名：对白内容" 或多行（不支持语速）
    2. 数组: [{"character": "...", "text": "...", "emotion": "...", "speed": 1.0}, ...]

    Args:
        dialogue_data: 对话数据（字符串或列表）
        character: 目标角色名（支持英文或中文）

    Returns:
        tuple: (对白文本, 情感标签, 语速倍数)
    """
    if not dialogue_data:
        return "", "", 1.0

    # 处理数组格式（新格式）
    if isinstance(dialogue_data, list):
        for item in dialogue_data:
            if isinstance(item, dict):
                item_char = item.get("character", "")
                if character:
                    if item_char.lower() == character.lower() or \
                       item_char.replace("_", " ").lower() == character.lower().replace("_", " "):
                        text = item.get("text", "")
                        emotion = item.get("emotion", "")
                        speed = item.get("speed", 1.0)
                        return text, emotion, speed
                else:
                    # 如果未指定角色，返回第一个对话项
                    text = item.get("text", "")
                    emotion = item.get("emotion", "")
                    speed = item.get("speed", 1.0)
                    return text, emotion, speed
        return "", "", 1.0

    # 处理字符串格式（旧格式：兼容性）
    if isinstance(dialogue_data, str):
        lines = dialogue_data.split("\n")

        # 如果指定了字符，尝试获取其中文名称
        target_chinese_name = None
        if character:
            target_chinese_name = CHARACTER_CHINESE_NAMES.get(character.lower())

        for line in lines:
            if "：" in line:
                parts = line.split("：", 1)
                char_name = parts[0].strip()
                content = parts[1].strip() if len(parts) > 1 else ""

                if character:
                    # 尝试英文名称匹配
                    if char_name.lower() == character.lower() or \
                       char_name.replace("_", " ").lower() == character.lower().replace("_", " "):
                        return content, "", 1.0
                    # 尝试中文名称匹配
                    if target_chinese_name and char_name == target_chinese_name:
                        return content, "", 1.0
                else:
                    # 如果未指定角色，返回第一行的对白
                    return content, "", 1.0

    return "", "", 1.0


def _convert_mp3_to_wav(mp3_path: Path, wav_path: Path) -> None:
    """Convert MP3 to WAV using FFmpeg."""
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(mp3_path),
        "-acodec", "pcm_s16le",
        "-ar", "24000",
        "-ac", "1",
        str(wav_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")


class EdgeTTSWrapper(EdgeTTS):
    """Wrapper around EdgeTTS that uses FFmpeg for MP3->WAV conversion."""

    async def synthesize(
        self,
        text: str,
        voice_id: str,
        output_path: Path,
        emotion: str = "",
    ) -> float:
        """Synthesize using Edge TTS, with FFmpeg-based MP3 to WAV conversion."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Always save as MP3 first
        mp3_path = output_path.with_suffix(".mp3")

        # Call parent's synthesize to save as MP3
        duration = await super().synthesize(
            text=text,
            voice_id=voice_id,
            output_path=mp3_path,
            emotion=emotion,
        )

        # Convert MP3 to WAV if needed
        if output_path.suffix.lower() == ".wav":
            _convert_mp3_to_wav(mp3_path, output_path)
            mp3_path.unlink()  # Delete temporary MP3

        return duration


# 角色配置（可在 episodes/{ep}/characters.json 中覆盖）
CHARACTER_VOICES = {
    "fuxi": {
        "provider": "fish",
        "voice_id": "default",  # Fish Audio voice ID
        "edge_voice_id": "zh-CN-YunyangNeural",  # Edge TTS fallback (male)
    },
    "fuxi_mother": {
        "provider": "fish",
        "voice_id": "default",
        "edge_voice_id": "zh-CN-XiaoxiaoNeural",  # Edge TTS female
    },
    "elder_woman": {
        "provider": "fish",
        "voice_id": "default",
        "edge_voice_id": "zh-CN-XiaoxiaoNeural",  # Edge TTS female
    },
    "shaman": {
        "provider": "fish",
        "voice_id": "default",
        "edge_voice_id": "zh-CN-YunjianNeural",  # Edge TTS male (deep voice)
    },
    "chief": {
        "provider": "fish",
        "voice_id": "default",
        "edge_voice_id": "zh-CN-YunyangNeural",  # Edge TTS male
    },
    "observer_ai": {
        "provider": "fish",
        "voice_id": "default",
        "edge_voice_id": "zh-CN-XiaoxiaoNeural",  # Edge TTS female for AI
    },
    "hunter_a": {
        "provider": "fish",
        "voice_id": "default",
        "edge_voice_id": "zh-CN-YunyangNeural",
    },
    "hunter_b": {
        "provider": "fish",
        "voice_id": "default",
        "edge_voice_id": "zh-CN-YunyangNeural",
    },
    "hunter_c": {
        "provider": "fish",
        "voice_id": "default",
        "edge_voice_id": "zh-CN-YunyangNeural",
    },
    "young_fuxi": {
        "provider": "fish",
        "voice_id": "default",
        "edge_voice_id": "zh-CN-YunyangNeural",
    },
    "nüwa": {
        "provider": "fish",
        "voice_id": "default",
        "edge_voice_id": "zh-CN-XiaoxiaoNeural",
    },
}

# 情感映射到 TTS 引擎支持的情感
EMOTION_MAP = {
    "fearful": "scared",
    "determined": "determined",
    "angry": "angry",
    "sad": "sad",
    "wonder": "curious",
    "confusion": "curious",
    "terror": "scared",
    "fear": "scared",
    "awe": "curious",
    "concern": "gentle",
    "brave": "brave",
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


async def synthesize_dialogue(
    text: str,
    character: str,
    emotion: str,
    output_path: Path,
    episode_id: str = "ep001",
    provider: str = "fish",
    tts_engine: TTSEngine | None = None,
) -> bool:
    """生成单句台词音频。

    Args:
        text: 台词文本
        character: 角色名称
        emotion: 情感标签
        output_path: 输出 WAV 路径
        episode_id: 剧集 ID
        provider: TTS 提供商 ('fish' 或 'edge')
        tts_engine: TTS 引擎实例（如不提供则自动创建）

    Returns:
        是否成功生成
    """
    if not tts_engine:
        # 默认使用指定的提供商
        if provider == "edge":
            tts_engine = EdgeTTSWrapper()
        else:
            tts_engine = FishTTS(api_base="http://localhost:8081")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    voice_config = get_voice_config(character, episode_id)

    # 根据提供商选择合适的 voice_id
    if provider == "edge":
        voice_id = voice_config.get("edge_voice_id", "zh-CN-XiaoxiaoNeural")
    else:
        voice_id = voice_config.get("voice_id", "default")

    # 映射情感
    mapped_emotion = EMOTION_MAP.get(emotion.lower(), emotion.lower())

    try:
        duration = await tts_engine.synthesize(
            text=text,
            voice_id=voice_id,
            output_path=output_path,
            emotion=mapped_emotion,
        )
        print(f'  ✓ {output_path.name}: {duration:.1f}s ({character})')
        return True
    except Exception as e:
        print(f"  ✗ Failed to synthesize: {e}")
        return False


async def synthesize_narration(
    text: str,
    output_path: Path,
    provider: str = "fish",
    tts_engine: TTSEngine | None = None,
) -> bool:
    """生成旁白音频。

    Args:
        text: 旁白文本
        output_path: 输出 WAV 路径
        provider: TTS 提供商 ('fish' 或 'edge')
        tts_engine: TTS 引擎实例

    Returns:
        是否成功生成
    """
    if not tts_engine:
        if provider == "edge":
            tts_engine = EdgeTTSWrapper()
        else:
            tts_engine = FishTTS(api_base="http://localhost:8081")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 旁白使用默认女性声音
    voice_id = "zh-CN-XiaoxiaoNeural" if provider == "edge" else "default"

    try:
        duration = await tts_engine.synthesize(
            text=text,
            voice_id=voice_id,
            output_path=output_path,
            emotion="gentle",
        )
        print(f'  ✓ 旁白: {output_path.name}: {duration:.1f}s')
        return True
    except Exception as e:
        print(f"  ✗ Failed to synthesize narration: {e}")
        return False


async def process_episode(episode_id: str, provider: str = "fish") -> list[Path]:
    """为整集生成所有语音音频。

    Args:
        episode_id: 剧集 ID
        provider: TTS 提供商 ('fish' 或 'edge')

    Returns:
        生成的音频文件列表
    """
    print(f"\n{'=' * 60}")
    print(f"语音合成 — {episode_id} (provider: {provider})")
    print(f"{'=' * 60}\n")

    # 创建 TTS 引擎
    if provider == "edge":
        tts_engine = EdgeTTSWrapper()
    else:
        tts_engine = FishTTS(api_base="http://localhost:8081")

    shots_data = load_shots(episode_id)
    dialogues = collect_dialogues(shots_data)
    generated = []

    # 生成对话
    for d in dialogues:
        audio_path = get_shot_audio_path(episode_id, d["shot_id"])

        # 获取角色信息
        character = (d.get("characters") or [None])[0] or "fuxi"
        emotion = d.get("emotion", "normal")

        # 原始对话可能包含多个角色，需要解析格式
        raw_dialogue = d.get("dialogue", "")

        # 提取指定角色的对白、情感和语速
        dialogue_text, dialogue_emotion, dialogue_speed = extract_dialogue_for_character(raw_dialogue, character)

        # 如果从对话中提取了情感，优先使用对话中的情感
        if dialogue_emotion:
            emotion = dialogue_emotion

        # 注：语速 (dialogue_speed) 可在未来扩展时用于调整 TTS 参数

        success = await synthesize_dialogue(
            text=dialogue_text,
            character=character,
            emotion=emotion,
            output_path=audio_path,
            episode_id=episode_id,
            provider=provider,
            tts_engine=tts_engine,
        )

        if success:
            generated.append(audio_path)

    # 生成旁白
    for shot in shots_data["shots"]:
        sfx = shot.get("sfx_bgm", "")
        if "旁白" in sfx or "narration" in sfx.lower():
            narration_text = sfx.split("'")[1] if "'" in sfx else sfx
            audio_path = get_shot_audio_path(episode_id, f"{shot['shot_id']}_narration")

            success = await synthesize_narration(
                text=narration_text,
                output_path=audio_path,
                provider=provider,
                tts_engine=tts_engine,
            )

            if success:
                generated.append(audio_path)

    print(f"\n共生成 {len(generated)} 个音频文件\n")
    return generated


async def generate_shot_audio(
    episode_id: str,
    shot_id: str,
    provider: str = "fish",
) -> Path | None:
    """为单个镜头生成音频。

    Args:
        episode_id: 剧集 ID (e.g., "ep001")
        shot_id: 镜头 ID (e.g., "S03")
        provider: TTS 提供商 ('fish' 或 'edge')

    Returns:
        生成的音频文件路径，如果未找到对话则返回None
    """
    print(f"\n{'=' * 60}")
    print(f"生成单镜头配音 — {episode_id} {shot_id} (provider: {provider})")
    print(f"{'=' * 60}\n")

    # 创建 TTS 引擎
    if provider == "edge":
        tts_engine = EdgeTTSWrapper()
    else:
        tts_engine = FishTTS(api_base="http://localhost:8081")

    shots_data = load_shots(episode_id)

    # 找到指定的镜头
    shot = None
    for s in shots_data["shots"]:
        if s["shot_id"] == shot_id:
            shot = s
            break

    if not shot:
        print(f"✗ 未找到镜头: {shot_id}")
        return None

    # 检查是否有对话
    raw_dialogue = shot.get("dialogue", "")
    if not raw_dialogue:
        print(f"✗ 镜头 {shot_id} 没有对话")
        return None

    # 获取角色和情感信息
    characters = shot.get("characters", [])
    character = characters[0] if characters else "fuxi"
    emotion = shot.get("emotion", "normal")

    # 解析对话格式，去掉角色名，并提取情感和语速
    dialogue_text, dialogue_emotion, dialogue_speed = extract_dialogue_for_character(raw_dialogue, character)

    if not dialogue_text:
        print(f"✗ 镜头 {shot_id} 中未找到角色 {character} 的对白")
        return None

    # 如果从对话中提取了情感，优先使用对话中的情感
    if dialogue_emotion:
        emotion = dialogue_emotion

    # 注：语速 (dialogue_speed) 可在未来扩展时用于调整 TTS 参数

    # 生成音频
    audio_path = get_shot_audio_path(episode_id, shot_id)

    success = await synthesize_dialogue(
        text=dialogue_text,
        character=character,
        emotion=emotion,
        output_path=audio_path,
        episode_id=episode_id,
        provider=provider,
        tts_engine=tts_engine,
    )

    if success:
        print(f"\n✅ 成功生成: {audio_path}")
        return audio_path
    else:
        print(f"\n❌ 生成失败: {shot_id}")
        return None


def main():
    """命令行入口"""
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m pipeline.synth_voice ep001                    # 生成整集")
        print("  python -m pipeline.synth_voice ep001 fish               # 指定provider")
        print("  python -m pipeline.synth_voice ep001 fish S03           # 生成单镜头")
        sys.exit(1)

    episode = sys.argv[1]
    provider = sys.argv[2] if len(sys.argv) > 2 else "fish"
    shot_id = sys.argv[3] if len(sys.argv) > 3 else None

    if shot_id:
        # 生成单镜头
        asyncio.run(generate_shot_audio(episode, shot_id, provider))
    else:
        # 生成整集
        asyncio.run(process_episode(episode, provider))


if __name__ == "__main__":
    main()
