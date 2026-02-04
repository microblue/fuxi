# 🎵 伏羲纪元 — 音频系统完整实现总结

## 实现概览

已成功实现 **专业级别的音频处理系统**，支持：

### ✅ 三层音频架构

```
┌────────────────────────────────────────────┐
│     Layer 3: 多轨混合 (AudioMixer)        │  ← 全局混合引擎
│  - 时间对齐, 音量控制, 淡入淡出, 混合    │
└──────────────────┬─────────────────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
┌────────────┐ ┌─────────┐ ┌──────────────┐
│ Layer 2:   │ │ Layer 2:│ │ Layer 2:     │
│ 配音系统   │ │ 音效&   │ │ BGM 系统     │
│ (TTS)      │ │ SFX 管理│ │ (Music)      │
└──────┬─────┘ └────┬────┘ └──────┬───────┘
       │            │             │
       ▼            ▼             ▼
┌────────────┐ ┌─────────┐ ┌──────────────┐
│ Layer 1:   │ │ Layer 1:│ │ Layer 1:     │
│synth_voice │ │manage_  │ │ shots.json   │
│.py         │ │sfx.py   │ │ (sfx_bgm)    │
└────────────┘ └─────────┘ └──────────────┘
```

---

## 📦 新增文件和模块

### 1. `pipeline/audio_engine.py` (251 行)

**核心功能**：多轨音频混合引擎

```python
# 主要类
class AudioTrack:
    """单个音频轨道（配音、SFX、BGM）"""
    - track_id: 轨道标识符
    - audio_path: 音频文件路径
    - start_time: 全局时间轴上的起始位置
    - volume: 相对音量 (0.0-1.0)
    - fade_in/fade_out: 淡入淡出时长
    - track_type: 轨道类型 (dialogue/sfx/bgm)

class AudioMixer:
    """多轨混合器"""
    - add_track(track): 添加轨道
    - build_ffmpeg_command(): 构建 FFmpeg 滤镜链
    - mix(output_path): 执行混合

# 辅助函数
- create_silence(duration_s, output_path)
- create_audio_pad(audio_path, pad_start, pad_end)
```

**特点**：
- ✅ 支持无限个音频轨道
- ✅ 自动时间对齐 (adelay)
- ✅ 独立音量控制 (volume)
- ✅ 平滑淡入淡出 (afade)
- ✅ FFmpeg 滤镜链自动生成

**示例**：

```python
from pipeline.audio_engine import AudioTrack, AudioMixer

mixer = AudioMixer()
mixer.add_track(AudioTrack("dialogue", Path("S01.wav"), 0.0, volume=1.0))
mixer.add_track(AudioTrack("sfx", Path("gasp.mp3"), 1.5, volume=0.7))
mixer.add_track(AudioTrack("bgm", Path("drums.mp3"), 0.0, volume=0.5, fade_in=1.0))
mixer.mix(Path("output.wav"))
```

---

### 2. `pipeline/synth_voice.py` (323 行，已升级)

**新增功能**：
- ✅ 多 TTS 提供商支持 (Fish Audio, Edge TTS, 占位符)
- ✅ 按角色配置不同音色
- ✅ 按情感自动调整速度和音高
- ✅ 旁白专用音色

**关键配置**：

```python
CHARACTER_VOICES = {
    "fuxi": {
        "provider": "fish_audio",
        "voice_id": "cn_male_youthful",
        "speed": 1.0,
        "pitch": 0,
    },
    "elder_woman": {
        "provider": "fish_audio",
        "voice_id": "cn_female_elderly",
        "speed": 0.95,
        "pitch": -5,
    },
    # ... 更多角色
}

EMOTION_PARAMS = {
    "fearful": {"speed_delta": 1.1, "pitch_delta": 10},
    "determined": {"speed_delta": 0.95, "pitch_delta": -5},
    # ... 更多情感
}
```

**主要 API**：

```python
# 生成单个配音
synthesize_line(
    text="台词文本",
    character="角色名",
    emotion="情感标签",
    output_path=Path("output.wav"),
    duration_s=3.0,
    episode_id="ep002"
)

# 生成旁白
synthesize_narration(
    text="旁白文本",
    output_path=Path("narration.wav"),
    duration_s=2.0,
    episode_id="ep002"
)

# 处理整集
process_episode("ep002")  # 自动生成所有配音
```

**TTS 集成**：

| 提供商 | 类 | 优点 | 缺点 |
|--------|-----|------|------|
| Fish Audio | `FishAudioTTS` | 高质量中文, 多音色 | 需要 API Key |
| Edge TTS | `EdgeTTS` | 免费, 本地快速 | 音质一般 |
| 占位符 | 内置 | 开发快速 | 无音频 |

---

### 3. `pipeline/manage_sfx.py` (373 行)

**功能**：从 shots.json 解析和管理音效与 BGM

**主要类**：

```python
class SFXEntry:
    """单个音效条目"""
    - effect_id: 音效标识符
    - effect_type: 类型 (action/ambient)
    - description: 描述
    - start_time: 相对时间
    - duration: 音效时长

class BGMEntry:
    """背景音乐条目（可跨镜头）"""
    - bgm_id: 音乐标识符
    - start_time: 全局时间
    - fade_in/fade_out: 淡入淡出
    - volume: 相对音量

class SFXParser:
    """解析 sfx_bgm 字段"""
    @staticmethod
    def parse_shot_sfx(shot, shot_start_time)
    @staticmethod
    def parse_shot_bgm(shot, shot_start_time)
    @staticmethod
    def parse_episode(episode_id)

class SFXLibrary:
    """音效库管理"""
    - 30+ 内置音效
    - get_sfx_path(sfx_name)
    - list_available_sfx()

class BGMLibrary:
    """BGM 库管理"""
    - 7+ 内置背景音乐
    - get_bgm_path(bgm_name)
```

**内置音效库**：

- 环境: ambient_wind, ambient_rain, ambient_fire, ambient_tribal_camp
- 人物: gasp_fear, gasp_shock, scream_woman, scream_terror, scrambling, footsteps_*
- 动作: weapon_clash, body_fall, bone_rattle
- 超自然: supernatural_pulse, energy_discharge, earth_crack

**内置 BGM**：

- tribal_drums, ominous_drone, supernatural_theme
- emotional_strings, epic_orchestral, tension_buildup, calm_ancient

---

## 📝 shots.json 音频格式

### 基础结构

```json
{
  "shot_id": "S01",
  "duration_s": 4,
  "dialogue": "台词文本",
  "characters": ["角色名"],
  "emotion": "情感标签",
  "sfx_bgm": "SFX: 音效1, 音效2. BGM: bgm_id(参数)"
}
```

### 音效格式

```
SFX: effect_name1, effect_name2, ...
```

示例：
```
SFX: footsteps on dirt, gasps, scrambling sounds
```

### BGM 格式

```
BGM: bgm_id(start=0, fade_in=0.5, fade_out=1, duration=10, volume=0.7)
```

**参数说明**：
| 参数 | 默认 | 说明 |
|------|------|------|
| start | 0 | 镜头内开始时间 |
| fade_in | 0 | 淡入时长 |
| fade_out | 0 | 淡出时长 |
| duration | ∞ | 总时长 |
| volume | 1.0 | 相对音量 |

### 完整示例

```json
{
  "shots": [
    {
      "shot_id": "S01",
      "duration_s": 4,
      "dialogue": "邪灵之眼......他被雷泽的恶灵附身了!",
      "characters": ["elder_woman"],
      "emotion": "terror",
      "sfx_bgm": "SFX: gasp_fear, bone_rattle. BGM: ominous_drone(fade_in=1, volume=0.7)"
    },
    {
      "shot_id": "S02",
      "duration_s": 3,
      "dialogue": "所有人都在看着伏羲...",
      "characters": ["tribe_members"],
      "emotion": "fear",
      "sfx_bgm": "SFX: scrambling. BGM: ominous_drone(volume=0.8)"
    },
    {
      "shot_id": "S03",
      "duration_s": 4,
      "dialogue": "",
      "characters": [],
      "emotion": "awe",
      "sfx_bgm": "BGM: ominous_drone(fade_out=1, volume=0.9)"
    }
  ]
}
```

---

## 🎛️ 配置文件

### 1. 角色音声配置

**全局**（`synth_voice.py`）：

```python
CHARACTER_VOICES = {
    "fuxi": {
        "provider": "fish_audio",
        "voice_id": "cn_male_youthful",
        "speed": 1.0,
        "pitch": 0,
    },
    # ... 其他角色
}
```

**按剧集**（`episodes/{ep}/characters.json`）：

```json
{
  "fuxi": {
    "provider": "edge_tts",
    "voice": "zh-CN-YunxiNeural",
    "speed": 1.1
  }
}
```

### 2. 环境变量

```bash
# Fish Audio API Key
export FISH_AUDIO_API_KEY="your_key_here"

# 可选：自定义音效库路径
export FUXI_SFX_LIBRARY="/path/to/custom/sfx"
```

---

## 🚀 使用流程

### 完整工作流

```bash
# 1. 准备 shots.json（定义音频配置）
编辑 episodes/ep002/shots.json
  - 添加 dialogue 和 characters
  - 设置 emotion 标签
  - 配置 sfx_bgm

# 2. 配置角色音声（可选）
编辑 synth_voice.py 中的 CHARACTER_VOICES
或创建 episodes/ep002/characters.json

# 3. 生成配音
python -m pipeline.synth_voice ep002

# 4. 验证音效和 BGM
python -m pipeline.manage_sfx ep002

# 5. 生成最终视频（包含音频混合）
python -m pipeline.render_video ep002

# 6. 播放和检验
ffplay episodes/ep002/video/final.mp4
```

### 代码级集成

```python
from pipeline.synth_voice import process_episode
from pipeline.manage_sfx import SFXParser
from pipeline.audio_engine import AudioTrack, AudioMixer

# 生成配音
process_episode("ep002")

# 解析音效和 BGM
sfx_list, bgm_list = SFXParser.parse_episode("ep002")

# 创建混合器
mixer = AudioMixer()

# 添加轨道...
for i, sfx in enumerate(sfx_list[:5]):
    mixer.add_track(AudioTrack(
        track_id=sfx.effect_id,
        audio_path=Path(f"audio/{sfx.effect_id}.mp3"),
        start_time=sfx.start_time,
        volume=0.6,
    ))

# 执行混合
mixer.mix(Path("output.wav"))
```

---

## 🎯 主要特性

### ✅ 已实现

- [x] 多 TTS 提供商集成 (Fish Audio, Edge TTS)
- [x] 按角色和情感的声音定制
- [x] 音效库管理 (30+ 内置音效)
- [x] BGM 库管理 (7+ 内置背景音乐)
- [x] 跨镜头 BGM 自动衔接
- [x] 多轨音频混合引擎
- [x] 时间对齐和同步
- [x] 音量包络和淡入淡出
- [x] FFmpeg 自动化

### 🔮 可扩展

- [ ] 为音效库添加更多音效（手动或 AI 生成）
- [ ] 集成其他 TTS (CosyVoice, Silero, etc.)
- [ ] 实时音频监控和可视化
- [ ] 高级音频效果 (EQ, Compression, Reverb)
- [ ] 自动场景音乐选择
- [ ] 语音克隆 (VoiceClone)

---

## 📚 文档

### 已编写

| 文件 | 内容 | 行数 |
|------|------|------|
| `AUDIO_SYSTEM_GUIDE.md` | 完整系统教程 | ~500 |
| `AUDIO_QUICK_START.md` | 快速开始指南 | ~300 |
| 本文件 | 实现总结 | 此文件 |

---

## 🔗 文件依赖

```
pipeline/
├── audio_engine.py           # 核心混合引擎
├── synth_voice.py            # 配音 (已升级)
├── manage_sfx.py             # 音效和 BGM 管理
├── render_video.py           # 最终视频渲染 (未修改，兼容)
└── utils.py                  # 通用工具 (被依赖)

episodes/
└── {ep}/
    ├── shots.json            # 镜头定义 + 音频配置
    ├── characters.json       # 角色音声配置 (可选)
    ├── audio/                # 生成的音频文件
    │   ├── S01.wav          # 配音
    │   ├── S02.wav
    │   └── ...
    └── video/
        └── final.mp4         # 最终视频
```

---

## 🧪 测试和验证

### 快速测试

```bash
# 1. 测试 Fish Audio
export FISH_AUDIO_API_KEY="test_key"
python -c "
from pipeline.synth_voice import FishAudioTTS
from pathlib import Path
FishAudioTTS.synthesize('你好', 'cn_male_youthful', Path('/tmp/test.wav'))
"

# 2. 测试 Edge TTS
python -c "
from pipeline.synth_voice import EdgeTTS
from pathlib import Path
EdgeTTS.synthesize('你好', Path('/tmp/test.wav'))
"

# 3. 测试 SFX 解析
python -m pipeline.manage_sfx ep002

# 4. 测试混合器
python -c "
from pipeline.audio_engine import AudioMixer
mixer = AudioMixer()
print(f'✓ AudioMixer 可用')
"
```

### 完整验证

```bash
# 1. 生成样本
python -m pipeline.synth_voice ep002
python -m pipeline.manage_sfx ep002

# 2. 检查输出
ls -lh episodes/ep002/audio/*.wav
ffprobe episodes/ep002/audio/S01.wav

# 3. 生成视频
python -m pipeline.render_video ep002

# 4. 播放测试
ffplay episodes/ep002/video/final.mp4
```

---

## 📋 集成检查清单

- [ ] 在 `shots.json` 中定义所有音频配置
- [ ] 配置 `CHARACTER_VOICES` 或创建 `characters.json`
- [ ] 选择和配置 TTS 提供商
- [ ] 运行 `python -m pipeline.synth_voice {ep}`
- [ ] 验证输出在 `episodes/{ep}/audio/`
- [ ] 运行 `python -m pipeline.manage_sfx {ep}` 检查解析
- [ ] 运行 `python -m pipeline.render_video {ep}`
- [ ] 播放最终视频验证音频

---

## 💡 常见问题

### Q: 配音文件很大吗?

A: 取决于 TTS。Edge TTS 生成压缩 MP3（小），Fish Audio 生成高质量 WAV（大）。

### Q: 可以混合多个 TTS 吗?

A: 可以。在 `CHARACTER_VOICES` 中为不同角色设置不同的 `provider`。

### Q: BGM 跨镜头时如何保持连续?

A: 系统自动合并相同 `bgm_id` 的条目，计算全局时间轴。

### Q: 如何添加自定义音效?

A: 在 `manage_sfx.py` 的 `SFXLibrary.builtin_sfx` 中添加，或直接放入 `audio/sfx_library/` 目录。

---

## 🎓 学习资源

### 音频基础
- **FFmpeg 滤镜文档**: https://ffmpeg.org/ffmpeg-filters.html#Audio-Filters
- **FFmpeg adelay**: 音频延迟和同步
- **FFmpeg afade**: 淡入淡出效果
- **FFmpeg amix**: 多轨混合

### TTS 集成
- **Fish Audio**: https://fish.audio
- **Edge TTS**: https://github.com/rany2/edge-tts
- **CosyVoice**: https://github.com/v-iashin/CosyVoice

### 音频工程
- 音量计量：-18dB FS = 80% perceived loudness
- 动态范围：配音 > BGM > SFX
- 频率范围：低频 BGM, 中频配音, 高频 SFX

---

## 📞 支持和反馈

- 查看 `AUDIO_SYSTEM_GUIDE.md` 了解详细用法
- 查看 `AUDIO_QUICK_START.md` 了解常见场景
- 检查 `manage_sfx.py` 中的注释了解解析逻辑
- 查看示例 `episodes/ep002/shots.json` 了解格式

