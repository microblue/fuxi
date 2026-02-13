# 伏羲纪元 — 完整制作工作流

这是完整的 AI 短剧制作管道，从资产定义到最终视频渲染。

## 工作流概览

```
┌─────────────────────────────────────────────────────────────────────┐
│  阶段 1：基础资产定义                                               │
├─────────────────────────────────────────────────────────────────────┤
│  ✅ assets/locations/locations.json      (场景/环境定义)           │
│  ✅ assets/characters/characters.json    (角色定义)               │
│  ✅ assets/props/props.json              (道具定义)               │
│  ✅ episodes/ep{N}/script.md             (剧本文本)               │
└─────────────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────────────┐
│  阶段 2：分镜规划                                                   │
├─────────────────────────────────────────────────────────────────────┤
│  📝 python -m pipeline.gen_shots ep001                              │
│     → episodes/ep001/shots.json                                     │
│        (包含 location_ref 字段指向 locations.json)                 │
│  📊 python -m pipeline.gen_keyframes_json ep001                     │
│     → episodes/ep001/keyframes.json                                 │
└─────────────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────────────┐
│  阶段 3：资产参考图生成 (T2I)                                       │
├─────────────────────────────────────────────────────────────────────┤
│  🖼️ python -m pipeline.gen_locations_refs                          │
│     → assets/locations/{location_id}/*_ref_*.png                   │
│  👤 python -m pipeline.gen_characters_refs                         │
│     → assets/characters/{character_id}/*_ref_*.png                 │
│  🎭 python -m pipeline.gen_props_refs                              │
│     → assets/props/{prop_id}/*_ref_*.png                           │
└─────────────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────────────┐
│  阶段 4：关键帧图生成 (I2I)                                         │
├─────────────────────────────────────────────────────────────────────┤
│  🎞️ python -m pipeline.gen_keyframe_images ep001 {shot_id}         │
│     → episodes/ep001/video/keyframes/{shot_id}_kf_*.png            │
│     (使用 location_ref 查找场景参考，基于 prompt 生成关键帧)       │
└─────────────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────────────┐
│  阶段 5：镜头视频生成 (I2V)                                         │
├─────────────────────────────────────────────────────────────────────┤
│  🎬 python -m pipeline.gen_shot_video ep001 {shot_id}              │
│     → episodes/ep001/video/{shot_id}_video.mp4                     │
│     (基于关键帧和 prompt_motion 生成运动视频)                      │
│     ⚙️ 支持转场配置、速度调整、裁剪                                │
└─────────────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────────────┐
│  阶段 6：音频处理                                                   │
├─────────────────────────────────────────────────────────────────────┤
│  🎙️ python -m pipeline.synth_voice ep001                           │
│     → episodes/ep001/audio/{shot_id}_dialogue.wav                  │
│     (基于 shots.json 的 dialogue 字段生成 TTS)                     │
│  🔊 python -m pipeline.manage_sfx ep001                            │
│     → episodes/ep001/audio/{shot_id}_sfx.wav                       │
│     (SFX 和背景音乐管理)                                            │
│  📝 python -m pipeline.build_subtitles ep001                       │
│     → episodes/ep001/video/subtitles.srt                           │
│     (生成字幕文件)                                                  │
└─────────────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────────────┐
│  阶段 7：最终合成 (FFmpeg)                                          │
├─────────────────────────────────────────────────────────────────────┤
│  🎬 python -m pipeline.render_video ep001                          │
│     → episodes/ep001/video/final.mp4                               │
│     • 序列拼接（硬切/转场）                                         │
│     • 音频混合（对白 + SFX + BGM）                                  │
│     • 字幕叠加                                                      │
│     • 分辨率：1920x1080 @ 24fps                                     │
└─────────────────────────────────────────────────────────────────────┘
              ↓
           ✨ FINAL.MP4 ✨
```

---

## 详细命令手册

### 1️⃣ 分镜规划

#### 生成 shots.json（从 script.md）
```bash
# 交互模式（推荐，可审阅每个镜头）
python -m pipeline.gen_shots ep001

# 自动模式（无交互直接保存）
python -m pipeline.gen_shots ep001 --auto

# 使用特定模型
python -m pipeline.gen_shots ep001 --model sonnet
```

**输出：**
- `episodes/ep001/shots.json`
  - 包含 20-30 个结构化镜头
  - 自动添加 `location_ref` 字段（指向 locations.json）
  - 包含所有视觉 / 运动提示词

#### 生成 keyframes.json
```bash
python -m pipeline.gen_keyframes_json ep001
```

**输出：**
- `episodes/ep001/keyframes.json` - 关键帧时间轴和配置
- `episodes/ep001/keyframes.md` - 可视化文档

---

### 2️⃣ 资产参考图生成

#### 场景参考图
```bash
# 本地 ComfyUI（默认）
python -m pipeline.gen_locations_refs

# 云端 SeaDream
python -m pipeline.gen_locations_refs --backend seadream

# 指定特定场景
python -m pipeline.gen_locations_refs "primordial_swamp_rainstorm"

# 生成多个候选
python -m pipeline.gen_locations_refs --num-candidates 5
```

**输出：**
- `assets/locations/{location_id}/{location_id}_ref_001.png` 等

#### 角色参考图
```bash
# 生成所有角色
python -m pipeline.gen_characters_refs

# 指定角色
python -m pipeline.gen_characters_refs Xihe Nuwa

# 云端生成
python -m pipeline.gen_characters_refs --backend seadream --num-candidates 3
```

**输出：**
- `assets/characters/{character_id}/{character_id}_ref_001.png` 等

#### 道具参考图
```bash
# 生成所有道具
python -m pipeline.gen_props_refs

# 指定道具（支持中文或键）
python -m pipeline.gen_props_refs 灵子 光盘

# 更多候选
python -m pipeline.gen_props_refs --num-candidates 5
```

**输出：**
- `assets/props/{prop_id}/{prop_id}_ref_001.png` 等

---

### 3️⃣ 关键帧图生成

#### 单镜头关键帧
```bash
# 生成特定镜头的关键帧序列
python -m pipeline.gen_keyframe_images ep001 S02

# 所有镜头
python -m pipeline.gen_keyframe_images ep001

# 指定生成数量
python -m pipeline.gen_keyframe_images ep001 S02 --num-candidates 5
```

**工作流：**
1. 读取 `shots.json` 中的 `location_ref` 字段
2. 在 `assets/locations/{location_ref}/` 中查找参考图
3. 第 1 帧：`location_ref + visual_prompt` (I2I, denoise=0.7)
4. 后续帧：`previous_frame + motion_prompt` (I2I, denoise=0.5)

**输出：**
- `episodes/ep001/video/keyframes/{shot_id}_kf_001.png` 等

---

### 4️⃣ 镜头视频生成

#### I2V 视频生成（基于关键帧）
```bash
# 单镜头
python -m pipeline.gen_shot_video ep001 S02

# 全部镜头（有超时和重试）
python -m pipeline.gen_shot_video ep001

# 使用不同速度（支持 0.5-2.0）
python -m pipeline.gen_shot_video ep001 S02 --speed 0.75
```

**配置参数（来自 shots.json）：**
- `duration_s` - 镜头时长
- `speed` - 时间缩放（0.5 = 2x 慢放）
- `trim_start` / `trim_end` - 帧裁剪（秒数）
- `prompt_motion` - I2V 运动描述

**输出：**
- `episodes/ep001/video/{shot_id}_video.mp4`

---

### 5️⃣ 音频处理

#### TTS 合成
```bash
# 生成全部对话音频
python -m pipeline.synth_voice ep001

# 特定镜头
python -m pipeline.synth_voice ep001 S02

# 指定速度（0.5-2.0）
python -m pipeline.synth_voice ep001 S02 --speed 1.2
```

**输出：**
- `episodes/ep001/audio/{shot_id}_dialogue.wav`

#### 字幕生成
```bash
python -m pipeline.build_subtitles ep001
```

**输出：**
- `episodes/ep001/video/subtitles.srt` (SRT 格式)
- `episodes/ep001/video/subtitles.vtt` (WebVTT 格式)

#### SFX 和背景音乐
```bash
python -m pipeline.manage_sfx ep001
```

**配置来自 shots.json：**
- `sfx_bgm` - 特效音和背景音乐描述

---

### 6️⃣ 最终合成

#### 完整渲染
```bash
# 标准合成（转场、音频混合、字幕）
python -m pipeline.render_video ep001

# 仅合成视频（无字幕）
python -m pipeline.render_video ep001 --no-subtitles

# 使用预设转场配置
python -m pipeline.render_video ep001 --transition-preset dramatic
```

**转场配置（shots.json）：**
```json
{
  "transitions": {
    "S05->S06": {"type": "fadewhite", "duration": 0.5},
    "S08->S09": {"type": "dissolve", "duration": 0.3}
  },
  "shots": [
    {
      "shot_id": "S05",
      "transition_out": "fade_out",
      "transition_duration_s": 0.5,
      ...
    }
  ]
}
```

**支持的转场类型：**
- `cut` / `hard_cut` - 硬切（无过渡）
- `fade` / `fade_out` - 黑色淡出
- `dissolve` - 溶解
- `fadewhite` - 白色淡出
- `xfade` - 交叉淡出

**输出：**
- `episodes/ep001/video/final.mp4` - 完整成品

---

## 📋 shots.json Schema（关键字段）

```json
{
  "episode": "ep001",
  "shots": [
    {
      "shot_id": "S01",
      "location": "lingzi_capital_skyline",
      "location_ref": "lingzi_capital_data_core",  // ← 新增
      "duration_s": 4,
      "characters": ["Xihe"],
      "camera": "extreme wide shot",
      "action": "...",
      "dialogue": [...],
      "emotion": "awe_to_dread",
      "prompt_visual": "...",
      "prompt_motion": "...",
      "transition_out": "cut",
      "transition_duration_s": 0,
      "sfx_bgm": "...",
      "speed": 1.0,         // 新增（可选）
      "trim_start": 0,      // 新增（可选）
      "trim_end": null      // 新增（可选）
    }
  ]
}
```

### location_ref 的作用

**为什么需要 location_ref？**
- `location`：这个镜头在故事中的名称（可能因集而异）
  - 例："leize_swamp_storm"（第一集的命名）
- `location_ref`：标准化的位置 ID（来自 locations.json）
  - 例："primordial_swamp_rainstorm"（全局统一 ID）

**好处：**
1. 跨集重用场景资产（同一场景在多集出现）
2. 自动查找参考图：`assets/locations/{location_ref}/`
3. 支持多种命名约定的转换
4. 关键帧生成时精确匹配场景信息

---

## 🔧 完整编排器

### 一键运行整个管道
```bash
# 从 script.md 到 final.mp4 的完整流程
python -m pipeline.generate_episode ep001

# 交互模式（逐步确认）
python -m pipeline.generate_episode ep001 --interactive
```

### generate_episode.py 流程
1. 读取 `script.md`
2. 生成 `shots.json`（自动添加 location_ref）
3. 生成 `keyframes.json`
4. 生成所有关键帧图
5. 生成所有镜头视频
6. 合成音频（对话 + SFX + BGM）
7. 最终渲染（带字幕）

---

## 📁 目录结构

```
fuxi/
├─ style_bible/                   # 创意资产库
│  ├─ world.md
│  ├─ tone.md
│  └─ camera_language.md
├─ pipeline/                      # 脚本和工具
│  ├─ gen_shots.py               # ✅ 自动添加 location_ref
│  ├─ gen_keyframes_json.py
│  ├─ gen_locations_refs.py      # 场景参考图
│  ├─ gen_characters_refs.py     # ✅ 新增
│  ├─ gen_props_refs.py          # ✅ 新增
│  ├─ gen_keyframe_images.py     # ✅ 使用 location_ref
│  ├─ gen_shot_video.py
│  ├─ synth_voice.py
│  ├─ build_subtitles.py
│  ├─ render_video.py
│  ├─ generate_episode.py        # 编排器
│  └─ utils.py
├─ assets/
│  ├─ locations/
│  │  ├─ locations.json          # ✅ 现已有 28 个全局位置 ID
│  │  ├─ lingzi_capital_data_core/
│  │  │  └─ lingzi_capital_data_core_ref_*.png
│  │  └─ primordial_swamp_rainstorm/
│  │     └─ primordial_swamp_rainstorm_ref_*.png
│  ├─ characters/
│  │  ├─ characters.json         # ✅ 现已有全部角色定义
│  │  ├─ Xihe/
│  │  │  └─ Xihe_ref_*.png       # ✅ 新增（由 gen_characters_refs.py 生成）
│  │  └─ Nuwa/
│  │     └─ Nuwa_ref_*.png
│  └─ props/
│     ├─ props.json              # ✅ 现已有 10+ 个道具定义
│     ├─ 灵子/
│     │  └─ 灵子_ref_*.png        # ✅ 新增（由 gen_props_refs.py 生成）
│     └─ 光盘/
│        └─ 光盘_ref_*.png
└─ episodes/
   └─ ep001/
      ├─ script.md
      ├─ shots.json              # ✅ 现有 location_ref 字段
      ├─ keyframes.json
      ├─ keyframes.md
      ├─ audio/
      │  ├─ S01_dialogue.wav
      │  ├─ S01_sfx.wav
      │  └─ ...
      └─ video/
         ├─ keyframes/
         │  ├─ S01_kf_001.png
         │  └─ ...
         ├─ S01_video.mp4
         ├─ S02_video.mp4
         ├─ ...
         ├─ subtitles.srt
         └─ final.mp4            # ✅ 最终成品
```

---

## 最近更新 (2026-02-10)

### ✅ 已完成

1. **location_ref 字段添加**
   - ✅ 手动添加到 `episodes/ep001/shots.json` 所有 20 个 shots
   - ✅ 创建位置映射字典（支持跨集场景重用）

2. **gen_shots.py 自动化**
   - ✅ 添加 `LOCATION_REF_MAPPING` 字典
   - ✅ 新增 `apply_location_refs()` 函数
   - ✅ 生成新 shots.json 时自动填充 location_ref

3. **gen_keyframe_images.py 优化**
   - ✅ 改为优先使用 `location_ref` 查找参考图
   - ✅ 保持 `location` 的向后兼容性

4. **角色和道具参考图脚本** ✨ NEW
   - ✅ `gen_characters_refs.py` - 生成角色肖像
   - ✅ `gen_props_refs.py` - 生成道具渲染
   - ✅ 支持 ComfyUI 和 SeaDream 后端选择
   - ✅ 支持批量生成多个候选

---

## 故障排查

### Q1: gen_keyframe_images.py 找不到场景参考图
**原因：** location_ref 对应的场景目录中没有参考图
**解决：**
```bash
# 确认场景参考图已生成
ls assets/locations/{location_ref}/
# 如果没有，先生成：
python -m pipeline.gen_locations_refs
```

### Q2: shots.json 中 location 不匹配 locations.json
**原因：** 位置名称不在 LOCATION_REF_MAPPING 中
**解决：**
```bash
# 查看所有已定义的位置
jq '.locations | keys' assets/locations/locations.json
# 在 pipeline/gen_shots.py 中添加新的映射
```

### Q3: 字幕时间不对齐
**原因：** `shots.json` 中的 `duration_s` 不精确
**解决：**
```bash
# 手动调整 duration_s 或使用视频分析：
ffprobe -v error -select_streams v:0 \
  -show_entries format=duration episodes/ep001/video/{shot_id}_video.mp4
```

---

## 生成工作流检查清单

- [ ] ✅ `locations.json` 已定义所有场景
- [ ] ✅ `characters.json` 已定义所有角色
- [ ] ✅ `props.json` 已定义所有道具
- [ ] ✅ `script.md` 已准备完成
- [ ] 运行 `gen_shots.py` → 生成 `shots.json` (带 location_ref)
- [ ] 运行 `gen_keyframes_json.py` → 生成 `keyframes.json`
- [ ] 运行 `gen_locations_refs.py` → 生成场景参考图
- [ ] 运行 `gen_characters_refs.py` → 生成角色参考图
- [ ] 运行 `gen_props_refs.py` → 生成道具参考图
- [ ] 运行 `gen_keyframe_images.py` → 生成关键帧
- [ ] 运行 `gen_shot_video.py` → 生成镜头视频
- [ ] 运行 `synth_voice.py` → 生成对话音频
- [ ] 运行 `build_subtitles.py` → 生成字幕
- [ ] 运行 `manage_sfx.py` → 处理 SFX/BGM
- [ ] 运行 `render_video.py` → 最终合成

✨ **成品：** `episodes/ep001/video/final.mp4`

---

*Last updated: 2026-02-10*
