# ep002 — 关键帧规划

## 概览

**总镜头数:** 18
**总时长:** 60s

关键帧策略:
- **第1帧（T2I）**: 文本到图像，设定场景/角色/气氛
- **后续帧（I2V）**: 基于第1帧作为参考，生成镜头内运动

---

## S01 — 伏羲从晨雾中走来，进入营地。族人们看到他，纷纷后退，面露恐惧。

**镜头时长:** 4s | **关键帧数:** 3
**地点:** huaxu_camp_entrance
**情感:** tension, unease

**视觉事件:**

  1. 伏羲晨雾现身 (wide shot, eye level)
  2. 族人惊恐后退 (wide shot, eye level)
  3. 金瞳微光闪烁 (medium wide shot, eye level)

**关键帧详情:**

### S01-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 4.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Cinematic wide shot of an ancient tribal camp at dawn, primitive thatched huts and animal skin tents scattered around. A...`

### S01-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 2.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S01-KF1 (本镜头第1帧)

### S01-KF3 (I2V (参考帧))

- **时间:** 4.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S01-KF1 (本镜头第1帧)

---

## S02 — 老妪指着伏羲，惊恐地喊叫

**镜头时长:** 3s | **关键帧数:** 3
**地点:** huaxu_camp_entrance
**情感:** terror, accusation

**视觉事件:**

  1. 老妪手指颤抖指向 (medium close-up, eye level)
  2. 身体颤抖尖叫 (medium close-up, eye level)
  3. 人群惊恐逃散 (medium close-up, eye level)

**关键帧详情:**

### S02-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Medium close-up of an elderly tribal woman (70+ years old, deeply wrinkled face, white tangled hair adorned with bone or...`

### S02-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S02-KF1 (本镜头第1帧)

### S02-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S02-KF1 (本镜头第1帧)

---

## S03 — 伏羲母亲冲上前，张开双臂保护儿子

**镜头时长:** 4s | **关键帧数:** 3
**地点:** huaxu_camp_entrance
**情感:** desperation, maternal love, defiance

**视觉事件:**

  1. 母亲冲入画面 (medium shot, low angle)
  2. 张臂护子 (medium shot, low angle)
  3. 伏羲闪烁 (medium shot, low angle)

**关键帧详情:**

### S03-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 4.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Medium shot with slight low angle of a middle-aged woman (Fuxi's mother, 40s, strong but weathered features, long dark h...`

### S03-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 2.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S03-KF1 (本镜头第1帧)

### S03-KF3 (I2V (参考帧))

- **时间:** 4.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S03-KF1 (本镜头第1帧)

---

## S04 — 会议帐篷内部，巫师和族长面对面，气氛凝重

**镜头时长:** 3s | **关键帧数:** 3
**地点:** council_tent_interior
**情感:** foreboding, political tension

**视觉事件:**

  1. 帐篷全景展示 (wide shot, eye level)
  2. 火光映照双方 (wide shot, eye level)
  3. 余烬迸发凝视 (wide shot, eye level)

**关键帧详情:**

### S04-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Wide establishing shot of a tribal council tent interior. Dark, atmospheric space illuminated by a central fire pit cast...`

### S04-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S04-KF1 (本镜头第1帧)

### S04-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S04-KF1 (本镜头第1帧)

---

## S05 — 巫师面色阴沉地发出警告

**镜头时长:** 4s | **关键帧数:** 3
**地点:** council_tent_interior
**情感:** menace, conviction, manipulation

**视觉事件:**

  1. 巫师阴影笼罩 (medium close-up, low angle)
  2. 手势咒语施放 (medium close-up, low angle)
  3. 眼神凝视警告 (close-up, low angle)

**关键帧详情:**

### S05-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 4.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Medium close-up with slight tilt up of the SHAMAN, making him appear imposing and threatening. His gaunt face half-lit b...`

### S05-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 2.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S05-KF1 (本镜头第1帧)

### S05-KF3 (I2V (参考帧))

- **时间:** 4.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S05-KF1 (本镜头第1帧)

---

## S06 — 族长犹豫不决，内心挣扎

**镜头时长:** 3s | **关键帧数:** 3
**地点:** council_tent_interior
**情感:** conflict, doubt, fatherly love

**视觉事件:**

  1. 下颚紧绷 (close-up, eye level)
  2. 目光闪躲 (close-up, eye level)
  3. 握紧扶手 (close-up, eye level)

**关键帧详情:**

### S06-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Close-up of the CHIEF's face (Fuxi's father), capturing his internal struggle. A strong, weathered face (50s, short gray...`

### S06-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S06-KF1 (本镜头第1帧)

### S06-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S06-KF1 (本镜头第1帧)

---

## S07 — 巫师反驳，声音尖锐

**镜头时长:** 2s | **关键帧数:** 2
**地点:** council_tent_interior
**情感:** accusation, fanaticism

**视觉事件:**

  1. 巫师起身指责 (medium shot, low angle)
  2. 阴影笼罩威慑 (medium close-up, low angle)

**关键帧详情:**

### S07-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 2.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Medium shot of the shaman, camera pushing in as he speaks with accusatory fervor. His body language aggressive, leaning ...`

### S07-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S07-KF1 (本镜头第1帧)

---

## S08 — 帐篷外传来警报声，两人同时反应

**镜头时长:** 2s | **关键帧数:** 2
**地点:** council_tent_interior
**情感:** alarm, urgency

**视觉事件:**

  1. 两人同时僵住 (wide shot, eye level)
  2. 帐门打开剪影 (wide shot, eye level)

**关键帧详情:**

### S08-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 2.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Wide shot of the council tent interior, both shaman and chief freeze mid-conversation, heads snapping toward the tent en...`

### S08-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S08-KF1 (本镜头第1帧)

---

## S09 — 燧人氏军队出现在边界，对峙华胥氏

**镜头时长:** 4s | **关键帧数:** 3
**地点:** tribe_border
**情感:** intimidation, impending conflict

**视觉事件:**

  1. 俯瞰战阵初现 (extreme wide shot, bird's eye view)
  2. 军队阵列展开 (wide shot, high angle)
  3. 首领踏步向前 (wide shot, eye level)

**关键帧详情:**

### S09-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 4.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Epic wide shot, camera craning down to reveal the confrontation at the tribal border. In the foreground, FIFTY SUIREN WA...`

### S09-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 2.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S09-KF1 (本镜头第1帧)

### S09-KF3 (I2V (参考帧))

- **时间:** 4.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S09-KF1 (本镜头第1帧)

---

## S10 — 燧人首领发出最后通牒

**镜头时长:** 3s | **关键帧数:** 3
**地点:** tribe_border
**情感:** aggression, dominance, threat

**视觉事件:**

  1. 首领仰头怒吼 (medium shot, low angle)
  2. 战锤举起闪光 (medium shot, low angle)
  3. 战士群起响应 (medium shot, low angle)

**关键帧详情:**

### S10-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Medium shot, low angle looking up at the SUIREN CHIEF, making him appear powerful and dominating. A burly, battle-harden...`

### S10-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S10-KF1 (本镜头第1帧)

### S10-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S10-KF1 (本镜头第1帧)

---

## S11 — 战斗爆发，伏羲被迫参战，左眼剧痛

**镜头时长:** 4s | **关键帧数:** 3
**地点:** tribe_border
**情感:** chaos, pain, reluctance

**视觉事件:**

  1. 伏羲卷入混战 (medium shot, eye level)
  2. 被动防御格挡 (medium shot, eye level)
  3. 左眼剧痛发作 (close-up, slightly low angle)

**关键帧详情:**

### S11-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 4.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Dynamic medium shot tracking FUXI as he's pulled into the battle chaos. Warriors from both sides clash around him - flin...`

### S11-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 2.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S11-KF1 (本镜头第1帧)

### S11-KF3 (I2V (参考帧))

- **时间:** 4.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S11-KF1 (本镜头第1帧)

---

## S12 — 坤卦能力爆发，地面塌陷，燧人战士陷入坑中

**镜头时长:** 4s | **关键帧数:** 3
**地点:** tribe_border
**情感:** shock, supernatural awe

**视觉事件:**

  1. 地面开始龟裂 (wide shot, eye level)
  2. 战士坠入塌陷 (wide shot, high angle)
  3. 坤卦光芒闪耀 (extreme wide shot, high angle)

**关键帧详情:**

### S12-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 4.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Epic wide shot with dramatic crane up revealing the supernatural event. FUXI stands at the center, his golden left eye b...`

### S12-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 2.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S12-KF1 (本镜头第1帧)

### S12-KF3 (I2V (参考帧))

- **时间:** 4.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S12-KF1 (本镜头第1帧)

---

## S13 — 双方战士都被震惊，惊呼妖术

**镜头时长:** 3s | **关键帧数:** 3
**地点:** tribe_border
**情感:** terror, disbelief, superstitious fear

**视觉事件:**

  1. 华胥战士惊恐 (close-up, eye level)
  2. 燧人老兵后退 (close-up, eye level)
  3. 众人齐呼妖术 (medium shot, low angle)

**关键帧详情:**

### S13-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Quick-cut reaction shot montage showing faces from BOTH sides frozen in identical terror. HUAXU WARRIOR: young man, dirt...`

### S13-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S13-KF1 (本镜头第1帧)

### S13-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S13-KF1 (本镜头第1帧)

---

## S14 — 战后，祭坛前聚集众人，伏羲被绑在祭柱上

**镜头时长:** 3s | **关键帧数:** 3
**地点:** tribal_altar
**情感:** dread, ritualistic menace

**视觉事件:**

  1. 祭坛全景展现 (wide shot, eye level)
  2. 人群骚动不安 (wide shot, eye level)
  3. 伏羲挣扎乌云压境 (wide shot, low angle)

**关键帧详情:**

### S14-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Wide establishing shot of the tribal ALTAR area - a raised stone platform with a massive wooden SACRIFICIAL PILLAR at it...`

### S14-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S14-KF1 (本镜头第1帧)

### S14-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S14-KF1 (本镜头第1帧)

---

## S15 — 巫师煽动族人

**镜头时长:** 3s | **关键帧数:** 3
**地点:** tribal_altar
**情感:** fanaticism, triumph, manipulation

**视觉事件:**

  1. 巫师张臂宣告 (medium shot, low angle)
  2. 仰头通灵指控 (medium shot, low angle)
  3. 族人狂热响应 (medium shot, low angle)

**关键帧详情:**

### S15-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Low angle medium shot of the SHAMAN at his most powerful and terrifying. He stands on the raised altar platform, arms sp...`

### S15-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S15-KF1 (本镜头第1帧)

### S15-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S15-KF1 (本镜头第1帧)

---

## S16 — 母亲哭喊，父亲低头不语

**镜头时长:** 4s | **关键帧数:** 3
**地点:** tribal_altar
**情感:** anguish, shame, helplessness

**视觉事件:**

  1. 母亲挣扎哭喊 (medium shot, eye level)
  2. 焦点转至父亲 (medium shot, eye level)
  3. 伏羲绝望低头 (medium shot, eye level)

**关键帧详情:**

### S16-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 4.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Emotionally devastating medium shot with focus pull. In the foreground, FUXI'S MOTHER is held back by tribe members, her...`

### S16-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 2.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S16-KF1 (本镜头第1帧)

### S16-KF3 (I2V (参考帧))

- **时间:** 4.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S16-KF1 (本镜头第1帧)

---

## S17 — 伏羲看着族人恐惧的眼神，心寒绝望

**镜头时长:** 4s | **关键帧数:** 3
**地点:** tribal_altar
**情感:** despair, betrayal, innocence

**视觉事件:**

  1. 泪水涌出 (close-up, eye level)
  2. 环顾敌意 (close-up, eye level)
  3. 低头绝望 (extreme close-up, slight high angle)

**关键帧详情:**

### S17-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 4.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Intimate close-up of FUXI's face, camera slowly pushing in. His young face (18, previously full of life, now hollow with...`

### S17-KF2 (I2V (参考帧))

- **时间:** 2.0s (持续 2.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S17-KF1 (本镜头第1帧)

### S17-KF3 (I2V (参考帧))

- **时间:** 4.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S17-KF1 (本镜头第1帧)

---

## S18 — 乌云汇聚，不祥的天象

**镜头时长:** 3s | **关键帧数:** 3
**地点:** tribal_altar
**情感:** dread, supernatural menace, cliffhanger

**视觉事件:**

  1. 祭坛全景仰视 (wide shot, eye level)
  2. 乌云急速汇聚 (wide shot, low angle)
  3. 天象笼罩村落 (extreme wide shot, worm's eye view)

**关键帧详情:**

### S18-KF1 (T2I (场景设置))

- **时间:** 0.0s (持续 3.0s)
- **类型:** T2I (场景设置)
- **Prompt:** `Dramatic wide shot tilting up from the altar scene to the sky. The altar with Fuxi bound visible at the bottom of frame,...`

### S18-KF2 (I2V (参考帧))

- **时间:** 1.5s (持续 1.5s)
- **类型:** I2V (参考帧)
- **参考帧:** S18-KF1 (本镜头第1帧)

### S18-KF3 (I2V (参考帧))

- **时间:** 3.0s (持续 0.0s)
- **类型:** I2V (参考帧)
- **参考帧:** S18-KF1 (本镜头第1帧)

---
