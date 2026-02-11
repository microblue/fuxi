"""
伏羲纪元 — 字幕生成模块

从 shots.json 提取台词和字幕，生成 SRT/VTT 字幕文件。
规则：
- 单行 ≤16 中文字符
- 时间严格对齐镜头时间（支持从实际音频获取时长）
- 不遮挡关键信息（通过位置标注控制）
"""

import subprocess
import sys
from pathlib import Path

# 确保 pipeline 目录在路径中
_pipeline_dir = Path(__file__).parent
if str(_pipeline_dir) not in sys.path:
    sys.path.insert(0, str(_pipeline_dir))

from utils import (
    format_timecode,
    get_episode_dir,
    load_shots,
)

# 中文字幕规则：每行 ≤16 字
MAX_LINE_LENGTH = 16

# 中文标点符号（优先在这些位置断行）
PUNCTUATION = "，。！？、；：……—""''"
# 不应在这些字符前断行
NO_BREAK_BEFORE = "，。！？、；：……—）】」'\"'"


def get_audio_duration(audio_path: Path) -> float | None:
    """获取音频文件时长（秒）"""
    if not audio_path.exists():
        return None
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "csv=p=0",
                str(audio_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except Exception:
        pass
    return None


def collect_subtitles_from_shots(shots_data: dict, episode_id: str) -> list[dict]:
    """
    从 shots.json 提取所有需要字幕的对话。
    
    - 正确处理 dialogue 数组格式
    - 尝试从实际音频获取时长做时间对齐
    - 如无音频则使用 shots.json 中的 duration_s
    """
    subtitles = []
    cumulative_time = 0.0
    ep_dir = get_episode_dir(episode_id)
    audio_dir = ep_dir / "audio"
    
    for shot in shots_data["shots"]:
        shot_id = shot["shot_id"]
        shot_duration = shot.get("duration_s", 3)
        
        # 检查是否有 subtitle 字段（优先）或 dialogue 字段
        subtitle_text = shot.get("subtitle")
        dialogues = shot.get("dialogue", [])
        
        # 如果有 subtitle 字段，直接使用
        if subtitle_text and isinstance(subtitle_text, str):
            subtitles.append({
                "shot_id": shot_id,
                "text": subtitle_text,
                "character": None,
                "start_s": cumulative_time,
                "end_s": cumulative_time + shot_duration,
            })
        
        # 处理 dialogue 数组
        elif dialogues and isinstance(dialogues, list):
            # 尝试获取实际音频时长
            audio_duration = None
            for ext in [".wav", ".mp3"]:
                audio_path = audio_dir / f"{shot_id}{ext}"
                audio_duration = get_audio_duration(audio_path)
                if audio_duration:
                    break
            
            # 计算每条对话的时长分配
            total_chars = sum(len(d.get("text", "")) for d in dialogues if isinstance(d, dict))
            actual_duration = audio_duration or shot_duration
            
            # 为每条对话分配时间
            local_time = cumulative_time
            for d in dialogues:
                if not isinstance(d, dict):
                    continue
                text = d.get("text", "")
                if not text:
                    continue
                    
                character = d.get("character", "")
                # 根据字符数按比例分配时长
                char_ratio = len(text) / total_chars if total_chars > 0 else 1
                line_duration = actual_duration * char_ratio
                # 最小时长 0.5 秒
                line_duration = max(line_duration, 0.5)
                
                subtitles.append({
                    "shot_id": shot_id,
                    "text": text,
                    "character": character,
                    "start_s": local_time,
                    "end_s": local_time + line_duration,
                })
                local_time += line_duration
        
        cumulative_time += shot_duration
    
    return subtitles


def split_subtitle_line(text: str, max_length: int = MAX_LINE_LENGTH) -> list[str]:
    """
    将超长字幕拆分为多行。
    
    规则：
    - 每行不超过 max_length 个字符（默认16字）
    - 优先在句末标点（。！？）后断行
    - 次优先在逗号、顿号后断行
    - 避免把数字和单位（如 0.03%）拆开
    - 避免单个标点在行首
    """
    if len(text) <= max_length:
        return [text]
    
    # 句末标点（强断点）
    STRONG_PUNCT = '。！？'
    # 句中标点（弱断点）
    WEAK_PUNCT = '，、；：'
    # 不应出现在行首的字符
    NO_START = '%。！？，、；：）】」』"》……—'
    
    lines = []
    start = 0
    
    while start < len(text):
        # 如果剩余文本不超过 max_length，直接加入
        if len(text) - start <= max_length:
            lines.append(text[start:])
            break
        
        # 在 [start, start+max_length] 范围内找最佳断点
        end = min(start + max_length, len(text))
        segment = text[start:end]
        
        # 从后往前找断点
        best_pos = -1
        best_priority = 0
        
        # 寻找强断点（句末标点）
        for i in range(len(segment) - 1, len(segment) // 3, -1):
            c = segment[i]
            # 检查断点后的字符是否可以做行首
            next_idx = start + i + 1
            if next_idx < len(text) and text[next_idx] in NO_START:
                continue  # 跳过，这个位置不适合断行
            
            if c in STRONG_PUNCT:
                best_pos = i + 1
                best_priority = 3
                break
            elif c in WEAK_PUNCT and best_priority < 2:
                best_pos = i + 1
                best_priority = 2
        
        if best_pos > 0:
            lines.append(segment[:best_pos])
            start = start + best_pos
        else:
            # 没找到好的断点，强制在 max_length 处断
            # 但要检查是否会把不该拆的东西拆开
            break_at = len(segment)
            
            # 检查下一个字符
            next_idx = start + break_at
            while next_idx < len(text) and text[next_idx] in NO_START:
                # 把这些字符也带上
                break_at += 1
                next_idx += 1
                if break_at > max_length + 3:  # 最多多带3个字符
                    break
            
            lines.append(text[start:start + break_at])
            start = start + break_at
    
    return lines


def format_timecode_vtt(seconds: float) -> str:
    """秒数转 VTT 时间码格式 HH:MM:SS.mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def generate_srt(episode_id: str) -> Path:
    """生成 SRT 字幕文件"""
    print(f"\n{'=' * 60}")
    print(f"字幕生成 — {episode_id} (SRT)")
    print(f"{'=' * 60}")

    shots_data = load_shots(episode_id)
    subtitles = collect_subtitles_from_shots(shots_data, episode_id)

    ep_dir = get_episode_dir(episode_id)
    srt_path = ep_dir / "video" / "subtitles.srt"
    srt_path.parent.mkdir(parents=True, exist_ok=True)

    srt_entries = []
    idx = 1

    for sub in subtitles:
        lines = split_subtitle_line(sub["text"])
        text_block = "\n".join(lines)
        start_tc = format_timecode(sub["start_s"])
        end_tc = format_timecode(sub["end_s"])

        entry = f"{idx}\n{start_tc} --> {end_tc}\n{text_block}\n"
        srt_entries.append(entry)
        
        char_info = f"[{sub['character']}] " if sub.get('character') else ""
        print(f"  [{sub['shot_id']}] {char_info}{start_tc} -> {end_tc}: {sub['text'][:30]}{'...' if len(sub['text']) > 30 else ''}")
        idx += 1

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))

    print(f"\n✅ SRT 字幕文件已生成: {srt_path}")
    print(f"   共 {len(srt_entries)} 条字幕")
    return srt_path


def generate_vtt(episode_id: str) -> Path:
    """生成 VTT 字幕文件"""
    print(f"\n{'=' * 60}")
    print(f"字幕生成 — {episode_id} (VTT)")
    print(f"{'=' * 60}")

    shots_data = load_shots(episode_id)
    subtitles = collect_subtitles_from_shots(shots_data, episode_id)

    ep_dir = get_episode_dir(episode_id)
    vtt_path = ep_dir / "video" / "subtitles.vtt"
    vtt_path.parent.mkdir(parents=True, exist_ok=True)

    vtt_entries = ["WEBVTT", ""]  # VTT 文件头

    for i, sub in enumerate(subtitles, 1):
        lines = split_subtitle_line(sub["text"])
        text_block = "\n".join(lines)
        start_tc = format_timecode_vtt(sub["start_s"])
        end_tc = format_timecode_vtt(sub["end_s"])

        # VTT 可以有可选的 cue identifier
        entry = f"{i}\n{start_tc} --> {end_tc}\n{text_block}\n"
        vtt_entries.append(entry)

    with open(vtt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(vtt_entries))

    print(f"\n✅ VTT 字幕文件已生成: {vtt_path}")
    print(f"   共 {len(subtitles)} 条字幕")
    return vtt_path


def generate_subtitles(episode_id: str, formats: list[str] = None) -> dict[str, Path]:
    """
    生成字幕文件（支持多种格式）
    
    Args:
        episode_id: 剧集 ID
        formats: 要生成的格式列表，默认 ["srt", "vtt"]
    
    Returns:
        格式到文件路径的映射
    """
    if formats is None:
        formats = ["srt", "vtt"]
    
    results = {}
    
    if "srt" in formats:
        results["srt"] = generate_srt(episode_id)
    
    if "vtt" in formats:
        results["vtt"] = generate_vtt(episode_id)
    
    return results


def generate_ass(episode_id: str) -> Path:
    """
    生成 ASS 字幕文件（高级格式，支持样式控制）

    TODO: 实现完整的 ASS 格式输出，支持：
    - 金句高亮样式
    - 字幕位置控制
    - 字体/颜色/描边设置
    """
    print("  [ASS] 高级字幕格式暂未实现，使用 SRT 替代")
    return generate_srt(episode_id)


if __name__ == "__main__":
    import sys

    episode = sys.argv[1] if len(sys.argv) > 1 else "ep001"
    
    # 支持命令行指定格式
    # 用法: python -m pipeline.build_subtitles ep001 [srt|vtt|both]
    format_arg = sys.argv[2] if len(sys.argv) > 2 else "both"
    
    if format_arg == "srt":
        generate_srt(episode)
    elif format_arg == "vtt":
        generate_vtt(episode)
    else:
        generate_subtitles(episode, ["srt", "vtt"])
