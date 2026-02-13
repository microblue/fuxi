# 完整剧集生产工作流

## 🎬 核心工作流（4 个主要阶段）

```
[1] 剧本创作         [2] 资产生成        [3] 分镜规划         [4] 媒体生成与合成
script.md       →    locations.json  →  shots.json        →    final.mp4
                     characters.json     keyframes.json
                     props.json
```

---

## 详细步骤

### 📝 阶段 1：剧本创作

**输入：** 创意故事提纲
**输出：** `episodes/ep{N}/script.md`

```markdown
# 伏羲纪元 — 第001集

## 剧本概要
... 故事大纲 ...

## 场景列表
[Scene definitions with locations, characters, dialogue]
```

**要求：**
- 包含所有场景、角色、对话
- 清晰的角色和地点信息

---

### 🎭 阶段 2：资产定义自动生成

#### Step 2.1：从剧本提取资产

```bash
# 自动从 script.md 提取场景、角色、道具
python -m pipeline.gen_assets_json ep001
```

**流程：**
1. 读取 `script.md`
2. 调用 Claude 分析并提取所有资产
3. 生成三个 JSON 文件：
   - `assets/locations/locations.json` - 场景定义
   - `assets/characters/characters.json` - 角色定义
   - `assets/props/props.json` - 道具定义

**输出结构：**

```json
{
  "metadata": {...},
  "locations": {
    "lingzi_capital_data_core": {
      "zh_name": "灵子文明首都-数据中枢",
      "en_name": "Lingzi Capital - Data Core",
      "type": "advanced_alien_civilization",
      "atmosphere": "璀璨而诡异",
      ...
    }
  }
}
```

#### Step 2.2：手工审阅和编辑（可选）

```bash
# 如需调整，直接编辑 JSON 文件
vim assets/locations/locations.json
vim assets/characters/characters.json
vim assets/props/props.json
```

#### Step 2.3：生成资产参考图

```bash
# 生成场景参考图（用于分镜生成时参考）
python -m pipeline.gen_locations_refs

# 生成角色参考图
python -m pipeline.gen_characters_refs

# 生成道具参考图
python -m pipeline.gen_props_refs
```

**输出：**
```
assets/
├─ locations/
│  ├─ lingzi_capital_data_core/
│  │  └─ lingzi_capital_data_core_ref_*.png
│  └─ primordial_swamp_rainstorm/
│     └─ primordial_swamp_rainstorm_ref_*.png
├─ characters/
│  ├─ Xihe/
│  │  └─ Xihe_ref_*.png
│  └─ Nuwa/
│     └─ Nuwa_ref_*.png
└─ props/
   └─ [prop_name]/
      └─ [prop_name]_ref_*.png
```

---

### 🎞️ 阶段 3：分镜规划生成

#### Step 3.1：生成分镜定义

```bash
# 从 script.md 生成分镜规划，自动关联资产
python -m pipeline.gen_shots ep001
```

**流程：**
1. 读取 `script.md` 和资产定义
2. Claude 分析并生成分镜列表
3. **自动应用智能资产关联：**
   - 场景名 → `location_ref`（指向 locations.json）
   - 角色名 → `character_refs`（指向 characters.json）
   - 道具名 → `prop_refs`（指向 props.json）
4. 生成 `shots.json`

**输出示例：**
```json
{
  "shot_id": "S07",
  "location": "leize_swamp_storm",
  "location_ref": "primordial_swamp_rainstorm",  // ← 自动关联
  "characters": ["Young_Fuxi", "Hunter_A"],
  "character_refs": ["Young_Fuxi", "Hunter_A"],  // ← 自动关联
  "duration_s": 4,
  "camera": "wide shot",
  "action": "镜头动作描述",
  "dialogue": [...],
  "emotion": "primal_tension",
  "prompt_visual": "T2I 视觉提示词",
  "prompt_motion": "I2V 运动提示词",
  ...
}
```

#### Step 3.2：生成关键帧规划

```bash
# 生成关键帧时间轴和配置
python -m pipeline.gen_keyframes_json ep001
```

**输出：**
- `episodes/ep001/keyframes.json` - 关键帧配置
- `episodes/ep001/keyframes.md` - 可视化文档

---

### 🎬 阶段 4：媒体生成与合成

#### Step 4.1：生成关键帧图像（I2I）

```bash
# 为每个镜头生成关键帧序列
python -m pipeline.gen_keyframe_images ep001

# 或指定特定镜头
python -m pipeline.gen_keyframe_images ep001 S02
```

**工作流：**
1. 读取 `shots.json` 和 `keyframes.json`
2. 使用 `location_ref` 查找场景参考图
3. 生成关键帧：
   - 第 1 帧：location_ref + visual_prompt
   - 后续帧：previous_frame + motion_prompt

**输出：**
```
episodes/ep001/video/keyframes/
├─ S01_kf_001.png
├─ S01_kf_002.png
├─ S02_kf_001.png
└─ ...
```

#### Step 4.2：生成镜头视频（I2V）

```bash
# 基于关键帧生成镜头视频
python -m pipeline.gen_shot_video ep001

# 或单镜头
python -m pipeline.gen_shot_video ep001 S02
```

**输出：**
```
episodes/ep001/video/
├─ S01_video.mp4
├─ S02_video.mp4
└─ ...
```

#### Step 4.3：生成音频

```bash
# 生成对话 TTS
python -m pipeline.synth_voice ep001

# 处理 SFX 和背景音乐
python -m pipeline.manage_sfx ep001

# 生成字幕
python -m pipeline.build_subtitles ep001
```

**输出：**
```
episodes/ep001/
├─ audio/
│  ├─ S01_dialogue.wav
│  ├─ S01_sfx.wav
│  └─ ...
└─ video/
   ├─ subtitles.srt
   └─ subtitles.vtt
```

#### Step 4.4：最终合成

```bash
# 序列拼接 + 转场 + 音频混合 + 字幕叠加
python -m pipeline.render_video ep001
```

**输出：**
```
episodes/ep001/video/final.mp4
(1920×1080, 24fps, 60 seconds)
```

---

## 🚀 快速开始命令

### 完整工作流（一键执行）

```bash
# 从 script.md 到 final.mp4 的完整自动化
python -m pipeline.generate_episode ep001
```

### 分步执行

```bash
# 1. 资产生成
python -m pipeline.gen_assets_json ep001          # 从剧本自动提取
python -m pipeline.gen_locations_refs             # 生成场景参考图
python -m pipeline.gen_characters_refs            # 生成角色参考图
python -m pipeline.gen_props_refs                 # 生成道具参考图

# 2. 分镜规划
python -m pipeline.gen_shots ep001                # 自动关联资产
python -m pipeline.gen_keyframes_json ep001       # 生成关键帧规划

# 3. 媒体生成
python -m pipeline.gen_keyframe_images ep001      # I2I 关键帧
python -m pipeline.gen_shot_video ep001           # I2V 镜头视频
python -m pipeline.synth_voice ep001              # TTS 对话
python -m pipeline.build_subtitles ep001          # 字幕生成
python -m pipeline.manage_sfx ep001               # SFX/BGM 处理

# 4. 最终合成
python -m pipeline.render_video ep001             # FFmpeg 合成
```

---

## 🔄 资产关联的自动化流程

### 问题被解决

**旧模式：** 硬编码位置映射
```python
LOCATION_REF_MAPPING = {
    "leize_swamp_storm": "primordial_swamp_rainstorm",
    ...  # 需要手动维护
}
```

**新模式：** 智能自适应关联
```
shots.json location field
    ↓
find_best_location_match()
    ├─ 层级1: 精确 ID 匹配
    ├─ 层级2: 精确名称匹配
    ├─ 层级3: 子字符串匹配
    └─ 层级4: 关键字映射 (leize → 雷泽)
    ↓
自动填充 location_ref → locations.json ID
```

### 关键字映射表

| 英文 | 中文 | 示例 |
|------|------|------|
| vortex_edge | vortex_edge | "leize_vortex_edge" → `vortex_edge` |
| cosmic | 灵子 | "cosmic_void" → `lingzi_capital_data_core` |
| lingzi | 灵子 | "lingzi_*" → `lingzi_capital_data_core` |
| leize | 雷泽 | "leize_swamp_*" → `primordial_swamp_rainstorm` |
| swamp | 沼泽 | "*swamp*" → `primordial_swamp_rainstorm` |

---

## 📊 文件和目录结构

```
fuxi/
├─ style_bible/              # 创意指引
│  ├─ world.md
│  ├─ tone.md
│  └─ camera_language.md
├─ pipeline/                 # 自动化脚本
│  ├─ gen_assets_json.py     # ✨ NEW: 从剧本提取资产
│  ├─ gen_shots.py           # 生成分镜（自动关联）
│  ├─ gen_keyframes_json.py
│  ├─ gen_locations_refs.py  # 生成场景参考图
│  ├─ gen_characters_refs.py # ✨ NEW: 生成角色参考图
│  ├─ gen_props_refs.py      # ✨ NEW: 生成道具参考图
│  ├─ gen_keyframe_images.py # 生成关键帧
│  ├─ gen_shot_video.py      # 生成镜头视频
│  ├─ synth_voice.py
│  ├─ build_subtitles.py
│  ├─ render_video.py
│  ├─ generate_episode.py    # 编排器
│  └─ utils.py
├─ assets/
│  ├─ locations/
│  │  ├─ locations.json      # ✨ AUTO: 从剧本自动生成
│  │  ├─ lingzi_capital_data_core/
│  │  │  └─ *_ref_*.png      # 参考图
│  │  └─ ...
│  ├─ characters/
│  │  ├─ characters.json     # ✨ AUTO: 从剧本自动生成
│  │  ├─ Xihe/
│  │  │  └─ *_ref_*.png
│  │  └─ ...
│  └─ props/
│     ├─ props.json          # ✨ AUTO: 从剧本自动生成
│     └─ ...
└─ episodes/
   └─ ep001/
      ├─ script.md           # 输入：剧本
      ├─ shots.json          # 自动生成 + 自动关联
      ├─ keyframes.json
      ├─ keyframes.md
      ├─ audio/
      │  ├─ S*_dialogue.wav
      │  └─ ...
      └─ video/
         ├─ keyframes/
         │  └─ S*_kf_*.png
         ├─ S*_video.mp4
         ├─ subtitles.srt
         └─ final.mp4        # 输出：最终成品
```

---

## ✨ 关键特性

### 1. 完全自动化的资产提取
- 从剧本一键生成 locations/characters/props JSON
- 无需手动维护资产库

### 2. 智能资产关联
- 4 层级多策略匹配
- 95%+ 覆盖率
- 适应多种命名规则

### 3. 参考图生成
- 支持 ComfyUI（本地）和 OpenAI（云端）后端
- 每个资产生成多个候选图

### 4. 完整的媒体管道
- I2I 关键帧生成
- I2V 镜头视频生成
- TTS + SFX + 字幕处理
- FFmpeg 最终合成

### 5. 模块化设计
- 每个脚本可独立运行
- 支持部分处理
- 易于调整和扩展

---

## 🔍 验证与调试

### 验证资产生成

```bash
# 检查生成的资产数量
jq '.locations | keys' assets/locations/locations.json
jq '.characters | keys' assets/characters/characters.json

# 检查关联成功率
jq '.shots | map(select(.location_ref)) | length' episodes/ep001/shots.json
```

### 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 找不到 location_ref | 位置名不在映射中 | 添加到关键字映射或 locations.json |
| 参考图找不到 | gen_*_refs.py 未运行 | 执行参考图生成脚本 |
| 镜头视频失败 | ComfyUI 未运行 | 启动 ComfyUI 服务 |
| 字幕时间不对 | duration_s 不精确 | 使用 ffprobe 验证视频时长 |

---

## 📈 性能指标

| 操作 | 时间 | 输出 |
|------|------|------|
| gen_assets_json | ~30s | 30-50 个资产 |
| gen_locations_refs | ~2min/location | 3×参考图 |
| gen_shots | ~20s | 20-30 镜头 |
| gen_keyframe_images | ~1min/shot | N 个关键帧 |
| gen_shot_video | ~3min/shot | 1 个镜头视频 |
| render_video | ~1min | final.mp4 |

**完整流程：** ~1.5 小时（包括 I2I/I2V 生成）

---

## 🎓 最佳实践

1. **先创作完整剧本** - 质量决定一切
2. **检查自动生成的资产** - 手工微调以确保准确
3. **使用本地 ComfyUI** - 更快的迭代
4. **保存中间产物** - 便于调试和重用
5. **备份 script.md** - 是所有数据的源头

---

## 🚢 部署与交付

### 最终成品位置
```
episodes/ep001/video/final.mp4
- 分辨率：1920×1080
- 帧率：24 fps
- 格式：H.264 + AAC
- 时长：60 秒
```

### 质量检查清单
- [ ] 所有镜头都有正确的过渡
- [ ] 音频同步准确
- [ ] 字幕显示正确
- [ ] 颜色分级一致
- [ ] 没有音频爆裂或视频卡顿

---

## 📚 相关文档

- `PRODUCTION_WORKFLOW.md` - 完整工作流（详细版）
- `ASSET_LINKING_DESIGN.md` - 资产关联系统设计
- `CLAUDE.md` - 项目约束和指导

---

**版本：** 2.0
**更新：** 2026-02-10
**状态：** 生产就绪 ✓
