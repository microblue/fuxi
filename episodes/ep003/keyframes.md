# ep003 — 关键帧规划

## 概览

**总镜头数:** 14
**总时长:** 47s

关键帧策略:
- **第1帧（T2I）**: 文本到图像，设定场景/角色/气氛
- **后续帧（I2V）**: 基于第1帧作为参考，生成镜头内运动

---

## S01 — 巫师在祭坛上点燃圣火，火焰在黄昏中升起，逐渐逼近被绑在祭坛柱上的伏羲

**镜头时长:** 4s | **关键帧数:** 3
**地点:** altar_dusk
**情感:** dread, tension

**视觉事件:**

  1. 高空俯瞰祭坛 (extreme wide shot, bird's eye view)
  2. 圣火点燃升起 (wide shot, high angle)
  3. 火光映照伏羲 (wide shot, eye level)

**关键帧详情:**

### S01-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 4.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Cinematic wide shot of an ancient primitive altar at dusk, golden-orange sky bleeding into purple. A shaman in bone orna...`

### S01-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 2.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S01-KF1 (本镜头第1帧)

### S01-KF3 (I2V (参考帧))

- **时间:** 4.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S01-KF1 (本镜头第1帧)

---

## S02 — 熵单位隐形于空中，白色光束突然射向伏羲额头，伏羲体内的金色代码流自动形成防御

**镜头时长:** 3s | **关键帧数:** 3
**地点:** altar_dusk
**情感:** shock, cosmic intervention

**视觉事件:**

  1. 白色光束射下 (medium shot, low angle)
  2. 金色代码防御 (medium shot, low angle)
  3. 能量碰撞火花 (medium shot, low angle)

**关键帧详情:**

### S02-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Cinematic medium shot with slight dutch angle. Fuxi bound to altar pillar, face illuminated by approaching flames. Above...`

### S02-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S02-KF1 (本镜头第1帧)

### S02-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S02-KF1 (本镜头第1帧)

---

## S03 — 族人抬头看向天空，惊恐地发现若隐若现的几何体

**镜头时长:** 2s | **关键帧数:** 2
**地点:** altar_dusk
**情感:** terror, awe

**视觉事件:**

  1. 族人仰头惊恐 (close-up, low angle)
  2. 焦点转移群体恐惧 (close-up, low angle)

**关键帧详情:**

### S03-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 2.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Low angle close-up of tribe member's face looking upward in terror. Weathered features, primitive face paint, wide eyes ...`

### S03-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S03-KF1 (本镜头第1帧)

---

## S04 — 伏羲在剧痛中集中精神，第一次主动用代码视觉观察火焰——看到无数跳跃的红色代码片段

**镜头时长:** 4s | **关键帧数:** 3
**地点:** code_vision_realm
**情感:** pain, revelation, determination

**视觉事件:**

  1. 瞳孔特写 (extreme close-up, eye level)
  2. 视觉转换 (extreme close-up, eye level)
  3. 代码视界 (wide shot, eye level)

**关键帧详情:**

### S04-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 4.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Extreme close-up of Fuxi's left eye, iris reflecting golden code symbols. Sweat and tears streak his face, veins visible...`

### S04-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 2.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S04-KF1 (本镜头第1帧)

### S04-KF3 (I2V (参考帧))

- **时间:** 4.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S04-KF1 (本镜头第1帧)

---

## S05 — 伏羲'推动'火焰代码的中心节点，现实中火焰逆流冲向空中的熵单位

**镜头时长:** 3s | **关键帧数:** 3
**地点:** altar_dusk
**情感:** triumph, shock, chaos

**视觉事件:**

  1. 火焰逆流升起 (wide shot, low angle)
  2. 熵单位遭遇火焰 (wide shot, eye level)
  3. 冲击波扩散 (extreme wide shot, high angle)

**关键帧详情:**

### S05-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Cinematic wide shot capturing the impossible moment. Fuxi on altar, arms straining against bonds, face contorted in conc...`

### S05-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S05-KF1 (本镜头第1帧)

### S05-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S05-KF1 (本镜头第1帧)

---

## S06 — 几何体完全显形，部落众人惊恐万分

**镜头时长:** 2s | **关键帧数:** 2
**地点:** altar_dusk
**情感:** primal terror, chaos

**视觉事件:**

  1. 几何体完全显现 (wide shot, low angle)
  2. 部落众人惊恐四散 (wide shot, low angle)

**关键帧详情:**

### S06-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 2.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Dramatic low angle wide shot from tribe's perspective. The entropy unit fully visible against darkening sky - a massive ...`

### S06-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S06-KF1 (本镜头第1帧)

---

## S07 — 火焰烧断铁链，伏羲摔下祭坛

**镜头时长:** 3s | **关键帧数:** 3
**地点:** altar_dusk
**情感:** relief, exhaustion, pain

**视觉事件:**

  1. 铁链断裂火花飞溅 (medium shot, eye level)
  2. 伏羲坠落祭坛 (medium shot, slightly high angle)
  3. 金色符文消退 (medium shot, low angle)

**关键帧详情:**

### S07-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Medium shot with handheld camera feel capturing raw moment. The reversed fire has burned through Fuxi's iron chains, met...`

### S07-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S07-KF1 (本镜头第1帧)

### S07-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S07-KF1 (本镜头第1帧)

---

## S08 — 族长复杂地看着儿子，宣布放逐

**镜头时长:** 4s | **关键帧数:** 3
**地点:** altar_dusk
**情感:** conflicted love, painful duty, sorrow

**视觉事件:**

  1. 族长缓步逼近 (medium shot, eye level)
  2. 手伸又缩回 (medium close-up, eye level)
  3. 艰难开口宣判 (medium shot, eye level)

**关键帧详情:**

### S08-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 4.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Intimate two-shot at eye level. Fuxi on ground, pushing himself up on one elbow, blood trailing from his mouth. The chie...`

### S08-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 2.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S08-KF1 (本镜头第1帧)

### S08-KF3 (I2V (参考帧))

- **时间:** 4.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S08-KF1 (本镜头第1帧)

---

## S09 — 伏羲擦去嘴角血，发誓要找到真相

**镜头时长:** 4s | **关键帧数:** 3
**地点:** altar_dusk
**情感:** determination, wounded pride, resolve

**视觉事件:**

  1. 擦拭血迹 (close-up, low angle)
  2. 缓缓起身 (close-up, low angle)
  3. 金光闪现 (close-up, low angle)

**关键帧详情:**

### S09-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 4.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Close-up of Fuxi's face with slight low angle suggesting rising strength. He wipes blood from the corner of his mouth wi...`

### S09-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 2.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S09-KF1 (本镜头第1帧)

### S09-KF3 (I2V (参考帧))

- **时间:** 4.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S09-KF1 (本镜头第1帧)

---

## S10 — 伏羲背起行囊，孤独走入荒野

**镜头时长:** 4s | **关键帧数:** 3
**地点:** wilderness_edge
**情感:** solitude, determination, melancholy

**视觉事件:**

  1. 伏羲踏入荒野 (wide shot, eye level)
  2. 回望故土 (wide shot, eye level)
  3. 融入苍茫暮色 (extreme wide shot, eye level)

**关键帧详情:**

### S10-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 4.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Cinematic wide shot of lonely figure walking into vast wilderness. Fuxi seen from behind, small against the immense land...`

### S10-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 2.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S10-KF1 (本镜头第1帧)

### S10-KF3 (I2V (参考帧))

- **时间:** 4.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S10-KF1 (本镜头第1帧)

---

## S11 — 天空中，三个熵单位远远跟随伏羲

**镜头时长:** 3s | **关键帧数:** 3
**地点:** sky_above_wilderness
**情感:** ominous, surveillance, cosmic threat

**视觉事件:**

  1. 熵单位悬浮监视 (extreme wide shot, high angle)
  2. 编队追踪移动 (wide shot, high angle)
  3. 单位聚焦伏羲 (wide shot, high angle)

**关键帧详情:**

### S11-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `High angle wide shot looking down from the sky. Below, the tiny figure of Fuxi walks into wilderness, a single point of ...`

### S11-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S11-KF1 (本镜头第1帧)

### S11-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S11-KF1 (本镜头第1帧)

---

## S12 — 伏羲独自面对世界，在代码视觉中看到万物皆由代码构成

**镜头时长:** 4s | **关键帧数:** 3
**地点:** wilderness_night
**情感:** wonder, isolation, enlightenment

**视觉事件:**

  1. 伏羲凝视世界 (medium wide shot, eye level)
  2. 仰望星空代码 (medium wide shot, slightly low angle)
  3. 万物皆代码 (medium wide shot, eye level)

**关键帧详情:**

### S12-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 4.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Medium wide shot of Fuxi standing alone in nighttime wilderness, camera slowly orbiting. He gazes at his surroundings wi...`

### S12-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 2.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S12-KF1 (本镜头第1帧)

### S12-KF3 (I2V (参考帧))

- **时间:** 4.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S12-KF1 (本镜头第1帧)

---

## S13 — 伏羲对天空低语，询问追踪者的身份

**镜头时长:** 3s | **关键帧数:** 3
**地点:** wilderness_night
**情感:** defiance, curiosity, vulnerability

**视觉事件:**

  1. 目光抬起寻天 (close-up, low angle)
  2. 神情变幻三重 (close-up, low angle)
  3. 侧首倾听无应 (close-up, low angle)

**关键帧详情:**

### S13-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Close-up of Fuxi's face against star-filled night sky. His expression mixes defiance with genuine curiosity, and beneath...`

### S13-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S13-KF1 (本镜头第1帧)

### S13-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S13-KF1 (本镜头第1帧)

---

## S14 — 没有回答，但伏羲的左眼中，昆仑山方向传来强烈的代码信号

**镜头时长:** 4s | **关键帧数:** 3
**地点:** wilderness_night
**情感:** calling, destiny, hope

**视觉事件:**

  1. 黑暗扫视无信号 (wide shot, eye level)
  2. 西方光柱爆发 (wide shot, eye level)
  3. 伏羲迈步向光 (wide shot, low angle)

**关键帧详情:**

### S14-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 4.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Starting as Fuxi's POV through code-vision: the night landscape is quiet data, no response to his question. Then, from t...`

### S14-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 2.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S14-KF1 (本镜头第1帧)

### S14-KF3 (I2V (参考帧))

- **时间:** 4.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S14-KF1 (本镜头第1帧)

---
