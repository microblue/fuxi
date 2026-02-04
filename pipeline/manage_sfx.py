"""
伏羲纪元 — 音效和背景音乐管理

从 shots.json 的 sfx_bgm 字段解析音效和背景音乐，
支持：
- 环境音效（ambient）：贯穿整个镜头
- 动作音效（action）：特定时间点
- 背景音乐（BGM）：可跨多个镜头，支持淡入淡出
- 旁白（narration）：独立轨道

示例 shots.json 格式：
{
  "shot_id": "S01",
  "duration_s": 4,
  "sfx_bgm": "SFX: footsteps, gasps; BGM: tribal_drums(intro=0.5s, fade_in=1s)"
}
"""

import re
import subprocess
from pathlib import Path
from typing import Any

from utils import get_episode_dir, load_shots


class SFXEntry:
    """单个音效条目"""

    def __init__(
        self,
        effect_id: str,           # "footstep_S01", "gasp_S01", etc.
        effect_type: str,         # "action" or "ambient"
        description: str,         # 描述
        start_time: float = 0.0,  # 相对于镜头开始的时间
        duration: float | None = None,  # 音效时长
    ):
        self.effect_id = effect_id
        self.effect_type = effect_type
        self.description = description
        self.start_time = start_time
        self.duration = duration
        self.audio_path = None  # 生成的音频文件


class BGMEntry:
    """背景音乐条目（可跨镜头）"""

    def __init__(
        self,
        bgm_id: str,              # "tribal_drums", "ominous_drone", etc.
        description: str,         # 描述
        start_time: float = 0.0,  # 全局时间轴上的开始
        duration: float | None = None,  # 总时长（None=贯穿整个剧集）
        fade_in: float = 0.0,     # 淡入时长
        fade_out: float = 0.0,    # 淡出时长
        volume: float = 1.0,      # 相对音量
    ):
        self.bgm_id = bgm_id
        self.description = description
        self.start_time = start_time
        self.duration = duration
        self.fade_in = fade_in
        self.fade_out = fade_out
        self.volume = volume
        self.audio_path = None


class SFXParser:
    """解析 sfx_bgm 字段的解析器"""

    @staticmethod
    def parse_shot_sfx(shot: dict, shot_start_time: float = 0.0) -> list[SFXEntry]:
        """
        从单个镜头的 sfx_bgm 字段提取所有音效。

        格式示例：
        "SFX: footsteps on dirt, gasps, scrambling sounds; BGM: ominous_drone"

        返回：[SFXEntry, SFXEntry, ...]
        """
        sfx_entries = []
        sfx_str = shot.get("sfx_bgm", "")

        if not sfx_str:
            return sfx_entries

        # 1. 分离 SFX 和 BGM 部分
        sfx_match = re.search(r"SFX:\s*([^;]*)", sfx_str, re.IGNORECASE)
        if sfx_match:
            sfx_part = sfx_match.group(1).strip()
            # 分割多个音效（逗号分隔）
            effects = [e.strip() for e in sfx_part.split(",")]
            for i, effect in enumerate(effects):
                if effect:
                    entry = SFXEntry(
                        effect_id=f"{shot['shot_id']}_sfx_{i}",
                        effect_type="action",
                        description=effect,
                        start_time=shot_start_time,
                        duration=shot.get("duration_s", 3.0),
                    )
                    sfx_entries.append(entry)

        return sfx_entries

    @staticmethod
    def parse_shot_bgm(shot: dict, shot_start_time: float = 0.0) -> list[BGMEntry]:
        """
        从单个镜头的 sfx_bgm 字段提取背景音乐。

        格式示例：
        "BGM: ominous_drone(start=0, fade_in=1, fade_out=0.5, volume=0.7)"

        返回：[BGMEntry, BGMEntry, ...]
        """
        bgm_entries = []
        sfx_str = shot.get("sfx_bgm", "")

        if not sfx_str:
            return bgm_entries

        # 2. 分离 BGM 部分
        bgm_match = re.search(r"BGM:\s*([^;]*)", sfx_str, re.IGNORECASE)
        if bgm_match:
            bgm_part = bgm_match.group(1).strip()
            # 可能有多个 BGM（逗号或 + 分隔）
            bgms = re.split(r"[,+]", bgm_part)

            for bgm in bgms:
                bgm = bgm.strip()
                if not bgm:
                    continue

                # 解析 bgm_id 和参数
                # 格式: "bgm_id" 或 "bgm_id(param1=val1, param2=val2)"
                match = re.match(r"(\w+)(?:\(([^)]*)\))?", bgm)
                if match:
                    bgm_id = match.group(1)
                    params_str = match.group(2) or ""

                    # 解析参数
                    params = {}
                    if params_str:
                        for param in params_str.split(","):
                            if "=" in param:
                                key, val = param.split("=")
                                key = key.strip()
                                val = val.strip()
                                try:
                                    params[key] = float(val)
                                except ValueError:
                                    params[key] = val

                    entry = BGMEntry(
                        bgm_id=bgm_id,
                        description=bgm,
                        start_time=shot_start_time + params.get("start", 0),
                        duration=params.get("duration"),
                        fade_in=params.get("fade_in", 0),
                        fade_out=params.get("fade_out", 0),
                        volume=params.get("volume", 1.0),
                    )
                    bgm_entries.append(entry)

        return bgm_entries

    @staticmethod
    def parse_episode(episode_id: str) -> tuple[list[SFXEntry], list[BGMEntry]]:
        """
        为整集解析所有音效和 BGM。

        返回: (sfx_list, bgm_list)
        """
        shots_data = load_shots(episode_id)
        all_sfx = []
        all_bgm = []

        cumulative_time = 0.0
        for shot in shots_data["shots"]:
            shot_duration = shot.get("duration_s", 3.0)

            # 解析该镜头的音效
            sfx_entries = SFXParser.parse_shot_sfx(shot, cumulative_time)
            all_sfx.extend(sfx_entries)

            # 解析该镜头的 BGM
            bgm_entries = SFXParser.parse_shot_bgm(shot, cumulative_time)
            all_bgm.extend(bgm_entries)

            cumulative_time += shot_duration

        return all_sfx, all_bgm


class SFXLibrary:
    """
    音效库管理器

    存储本地音效文件，支持按名称查找和生成。
    """

    def __init__(self, episode_id: str):
        self.episode_id = episode_id
        self.library_dir = get_episode_dir(episode_id) / "audio" / "sfx_library"
        self.library_dir.mkdir(parents=True, exist_ok=True)

        # 内置音效库
        self.builtin_sfx = {
            # 环境音效
            "ambient_wind": "environmental wind noise, medium intensity",
            "ambient_rain": "soft rain falling on leaves",
            "ambient_fire": "crackling fire and embers",
            "ambient_tribal_camp": "distant voices, animals, camp sounds",

            # 动作音效
            "footsteps_dirt": "footsteps on loose dirt, dry ground",
            "footsteps_leaves": "walking through dried leaves, crunching",
            "footsteps_grass": "soft footsteps on grass",
            "gasp_fear": "sharp intake of breath, fearful gasp",
            "gasp_shock": "surprised gasp",
            "scream_woman": "high-pitched scream, female voice",
            "scream_terror": "primal scream of terror",
            "scrambling": "people scrambling, panic sounds",
            "weapon_clash": "bone and stone weapons clashing",
            "body_fall": "body falling to ground, heavy impact",
            "bone_rattle": "bone jewelry and necklaces rattling",

            # 情感/超自然
            "supernatural_pulse": "supernatural energy pulse, ethereal tone",
            "golden_glow_sound": "visual sound effect, magical glow",
            "energy_discharge": "electrical discharge, power buildup",
            "earth_crack": "earth cracking, ground collapsing",
        }

    def get_sfx_path(self, sfx_name: str) -> Path:
        """获取音效文件路径（或生成）"""
        # 先检查本地是否存在
        local_path = self.library_dir / f"{sfx_name}.mp3"
        if local_path.exists():
            return local_path

        # 如果是内置音效名称，返回库路径（假设已手动添加）
        if sfx_name in self.builtin_sfx:
            return local_path

        return None

    def list_available_sfx(self) -> list[str]:
        """列出所有可用的音效"""
        return list(self.builtin_sfx.keys())


class BGMLibrary:
    """背景音乐库管理器"""

    def __init__(self, episode_id: str):
        self.episode_id = episode_id
        self.library_dir = get_episode_dir(episode_id) / "audio" / "bgm_library"
        self.library_dir.mkdir(parents=True, exist_ok=True)

        # 内置 BGM
        self.builtin_bgm = {
            "tribal_drums": "tribal rhythm, primitive drums, low frequency",
            "ominous_drone": "low ominous drone, building tension",
            "supernatural_theme": "ethereal, otherworldly music",
            "emotional_strings": "sad emotional strings, melancholic",
            "epic_orchestral": "grand orchestral score, heroic",
            "tension_buildup": "gradual tension building, discordant strings",
            "calm_ancient": "calm, ancient ceremonial music",
        }

    def get_bgm_path(self, bgm_name: str) -> Path:
        """获取 BGM 文件路径"""
        local_path = self.library_dir / f"{bgm_name}.mp3"
        if local_path.exists():
            return local_path
        return None


def generate_test_audio(output_path: Path, duration_s: float = 3.0, description: str = "") -> None:
    """
    为开发用途生成测试音频。

    实际使用中，这些会被替换为真实的音效库文件。
    """
    # 生成白噪声或简单的测试音
    cmd = (
        f'ffmpeg -y -f lavfi -i "anoise=c=white:r=48000:d={duration_s}" '
        f'-ar 44100 -t {duration_s} "{output_path}"'
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to generate test audio: {result.stderr}")


def print_sfx_bgm_summary(episode_id: str) -> None:
    """打印整集音效和 BGM 的摘要"""
    print(f"\n{'=' * 60}")
    print(f"音效和 BGM 摘要 — {episode_id}")
    print(f"{'=' * 60}")

    sfx_list, bgm_list = SFXParser.parse_episode(episode_id)

    print(f"\n【音效 (SFX)】共 {len(sfx_list)} 条")
    for sfx in sfx_list:
        print(f"  • {sfx.effect_id}: {sfx.description}")
        print(f"    时间: {sfx.start_time:.2f}s, 时长: {sfx.duration:.2f}s")

    print(f"\n【背景音乐 (BGM)】共 {len(bgm_list)} 条")
    for bgm in bgm_list:
        print(f"  • {bgm.bgm_id}: {bgm.description}")
        print(f"    时间: {bgm.start_time:.2f}s")
        if bgm.fade_in > 0:
            print(f"    淡入: {bgm.fade_in:.2f}s")
        if bgm.fade_out > 0:
            print(f"    淡出: {bgm.fade_out:.2f}s")
        if bgm.volume != 1.0:
            print(f"    音量: {bgm.volume:.1f}x")


if __name__ == "__main__":
    import sys

    episode = sys.argv[1] if len(sys.argv) > 1 else "ep002"
    print_sfx_bgm_summary(episode)
