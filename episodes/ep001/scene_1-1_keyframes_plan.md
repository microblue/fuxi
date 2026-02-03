# 场景 1-1 关键帧生成计划

## 场景信息
- **名称**: 灵子文明首都·数据中枢
- **时间**: 毁灭时刻
- **镜头**: S01 → S02 → S03 → S04 → S05
- **总时长**: 16s
- **T2I关键帧**: 5个

---

## 关键帧生成清单

### 1️⃣ S01-KF1 | 3秒 | 城市开场 → 危机

**情感**: awe turning to dread
**镜头描述**: 极致璀璨的未来都市。建筑由光构成，数据河流在空中流淌。突然，所有光芒开始抽搐，城市响起刺耳警报。

**T2I Prompt**:
```
breathtaking futuristic city built entirely of light, luminous architecture,
rivers of data flowing through the sky between buildings, suddenly all light
begins glitching and stuttering, piercing alarm, city-scale emergency,
vertical 9:16 framing
```

**关键视觉元素**:
- ✨ 光构建的未来建筑
- 🌊 空中数据河流
- ⚡ 灯光抽搐效果
- 🚨 警报视觉提示

**生成参数**:
```
Size: 1344×768 (16:9)
Steps: 20
Seed: 0
Guidance: 1.0 (Flux 2)
```

**后续I2V帧**:
- S01-KF2 (1.5s) - 数据流动画
- S01-KF3 (3.0s) - 警报加强

---

### 2️⃣ S02-KF1 | 3秒 | 羲和登场

**情感**: focused urgency
**镜头描述**: 羲和（30岁，身着流光长袍，左眼有金色纹路）站在中枢塔顶，手指在空中快速滑动，金色数据流随指尖飞舞。

**T2I Prompt**:
```
man age 30 in flowing luminous robe standing atop central tower, golden
patterns on left eye, fingers rapidly swiping through air, golden data
streams following fingertips, city glitching in background, dramatic lighting
```

**关键视觉元素**:
- 👨 男性角色（30岁，东方面孔）
- 👗 流光长袍（科幻风格）
- 👁️ 左眼金色纹路（八卦花纹）
- ✨ 金色数据流围绕手指
- 🏗️ 背景中枢塔顶

**生成参数**:
```
Size: 1344×768 (16:9)
Steps: 20
Seed: 1000
Guidance: 1.0
```

**后续I2V帧**:
- S02-KF2 (3.0s) - 手指舞蹈动作

---

### 3️⃣ S03-KF1 | 3秒 | 特写决断

**情感**: resolute courage, noble sacrifice
**镜头描述**: 羲和微笑，从容决断。

**T2I Prompt**:
```
close-up of 30-year-old man with golden patterns on left eye, luminous robe,
calm determined smile, golden data reflections on face, city alarm lights
in background
```

**关键视觉元素**:
- 😊 微笑表情（坚定、温和）
- 👁️ 左眼金色纹路清晰可见
- 💫 脸部金色数据反光
- 🎬 特写/近景（脸部占画面60%）
- 🔴 背景警报灯闪烁

**生成参数**:
```
Size: 1344×768 (16:9)
Steps: 20
Seed: 2000
Guidance: 1.0
```

**后续I2V帧**:
- S03-KF2 (3.0s) - 微笑维持 → 坚定表情

---

### 4️⃣ S04-KF1 | 4秒 | 能量爆发

**情感**: epic sacrifice, cosmic scale
**镜头描述**: 羲和将双手按在控制台，全身数据被抽取。城市中心升起一道通天光柱，分裂为亿万光点洒向宇宙。最后一刻，一个光点中隐约可见八卦图案。

**T2I Prompt**:
```
man pressing both hands on holographic console, luminous data being extracted
from entire body creating flowing light trails, massive light pillar erupting
from city center reaching into sky, pillar fragmenting into billions of light
points scattering into cosmos, one light point contains faint bagua pattern
```

**关键视觉元素**:
- 🙌 双手按在全息控制台上
- 💫 全身能量被抽取（向上流动）
- 🌈 光柱通天（宇宙尺度）
- ✨ 光柱分裂为数十亿光点
- ☯️ 某个光点中的八卦图案（伏线）
- 🌌 背景宇宙空间视角

**生成参数**:
```
Size: 1344×768 (16:9)
Steps: 20
Seed: 3000
Guidance: 1.0
```

**后续I2V帧**:
- S04-KF2 (2.0s) - 数据上升 → 光柱形成
- S04-KF3 (4.0s) - 光柱扩散 → 光点散射

---

### 5️⃣ S05-KF1 | 3秒 | 温柔消散

**情感**: tender farewell, bittersweet
**镜头描述**: 羲和身体逐渐透明，面带微笑说出最后的话。彻底消散。

**T2I Prompt**:
```
close-up of man's face becoming transparent and dissolving into light particles,
gentle smile, golden eye patterns fading, body dissolving into luminous data
fragments drifting upward, bittersweet final moment
```

**关键视觉元素**:
- 😊 温柔微笑（保持到最后）
- 👁️ 金色眼纹褪去
- 👁️ 半透明的身体
- ✨ 化作光粒上升
- 💔 悲伤但美丽的氛围
- 🌫️ 逐渐淡出的视觉效果

**生成参数**:
```
Size: 1344×768 (16:9)
Steps: 20
Seed: 4000
Guidance: 1.0
```

**后续I2V帧**:
- S05-KF2 (1.5s) - 身体变透明过程
- S05-KF3 (3.0s) - 化作光粒 → 淡白色转场

---

## 生成执行步骤

### 方式 1: 单场景生成（推荐）

```bash
# 一键生成场景1-1的所有T2I关键帧
pixi run python -m pipeline.generate_scene_keyframes ep001 1-1

# 生成多个候选（更好的覆盖率）
pixi run python -m pipeline.generate_scene_keyframes ep001 1-1 --num-candidates 3
```

### 方式 2: 单个关键帧生成

```bash
# 如果想单独调整某个关键帧
pixi run python -m pipeline.generate_shot_images ep001 --shot-ids S01 S02 S03 S04 S05
```

### 方式 3: 完整管线生成

```bash
# 包含所有阶段（分镜 → 关键帧 → T2I → TTS → 字幕）
pixi run python -m pipeline.generate_episode ep001
```

---

## 输出文件结构

生成完成后，文件结构如下：

```
episodes/ep001/
├── keyframes.json               # 关键帧元数据
├── keyframes.md                 # 关键帧文档
├── scene_1-1_keyframes_plan.md  # 本文件
└── video/
    └── keyframes/               # 关键帧图像输出目录
        ├── S01-KF1_seed0000.png      # 1344×768
        ├── S01-KF1_seed0001.png      # 候选2
        ├── S01-KF1_seed0002.png      # 候选3
        ├── S02-KF1_seed1000.png
        ├── S02-KF1_seed1001.png
        ├── S02-KF1_seed1002.png
        ├── S03-KF1_seed2000.png
        ├── ...
        └── S05-KF1_seed4002.png
```

---

## 质量检查清单

生成后请检查：

- [ ] **S01-KF1** 城市建筑：是否由光构成？是否有数据河流？
- [ ] **S01-KF1** 故障效果：是否有抽搐/闪烁感？
- [ ] **S02-KF1** 羲和角色：年龄正确（30岁）？左眼金色纹路清晰？
- [ ] **S02-KF1** 流光长袍：科幻质感是否明显？
- [ ] **S03-KF1** 特写脸部：微笑表情是否温和而坚定？
- [ ] **S03-KF1** 金色数据：脸部反光是否有金色调？
- [ ] **S04-KF1** 能量爆发：光柱从地面升起是否清晰？
- [ ] **S04-KF1** 宇宙感：背景是否有星空或宇宙感？
- [ ] **S04-KF1** 八卦图案：光点中的八卦是否可见（即使很小）？
- [ ] **S05-KF1** 消散效果：身体是否逐渐变透明？
- [ ] **S05-KF1** 光粒上升：是否有向上飘升的光粒感？
- [ ] **整体风格** 统一性：5个关键帧的色调/光影是否连贯？

---

## 后续 I2V 生成

一旦T2I关键帧生成完成，每个T2I帧会触发多个I2V帧：

```json
S01: T2I(KF1) + I2V(KF2,KF3)
S02: T2I(KF1) + I2V(KF2)
S03: T2I(KF1) + I2V(KF2)
S04: T2I(KF1) + I2V(KF2,KF3)
S05: T2I(KF1) + I2V(KF2,KF3)
```

**总计**: 5 T2I + 13 I2V = 18个完整关键帧视频片段

---

## 视觉参考指南

### 灵子文明风格特征

1. **颜色调色板**:
   - 主色: 蓝色、紫色、金色、白色
   - 不推荐: 暖色、橙色、红色（会破坏未来感）

2. **光效**:
   - 冷光（LED蓝光）为主
   - 金色作为能量核心
   - 强对比（亮 vs 暗）

3. **建筑风格**:
   - 几何化、参数化设计
   - 悬浮感（反重力）
   - 有机流线与硬边界的混合

4. **动效参考**:
   - 数据流：平滑、有规律、呈波浪或螺旋形
   - 能量爆发：从中心向外放射，快速且有力
   - 消散：缓慢、温柔、向上漂浮

---

## 常见问题

**Q: 为什么是1344×768而不是1920×1080？**
A: T2I（Flux）和I2V（LTX）的最优分辨率是1344×768。最终合成时会上采样到1920×1080。

**Q: 可以修改prompt吗？**
A: 可以，直接编辑keyframes.json中的"prompt"字段，然后重新运行生成。

**Q: 需要生成3个候选吗？**
A: 推荐至少2个。3个会获得最好的视觉多样性，但生成时间会增加。

**Q: 生成失败怎么办？**
A: 检查ComfyUI是否运行（localhost:8188），以及显存是否足够（建议≥16GB）。

---

最后更新: 2026-02-02
