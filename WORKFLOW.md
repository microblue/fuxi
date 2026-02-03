# 伏羲纪元 — 完整生产工作流

## 整体架构

```
[Script (script.md)]
        ↓
[LLM 分镜规划 (shots.json)]
        ↓
[Keyframe JSON (prompt_visual + metadata)]
        ↓
[Prompt Generator (utils.parse_prompt_file)]
        ↓
[Flux 批量出图 (generate_shot_images.py)]
        ↓
[Keyframe 图片库 (episodes/{id}/video/S*_gen_*.png)]
        ↓
[LTX-2 补间 (generate_episode_videos.py)]
        ↓
[视频素材库 (episodes/{id}/video/S*_video.mp4)]
        ↓
[最终合成 (render_video.py)]
        ↓
[final.mp4 + 音频混合]
```

---

## Phase 1: 脚本输入

**文件:** `episodes/{episode_id}/script.md`

剧本包含：
- 人物台词与情感标注
- 场景描述
- 节奏标记

---

## Phase 2: 分镜规划 (LLM Shot Planning)

**文件:** `episodes/{episode_id}/shots.json`

### 核心数据结构

```json
{
  "episode": "ep001",
  "format": {
    "resolution": "1920x1080",
    "aspect_ratio": "16:9",
    "fps": 24
  },
  "transitions": {
    "S05->S06": {"type": "fadewhite", "dur": 0.5},
    "S08->S09": {"type": "dissolve", "dur": 0.5}
  },
  "shots": [
    {
      "shot_id": "S01",
      "duration_s": 3.0,
      "location": "lingzi_normal",
      "characters": ["Fuxi"],
      "camera": "wide shot, establishing",
      "action": "city lights flicker",
      "dialogue": "什么情况？",
      "emotion": "confusion",
      "prompt_visual": "[From style_bible + shot details]",
      "prompt_motion": "[LTX-2 motion prompt]",
      "speed": 1.0,           // 慢动作倍数 (0.5 = 2x slow)
      "trim_start": 0.0,      // 从头裁剪秒数
      "trim_end": null        // 到尾裁剪秒数
    }
  ]
}
```

### 关键字段说明

| 字段 | 用途 | 示例 |
|------|------|------|
| `shot_id` | 镜头编号 | S01, S02 |
| `duration_s` | 目标时长 | 2.5 |
| `location` | 场景ID | lingzi_normal, swamp_storm |
| `characters` | 参演角色 | ["Fuxi", "Entity"] |
| `camera` | 景别/运镜 | wide shot, close-up |
| `action` | 画面动作 | hand reaches crystal |
| `dialogue` | 台词 | 女娲在吗？ |
| `emotion` | 情绪标签 | fear, determination |
| `prompt_visual` | T2I提示词 | [完整Flux提示] |
| `prompt_motion` | I2V提示词 | [完整LTX-2提示] |
| `speed` | 速度倍数 | 0.5 (2x slow) |
| `transitions` | 转场配置 | {type, dur} |

---

## Phase 3: 关键帧JSON生成

**输出:** `episodes/{episode_id}/shots.json` (包含 prompt_visual + prompt_motion)

### 提示词生成规则

根据 `style_bible/prompt_templates.md` 中的模块化结构：

```
[STYLE PREFIX]
cinematic film still, photorealistic, 16:9 horizontal aspect ratio,
movie quality lighting, shallow depth of field

[CHARACTER PREFIX]
(从角色卡提取外貌、服装特征)

[LOCATION PREFIX]
(从场景卡提取环境、照明、氛围)

[SHOT ACTION]
(从 shots.json action 字段)

[CAMERA LANGUAGE]
(从 shots.json camera 字段)

[LIGHTING]
(根据 emotion 和 action)

[MOOD]
(根据 emotion 字段)
```

### 示例

```json
{
  "shot_id": "S03",
  "prompt_visual": "cinematic film still, photorealistic, 16:9 horizontal aspect ratio, movie quality lighting, shallow depth of field, epic sci-fi meets ancient mythology aesthetic, data-punk visual style, young male age 16, angular face, long black hair half-tied, dark brown fur vest, barefoot, dark swamp at night, rain, glowing silver-blue vortex in water, hand touching translucent crystal, golden data streams erupting from crystal flowing up arm like glowing veins, extreme close-up hand → face, dynamic cut, golden energy burst from crystal illuminating face from below, shock, searing pain, transformation, point of no return",

  "prompt_motion": "hand slowly moves toward glowing crystal in dark swamp water, fingers touch surface, explosive golden light burst erupts upward, energy cascades along arm like liquid fire, face recoils in pain and wonder, left eye flares with intense golden light, camera pulls back revealing character in full body convulsion"
}
```

---

## Phase 4: Prompt Generator (文本处理)

**工具函数:** `pipeline/utils.parse_prompt_file()`

### 支持的格式

#### 格式 1: 结构化标记
```
[POSITIVE PROMPT]
cinematic film still...

[NEGATIVE PROMPT]
anatomy error, face distortion...
```

#### 格式 2: 图像/视频提示分离
```
[IMAGE PROMPT]
cinematic scene...

[VIDEO PROMPT]
motion description...

[NEGATIVE]
artifacts, distortion...
```

#### 格式 3: 单一提示
```
cinematic film still, photorealistic...
(entire file treated as positive)
```

### 默认负向提示

```
anatomy error, face distortion, extra limbs, extra fingers, watermark, text artifacts,
oversharpen, uncanny look, blurry, low quality, cartoon, anime, illustration style,
deformed face, asymmetric eyes, bad proportions, cropped, out of frame
```

---

## Phase 5: Flux 批量出图 (T2I Generation)

**脚本:** `pipeline/generate_shot_images.py`

### 工作流

```python
for shot in shots_data["shots"]:
    prompt_visual = shot["prompt_visual"]

    for i in range(num_candidates):  # 默认3张
        seed = random.randint(0, 2^31-1)

        image = ComfyUIImageGen().generate(
            prompt=prompt_visual,
            output_path=f"{episode_id}/video/{shot_id}_gen_{i:03d}_seed{seed}.png",
            size="1344x768",      # 16:9 horizontal
            quality="high"
        )
```

### 调用方式

```bash
# 全episode
python -m pipeline.generate_shot_images ep001

# 特定镜头
python -m pipeline.generate_shot_images ep001 S03 S04

# 自定义候选数
python -m pipeline.generate_shot_images ep001 --num-candidates 5
```

### 输出

```
episodes/ep001/video/
├── S01_gen_001_seed12345.png
├── S01_gen_002_seed67890.png
├── S01_gen_003_seed11111.png
├── S02_gen_001_seed22222.png
...
```

---

## Phase 6: Keyframe 图片库

**位置:** `episodes/{episode_id}/video/S*_gen_*.png`

### 用途

- 供视频编导人工选择最佳候选
- 作为 LTX-2 I2V 的输入 keyframe
- 存档用于质量审核

### 命名约定

```
{shot_id}_gen_{num:03d}_seed{seed}.png

S01_gen_001_seed42.png    # 第1个候选，seed=42
S01_gen_002_seed999.png   # 第2个候选，seed=999
```

---

## Phase 7: LTX-2 补间 (I2V Generation)

**脚本:** `pipeline/generate_episode_videos.py` / `pipeline/generate_shot_video.py`

### 工作流

```
输入 Keyframe (S01_gen_001_seed42.png)
         ↓
LTX-2 I2V 工作流
         ↓
输出视频 (S01_video.mp4, 1344×768, ~4.8s)
```

### 配置参数

- **帧数:** 121 (@ 25fps = 4.84s)
- **分辨率:** 1344×768 (16:9)
- **Stage 1:** Euler + CFG=4.0, 20 steps
- **Stage 2:** Gradient estimation + DistilledLoRA, 4 steps

### 调用方式

```bash
# 单镜头生成
python -m pipeline.generate_shot_video ep001 S01 \
  --input-image video/S01_gen_001_seed42.png \
  --frames 121 \
  --seed1 42 --seed2 420

# 全episode批量生成
python -m pipeline.generate_episode_videos ep001

# 特定镜头批量生成
python -m pipeline.generate_episode_videos ep001 S03 S04 S05
```

### 输出

```
episodes/ep001/video/
├── S01_video.mp4
├── S02_video.mp4
├── S03_video.mp4
...
```

---

## Phase 8: 最终合成 (Video Composition)

**脚本:** `pipeline/render_video.py`

### 工作流 (5个阶段)

#### 阶段 1: 规格化镜头
```
源视频 (various resolutions)
   ↓
Scale → Pad → 1920×1080 @ 24fps
   ↓
Normalized shots (video/temp_compose/S*.mp4)
```

支持：
- 速度调整 (`speed` 字段，0.5 = 2x slow)
- 裁剪 (`trim_start`, `trim_end` 字段)

#### 阶段 2: 转场规划
从 `shots.json` 的 `transitions` 字段读取：
```json
{
  "S01->S02": {"type": "hard_cut", "dur": 0},
  "S02->S03": {"type": "fadewhite", "dur": 0.5},
  "S03->S04": {"type": "dissolve", "dur": 0.5}
}
```

支持的转场类型：
- `hard_cut` (立即切换)
- `fadewhite` (淡白色过渡)
- `dissolve` (溶解)
- `xfade` (通用交叉淡出)

#### 阶段 3: 组内硬切拼接
```
[S01] --hard_cut--> [S02] --hard_cut--> [S03]
           ↓
        Group 1
        (concat)

[Group 1] --fadewhite--> [S04] --hard_cut--> [S05]
                            ↓
                        Group 2
```

#### 阶段 4: 组间转场 (xfade)
```
[Group 1] (5.2s)
    ↓
xfade(duration=0.5s, offset=4.7s)
    ↓
[Group 2] (3.1s)
    ↓
[Final video with transitions]
```

#### 阶段 5: 音频混合
```
Video track (无声)
   +
Audio S01 (adelay 0ms)
   +
Audio S02 (adelay 3000ms)
   +
Audio S03 (adelay 5200ms)
   ↓
amix (normalize=0)
   ↓
final.mp4 (video + audio)
```

### 调用方式

```bash
python -m pipeline.render_video ep001
```

### 输出

```
episodes/ep001/video/final.mp4
```

### 报告

```
========================================
✅ 合成完毕
   输出: episodes/ep001/video/final.mp4
   时长: 45.3s (0.8 min)
   大小: 285.7 MB
   镜头: 20
========================================

时间轴:
    0.00s  🔊  S01  (3.00s)
    3.00s  🔊  S02  (2.50s)
    5.50s     S03  (2.00s)
    ...
```

---

## Phase 9: 音频混合 & 最终输出

**工具:** FFmpeg (amix + aac编码)

### 音频搜索规则

```python
# 对于每个镜头 shot_id:
# 1. 查找 {shot_id}.wav
# 2. 查找 {shot_id}_narration.wav
# 3. 应用 adelay = shot_start_time * 1000 ms
```

### 最终输出规格

```
episodes/{episode_id}/video/final.mp4

规格:
  ✓ 分辨率: 1920×1080
  ✓ 帧率: 24fps
  ✓ 编码: H.264 (libx264, crf=18)
  ✓ 音频: AAC, 192kbps
  ✓ 容器: MP4 (+faststart)
```

---

## 完整Pipeline 执行

### 单命令执行全流程

```bash
python -m pipeline.generate_episode ep001
```

执行顺序：

```
[0] 目录验证
[1] 文件验证 (script.md, shots.json)
[2] 图片生成 (T2I)          ← generate_shot_images.py
[3] 语音合成                ← synth_voice.py
[4] 字幕生成                ← build_subtitles.py
[5] 视频生成 (I2V, 可选)    ← generate_episode_videos.py (手动)
[6] 视频合成                ← render_video.py
[7] 日志输出                → episodes/ep001/video/render_log.txt
```

### 流程图

```
start
  ↓
[validate_episode]
  ├─ script.md 存在?
  └─ shots.json 格式正确?
  ↓
[generate_shot_images]
  ├─ 读取 shots.json
  ├─ 提取 prompt_visual
  └─ 调用 Flux 生成 T2I 候选
  ↓
[synth_voice]
  ├─ 遍历所有 shots
  ├─ TTS 合成音频
  └─ 输出 {shot_id}.wav
  ↓
[generate_srt]
  ├─ 读取 dialogue / subtitle
  └─ 生成时间对齐字幕
  ↓
[generate_episode_videos (可选)]
  ├─ 选择最佳 keyframe
  ├─ 调用 LTX-2 I2V
  └─ 输出 {shot_id}_video.mp4
  ↓
[render_video]
  ├─ 规格化镜头
  ├─ 应用转场
  ├─ 拼接视频
  ├─ 混合音频
  └─ 输出 final.mp4
  ↓
end
```

---

## 配置文件清单

| 文件 | 角色 | 更新频率 |
|------|------|---------|
| `episodes/{id}/script.md` | 原始剧本 | 每剧集一次 |
| `episodes/{id}/shots.json` | 分镜规划 + 配置 | 每次迭代 |
| `style_bible/prompt_templates.md` | Prompt模板 | 定期优化 |
| `style_bible/character_templates.md` | 角色卡 | 按需更新 |
| `pipeline/utils.py` | 共享工具函数 | 按需扩展 |

---

## 环境依赖

```
系统工具:
  ✓ ffmpeg (视频处理)
  ✓ ffprobe (时长检测)

Python 库:
  ✓ creative-toolkit (Flux 图片生成)
  ✓ ComfyUI HTTP API (LTX-2 视频生成)
  ✓ pydantic (数据验证)
  ✓ pathlib (路径操作)
```

---

## 最佳实践

### 1. Prompt 工程

- 始终使用 `style_bible/prompt_templates.md` 中的模块化结构
- 在 `[NEGATIVE PROMPT]` 中包含完整的负向提示
- 根据 `emotion` 字段调整光线和氛围

### 2. 视频参数

- **标准设置:** 1920×1080, 24fps, ~3-5s per shot
- **慢动作:** 使用 `speed: 0.5` (不要修改 `duration_s`)
- **转场:** 保持 <= 0.5s (太长会破坏节奏)

### 3. 质量检查

- 生成后检查 `render_log.txt` 中的时间轴
- 验证所有音频已正确延迟
- 检查最终 `final.mp4` 的时长与预期相符

### 4. 迭代工作流

```
1. 调整 shots.json (prompt, transitions, speed)
   ↓
2. 重新生成受影响的阶段 (T2I / I2V)
   ↓
3. 运行 render_video 进行最终合成
   ↓
4. 审查 final.mp4
   ↓
5. 如不满意，返回步骤 1
```

---

## 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `No video output for S01` | I2V 失败 | 检查 keyframe 质量，重试 |
| `Duration mismatch` | 调整未应用 | 验证 `speed` / `trim_*` 字段 |
| `Audio out of sync` | 时间轴计算错误 | 检查 transitions 配置 |
| `ffmpeg: unknown encoder` | 编码器缺失 | `apt install ffmpeg` |

---

## 版本控制

```
.gitignore:
  ✓ episodes/*/video/*.mp4    (视频文件)
  ✓ episodes/*/video/temp_*   (临时文件)
  ✓ episodes/*/audio/*.wav    (音频文件)
  ✓ episodes/*/video/final.mp4 (最终输出)

提交内容:
  ✓ script.md
  ✓ shots.json
  ✓ prompts/*.txt
  ✓ report.md
```

---

## 下一步扩展

- [ ] GPU 加速 (CUDA 并行生成)
- [ ] 色彩分级 (LUT 应用)
- [ ] 字幕烧录 (ASS/SRT 集成)
- [ ] 背景音乐混合 (BGM 轨道)
- [ ] 动态渲染 (实时预览)

---

**最后更新:** 2026-02-02
**Pipeline 版本:** 2.0 (Post-Migration)
**状态:** 生产就绪 ✅
