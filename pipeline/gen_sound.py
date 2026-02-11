"""
伏羲纪元 — 完整声音生成管道

为整集生成和混合所有音轨：
1. 生成配音（对话 + 旁白）
2. 处理音效和 BGM
3. 混合多轨音频为最终输出

Usage:
    python -m pipeline.gen_sound ep002
    python -m pipeline.gen_sound ep002 --provider edge
    python -m pipeline.gen_sound ep002 --provider fish --local
"""

import argparse
import asyncio
from pathlib import Path

from creative_toolkit.ffmpeg.audio import AudioMixer, AudioTrack

from pipeline.manage_sfx import SFXLibrary, SFXParser
from pipeline.synth_voice import (
    process_episode as process_dialogues,
    generate_shot_audio,
    extract_dialogue_for_character,
)
from pipeline.utils import get_episode_dir, load_shots, collect_dialogues


def _find_character_reference_audio(
    episode_id: str,
    character: str,
) -> Path | None:
    """查找角色的参考音频。

    Args:
        episode_id: 剧集 ID
        character: 角色名

    Returns:
        参考音频路径，如果找不到则返回 None
    """
    ep_dir = get_episode_dir(episode_id)
    audio_dir = ep_dir / "audio"

    # 查找该角色的参考音频文件
    # 优先级：reference_{character}.wav > {character}_reference.wav
    for pattern in [f"reference_{character.lower()}.wav", f"{character.lower()}_reference.wav"]:
        ref_audio = audio_dir / pattern
        if ref_audio.exists():
            return ref_audio

    return None


async def generate_all_sound(
    episode_id: str,
    provider: str = "fish",
    output_dir: Path | None = None,
) -> Path:
    """为整集生成完整的声音（配音 + 音效 + BGM）。

    根据 shots.json 中的对话参数（emotion、speed）生成不同风格的音频。
    如果存在角色参考音频，可用于调整 TTS 的音色特性。

    Args:
        episode_id: 剧集 ID (e.g., "ep002")
        provider: TTS 提供商 ("fish" 或 "edge")
        output_dir: 输出目录（默认: episodes/{ep}/audio）

    Returns:
        生成的音频文件路径
    """
    ep_dir = get_episode_dir(episode_id)
    if output_dir is None:
        output_dir = ep_dir / "audio"

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 70}")
    print(f"🎵 完整声音生成 — {episode_id}")
    print(f"{'=' * 70}\n")

    # 加载 shots.json 以提取对话参数
    shots_data = load_shots(episode_id)
    dialogues = collect_dialogues(shots_data)

    # 统计对话参数信息（用于调试和日志）
    print("📋 对话参数统计:")
    emotions_count = {}
    speeds_count = {}
    for d in dialogues:
        emotion = d.get("emotion", "normal")
        emotions_count[emotion] = emotions_count.get(emotion, 0) + 1
        # 如果对话数据是新格式（数组），可以提取每句的速度
        raw_dialogue = d.get("dialogue", "")
        if isinstance(raw_dialogue, list):
            for item in raw_dialogue:
                if isinstance(item, dict):
                    speed = item.get("speed", 1.0)
                    speed_key = f"{speed}x"
                    speeds_count[speed_key] = speeds_count.get(speed_key, 0) + 1
    print(f"  • 情感分布: {emotions_count}")
    if speeds_count:
        print(f"  • 语速分布: {speeds_count}")
    print()

    # ============================================================
    # 步骤 1: 生成所有配音（对话 + 旁白）
    # ============================================================
    print("📝 [1/4] 生成配音（遵循 shots.json 参数）...\n")
    dialogue_files = await process_dialogues(episode_id, provider)

    if not dialogue_files:
        print("⚠️  未找到需要配音的镜头")
        return None

    # ============================================================
    # 步骤 2: 加载音效和 BGM 信息
    # ============================================================
    print("\n🎧 [2/4] 加载音效和 BGM...\n")

    sfx_list, bgm_list = SFXParser.parse_episode(episode_id)
    sfx_lib = SFXLibrary(episode_id)

    print(f"  • 音效: {len(sfx_list)} 条")
    print(f"  • BGM: {len(bgm_list)} 条")

    # ============================================================
    # 步骤 3: 构建混音器
    # ============================================================
    print("\n🎚️  [3/4] 构建音轨...\n")

    shots_data = load_shots(episode_id)
    mixer = AudioMixer()

    # 添加配音轨道
    cumulative_time = 0.0
    for shot in shots_data["shots"]:
        shot_id = shot["shot_id"]
        shot_duration = shot.get("duration_s", 3.0)

        # 查找该镜头的配音文件
        dialogue_path = output_dir / f"{shot_id}.wav"
        if dialogue_path.exists():
            mixer.add_track(
                AudioTrack(
                    track_id=f"dialogue_{shot_id}",
                    audio_path=dialogue_path,
                    start_time=cumulative_time,
                    volume=1.0,  # 配音总是 100% 音量
                    fade_in=0.0,
                    fade_out=0.0,
                    track_type="dialogue",
                )
            )
            print(f"  ✓ 添加配音: {shot_id}")

        # 添加 SFX（音效）
        for sfx in sfx_list:
            if sfx.effect_id.startswith(shot_id):
                # 获取音效文件（这里假设已手动或自动生成）
                sfx_path = sfx_lib.get_sfx_path(sfx.description.split()[0])
                if sfx_path and sfx_path.exists():
                    mixer.add_track(
                        AudioTrack(
                            track_id=sfx.effect_id,
                            audio_path=sfx_path,
                            start_time=cumulative_time + sfx.start_time,
                            volume=0.6,  # SFX 60%
                            track_type="sfx",
                        )
                    )
                    print(f"  ✓ 添加音效: {sfx.effect_id}")

        cumulative_time += shot_duration

    # 添加 BGM（背景音乐）
    for bgm in bgm_list:
        bgm_path = None  # 这里可以连接到真实的 BGM 库
        if bgm_path and bgm_path.exists():
            mixer.add_track(
                AudioTrack(
                    track_id=bgm.bgm_id,
                    audio_path=bgm_path,
                    start_time=bgm.start_time,
                    volume=bgm.volume,
                    fade_in=bgm.fade_in,
                    fade_out=bgm.fade_out,
                    track_type="bgm",
                )
            )
            print(f"  ✓ 添加 BGM: {bgm.bgm_id}")

    # ============================================================
    # 步骤 4: 执行混音
    # ============================================================
    print("\n🎛️  [4/4] 混合音轨...\n")

    output_audio = output_dir / f"{episode_id}_final_audio.wav"

    try:
        mixer.mix(output_audio)
        print(f"\n✅ 声音生成完成!")
        print(f"   输出文件: {output_audio}")
        print(f"   总轨道数: {len(mixer.tracks)}")
        print(f"   总时长: {mixer.total_duration:.1f}s\n")
        return output_audio
    except Exception as e:
        print(f"\n❌ 混音失败: {e}")
        return None


async def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="伏羲纪元 - 完整声音生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用 Fish Audio 生成声音
  python -m pipeline.gen_sound ep002

  # 使用 Edge TTS 生成声音
  python -m pipeline.gen_sound ep002 --provider edge

  # 指定输出目录
  python -m pipeline.gen_sound ep002 --output /path/to/output
        """,
    )

    parser.add_argument("episode", help="剧集 ID (e.g., ep002)")
    parser.add_argument(
        "--provider",
        default="fish",
        choices=["fish", "edge"],
        help="TTS 提供商 (默认: fish)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="输出目录 (默认: episodes/{ep}/audio)",
    )

    args = parser.parse_args()

    output_path = await generate_all_sound(
        episode_id=args.episode,
        provider=args.provider,
        output_dir=args.output,
    )

    if output_path:
        return 0
    else:
        return 1


if __name__ == "__main__":
    import sys

    exit_code = asyncio.run(main())
    sys.exit(exit_code)
