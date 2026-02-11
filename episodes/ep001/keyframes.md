# ep001 — 关键帧规划

## 概览

**总镜头数:** 20
**总时长:** 69s

关键帧策略:
- **第1帧（T2I）**: 文本到图像，设定场景/角色/气氛
- **后续帧（I2V）**: 基于第1帧作为参考，生成镜头内运动

---

## S01 — 极致璀璨的未来都市全貌展现。建筑由纯光构成，数据河流在空中流淌，城市如同一颗发光

**镜头时长:** 4s | **关键帧数:** 3
**地点:** 灵子文明首都·数据中枢 - 全景俯瞰
**情感:** 震撼、壮美转向不安

**视觉事件:**

  1. 太空俯瞰都市 (extreme wide shot, bird's eye view)
  2. 急速下降穿越 (wide shot, high angle)
  3. 全城异常闪烁 (wide shot, high angle)

**关键帧详情:**

### S01-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** extreme wide shot
- **相机角度:** bird's eye view
- **参考图像:** location/灵子文明首都·数据中枢 - 全景俯瞰
- **Prompt:** `camera positioned at orbital altitude, looking straight down at the luminescent megalopolis below Breathtaking futuristi...`

### S01-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** high angle
- **参考帧:** S01-KF1
- **Motion Prompt:** `camera rapidly descending through atmosphere, passing through layers of holographic data streams and glowing aerial high...`

### S01-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** high angle
- **参考帧:** S01-KF2
- **Motion Prompt:** `camera hovering above city skyline, capturing the full metropolitan vista as systems malfunction Camera rapidly descends...`

---

## S02 — 羲和（30岁，身着流光长袍，左眼有金色纹路）站在中枢塔顶，手指在空中快速滑动操控

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 灵子文明首都·数据中枢 - 中枢塔顶
**情感:** 紧迫、专注、英雄气概

**视觉事件:**

  1. 侧后方操控数据 (medium shot, eye level)
  2. 数据流环绕飞舞 (medium shot, eye level)
  3. 正面揭示决心 (medium shot, eye level)

**关键帧详情:**

### S02-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** eye level
- **参考图像:** character/羲和
- **Prompt:** `camera positioned behind and to the left of subject, capturing back and side profile, beginning orbital movement A majes...`

### S02-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** eye level
- **参考帧:** S02-KF1
- **Motion Prompt:** `camera at 90-degree side position, capturing profile view during orbital movement Character's fingers rapidly swipe and ...`

### S02-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** eye level
- **参考帧:** S02-KF2
- **Motion Prompt:** `camera arrives at frontal position, revealing subject's face directly Character's fingers rapidly swipe and manipulate f...`

---

## S03 — 观测者AI以温柔女声发出警告。羲和摇头，表情坚毅，提出火种协议。

**镜头时长:** 4s | **关键帧数:** 3
**地点:** 灵子文明首都·数据中枢 - 中枢塔顶
**情感:** 紧迫、决断

**视觉事件:**

  1. AI警告倒计时 (medium close-up, eye level)
  2. 羲和坚定摇头 (medium close-up, eye level)
  3. 提出火种协议 (close-up, eye level)

**关键帧详情:**

### S03-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** medium close-up
- **相机角度:** eye level
- **参考图像:** character/羲和
- **Prompt:** `camera positioned at medium-close distance, frontal angle capturing both character and holographic AI on the side Close-...`

### S03-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** medium close-up
- **相机角度:** eye level
- **参考帧:** S03-KF1
- **Motion Prompt:** `camera slowly pushing in toward character's face, maintaining frontal framing Character shakes head firmly while speakin...`

### S03-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** eye level
- **参考帧:** S03-KF2
- **Motion Prompt:** `camera completed push-in, now close to character's face capturing intense emotional moment Character shakes head firmly ...`

---

## S04 — 观测者AI告知存活率极低且无法保留记忆。羲和微笑，授权执行火种协议。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 灵子文明首都·数据中枢 - 中枢塔顶
**情感:** 悲壮、决绝、浪漫主义的牺牲

**视觉事件:**

  1. 微笑浮现 (close-up, eye level)
  2. 金纹亮起 (close-up, eye level)
  3. 眼部聚焦 (extreme close-up, eye level)

**关键帧详情:**

### S04-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** close-up
- **相机角度:** eye level
- **参考图像:** character/羲和
- **Prompt:** `camera positioned close to face, framing full facial features with golden eye tattoo visible Extreme close-up of a heroi...`

### S04-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** eye level
- **参考帧:** S04-KF1
- **Motion Prompt:** `camera slowly pushing in, transitioning focus from full face to upper face area A serene smile slowly forms on the chara...`

### S04-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考帧:** S04-KF2
- **Motion Prompt:** `camera extremely close to left eye, filling frame with glowing golden iris and circuit tattoo A serene smile slowly form...`

---

## S05 — 羲和将双手按在控制台上，全身数据被抽取。城市中心升起一道通天光柱，分裂为亿万光点

**镜头时长:** 4s | **关键帧数:** 3
**地点:** 灵子文明首都·数据中枢 - 中枢塔顶
**情感:** 壮烈、升华、宇宙级的壮美

**视觉事件:**

  1. 双手按下光芒涌动 (extreme wide shot, high angle)
  2. 通天光柱冲天而起 (extreme wide shot, low angle)
  3. 光点洒落八卦浮现 (extreme wide shot, bird's eye view)

**关键帧详情:**

### S05-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** extreme wide shot
- **相机角度:** high angle
- **参考图像:** location/灵子文明首都·数据中枢 - 中枢塔顶
- **Prompt:** `camera positioned high above, looking down at figure and control console from behind Epic wide shot of a figure pressing...`

### S05-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** extreme wide shot
- **相机角度:** low angle
- **参考帧:** S05-KF1
- **Motion Prompt:** `camera rapidly ascending vertically, pulling back to reveal massive scale of light pillar erupting from city center Char...`

### S05-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** extreme wide shot
- **相机角度:** bird's eye view
- **参考帧:** S05-KF2
- **Motion Prompt:** `camera at cosmic height, stabilized, one glowing particle with bagua symbol drifting toward lens Character presses hands...`

---

## S06 — 羲和身体逐渐透明化，最后留下遗言，身影消散为光尘。

**镜头时长:** 4s | **关键帧数:** 3
**地点:** 灵子文明首都·数据中枢 - 中枢塔顶
**情感:** 释然、温柔的悲伤

**视觉事件:**

  1. 身体边缘透明化 (medium shot, eye level)
  2. 遗言微笑消散 (medium shot, eye level)
  3. 金瞳渐隐入暗 (medium shot, eye level)

**关键帧详情:**

### S06-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** eye level
- **参考图像:** character/羲和
- **Prompt:** `camera positioned at medium distance, frontal view with soft focus beginning to diffuse edges A translucent ghostly figu...`

### S06-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** eye level
- **参考帧:** S06-KF1
- **Motion Prompt:** `camera maintains frontal position, focus progressively softening as subject dissolves further Character's body slowly be...`

### S06-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** eye level
- **参考帧:** S06-KF2
- **Motion Prompt:** `camera static as subject fully dissolves, focus tracking the last glowing eye before fading to darkness Character's body...`

---

## S07 — 暴雨之夜，原始粗犷的沼泽景象。少年伏羲与三名猎人在雷泽中追踪雷兽足迹，脚踏泥泞。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 上古雷泽·沼泽地带
**情感:** 原始、紧张、充满生命力

**视觉事件:**

  1. 雷泽夜雨全景 (extreme wide shot, low angle)
  2. 追踪雷兽足迹 (wide shot, low angle)
  3. 闪电照亮前路 (wide shot, low angle)

**关键帧详情:**

### S07-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** extreme wide shot
- **相机角度:** low angle
- **参考图像:** location/上古雷泽·沼泽地带
- **Prompt:** `camera positioned at water level, low angle capturing vast swampland and stormy sky Primordial swampland at night during...`

### S07-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** low angle
- **参考帧:** S07-KF1
- **Motion Prompt:** `camera tracking at knee height through water, following the group from behind-side angle Heavy rain falling in sheets, c...`

### S07-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** low angle
- **参考帧:** S07-KF2
- **Motion Prompt:** `camera low and stable, capturing dramatic lightning illumination of the hunting party against stormy landscape Heavy rai...`

---

## S08 — 猎人甲大喊让伏羲看天上。镜头随伏羲目光快速甩向天空——天空撕裂，银蓝色几何光流倾

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 上古雷泽·沼泽地带
**情感:** 惊骇、神秘

**视觉事件:**

  1. 猎人示警仰望 (medium shot, eye level)
  2. 快速甩镜上移 (medium shot to wide shot, tilting rapidly upward)
  3. 天空光流倾泻 (extreme wide shot, worm's eye view)

**关键帧详情:**

### S08-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** eye level
- **参考图像:** location/上古雷泽·沼泽地带
- **Prompt:** `camera at character level, capturing hunter and young Fuxi in swamp terrain, rain falling heavily around them Dramatic l...`

### S08-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium shot to wide shot
- **相机角度:** tilting rapidly upward
- **参考帧:** S08-KF1
- **Motion Prompt:** `camera whip-panning vertically following Fuxi's gaze upward, motion blur on edges, rain streaks becoming vertical lines ...`

### S08-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** extreme wide shot
- **相机角度:** worm's eye view
- **参考帧:** S08-KF2
- **Motion Prompt:** `camera at extreme low angle looking straight up at torn sky, silver-blue geometric light cascading down through parted s...`

---

## S09 — 伏羲左眼突然刺痛，手捂眼睛。光流坠入沼泽中央，溶解成发光漩涡。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 上古雷泽·沼泽地带
**情感:** 痛苦、困惑、命运的触碰

**视觉事件:**

  1. 眼瞳收缩刺痛 (extreme close-up, eye level)
  2. 金色闪光显现 (extreme close-up, eye level)
  3. 手掌遮眼 (extreme close-up, eye level)

**关键帧详情:**

### S09-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考图像:** character/少年伏羲
- **Prompt:** `macro lens positioned directly in front of left eye, filling frame with iris detail Extreme close-up of a young boy's le...`

### S09-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考帧:** S09-KF1
- **Motion Prompt:** `macro lens maintaining intimate eye detail, subtle trembling visible in frame Eye contracts in pain with pupil rapidly d...`

### S09-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考帧:** S09-KF2
- **Motion Prompt:** `macro lens capturing hand rushing into frame to cover eye, background glow reflected in visible right eye Eye contracts ...`

---

## S10 — 伏羲独自走近发光漩涡。漩涡中心浮着一块半透明晶体，散发出神秘的光芒。他伸手向晶体

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 漩涡边缘
**情感:** 神秘、敬畏、命运的吸引

**视觉事件:**

  1. 少年缓步前行 (medium shot, low angle)
  2. 接近漩涡 (medium shot, low angle)
  3. 伸手触碰 (medium close-up, low angle)

**关键帧详情:**

### S10-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** low angle
- **参考图像:** location/漩涡边缘
- **Prompt:** `camera positioned low at knee height, frontal view capturing boy and distant vortex A teenage boy in primitive animal hi...`

### S10-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** low angle
- **参考帧:** S10-KF1
- **Motion Prompt:** `camera slowly pushing forward, maintaining low angle, closing distance to boy and vortex Boy slowly walks forward throug...`

### S10-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** medium close-up
- **相机角度:** low angle
- **参考帧:** S10-KF2
- **Motion Prompt:** `camera pushed closer, low frontal angle emphasizing reaching gesture toward glowing crystal Boy slowly walks forward thr...`

---

## S11 — 手指触碰晶体的瞬间！金色数据流顺手臂涌入！伏羲痛苦跪地，左眼爆发出强光。当他再次

**镜头时长:** 4s | **关键帧数:** 3
**地点:** 漩涡边缘
**情感:** 剧烈痛苦、觉醒、蜕变

**视觉事件:**

  1. 触碰瞬间爆发 (extreme close-up, eye level)
  2. 跪地痛苦尖叫 (medium shot, low angle)
  3. 金瞳八卦显现 (extreme close-up, eye level)

**关键帧详情:**

### S11-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考图像:** character/少年伏羲
- **Prompt:** `camera extremely close to hand and crystal contact point, capturing the moment of explosive energy transfer A young boy ...`

### S11-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** low angle
- **参考帧:** S11-KF1
- **Motion Prompt:** `camera pulling back quickly from subject kneeling in swamp water, capturing full body convulsion and energy surge The in...`

### S11-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考帧:** S11-KF2
- **Motion Prompt:** `camera positioned extremely close to left eye, macro lens capturing pupil transformation detail The instant of contact t...`

---

## S12 — 代码视觉首次展现：看树木出现绿色生长代码串；看水面出现分子结构网格；看自己手出现

**镜头时长:** 4s | **关键帧数:** 3
**地点:** 漩涡边缘
**情感:** 震惊、敬畏、世界观颠覆

**视觉事件:**

  1. 扫视树木代码 (medium shot, eye level)
  2. 扫视水面网格 (medium shot, high angle)
  3. 凝视双手电流 (close-up, high angle)

**关键帧详情:**

### S12-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** eye level
- **参考图像:** location/漩涡边缘
- **Prompt:** `POV camera snapping towards ancient trees, first-person subjective view with slight instability First-person POV through...`

### S12-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** high angle
- **参考帧:** S12-KF1
- **Motion Prompt:** `POV camera snapping down towards water surface, subjective downward gaze with digital transition glitch POV camera quick...`

### S12-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** high angle
- **参考帧:** S12-KF2
- **Motion Prompt:** `POV camera looking down at own trembling hands, extreme subjective close framing POV camera quickly pans to trees where ...`

---

## S13 — 三个苍白的正八面体几何体无声降下，悬浮在沼泽上方，散发冰冷的白光。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 熵单位降临地点
**情感:** 恐惧、威胁、不祥

**视觉事件:**

  1. 几何体初现天际 (extreme wide shot, low angle)
  2. 降临逼近地面 (wide shot, low angle)
  3. 悬浮沼泽上方 (wide shot, worm's eye view)

**关键帧详情:**

### S13-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** extreme wide shot
- **相机角度:** low angle
- **参考图像:** location/熵单位降临地点
- **Prompt:** `camera positioned low in swamp environment, looking up at dark stormy sky, three octahedral shapes emerging from clouds ...`

### S13-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** low angle
- **参考帧:** S13-KF1
- **Motion Prompt:** `camera maintains low position, geometric entities now closer, scanning beams visible sweeping across terrain Three octah...`

### S13-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** worm's eye view
- **参考帧:** S13-KF2
- **Motion Prompt:** `camera at ground level among swamp vegetation, three octahedrons hovering in formation above, cold light illuminating or...`

---

## S14 — 熵单位发出机械音宣布检测到异常。黑色数据流卷向猎人乙，猎人身体开始像素化分解。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 熵单位降临地点
**情感:** 恐怖、残酷

**视觉事件:**

  1. 黑色触须伸出 (medium shot, eye level)
  2. 触须缠绕猎人 (medium close-up, eye level)
  3. 身体像素化分解 (close-up, low angle)

**关键帧详情:**

### S14-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** eye level
- **参考图像:** character/猎人乙
- **Prompt:** `camera positioned at medium distance capturing both the octahedral entity and the hunter in frame A terrified tribal hun...`

### S14-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium close-up
- **相机角度:** eye level
- **参考帧:** S14-KF1
- **Motion Prompt:** `camera tracking closer to the hunter as tendrils make contact, following the spreading dissolution Black jagged data ten...`

### S14-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** low angle
- **参考帧:** S14-KF2
- **Motion Prompt:** `camera low angle capturing the hunter's fragmenting form with black pixels spiraling upward toward the entity Black jagg...`

---

## S15 — 伏羲怒吼"不！"无意识伸手。在代码视觉中，他看到黑色数据流的锯齿状结构，本能地"

**镜头时长:** 4s | **关键帧数:** 3
**地点:** 熵单位降临地点
**情感:** 愤怒、本能觉醒、力量爆发

**视觉事件:**

  1. 伏羲怒吼伸手 (medium shot, eye level)
  2. 代码视觉撕裂 (close-up, eye level)
  3. 黑色数据爆散 (close-up, eye level)

**关键帧详情:**

### S15-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** eye level
- **参考图像:** character/少年伏羲
- **Prompt:** `camera positioned at medium distance capturing boy's upper body, moving closer to emphasize the desperate reach A teenag...`

### S15-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** eye level
- **参考帧:** S15-KF1
- **Motion Prompt:** `POV code-vision perspective showing hand grasping the data structure, intimate digital realm framing Boy lurches forward...`

### S15-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** eye level
- **参考帧:** S15-KF2
- **Motion Prompt:** `camera snapping back to normal reality view, close framing on the physical aftermath Boy lurches forward with arm outstr...`

---

## S16 — 熵单位发出威胁等级提升警告。更多数据触手伸出。伏羲尝试操控地面代码，让泥土变成流

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 熵单位降临地点
**情感:** 紧张、反击、危机中的智慧

**视觉事件:**

  1. 金色代码线扩散 (extreme wide shot, bird's eye view)
  2. 地面变流沙 (wide shot, high angle)
  3. 熵单位下沉挣扎 (wide shot, bird's eye view)

**关键帧详情:**

### S16-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** extreme wide shot
- **相机角度:** bird's eye view
- **参考图像:** location/熵单位降临地点
- **Prompt:** `camera positioned directly overhead at high altitude, capturing full battlefield scope Overhead shot of a swamp battlefi...`

### S16-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** high angle
- **参考帧:** S16-KF1
- **Motion Prompt:** `camera maintaining high overhead position, slight angle to show depth of terrain transformation Boy slams hands toward t...`

### S16-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** bird's eye view
- **参考帧:** S16-KF2
- **Motion Prompt:** `camera overhead capturing full extent of terrain liquefaction and entity struggle Boy slams hands toward the ground, gol...`

---

## S17 — 远处山崖上，一支缠绕绿光的骨箭射来！命中一个熵单位。女娲（17岁）现身高喊"跑啊

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 熵单位降临地点
**情感:** 惊喜、援助到来、紧迫

**视觉事件:**

  1. 骨箭翠光飞射 (extreme wide shot, eye level)
  2. 绿光命中熵体 (medium shot, low angle)
  3. 女娲英姿呐喊 (wide shot, low angle)

**关键帧详情:**

### S17-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** extreme wide shot
- **相机角度:** eye level
- **参考图像:** location/熵单位降临地点
- **Prompt:** `camera positioned at distance tracking the bone arrow's trajectory through stormy sky A bone arrow wrapped in spiraling ...`

### S17-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** low angle
- **参考帧:** S17-KF1
- **Motion Prompt:** `camera low angle capturing the moment of impact on octahedral entity A glowing green-wrapped bone arrow flies through th...`

### S17-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** low angle
- **参考帧:** S17-KF2
- **Motion Prompt:** `camera whip-pans to distant cliff edge framing heroic silhouette against lightning A glowing green-wrapped bone arrow fl...`

---

## S18 — 伏羲踉跄逃离沼泽，回头望了一眼漩涡中汇合的几何体，然后继续奔跑。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 熵单位降临地点
**情感:** 紧张、逃离、心有不甘

**视觉事件:**

  1. 伏羲狂奔踩水 (medium shot, eye level)
  2. 回望几何体汇合 (medium close-up, eye level)
  3. 继续逃亡穿越 (medium shot, low angle)

**关键帧详情:**

### S18-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** eye level
- **参考图像:** location/熵单位降临地点
- **Prompt:** `handheld camera following behind subject at close pursuit distance, shaking with running rhythm A teenage boy running de...`

### S18-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium close-up
- **相机角度:** eye level
- **参考帧:** S18-KF1
- **Motion Prompt:** `handheld camera swinging to capture subject's face as he looks back, revealing background pursuers Boy runs frantically ...`

### S18-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** low angle
- **参考帧:** S18-KF2
- **Motion Prompt:** `low handheld camera pushing forward through branches and rain, dynamic pursuit perspective Boy runs frantically through ...`

---

## S19 — 三个熵单位汇合，发出最终报告。机械音声明目标丢失，标记星球存在原生代码操控者，向

**镜头时长:** 4s | **关键帧数:** 3
**地点:** 熵单位降临地点
**情感:** 不祥、威胁未消、悬念

**视觉事件:**

  1. 三体汇合成阵 (wide shot, low angle)
  2. 光束传输数据 (medium shot, eye level)
  3. 熵体缓升消隐 (medium wide shot, low angle)

**关键帧详情:**

### S19-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** wide shot
- **相机角度:** low angle
- **参考图像:** location/熵单位降临地点
- **Prompt:** `camera positioned low, looking up at three converging octahedral entities forming triangular pattern above dark swamp Th...`

### S19-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** eye level
- **参考帧:** S19-KF1
- **Motion Prompt:** `camera pushing forward toward nearest entity, beam of encoded light visible shooting upward from convergence point Three...`

### S19-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** medium wide shot
- **相机角度:** low angle
- **参考帧:** S19-KF2
- **Motion Prompt:** `camera slowly pulling back as three entities begin ascending into clouds, light beam fading Three octahedral entities sl...`

---

## S20 — 伏羲停下脚步，回头望向远方。雨水流过他的脸。左眼中暗金色的八卦图案缓缓旋转。本集

**镜头时长:** 4s | **关键帧数:** 3
**地点:** 上古雷泽·沼泽地带
**情感:** 沉思、命运的重量、未完待续

**视觉事件:**

  1. 雨水流淌侧脸 (close-up, eye level)
  2. 眨眼显露异瞳 (extreme close-up, eye level)
  3. 八卦旋转渐黑 (extreme close-up, eye level)

**关键帧详情:**

### S20-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** close-up
- **相机角度:** eye level
- **参考图像:** character/少年伏羲
- **Prompt:** `camera positioned at close distance, capturing profile view of subject's face from the side Cinematic close-up of a rain...`

### S20-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考帧:** S20-KF1
- **Motion Prompt:** `camera slowly pushing in toward subject's left eye, transitioning from profile to eye detail Rain streams down the boy's...`

### S20-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考帧:** S20-KF2
- **Motion Prompt:** `camera at extreme close position on left eye, edges of frame darkening with vignette effect Rain streams down the boy's ...`

---
