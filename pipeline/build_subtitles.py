"""
伏羲纪元 — 字幕生成模块

从 shots.json 提取台词和字幕，生成 SRT 字幕文件。
规则：
- 单行 ≤16 中文字符
- 时间严格对齐镜头时间
- 不遮挡关键信息（通过位置标注控制）
"""

from pathlib import Path

from utils import (
    collect_subtitles,
    format_timecode,
    get_episode_dir,
    load_shots,
)

SUBTITLE_FONTSIZE = 40  # burn_subtitles force_style FontSize
SCREEN_WIDTH = 1080
MAX_LINE_LENGTH = SCREEN_WIDTH * 2 // 3 // SUBTITLE_FONTSIZE  # 2/3 屏宽换行 → 18 字符


def split_subtitle_line(text: str) -> list[str]:
    """将超长字幕拆分为多行，每行不超过 MAX_LINE_LENGTH 个字符（2/3 屏宽）"""
    if len(text) <= MAX_LINE_LENGTH:
        return [text]

    lines = []
    # 优先在标点处断行
    punctuation = "，。！？、；：……—"
    current = ""
    for char in text:
        current += char
        if len(current) >= MAX_LINE_LENGTH or (
            char in punctuation and len(current) > MAX_LINE_LENGTH // 2
        ):
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    return lines


def generate_srt(episode_id: str) -> Path:
    """生成 SRT 字幕文件"""
    print(f"\n{'=' * 60}")
    print(f"字幕生成 — {episode_id}")
    print(f"{'=' * 60}")

    shots_data = load_shots(episode_id)
    subtitles = collect_subtitles(shots_data)

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
        print(f"  [{sub['shot_id']}] {start_tc} -> {end_tc}: {sub['text']}")
        idx += 1

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))

    print(f"\n字幕文件已生成: {srt_path}")
    print(f"共 {len(srt_entries)} 条字幕")
    return srt_path


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
    generate_srt(episode)
