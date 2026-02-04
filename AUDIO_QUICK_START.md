# 🎵 音频系统快速开始

## 30秒快速演示

### 准备工作

```bash
# 确保 shots.json 包含音频配置
# 编辑 episodes/ep002/shots.json：

{
  "shots": [
    {
      "shot_id": "S01",
      "dialogue": "邪灵之眼......他被雷泽的恶灵附身了!",
      "characters": ["elder_woman"],
      "emotion": "terror",
      "duration_s": 3,
      "sfx_bgm": "SFX: gasp_fear, bone_rattle. BGM: ominous_drone(fade_in=0.5, volume=0.7)"
    }
  ]
}
```

### 运行音频流程

```bash
# 1. 生成配音（3 种选项）

# 选项 A: Fish Audio (高质量)
export FISH_AUDIO_API_KEY="your_key"
python -m pipeline.synth_voice ep002

# 选项 B: Edge TTS (免费)
pip install edge-tts
python -m pipeline.synth_voice ep002

# 选项 C: 占位符 (开发用)
python -m pipeline.synth_voice ep002  # 自动生成静音

# 2. 查看音效和 BGM
python -m pipeline.manage_sfx ep002

# 3. 生成最终视频（包含音频混合）
python -m pipeline.render_video ep002
```

---

## 核心概念速查

### 配音配置

```python
# 在 synth_voice.py 中修改：
CHARACTER_VOICES = {
    "fuxi": {
        "provider": "fish_audio",     # fish_audio / edge_tts
        "voice_id": "cn_male_youthful",
        "speed": 1.0,
        "pitch": 0,
    }
}
```

### 情感调整

```python
# 自动应用的情感参数：
EMOTION_PARAMS = {
    "fearful": {"speed_delta": 1.1, "pitch_delta": 10},      # ↑快 ↑高
    "determined": {"speed_delta": 0.95, "pitch_delta": -5},  # ↓慢 ↓低
    "angry": {"speed_delta": 1.15, "pitch_delta": 15},
    "sad": {"speed_delta": 0.85, "pitch_delta": -10},
}
```

---

## shots.json 音频配置语法

### 基础格式

```
"sfx_bgm": "SFX: 音效1, 音效2, ... BGM: bgm_id(...参数...)"
```

### 音效示例

```json
"sfx_bgm": "SFX: footsteps, gasp_fear, bone_rattle"
```

### BGM 示例

```json
"sfx_bgm": "BGM: ominous_drone(fade_in=0.5, volume=0.7)"
```

### 综合示例

```json
{
  "shot_id": "S01",
  "duration_s": 4,
  "dialogue": "...",
  "characters": ["elder_woman"],
  "emotion": "terror",
  "sfx_bgm": "SFX: gasp_fear, scrambling. BGM: tribal_drums(fade_in=1, volume=0.6)"
}
```

---

## 跨镜头 BGM 连接

### 场景：BGM 从 S01 → S03

```json
{
  "shots": [
    {
      "shot_id": "S01",
      "duration_s": 4,
      "sfx_bgm": "BGM: ominous_drone(fade_in=0.5, volume=0.5)"
    },
    {
      "shot_id": "S02",
      "duration_s": 3,
      "sfx_bgm": "BGM: ominous_drone(volume=0.7)"  // 继续，音量提升
    },
    {
      "shot_id": "S03",
      "duration_s": 4,
      "sfx_bgm": "BGM: ominous_drone(fade_out=1, volume=0.8)"  // 淡出
    }
  ]
}
```

**系统自动处理**：
- 识别 3 个 `ominous_drone` 条目
- 合并为单一 BGM 轨道（总时长: 11 秒）
- 应用淡入/淡出和音量包络

---

## 音频轨道优先级和音量

### 推荐配置

```
配音轨      1.0  ████████████ (主轨，不能减小)
└─ 旁白     1.0  ████████████

主 BGM      0.6  ███████░░░░░
└─ 次 BGM   0.3  ████░░░░░░░░

动作 SFX    0.7  ████████░░░░
环境 SFX    0.4  █████░░░░░░░
```

### 在代码中设置

```python
from pipeline.audio_engine import AudioTrack, AudioMixer

mixer = AudioMixer()

# 配音 (100%)
mixer.add_track(AudioTrack(
    track_id="dialogue",
    audio_path=Path("S01.wav"),
    start_time=0.0,
    volume=1.0,
))

# BGM (60%)
mixer.add_track(AudioTrack(
    track_id="bgm",
    audio_path=Path("tribal_drums.mp3"),
    start_time=0.0,
    volume=0.6,
    fade_in=0.5,
))

# SFX (70%)
mixer.add_track(AudioTrack(
    track_id="sfx",
    audio_path=Path("footsteps.mp3"),
    start_time=1.0,
    volume=0.7,
))

mixer.mix(Path("output.wav"))
```

---

## 常见场景模板

### 场景 1: 简单对话

```json
{
  "shot_id": "S01",
  "duration_s": 3,
  "dialogue": "台词",
  "characters": ["character_name"],
  "emotion": "normal",
  "sfx_bgm": "BGM: calm_ancient(volume=0.5)"
}
```

### 场景 2: 紧张动作

```json
{
  "shot_id": "S05",
  "duration_s": 4,
  "dialogue": "受伤的叫声",
  "characters": ["fuxi"],
  "emotion": "fearful",
  "sfx_bgm": "SFX: weapon_clash, body_fall. BGM: tension_buildup(fade_in=1, volume=0.8)"
}
```

### 场景 3: 神秘时刻

```json
{
  "shot_id": "S10",
  "duration_s": 5,
  "dialogue": "",
  "characters": [],
  "emotion": "wonder",
  "sfx_bgm": "SFX: supernatural_pulse. BGM: supernatural_theme(fade_in=0.5, volume=0.6)"
}
```

### 场景 4: 群戏

```json
{
  "shot_id": "S15",
  "duration_s": 6,
  "dialogue": "众人的尖叫声",
  "characters": ["tribe_members"],
  "emotion": "terror",
  "sfx_bgm": "SFX: scream_terror, scrambling, earth_crack. BGM: epic_orchestral(fade_in=1.5, volume=0.9)"
}
```

---

## 音效库参考

### 环境音效
- `ambient_wind` - 风声
- `ambient_rain` - 雨声
- `ambient_fire` - 火焰声
- `ambient_tribal_camp` - 营地背景

### 人物音效
- `gasp_fear` - 恐惧的喘息
- `gasp_shock` - 惊讶的喘气
- `scream_woman` - 女性尖叫
- `scream_terror` - 恐怖尖叫
- `scrambling` - 人群慌乱
- `footsteps_dirt` - 泥地脚步
- `footsteps_leaves` - 落叶脚步

### 动作音效
- `weapon_clash` - 武器碰撞
- `body_fall` - 身体摔倒
- `bone_rattle` - 骨头声响

### 超自然音效
- `supernatural_pulse` - 神秘脉动
- `energy_discharge` - 能量释放
- `earth_crack` - 地裂声

### 背景音乐
- `tribal_drums` - 部落鼓声
- `ominous_drone` - 不祥低音
- `supernatural_theme` - 神秘主题
- `emotional_strings` - 情感弦乐
- `epic_orchestral` - 史诗交响
- `tension_buildup` - 紧张递升
- `calm_ancient` - 古代安宁

---

## 故障排查

### ❌ 配音未生成

```bash
# 检查 .env 或环境变量
echo $FISH_AUDIO_API_KEY

# 如果未设置，改用 Edge TTS
pip install edge-tts
# 重新运行
```

### ❌ 音频混合失败

```bash
# 检查输入音频文件是否存在
ls episodes/ep002/audio/

# 使用 ffprobe 验证文件完整性
ffprobe episodes/ep002/audio/S01.wav
```

### ❌ BGM 不同步

```bash
# 在 manage_sfx.py 中验证时间计算
python -m pipeline.manage_sfx ep002
# 检查输出的时间轴是否正确
```

### ❌ 声音太小或太大

```python
# 调整轨道音量（0.0-1.0）
mixer.add_track(AudioTrack(
    ...,
    volume=0.8,  # 降低到 80%
))
```

---

## 关键命令速查

| 任务 | 命令 |
|------|------|
| 生成配音 | `python -m pipeline.synth_voice ep002` |
| 查看音效和 BGM | `python -m pipeline.manage_sfx ep002` |
| 生成最终视频 | `python -m pipeline.render_video ep002` |
| 测试单个 TTS | `python -c "from pipeline.synth_voice import synthesize_line; ..."` |

---

## 下一步

- ✅ 配置角色音声 → 编辑 `synth_voice.py` 的 `CHARACTER_VOICES`
- ✅ 设置 TTS API → 配置 `FISH_AUDIO_API_KEY` 或安装 `edge-tts`
- ✅ 定义音效和 BGM → 编辑 `shots.json` 的 `sfx_bgm` 字段
- ✅ 生成和混合 → 运行管线脚本
- ✅ 检查结果 → 播放 `episodes/ep002/video/final.mp4`

---

## 完整流程检查清单

- [ ] 1. 编辑 `episodes/{ep}/shots.json`
  - [ ] 所有对话镜头有 `dialogue` 和 `characters` 字段
  - [ ] 所有镜头有 `emotion` 标签
  - [ ] 关键镜头有 `sfx_bgm` 定义

- [ ] 2. 配置角色声音
  - [ ] 修改 `synth_voice.py` 中的 `CHARACTER_VOICES` （或创建 `characters.json`）
  - [ ] 测试至少一个角色

- [ ] 3. 设置 TTS
  - [ ] 选择提供商 (Fish Audio / Edge TTS / 占位符)
  - [ ] 安装必要的依赖 (`pip install edge-tts` 或 `requests`)
  - [ ] 配置 API Key（如需要）

- [ ] 4. 生成音频
  - [ ] 运行 `python -m pipeline.synth_voice {ep}`
  - [ ] 验证输出文件在 `episodes/{ep}/audio/`

- [ ] 5. 验证音效和 BGM
  - [ ] 运行 `python -m pipeline.manage_sfx {ep}`
  - [ ] 检查时间轴和参数解析

- [ ] 6. 生成最终视频
  - [ ] 运行 `python -m pipeline.render_video {ep}`
  - [ ] 播放 `episodes/{ep}/video/final.mp4` 验证音频

