# 伏羲纪元 — 音频系统完整指南

## 系统架构概览

### 三层音频架构

```
┌─────────────────────────────────────────────────────────────┐
│                    最终合成视频 (final.mp4)                 │
│                      + 混合音频轨道                         │
└──────────────────────────┬──────────────────────────────────┘
                           ▲
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────┐        ┌─────────┐      ┌──────────────┐
   │  配音   │        │ 音效 &  │      │   背景音乐   │
   │ 轨道    │        │  BGM    │      │   轨道       │
   │         │        │  轨道   │      │              │
   └────┬────┘        └────┬────┘      └──────┬───────┘
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────────────────────────────────────────────────────┐
   │           AudioMixer（多轨混合引擎）                    │
   │  - 时间对齐（adelay）                                  │
   │  - 音量控制（volume）                                  │
   │  - 淡入淡出（afade）                                   │
   │  - 多轨混合（amix）                                    │
   └─────────────────────────────────────────────────────────┘
```

---

## 1️⃣ 配音系统 (`synth_voice.py`)

### 工作流程

```
shots.json (台词 + 角色信息)
    ↓
synthesize_line(text, character, emotion, ...)
    ↓
TTS 提供商选择链：
  ✓ Fish Audio (高质量中文，需 API Key)
  ✓ Edge TTS (免费，无需 API)
  ✓ 占位符 (开发用，生成静音)
    ↓
.wav 音频文件 (episodes/{ep}/audio/)
```

### 配置角色声音

**方式 1: 全局配置**（`synth_voice.py` 中的 `CHARACTER_VOICES`）

```python
CHARACTER_VOICES = {
    "fuxi": {
        "provider": "fish_audio",
        "voice_id": "cn_male_youthful",
        "speed": 1.0,       # 1.0 = 正常速度
        "pitch": 0,         # 0 = 标准音高
    },
    "elder_woman": {
        "provider": "fish_audio",
        "voice_id": "cn_female_elderly",
        "speed": 0.95,      # 95% 的正常速度
        "pitch": -5,        # 降低 5 个半音
    },
}
```

**方式 2: 按剧集自定义**（`episodes/{ep}/characters.json`）

```json
{
  "fuxi": {
    "provider": "edge_tts",
    "voice": "zh-CN-YunxiNeural",
    "speed": 1.1
  },
  "shaman": {
    "provider": "fish_audio",
    "voice_id": "cn_male_deep",
    "pitch": -15
  }
}
```

### 情感参数

系统自动根据 `emotion` 字段调整速度和音高：

```python
EMOTION_PARAMS = {
    "fearful": {"speed_delta": 1.1, "pitch_delta": 10},      # 快速 + 升高
    "determined": {"speed_delta": 0.95, "pitch_delta": -5},  # 缓慢 + 降低
    "angry": {"speed_delta": 1.15, "pitch_delta": 15},       # 很快 + 很高
    "sad": {"speed_delta": 0.85, "pitch_delta": -10},        # 很慢 + 很低
}
```

### 使用方法

```bash
# 生成 ep002 的所有配音
python -m pipeline.synth_voice ep002

# 输出示例：
# ============================================================
# 语音合成 — ep002
# ============================================================
#   [TTS] S01.wav: "邪灵之眼......他被雷泽的恶灵附身了!"
#         character=elder_woman, emotion=terror, 3.0s
#     ✓ Generated via Fish Audio
#   [TTS] S02.wav: "伏羲，你怎样了？"
#         character=fuxi_mother, emotion=concern, 2.5s
#     ✓ Generated via Fish Audio
# ...
```

---

## 2️⃣ 音效和 BGM 系统 (`manage_sfx.py`)

### 在 `shots.json` 中定义音效和 BGM

```json
{
  "shot_id": "S01",
  "duration_s": 4,
  "sfx_bgm": "SFX: footsteps on dirt, gasps, scrambling sounds. BGM: ominous_drone(fade_in=1, volume=0.7)"
}
```

### 音效格式

```
SFX: effect1, effect2, effect3
```

**音效类型：**

| 类别 | 示例 | 用途 |
|------|------|------|
| 环境音效 | ambient_wind, ambient_fire | 贯穿整个镜头的氛围 |
| 动作音效 | footsteps, gasp, scream | 特定动作的声音 |
| 超自然 | supernatural_pulse, energy_discharge | 奇幻/科幻效果 |

### 背景音乐格式

```
BGM: bgm_id(start=0, fade_in=1, fade_out=0.5, duration=10, volume=0.8)
```

**参数说明：**

| 参数 | 默认 | 说明 |
|------|------|------|
| `start` | 0 | 镜头内开始时间（秒） |
| `fade_in` | 0 | 淡入时长（秒） |
| `fade_out` | 0 | 淡出时长（秒） |
| `duration` | - | 音乐总时长（可选，省略表示贯穿） |
| `volume` | 1.0 | 相对音量（0.0-1.0） |

### 跨镜头 BGM 示例

```json
{
  "shots": [
    {
      "shot_id": "S01",
      "duration_s": 4,
      "sfx_bgm": "SFX: footsteps; BGM: tribal_drums(fade_in=0.5, volume=0.6)"
    },
    {
      "shot_id": "S02",
      "duration_s": 3,
      "sfx_bgm": "SFX: gasp_fear; BGM: tribal_drums(volume=0.7)"
    },
    {
      "shot_id": "S03",
      "duration_s": 4,
      "sfx_bgm": "SFX: scream; BGM: tribal_drums(fade_out=1, volume=0.8)"
    }
  ]
}
```

> **说明**：`tribal_drums` 从 S01 开始，逐渐加强到 S03，最后淡出。系统会自动计算全局时间轴并合并重叠的 BGM 轨道。

### 查看音效和 BGM 摘要

```bash
python -m pipeline.manage_sfx ep002

# 输出：
# ============================================================
# 音效和 BGM 摘要 — ep002
# ============================================================
#
# 【音效 (SFX)】共 12 条
#   • S01_sfx_0: footsteps on dirt
#     时间: 0.00s, 时长: 4.00s
#   • S01_sfx_1: gasps
#     时间: 0.00s, 时长: 4.00s
# ...
#
# 【背景音乐 (BGM)】共 3 条
#   • tribal_drums: tribal_drums(fade_in=0.5, volume=0.6)
#     时间: 0.00s
#     淡入: 0.50s
#     音量: 0.6x
```

---

## 3️⃣ 多轨音频混合 (`audio_engine.py`)

### 核心组件

#### `AudioTrack` - 单个音轨

```python
from pipeline.audio_engine import AudioTrack, AudioMixer

# 创建配音轨
dialogue_track = AudioTrack(
    track_id="dialogue_S01",
    audio_path=Path("episodes/ep002/audio/S01.wav"),
    start_time=0.0,           # 从 0 秒开始
    volume=1.0,
    fade_in=0.2,              # 淡入 0.2 秒
    track_type="dialogue"
)
```

#### `AudioMixer` - 混合器

```python
mixer = AudioMixer(output_sample_rate=44100)

# 添加轨道
mixer.add_track(dialogue_track)
mixer.add_track(sfx_track)
mixer.add_track(bgm_track)

# 执行混合
output_path = Path("episodes/ep002/audio/mixed.wav")
mixer.mix(output_path)
```

### 混合器工作原理

1. **时间对齐** - 使用 `adelay` 将所有轨道对齐到全局时间轴
2. **音量控制** - 使用 `volume` 滤镜调整每个轨道的相对音量
3. **淡入淡出** - 使用 `afade` 在轨道开始和结束时平滑过渡
4. **多轨混合** - 使用 `amix` 滤镜将所有轨道混合为单一输出

### FFmpeg 滤镜链示例

```
输入文件：
  - dialogue.wav (配音)
  - sfx.wav (音效)
  - bgm.wav (背景音乐)

滤镜链：
[0:a] aformat=sample_rates=44100 [a0];
[a0] adelay=0|0 [a0d];
[a0d] afade=t=in:st=0:d=0.2 [a0f];
[a0f] volume=1.0 [a0v];

[1:a] aformat=sample_rates=44100 [a1];
[a1] adelay=1000|1000, volume=0.7 [a1d];

[2:a] aformat=sample_rates=44100 [a2];
[a2] adelay=500|500, volume=0.5 [a2d];
[a2d] afade=t=out:st=58:d=1 [a2f];

[a0v][a1d][a2f] amix=inputs=3:duration=longest [out]
```

---

## 4️⃣ 完整工作流程

### 单镜头配音 + 音效混合

```python
from pathlib import Path
from pipeline.audio_engine import AudioTrack, AudioMixer
from pipeline.synth_voice import synthesize_line
from pipeline.manage_sfx import SFXParser, SFXLibrary

# 步骤 1: 生成配音
audio_path = Path("episodes/ep002/audio/S01.wav")
synthesize_line(
    text="邪灵之眼......",
    character="elder_woman",
    emotion="terror",
    output_path=audio_path,
    duration_s=3.0,
    episode_id="ep002"
)

# 步骤 2: 获取音效
sfx_list, _ = SFXParser.parse_episode("ep002")  # 从 shots.json 解析

# 步骤 3: 构建混音器
mixer = AudioMixer()

# 添加配音轨
mixer.add_track(AudioTrack(
    track_id="dialogue_S01",
    audio_path=audio_path,
    start_time=0.0,
    volume=1.0,
))

# 添加音效轨（从库中获取）
sfx_lib = SFXLibrary("ep002")
for sfx in sfx_list[:2]:  # 添加前两个音效
    sfx_audio = sfx_lib.get_sfx_path(sfx.description.split()[0])
    if sfx_audio:
        mixer.add_track(AudioTrack(
            track_id=sfx.effect_id,
            audio_path=sfx_audio,
            start_time=sfx.start_time,
            volume=0.6,
            track_type="sfx"
        ))

# 步骤 4: 混合并导出
output = Path("episodes/ep002/audio/S01_mixed.wav")
mixer.mix(output)
```

### 完整剧集处理

```python
from pipeline.gen_episode import process_episode

# 运行完整管线：
# 1. 生成所有镜头的配音
# 2. 解析音效和 BGM
# 3. 混合所有轨道
# 4. 生成最终视频（带音频）
process_episode("ep002")
```

---

## 5️⃣ TTS 集成指南

### 使用 Fish Audio（推荐）

**优点**：
- 高质量中文语音
- 多种音色选择
- 支持情感控制

**安装和配置**：

```bash
# 1. 安装依赖
pip install requests

# 2. 获取 API Key
# 访问 https://fish.audio，注册并创建 API Key

# 3. 设置环境变量
export FISH_AUDIO_API_KEY="your_api_key_here"

# 4. 在 synth_voice.py 中配置角色
CHARACTER_VOICES["fuxi"]["provider"] = "fish_audio"
```

**使用**：

```python
from pipeline.synth_voice import synthesize_line

synthesize_line(
    text="我是伏羲",
    character="fuxi",
    emotion="determined",
    output_path=Path("output.wav"),
    duration_s=2.0
)
```

### 使用 Edge TTS（免费）

**优点**：
- 免费无需 API Key
- 无需在线（使用本地缓存）
- 中文支持较好

**安装**：

```bash
pip install edge-tts
```

**使用**：

```python
from pipeline.synth_voice import EdgeTTS

EdgeTTS.synthesize(
    text="我是伏羲",
    output_path=Path("output.wav"),
    voice="zh-CN-YunxiNeural",  # 中文女性
    speed=1.0
)
```

### 音色选择参考

| 音色 ID | 描述 | 适合角色 |
|---------|------|---------|
| `cn_male_youthful` | 年轻男性 | Fuxi |
| `cn_male_deep` | 深沉男性 | 萨满、族长 |
| `cn_female_warm` | 温暖女性 | 伏羲母亲 |
| `cn_female_elderly` | 老年女性 | 老妪 |
| `cn_male_narration` | 旁白专用 | 旁白 |

---

## 6️⃣ 常见问题和故障排除

### Q1: 配音文件生成很慢

**A**: Fish Audio 调用外部 API，可能受网络影响。
- 使用 Edge TTS 作为本地快速方案
- 批量生成时添加延迟避免 API 限流

### Q2: 音效和 BGM 不对齐

**A**: 检查 `shots.json` 中的时间计算。
- 使用 `manage_sfx.py` 验证解析结果
- 确保 `start_time` 和 `fade_in/fade_out` 计算正确

### Q3: 混音输出声音太小或太大

**A**: 调整轨道音量参数。

```python
# 降低 BGM 音量
mixer.add_track(AudioTrack(
    ...,
    volume=0.5,  # 50% 音量
))
```

### Q4: 特定字符发音错误

**A**: 使用拼音或替代词。

```python
# 代替 "伏羲" （可能发音不清）
text = "fu xi"  # 拼音形式
```

---

## 7️⃣ 最佳实践

### 音量级别建议

| 轨道 | 推荐音量 | 说明 |
|------|--------|------|
| 配音 | 1.0 | 100%，主轨道 |
| 主 BGM | 0.5-0.6 | 不应盖过配音 |
| 次 BGM | 0.3-0.4 | 氛围补充 |
| 动作 SFX | 0.5-0.7 | 突出关键声音 |
| 环境 SFX | 0.3-0.4 | 背景氛围 |

### 淡入淡出最佳实践

```
镜头 1 (4s)           镜头 2 (3s)           镜头 3 (4s)
├─ BGM: tribal_drums  ├─ SFX: gasp         ├─ BGM: tension_buildup
│  (fade_in=0.5)      │                    │  (fade_in=0)
│  (duration=11)      │                    │  (fade_out=1)
│                     │                    │
└─────────────────────┴────────────────────┘
0s                    4s                   7s                   11s

关键点：
1. 总 BGM 时长覆盖所有使用的镜头
2. 淡出时长不应超过镜头时长
3. 淡入/淡出应与场景变化对齐
```

---

## 📋 检查清单

- [ ] 在 `shots.json` 中为所有有台词的镜头添加 `dialogue` 和 `characters` 字段
- [ ] 配置 `CHARACTER_VOICES` 中的所有角色
- [ ] 在 `sfx_bgm` 字段中定义音效和 BGM
- [ ] 设置 TTS API Key（如果使用 Fish Audio）
- [ ] 运行 `python -m pipeline.synth_voice ep002` 生成配音
- [ ] 运行 `python -m pipeline.manage_sfx ep002` 验证音效和 BGM
- [ ] 生成并测试最终视频：`python -m pipeline.render_video ep002`

---

## 📚 相关文件

| 文件 | 用途 |
|------|------|
| `pipeline/audio_engine.py` | 多轨混合核心引擎 |
| `pipeline/synth_voice.py` | TTS 配音系统 |
| `pipeline/manage_sfx.py` | 音效和 BGM 管理 |
| `episodes/{ep}/shots.json` | 镜头定义（含音频配置） |
| `episodes/{ep}/characters.json` | 角色音声配置（可选） |
| `episodes/{ep}/audio/` | 生成的音频文件 |

