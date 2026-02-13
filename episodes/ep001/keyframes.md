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
  2. 俯冲穿越数据流 (wide shot, high angle)
  3. 全城光芒闪烁 (wide shot, high angle)

**关键帧详情:**

### S01-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** extreme wide shot
- **相机角度:** bird's eye view
- **参考图像:** location/灵子文明首都·数据中枢 - 全景俯瞰
- **Prompt:** `camera at orbital altitude, looking straight down at luminescent megalopolis Breathtaking futuristic megalopolis from ae...`

### S01-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** high angle
- **参考帧:** S01-KF1
- **Motion Prompt:** `camera at mid-altitude, rapidly descending through streams of flowing data between holographic towers Camera rapidly des...`

### S01-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** high angle
- **参考帧:** S01-KF2
- **Motion Prompt:** `camera hovering above cityscape, capturing sudden system malfunction across entire metropolis Camera rapidly descends fr...`

---

## S02 — 羲和（30岁，身着流光长袍，左眼有金色纹路）站在中枢塔顶，手指在空中快速滑动操控

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 灵子文明首都·数据中枢 - 中枢塔顶
**情感:** 紧迫、专注、英雄气概

**视觉事件:**

  1. 侧后方操控数据 (medium shot, eye level)
  2. 环绕至侧面 (medium shot, eye level)
  3. 正面揭示决意 (medium shot, eye level)

**关键帧详情:**

### S02-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** eye level
- **参考图像:** character/羲和
- **Prompt:** `camera positioned behind and to the side of subject, approximately 45 degrees from back, capturing profile and flowing r...`

### S02-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** eye level
- **参考帧:** S02-KF1
- **Motion Prompt:** `camera at 90-degree side position, profile view of subject with data console visible Character's fingers rapidly swipe a...`

### S02-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** eye level
- **参考帧:** S02-KF2
- **Motion Prompt:** `camera arrives at frontal position, facing subject directly with tower pinnacle backdrop Character's fingers rapidly swi...`

---

## S03 — 观测者AI以温柔女声发出警告。羲和摇头，表情坚毅，提出火种协议。

**镜头时长:** 4s | **关键帧数:** 3
**地点:** 灵子文明首都·数据中枢 - 中枢塔顶
**情感:** 紧迫、决断

**视觉事件:**

  1. 羲和坚定摇头 (medium close-up, eye level)
  2. AI脉动警告 (medium close-up, eye level)
  3. 提出火种协议 (close-up, eye level)

**关键帧详情:**

### S03-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** medium close-up
- **相机角度:** eye level
- **参考图像:** character/羲和
- **Prompt:** `camera positioned at medium-close distance, frontal angle on Xi He with holographic AI visible on the right side Close-u...`

### S03-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** medium close-up
- **相机角度:** eye level
- **参考帧:** S03-KF1
- **Motion Prompt:** `camera begins subtle push-in motion, maintaining frontal framing while holographic AI pulses with warning intensity Char...`

### S03-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** eye level
- **参考帧:** S03-KF2
- **Motion Prompt:** `camera completed push-in to close-up framing, tight on character's determined face with AI partially visible Character s...`

---

## S04 — 观测者AI告知存活率极低且无法保留记忆。羲和微笑，授权执行火种协议。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 灵子文明首都·数据中枢 - 中枢塔顶
**情感:** 悲壮、决绝、浪漫主义的牺牲

**视觉事件:**

  1. 微笑初现 (close-up, eye level)
  2. 金眸闪耀 (close-up, eye level)
  3. 泪光凝聚 (extreme close-up, eye level)

**关键帧详情:**

### S04-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** close-up
- **相机角度:** eye level
- **参考图像:** character/羲和
- **Prompt:** `camera positioned close to subject's face, capturing full facial features with emphasis on forming smile Extreme close-u...`

### S04-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** eye level
- **参考帧:** S04-KF1
- **Motion Prompt:** `camera slowly pushing in, framing tightens from face to upper face region, left eye becoming more prominent A serene smi...`

### S04-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考帧:** S04-KF2
- **Motion Prompt:** `camera very close, framing centered on glowing left eye with partial smile visible, intimate extreme close-up A serene s...`

---

## S05 — 羲和将双手按在控制台上，全身数据被抽取。城市中心升起一道通天光柱，分裂为亿万光点

**镜头时长:** 4s | **关键帧数:** 3
**地点:** 灵子文明首都·数据中枢 - 中枢塔顶
**情感:** 壮烈、升华、宇宙级的壮美

**视觉事件:**

  1. 羲和按压控制台 (extreme wide shot, high angle)
  2. 通天光柱爆发 (extreme wide shot, high angle)
  3. 八卦光点飘向镜头 (extreme wide shot, bird's eye view)

**关键帧详情:**

### S05-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** extreme wide shot
- **相机角度:** high angle
- **参考图像:** location/灵子文明首都·数据中枢 - 中枢塔顶
- **Prompt:** `camera positioned high above the central tower, looking down at the figure at the console Epic wide shot of a figure pre...`

### S05-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** extreme wide shot
- **相机角度:** high angle
- **参考帧:** S05-KF1
- **Motion Prompt:** `camera rapidly ascending and pulling back, revealing the massive light pillar erupting from city center Character presse...`

### S05-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** extreme wide shot
- **相机角度:** bird's eye view
- **参考帧:** S05-KF2
- **Motion Prompt:** `camera at cosmic height overlooking the scattering light seeds, one glowing particle with bagua symbol drifting toward l...`

---

## S06 — 羲和身体逐渐透明化，最后留下遗言，身影消散为光尘。

**镜头时长:** 4s | **关键帧数:** 3
**地点:** 灵子文明首都·数据中枢 - 中枢塔顶
**情感:** 释然、温柔的悲伤

**视觉事件:**

  1. 身体边缘透明化 (medium shot, eye level)
  2. 遗言微笑消散 (medium shot, eye level)
  3. 金瞳渐隐入黑 (medium shot, eye level)

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
- **Motion Prompt:** `camera maintains frontal medium framing, focus gradually softening as subject dissolves Character's body slowly becomes ...`

### S06-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** eye level
- **参考帧:** S06-KF2
- **Motion Prompt:** `camera static as subject fully dissolves, focus on last visible golden circuit eye fading into darkness Character's body...`

---

## S07 — 暴雨之夜，原始粗犷的沼泽景象。少年伏羲与三名猎人在雷泽中追踪雷兽足迹，脚踏泥泞。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 上古雷泽·沼泽地带
**情感:** 原始、紧张、充满生命力

**视觉事件:**

  1. 雷泽夜雨追踪 (extreme wide shot, low angle)
  2. 泥泞艰难跋涉 (wide shot, low angle)
  3. 闪电照亮前路 (wide shot, worm's eye view)

**关键帧详情:**

### S07-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** extreme wide shot
- **相机角度:** low angle
- **参考图像:** location/上古雷泽·沼泽地带
- **Prompt:** `camera positioned at water level, capturing the vast swamp expanse with figures silhouetted against lightning Primordial...`

### S07-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** low angle
- **参考帧:** S07-KF1
- **Motion Prompt:** `camera tracking at knee height beside the wading group, rain sheets falling, water splashing Heavy rain falling in sheet...`

### S07-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** worm's eye view
- **参考帧:** S07-KF2
- **Motion Prompt:** `camera very low in water, tilting up to capture figures against dramatic lightning-lit sky Heavy rain falling in sheets,...`

---

## S08 — 猎人甲大喊让伏羲看天上。镜头随伏羲目光快速甩向天空——天空撕裂，银蓝色几何光流倾

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 上古雷泽·沼泽地带
**情感:** 惊骇、神秘

**视觉事件:**

  1. 猎人示警仰望 (medium shot, eye level)
  2. 快速甩镜上移 (transitional shot, tilting from eye level to low angle)
  3. 天空撕裂光流 (extreme wide shot, worm's eye view)

**关键帧详情:**

### S08-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** eye level
- **参考图像:** character/少年伏羲
- **Prompt:** `camera at character level in swamp terrain, framing hunter and young Fuxi from mid-body up Dramatic low angle looking up...`

### S08-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** transitional shot
- **相机角度:** tilting from eye level to low angle
- **参考帧:** S08-KF1
- **Motion Prompt:** `camera whip-panning vertically from character level toward sky, motion blur visible, following Fuxi's gaze upward Camera...`

### S08-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** extreme wide shot
- **相机角度:** worm's eye view
- **参考帧:** S08-KF2
- **Motion Prompt:** `camera pointing directly upward at dramatic low angle, capturing full sky expanse with geometric light cascade Camera wh...`

---

## S09 — 伏羲左眼突然刺痛，手捂眼睛。光流坠入沼泽中央，溶解成发光漩涡。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 上古雷泽·沼泽地带
**情感:** 痛苦、困惑、命运的触碰

**视觉事件:**

  1. 眼睛特写痛楚 (extreme close-up, eye level)
  2. 瞳孔金光闪现 (extreme close-up, eye level)
  3. 手捂眼睛定格 (extreme close-up, eye level)

**关键帧详情:**

### S09-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考图像:** character/少年伏羲
- **Prompt:** `macro lens positioned extremely close to left eye, filling frame with iris detail Extreme close-up of a young boy's left...`

### S09-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考帧:** S09-KF1
- **Motion Prompt:** `macro lens holding steady on dilating pupil, capturing golden spark deep in iris Eye contracts in pain with pupil rapidl...`

### S09-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考帧:** S09-KF2
- **Motion Prompt:** `macro lens capturing hand rushing into frame to cover eye, motion blur transitioning to stillness Eye contracts in pain ...`

---

## S10 — 伏羲独自走近发光漩涡。漩涡中心浮着一块半透明晶体，散发出神秘的光芒。他伸手向晶体

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 漩涡边缘
**情感:** 神秘、敬畏、命运的吸引

**视觉事件:**

  1. 少年缓步靠近 (medium shot, low angle)
  2. 晶体悬浮旋转 (medium shot, low angle)
  3. 伸手触向晶体 (medium close-up, low angle)

**关键帧详情:**

### S10-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** low angle
- **参考图像:** location/漩涡边缘
- **Prompt:** `camera positioned low near water surface, frontal view facing the boy, medium distance from subject with glowing vortex ...`

### S10-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** low angle
- **参考帧:** S10-KF1
- **Motion Prompt:** `camera closer to subject, low angle capturing both boy and hovering crystal, vortex light intensifying in frame Boy slow...`

### S10-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** medium close-up
- **相机角度:** low angle
- **参考帧:** S10-KF2
- **Motion Prompt:** `camera now close to subject, low angle emphasizing boy's reaching gesture toward crystal, vortex light at peak intensity...`

---

## S11 — 手指触碰晶体的瞬间！金色数据流顺手臂涌入！伏羲痛苦跪地，左眼爆发出强光。当他再次

**镜头时长:** 4s | **关键帧数:** 3
**地点:** 漩涡边缘
**情感:** 剧烈痛苦、觉醒、蜕变

**视觉事件:**

  1. 触碰爆发 (extreme close-up, eye level)
  2. 痛苦跪地 (medium shot, low angle)
  3. 瞳孔蜕变 (extreme close-up, eye level)

**关键帧详情:**

### S11-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考图像:** character/少年伏羲
- **Prompt:** `camera extremely close to point of contact between finger and crystal A young boy kneeling in swamp water screaming in p...`

### S11-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** low angle
- **参考帧:** S11-KF1
- **Motion Prompt:** `camera pulling back from subject kneeling in swamp water, capturing full body convulsion The instant of contact triggers...`

### S11-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考帧:** S11-KF2
- **Motion Prompt:** `camera locked extremely close to left eye, macro lens detail The instant of contact triggers an explosive surge of golde...`

---

## S12 — 代码视觉首次展现：看树木出现绿色生长代码串；看水面出现分子结构网格；看自己手出现

**镜头时长:** 4s | **关键帧数:** 3
**地点:** 漩涡边缘
**情感:** 震惊、敬畏、世界观颠覆

**视觉事件:**

  1. 树木代码涌现 (medium shot, eye level)
  2. 水面分子网格 (medium shot, high angle)
  3. 手部生物电流 (close-up, high angle)

**关键帧详情:**

### S12-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** eye level
- **参考图像:** location/漩涡边缘
- **Prompt:** `POV camera snapping to view ancient trees, first-person perspective at eye height First-person POV through code vision: ...`

### S12-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** high angle
- **参考帧:** S12-KF1
- **Motion Prompt:** `POV camera snapping down to water surface, looking at molecular patterns POV camera quickly pans to trees where green co...`

### S12-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** high angle
- **参考帧:** S12-KF2
- **Motion Prompt:** `POV looking down at own trembling hands held in front of body POV camera quickly pans to trees where green code strings ...`

---

## S13 — 三个苍白的正八面体几何体无声降下，悬浮在沼泽上方，散发冰冷的白光。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 熵单位降临地点
**情感:** 恐惧、威胁、不祥

**视觉事件:**

  1. 几何体显现天际 (extreme wide shot, low angle)
  2. 几何体缓降扫描 (extreme wide shot, low angle)
  3. 悬浮沼泽上方 (extreme wide shot, low angle)

**关键帧详情:**

### S13-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** extreme wide shot
- **相机角度:** low angle
- **参考图像:** location/熵单位降临地点
- **Prompt:** `camera positioned low at swamp level, angled upward toward stormy sky, capturing vast atmospheric scale Three pale white...`

### S13-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** extreme wide shot
- **相机角度:** low angle
- **参考帧:** S13-KF1
- **Motion Prompt:** `camera maintains low position, octahedra now mid-descent, scanning beams visible sweeping terrain below Three octahedral...`

### S13-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** extreme wide shot
- **相机角度:** low angle
- **参考帧:** S13-KF2
- **Motion Prompt:** `camera low at ground level, octahedra hovering above swamp surface, energy fields fully visible creating contrast with o...`

---

## S14 — 熵单位发出机械音宣布检测到异常。黑色数据流卷向猎人乙，猎人身体开始像素化分解。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 熵单位降临地点
**情感:** 恐怖、残酷

**视觉事件:**

  1. 数据触手伸向猎人 (medium shot, eye level)
  2. 身体开始像素化 (medium close-up, eye level)
  3. 数据粒子上升消散 (close-up, low angle)

**关键帧详情:**

### S14-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** eye level
- **参考图像:** character/猎人乙
- **Prompt:** `camera positioned at medium distance capturing both the octahedral entity and the hunter, slightly off-center framing A ...`

### S14-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium close-up
- **相机角度:** eye level
- **参考帧:** S14-KF1
- **Motion Prompt:** `camera pushing in towards the hunter focusing on contact points where dissolution begins Black jagged data tendrils lash...`

### S14-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** low angle
- **参考帧:** S14-KF2
- **Motion Prompt:** `camera at low position tilting upward following the spiral of black data particles ascending toward the entity Black jag...`

---

## S15 — 伏羲怒吼"不！"无意识伸手。在代码视觉中，他看到黑色数据流的锯齿状结构，本能地"

**镜头时长:** 4s | **关键帧数:** 3
**地点:** 熵单位降临地点
**情感:** 愤怒、本能觉醒、力量爆发

**视觉事件:**

  1. 伏羲怒吼伸手 (medium shot, eye level)
  2. 代码视觉锯齿流 (close-up, eye level)
  3. 黑色代码撕裂爆散 (close-up, eye level)

**关键帧详情:**

### S15-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** eye level
- **参考图像:** character/少年伏羲
- **Prompt:** `camera positioned at medium distance, framing the boy from waist up as he lunges forward A teenage boy with blazing dark...`

### S15-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** eye level
- **参考帧:** S15-KF1
- **Motion Prompt:** `POV camera showing code-vision perspective, subjective view of data stream Boy lurches forward with arm outstretched, le...`

### S15-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** eye level
- **参考帧:** S15-KF2
- **Motion Prompt:** `camera snaps back to normal view, close framing on the violent destruction of data stream Boy lurches forward with arm o...`

---

## S16 — 熵单位发出威胁等级提升警告。更多数据触手伸出。伏羲尝试操控地面代码，让泥土变成流

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 熵单位降临地点
**情感:** 紧张、反击、危机中的智慧

**视觉事件:**

  1. 金色代码线扩散 (extreme wide shot, bird's eye view)
  2. 地面变流沙 (wide shot, high angle)
  3. 熵单位下沉挣扎 (wide shot, high angle)

**关键帧详情:**

### S16-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** extreme wide shot
- **相机角度:** bird's eye view
- **参考图像:** location/熵单位降临地点
- **Prompt:** `camera positioned directly overhead, capturing full battlefield from above Overhead shot of a swamp battlefield, a young...`

### S16-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** high angle
- **参考帧:** S16-KF1
- **Motion Prompt:** `camera maintaining overhead position, slight angle to show depth of terrain transformation Boy slams hands toward the gr...`

### S16-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** high angle
- **参考帧:** S16-KF2
- **Motion Prompt:** `camera overhead capturing full effect of terrain manipulation and entity struggle Boy slams hands toward the ground, gol...`

---

## S17 — 远处山崖上，一支缠绕绿光的骨箭射来！命中一个熵单位。女娲（17岁）现身高喊"跑啊

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 熵单位降临地点
**情感:** 惊喜、援助到来、紧迫

**视觉事件:**

  1. 骨箭飞行 (wide shot, eye level)
  2. 箭矢命中 (medium shot, low angle)
  3. 女娲呼喊 (medium wide shot, low angle)

**关键帧详情:**

### S17-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** wide shot
- **相机角度:** eye level
- **参考图像:** location/熵单位降临地点
- **Prompt:** `camera positioned parallel to arrow trajectory, tracking the projectile through space A bone arrow wrapped in spiraling ...`

### S17-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** low angle
- **参考帧:** S17-KF1
- **Motion Prompt:** `camera low and close to impact point, capturing explosion upward A glowing green-wrapped bone arrow flies through the fr...`

### S17-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** medium wide shot
- **相机角度:** low angle
- **参考帧:** S17-KF2
- **Motion Prompt:** `camera on cliff edge looking up at heroic figure silhouetted against lightning A glowing green-wrapped bone arrow flies ...`

---

## S18 — 伏羲踉跄逃离沼泽，回头望了一眼漩涡中汇合的几何体，然后继续奔跑。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** 熵单位降临地点
**情感:** 紧张、逃离、心有不甘

**视觉事件:**

  1. 沼泽狂奔 (medium shot, eye level)
  2. 回望威胁 (medium close-up, low angle)
  3. 踉跄前行 (medium shot, eye level)

**关键帧详情:**

### S18-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** eye level
- **参考图像:** location/熵单位降临地点
- **Prompt:** `handheld camera following behind subject at medium distance, shaky pursuit style tracking through swamp terrain A teenag...`

### S18-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium close-up
- **相机角度:** low angle
- **参考帧:** S18-KF1
- **Motion Prompt:** `handheld camera swings to capture boy's backward glance, slightly below eye level, chaotic motion following his turn Boy...`

### S18-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** eye level
- **参考帧:** S18-KF2
- **Motion Prompt:** `handheld camera continues aggressive pursuit, closer distance, maximum shake intensity as subject stumbles forward Boy r...`

---

## S19 — 三个熵单位汇合，发出最终报告。机械音声明目标丢失，标记星球存在原生代码操控者，向

**镜头时长:** 4s | **关键帧数:** 3
**地点:** 熵单位降临地点
**情感:** 不祥、威胁未消、悬念

**视觉事件:**

  1. 三体汇合成阵 (medium shot, low angle)
  2. 光束射向云端 (medium shot, low angle)
  3. 实体缓缓升空 (medium wide shot, low angle)

**关键帧详情:**

### S19-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** low angle
- **参考图像:** location/熵单位降临地点
- **Prompt:** `camera positioned at medium distance below the three converging octahedral entities, looking up at their triangular form...`

### S19-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** low angle
- **参考帧:** S19-KF1
- **Motion Prompt:** `camera slowly pushing forward toward the nearest entity while maintaining upward angle, capturing the encoded light beam...`

### S19-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** medium wide shot
- **相机角度:** low angle
- **参考帧:** S19-KF2
- **Motion Prompt:** `camera pulling back slowly as the three entities begin ascending, revealing their departure from the swamp location Thre...`

---

## S20 — 伏羲停下脚步，回头望向远方。雨水流过他的脸。左眼中暗金色的八卦图案缓缓旋转。本集

**镜头时长:** 4s | **关键帧数:** 3
**地点:** 上古雷泽·沼泽地带
**情感:** 沉思、命运的重量、未完待续

**视觉事件:**

  1. 雨水流淌侧脸 (close-up, eye level)
  2. 眨眼露出异瞳 (extreme close-up, eye level)
  3. 八卦旋转渐黑 (extreme close-up, eye level)

**关键帧详情:**

### S20-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** close-up
- **相机角度:** eye level
- **参考图像:** character/少年伏羲
- **Prompt:** `camera positioned at close range capturing side profile of face, slight angle to emphasize cheekbone and eye Cinematic c...`

### S20-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考帧:** S20-KF1
- **Motion Prompt:** `camera slowly pushing in toward left eye, framing tightens from face to eye region Rain streams down the boy's face in s...`

### S20-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考帧:** S20-KF2
- **Motion Prompt:** `camera at maximum proximity to left eye, iris fills majority of frame Rain streams down the boy's face in slow motion, a...`

---
