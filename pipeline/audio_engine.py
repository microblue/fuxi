"""
伏羲纪元 — 音频处理引擎

支持：
1. 多轨音频混合（配音、音效、BGM）
2. 动态音量和淡入淡出
3. 跨镜头音频衔接
4. 音频时间对齐

架构：
- 配音轨（dialogue）: 角色或旁白配音
- SFX 轨（sfx）: 环境音效、动作音效
- BGM 轨（bgm）: 背景音乐（可跨多个镜头）
- 总输出：混合后的立体声或单声道 WAV
"""

import subprocess
import sys
from pathlib import Path
from typing import Any


class AudioTrack:
    """单个音频轨道的定义"""
    def __init__(
        self,
        track_id: str,           # "dialogue_S01", "sfx_S01", "bgm_main"
        audio_path: Path,        # 音频文件路径
        start_time: float,       # 在总时间轴上的起始位置（秒）
        duration: float | None = None,  # 时长（None=使用原始）
        volume: float = 1.0,     # 音量倍数（0.0-1.0）
        fade_in: float = 0.0,    # 淡入时长（秒）
        fade_out: float = 0.0,   # 淡出时长（秒）
        track_type: str = "dialogue",  # dialogue/sfx/bgm
    ):
        self.track_id = track_id
        self.audio_path = audio_path
        self.start_time = start_time
        self.duration = duration
        self.volume = volume
        self.fade_in = fade_in
        self.fade_out = fade_out
        self.track_type = track_type

    def to_ffmpeg_filter(self) -> tuple[str, str]:
        """
        转换为 FFmpeg 滤镜片段。

        返回: (input_label, filter_spec)
        例如: ("[a:0]", "[a0_faded]aformat=sample_rates=44100[a0_faded]")
        """
        # 该函数由 AudioMixer 调用
        pass


class AudioMixer:
    """
    多轨音频混合器

    使用 FFmpeg 的高级滤镜链来：
    - 加载多个音频文件
    - 应用增益、淡入淡出
    - 时间对齐（使用 atrim 和 adelay）
    - 多轨混合（amix 滤镜）
    """

    def __init__(self, output_sample_rate: int = 44100):
        self.tracks: dict[str, AudioTrack] = {}
        self.output_sample_rate = output_sample_rate
        self.total_duration = 0.0

    def add_track(self, track: AudioTrack) -> None:
        """添加音频轨道"""
        self.tracks[track.track_id] = track
        # 更新总时长
        end_time = track.start_time + (track.duration or self._get_audio_duration(track.audio_path))
        self.total_duration = max(self.total_duration, end_time)

    @staticmethod
    def _get_audio_duration(audio_path: Path) -> float:
        """使用 ffprobe 获取音频时长"""
        cmd = (
            f'ffprobe -v error -show_entries format=duration '
            f'-of default=noprint_wrappers=1:nokey=1:novalidate=1 "{audio_path}"'
        )
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        try:
            return float(result.stdout.strip())
        except (ValueError, AttributeError):
            return 0.0

    def build_ffmpeg_command(self, output_path: Path) -> str:
        """
        构建完整的 FFmpeg 命令用于多轨混合。

        示例：
        ffmpeg -i dialogue.wav -i sfx.wav -i bgm.wav \
               -filter_complex "
               [0:a] aformat=sample_rates=44100 [a0];
               [1:a] aformat=sample_rates=44100 [a1];
               [2:a] aformat=sample_rates=44100 [a2];
               [a0] adelay=0|0 [a0d];
               [a1] adelay=2000|2000, volume=0.8 [a1d];
               [a2] adelay=1000|1000, volume=0.5, afade=t=in:st=1:d=2 [a2d];
               [a0d][a1d][a2d] amix=inputs=3:duration=longest [out]
               " \
               -map "[out]" output.wav
        """
        if not self.tracks:
            raise ValueError("No audio tracks added")

        # 1. 构建输入列表
        inputs = []
        input_labels = []
        for i, track_id in enumerate(sorted(self.tracks.keys())):
            track = self.tracks[track_id]
            inputs.append(f'-i "{track.audio_path}"')
            input_labels.append(f"[{i}:a]")

        input_str = " ".join(inputs)

        # 2. 构建滤镜链
        filter_parts = []
        delayed_labels = []

        for i, track_id in enumerate(sorted(self.tracks.keys())):
            track = self.tracks[track_id]

            # 格式化
            fmt_label = f"a{i}_fmt"
            filter_parts.append(f"{input_labels[i]} aformat=sample_rates={self.output_sample_rate} [{fmt_label}]")

            # 时间延迟（转换秒为毫秒）
            delay_ms = int(track.start_time * 1000)
            delay_label = f"a{i}_delayed"
            filter_parts.append(f"[{fmt_label}] adelay={delay_ms}|{delay_ms} [{delay_label}]")

            # 音量和淡入淡出
            processed_label = delay_label

            # 应用淡入
            if track.fade_in > 0:
                fade_in_label = f"a{i}_fadein"
                filter_parts.append(
                    f"[{processed_label}] afade=t=in:st={track.start_time}:d={track.fade_in} [{fade_in_label}]"
                )
                processed_label = fade_in_label

            # 应用淡出
            if track.fade_out > 0:
                fade_out_label = f"a{i}_fadeout"
                fade_out_start = track.start_time + (track.duration or self._get_audio_duration(track.audio_path)) - track.fade_out
                filter_parts.append(
                    f"[{processed_label}] afade=t=out:st={fade_out_start}:d={track.fade_out} [{fade_out_label}]"
                )
                processed_label = fade_out_label

            # 应用音量
            if track.volume != 1.0:
                volume_label = f"a{i}_volume"
                filter_parts.append(f"[{processed_label}] volume={track.volume} [{volume_label}]")
                processed_label = volume_label

            delayed_labels.append(f"[{processed_label}]")

        # 3. 混合所有轨道
        if len(delayed_labels) == 1:
            # 单轨，直接输出
            filter_parts.append(f"{delayed_labels[0]} [{delayed_labels[0][1:-1]}]")
            final_label = delayed_labels[0][1:-1]
        else:
            # 多轨混合
            mix_input = "".join(delayed_labels)
            final_label = "audio_out"
            filter_parts.append(
                f"{mix_input} amix=inputs={len(delayed_labels)}:duration=longest [{final_label}]"
            )

        filter_complex = ";".join(filter_parts)

        # 4. 构建完整命令
        cmd = (
            f'ffmpeg -y {input_str} '
            f'-filter_complex "{filter_complex}" '
            f'-map "[{final_label}]" '
            f'-c:a libmp3lame -q:a 4 '
            f'"{output_path}"'
        )
        return cmd

    def mix(self, output_path: Path) -> Path:
        """执行混合操作"""
        if not self.tracks:
            raise ValueError("No tracks to mix")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = self.build_ffmpeg_command(output_path)

        print(f"  [Audio Mix] Mixing {len(self.tracks)} tracks...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"  ✗ Audio mixing failed:\n{result.stderr}")
            sys.exit(1)

        print(f"  ✓ Mixed audio saved: {output_path}")
        return output_path


def create_silence(duration_s: float, output_path: Path, sample_rate: int = 44100) -> Path:
    """生成指定时长的静音音频"""
    cmd = (
        f'ffmpeg -y -f lavfi -i anullsrc=r={sample_rate}:cl=mono '
        f'-t {duration_s} "{output_path}"'
    )
    subprocess.run(cmd, shell=True, capture_output=True)
    return output_path


def create_audio_pad(audio_path: Path, pad_start: float, pad_end: float, output_path: Path) -> Path:
    """在音频前后补充静音"""
    cmd = (
        f'ffmpeg -y -i "{audio_path}" '
        f'-af "adelay={int(pad_start*1000)}|{int(pad_start*1000)}, '
        f'apad=whole_dur={pad_start + AudioMixer._get_audio_duration(audio_path) + pad_end}" '
        f'"{output_path}"'
    )
    subprocess.run(cmd, shell=True, capture_output=True)
    return output_path
