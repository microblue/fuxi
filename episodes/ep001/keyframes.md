# ep001 — 关键帧规划

## 概览

**总镜头数:** 20
**总时长:** 58s

关键帧策略:
- **第1帧（T2I）**: 文本到图像，设定场景/角色/气氛
- **后续帧（I2V）**: 基于第1帧作为参考，生成镜头内运动

---

## S01 — 城市开场 → 危机

**镜头时长:** 3s | **关键帧数:** 3
**地点:** lingzi_civilization_capital
**情感:** awe turning to dread

**视觉事件:**

  1. 城市全景
  2. 灯光故障
  3. 警报闪烁

**关键帧详情:**

### S01-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `breathtaking futuristic city built entirely of light, luminous architecture, rivers of data flowing through the sky betw...`

### S01-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S01-KF1 (本镜头第1帧)

### S01-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S01-KF1 (本镜头第1帧)

---

## S02 — 羲和登场

**镜头时长:** 3s | **关键帧数:** 2
**地点:** lingzi_civilization_capital
**情感:** focused urgency

**视觉事件:**

  1. 中枢塔顶
  2. 数据流舞蹈

**关键帧详情:**

### S02-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `East Asian man age 30, serene celestial sage bearing, standing atop central tower in flowing luminous robes with I-Ching...`

### S02-KF2 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S02-KF1 (本镜头第1帧)

---

## S03 — 特写决断

**镜头时长:** 3s | **关键帧数:** 2
**地点:** lingzi_civilization_capital
**情感:** resolute courage, noble sacrifice

**视觉事件:**

  1. 脸部特写
  2. 微笑→决心

**关键帧详情:**

### S03-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `close-up of East Asian celestial sage age 30 with chiseled noble features, left eye glowing with golden spiral patterns ...`

### S03-KF2 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S03-KF1 (本镜头第1帧)

---

## S04 — 能量爆发

**镜头时长:** 4s | **关键帧数:** 3
**地点:** lingzi_civilization_capital
**情感:** epic sacrifice, cosmic scale

**视觉事件:**

  1. 数据提取
  2. 光柱升起
  3. 光点散射

**关键帧详情:**

### S04-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 4.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `celestial East Asian sage pressing both hands on holographic console, luminous data being extracted from entire body in ...`

### S04-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 2.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S04-KF1 (本镜头第1帧)

### S04-KF3 (I2V (参考帧))

- **时间:** 4.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S04-KF1 (本镜头第1帧)

---

## S05 — 温柔消散

**镜头时长:** 3s | **关键帧数:** 3
**地点:** lingzi_civilization_capital
**情感:** tender farewell, bittersweet

**视觉事件:**

  1. 身体透明
  2. 微笑保持
  3. 化作光粒

**关键帧详情:**

### S05-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `close-up of East Asian sage's face becoming transparent and dissolving into luminous particles, gentle knowing smile con...`

### S05-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S05-KF1 (本镜头第1帧)

### S05-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S05-KF1 (本镜头第1帧)

---

## S06 — 时空硬切

**镜头时长:** 3s | **关键帧数:** 2
**地点:** primordial_swamp_night
**情感:** primal, sudden alarm

**视觉事件:**

  1. 沼泽猎人
  2. 向上惊呼

**关键帧详情:**

### S06-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `primitive swamp at stormy night, torrential rain, young East Asian boy 16 years old with noble bearing despite animal hi...`

### S06-KF2 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S06-KF1 (本镜头第1帧)

---

## S07 — 火种降临

**镜头时长:** 3s | **关键帧数:** 3
**地点:** primordial_swamp_night
**情感:** awe, pain, mystery

**视觉事件:**

  1. 天空撕裂
  2. 蓝光坠落
  3. 伏羲痛楚

**关键帧详情:**

### S07-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `sky tearing open with silver-blue geometric light streams (celestial fire seed 火种) falling — not lightning but sacred st...`

### S07-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S07-KF1 (本镜头第1帧)

### S07-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S07-KF1 (本镜头第1帧)

---

## S08 — 漩涡吸引

**镜头时长:** 2s | **关键帧数:** 2
**地点:** primordial_swamp_night
**情感:** drawn, hypnotic pull

**视觉事件:**

  1. 发光漩涡
  2. 伏羲靠近

**关键帧详情:**

### S08-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 2.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `glowing silver-blue vortex in swamp water, translucent geometric crystal floating at hypnotic center (原始密码晶体 primordial ...`

### S08-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S08-KF1 (本镜头第1帧)

---

## S09 — 觉醒触发

**镜头时长:** 3s | **关键帧数:** 3
**地点:** primordial_swamp_night
**情感:** shock, searing pain, transformation

**视觉事件:**

  1. 手触晶体
  2. 能量涌入
  3. 跪地爆光

**关键帧详情:**

### S09-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `extreme close-up of young East Asian hand touching translucent crystal, golden data streams erupting from crystal flowin...`

### S09-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S09-KF1 (本镜头第1帧)

### S09-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S09-KF1 (本镜头第1帧)

---

## S10 — 代码视觉三层

**镜头时长:** 3s | **关键帧数:** 3
**地点:** primordial_swamp_night
**情感:** disorientation, wonder

**视觉事件:**

  1. 眼睛变色
  2. 树木代码绿
  3. 水面分子蓝

**关键帧详情:**

### S10-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `extreme close-up of left eye, pupil transformed to dark gold with tiny rotating bagua pattern (太极八卦 yin-yang Eight Trigr...`

### S10-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S10-KF1 (本镜头第1帧)

### S10-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S10-KF1 (本镜头第1帧)

---

## S11 — 存在危机

**镜头时长:** 2s | **关键帧数:** 2
**地点:** primordial_swamp_night
**情感:** shock, existential realization

**视觉事件:**

  1. 看手
  2. 看世界

**关键帧详情:**

### S11-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 2.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `medium close-up of 16-year-old East Asian boy in animal hide, kneeling in shallow swamp water, looking at own hands in p...`

### S11-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S11-KF1 (本镜头第1帧)

---

## S12 — 氛围反转

**镜头时长:** 2s | **关键帧数:** 2
**地点:** primordial_swamp_night
**情感:** sudden dread, atmosphere shift

**视觉事件:**

  1. 天色变暗
  2. 威胁降临

**关键帧详情:**

### S12-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 2.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `wide high-angle shot of dark swamp, sky rapidly darkening beyond normal storm, unnatural shadow spreading, boy tiny in f...`

### S12-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S12-KF1 (本镜头第1帧)

---

## S13 — 敌人登场

**镜头时长:** 3s | **关键帧数:** 2
**地点:** primordial_swamp_night
**情感:** cold menace, mechanical threat

**视觉事件:**

  1. 三个几何体
  2. 无声下降

**关键帧详情:**

### S13-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `three pale white octahedron geometric entities descending silently from darkened sky, glowing red cracks on surfaces, fl...`

### S13-KF2 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S13-KF1 (本镜头第1帧)

---

## S14 — 恐怖杀戮

**镜头时长:** 3s | **关键帧数:** 3
**地点:** primordial_swamp_night
**情感:** horror, helplessness

**视觉事件:**

  1. 黑色触手
  2. 像素化上升
  3. 彻底分解

**关键帧详情:**

### S14-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `black corrupting data tendrils shooting from octahedron with terrible speed, wrapping around adult East Asian tribal hun...`

### S14-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S14-KF1 (本镜头第1帧)

### S14-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S14-KF1 (本镜头第1帧)

---

## S15 — 本能反击

**镜头时长:** 4s | **关键帧数:** 3
**地点:** primordial_swamp_night
**情感:** rage, instinctive power

**视觉事件:**

  1. 怒吼
  2. 代码视觉
  3. 能量爆发

**关键帧详情:**

### S15-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 4.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `close-up of East Asian boy's face screaming in rage and primal power, left eye blazing with intense golden light and I-C...`

### S15-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 2.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S15-KF1 (本镜头第1帧)

### S15-KF3 (I2V (参考帧))

- **时间:** 4.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S15-KF1 (本镜头第1帧)

---

## S16 — 地面变幻

**镜头时长:** 3s | **关键帧数:** 3
**地点:** primordial_swamp_night
**情感:** escalating danger, desperate improvisation

**视觉事件:**

  1. 触手延伸
  2. 手按地面
  3. 流沙困敌

**关键帧详情:**

### S16-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `full shot of 16-year-old East Asian boy facing three floating octahedra, more black corrupting tendrils extending, boy s...`

### S16-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S16-KF1 (本镜头第1帧)

### S16-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S16-KF1 (本镜头第1帧)

---

## S17 — 女娲救场

**镜头时长:** 3s | **关键帧数:** 2
**地点:** primordial_swamp_night
**情感:** urgent rescue, adrenaline

**视觉事件:**

  1. 绿光骨箭
  2. 女娲现身

**关键帧详情:**

### S17-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `wide shot: glowing green bone arrow streaking through rain from distant cliff with ethereal green sacred light; on cliff...`

### S17-KF2 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S17-KF1 (本镜头第1帧)

---

## S18 — 敌人汇合

**镜头时长:** 3s | **关键帧数:** 2
**地点:** primordial_swamp_night
**情感:** cold calculation, ominous promise

**视觉事件:**

  1. 聚集成阵
  2. 红光脉动

**关键帧详情:**

### S18-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `three octahedron entities regrouping in formation, red cracks pulsing in synchronized pattern, scanning the swamp where ...`

### S18-KF2 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S18-KF1 (本镜头第1帧)

---

## S19 — 逃离回头

**镜头时长:** 3s | **关键帧数:** 2
**地点:** primordial_swamp_night
**情感:** shaken survival, lingering fear, questions unanswered

**视觉事件:**

  1. 回身看
  2. 眼光微亮

**关键帧详情:**

### S19-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `medium close-up of 16-year-old East Asian boy pausing in rain, looking back over shoulder with haunted expression, breat...`

### S19-KF2 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S19-KF1 (本镜头第1帧)

---

## S20 — 本集终

**镜头时长:** 2s | **关键帧数:** 1
**地点:** black_screen
**情感:** lingering suspense

**视觉事件:**

  1. 黑屏
  2. 字幕

**关键帧详情:**

### S20-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 2s)
- **类型:** T2I (场景设置)
- **Prompt:** `pure black screen with white text fading in`

---
