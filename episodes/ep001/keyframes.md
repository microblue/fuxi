# ep001 — 关键帧规划

## 概览

**总镜头数:** 20
**总时长:** 58s

关键帧策略:
- **第1帧（T2I）**: 文本到图像，设定场景/角色/气氛
- **后续帧（I2V）**: 基于第1帧作为参考，生成镜头内运动

---

## S01 — 极致璀璨的未来都市。建筑由光构成，数据河流在空中流淌。突然，所有光芒开始抽搐，城

**镜头时长:** 3s | **关键帧数:** 3
**地点:** lingzi_civilization_capital
**情感:** awe turning to dread

**视觉事件:**

  1. 都市全景俯瞰 (extreme wide shot, bird's eye view)
  2. 光芒抽搐闪烁 (wide shot, high angle)
  3. 城市警报爆发 (wide shot, slightly high angle)

**关键帧详情:**

### S01-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** extreme wide shot
- **相机角度:** bird's eye view
- **参考图像:** location/lingzi_civilization_capital
- **Prompt:** `crane positioned high above the city, beginning descent, capturing full metropolitan expanse breathtaking futuristic cit...`

### S01-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** high angle
- **参考帧:** S01-KF1
- **Motion Prompt:** `crane mid-descent, capturing city at three-quarter view as glitch begins smooth crane down revealing city, then sudden g...`

### S01-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** slightly high angle
- **参考帧:** S01-KF2
- **Motion Prompt:** `crane completing descent, lower vantage revealing city-wide emergency state smooth crane down revealing city, then sudde...`

---

## S02 — 羲和（30岁，身着流光长袍，左眼有金色纹路）站在中枢塔顶，手指在空中快速滑动，金

**镜头时长:** 3s | **关键帧数:** 3
**地点:** lingzi_civilization_capital
**情感:** focused urgency

**视觉事件:**

  1. 指尖触碰数据流 (medium shot, low angle)
  2. 数据流随指飞舞 (medium shot, low angle)
  3. 城市光影闪烁 (medium shot, low angle)

**关键帧详情:**

### S02-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** low angle
- **参考图像:** character/xihe
- **Prompt:** `handheld camera positioned slightly below eye level, capturing subject from waist up with tower edge visible East Asian ...`

### S02-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** low angle
- **参考帧:** S02-KF1
- **Motion Prompt:** `handheld with subtle organic movement, maintaining framing on hands and upper body, slight rightward drift fingers danci...`

### S02-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** low angle
- **参考帧:** S02-KF2
- **Motion Prompt:** `handheld camera with natural breathing motion, framing subject against flickering cityscape backdrop fingers dancing thr...`

---

## S03 — 羲和微笑，从容决断。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** lingzi_civilization_capital
**情感:** resolute courage, noble sacrifice

**视觉事件:**

  1. 凝视决断 (close-up, eye level)
  2. 微笑浮现 (close-up, eye level)
  3. 颔首授权 (close-up, eye level)

**关键帧详情:**

### S03-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** close-up
- **相机角度:** eye level
- **参考图像:** character/xihe
- **Prompt:** `camera positioned at intimate close-up distance, framing face from forehead to chin, centered on eyes close-up of East A...`

### S03-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** eye level
- **参考帧:** S03-KF1
- **Motion Prompt:** `camera maintains intimate close-up framing, slight focus pull emphasizing forming smile steady shot, subtle smile formin...`

### S03-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** eye level
- **参考帧:** S03-KF2
- **Motion Prompt:** `camera holds steady as subject performs slight downward head nod, maintaining close framing steady shot, subtle smile fo...`

---

## S04 — 羲和将双手按在控制台，全身数据被抽取。城市中心升起一道通天光柱，分裂为亿万光点洒

**镜头时长:** 4s | **关键帧数:** 3
**地点:** lingzi_civilization_capital
**情感:** epic sacrifice, cosmic scale

**视觉事件:**

  1. 双手按下控制台 (medium shot, eye level)
  2. 数据抽离光柱爆发 (wide shot, low angle)
  3. 光点散落宇宙 (extreme wide shot, bird's eye view)

**关键帧详情:**

### S04-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** eye level
- **参考图像:** character/xihe
- **Prompt:** `camera positioned at medium distance facing holographic console, capturing upper body and hands celestial East Asian sag...`

### S04-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** low angle
- **参考帧:** S04-KF1
- **Motion Prompt:** `camera pulling back and tilting upward as light pillar erupts, revealing city scale hands press down, data rips from bod...`

### S04-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** extreme wide shot
- **相机角度:** bird's eye view
- **参考帧:** S04-KF2
- **Motion Prompt:** `camera at cosmic distance looking down, revealing infinite expanse as light fragments scatter hands press down, data rip...`

---

## S05 — 羲和身体逐渐透明，面带微笑说出最后的话。彻底消散。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** lingzi_civilization_capital
**情感:** tender farewell, bittersweet

**视觉事件:**

  1. 面容开始透明 (close-up, eye level)
  2. 微笑诀别消散 (close-up, eye level)
  3. 化光消逝白屏 (close-up, eye level)

**关键帧详情:**

### S05-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** close-up
- **相机角度:** eye level
- **参考图像:** character/xihe
- **Prompt:** `camera positioned intimately close to subject's face, static framing capturing delicate facial features close-up of East...`

### S05-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** eye level
- **参考帧:** S05-KF1
- **Motion Prompt:** `camera maintains intimate close framing as subject dissolves, capturing final expression body slowly becoming transparen...`

### S05-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** eye level
- **参考帧:** S05-KF2
- **Motion Prompt:** `camera holds position as visual field transforms to pure luminous white body slowly becoming transparent from edges inwa...`

---

## S06 — 硬切到原始世界。暴雨夜，沼泽地带。伏羲（16岁）与猎人正在追踪雷兽足迹。猎人甲抬

**镜头时长:** 3s | **关键帧数:** 3
**地点:** primordial_swamp_night
**情感:** primal, sudden alarm

**视觉事件:**

  1. 暴雨沼泽追踪 (wide shot, low angle)
  2. 猎人突然止步 (medium shot, low angle)
  3. 众人仰望惊呼 (medium shot, low angle)

**关键帧详情:**

### S06-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** wide shot
- **相机角度:** low angle
- **参考图像:** location/primordial_swamp_night
- **Prompt:** `handheld camera low to the ground, pushing through swamp vegetation, capturing figures moving through torrential rain pr...`

### S06-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** low angle
- **参考帧:** S06-KF1
- **Motion Prompt:** `handheld camera stabilizes at low angle, framing hunters and young Fuxi as they halt abruptly, rain pouring down charact...`

### S06-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** low angle
- **参考帧:** S06-KF2
- **Motion Prompt:** `handheld camera tilts upward following hunter's pointing gesture and their gazes toward the stormy sky characters moving...`

---

## S07 — 天空撕裂，不是闪电，而是银蓝色、有几何形状的光流——火种残迹。光流坠入沼泽中央。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** primordial_swamp_night
**情感:** awe, pain, mystery

**视觉事件:**

  1. 天空撕裂光流降 (wide shot, low angle)
  2. 光坠沼泽涡漩起 (medium wide shot, eye level)
  3. 少年握眼剧痛 (close-up, eye level)

**关键帧详情:**

### S07-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** wide shot
- **相机角度:** low angle
- **参考图像:** location/primordial_swamp_night
- **Prompt:** `camera positioned low at swamp level, tilting upward toward the tearing sky, capturing vast primordial landscape sky tea...`

### S07-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium wide shot
- **相机角度:** eye level
- **参考帧:** S07-KF1
- **Motion Prompt:** `camera at medium distance capturing the impact point, swamp center framed with boy visible in foreground edge camera til...`

### S07-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** eye level
- **参考帧:** S07-KF2
- **Motion Prompt:** `camera close to subject after rack focus shift, intimate framing on boy's face and hand gripping eye camera tilts up to ...`

---

## S08 — 光流坠入沼泽中央，溶解成发光漩涡。漩涡中心浮着一块半透明晶体。伏羲独自走近。

**镜头时长:** 2s | **关键帧数:** 2
**地点:** primordial_swamp_night
**情感:** drawn, hypnotic pull

**视觉事件:**

  1. 漩涡发光浮晶 (medium shot, eye level)
  2. 伏羲近前晶体 (medium close-up, eye level)

**关键帧详情:**

### S08-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** eye level
- **参考图像:** character/fuxi
- **Prompt:** `camera positioned at medium distance behind and to the side of Fuxi, framing both boy and glowing vortex ahead glowing s...`

### S08-KF2 (i2v)

- **时间:** 1.0s (持续 0.0s)
- **类型:** i2v
- **景别:** medium close-up
- **相机角度:** eye level
- **参考帧:** S08-KF1
- **Motion Prompt:** `camera pushed in closer, now framing Fuxi's upper body with vortex and crystal prominent in background slow push in foll...`

---

## S09 — 伏羲伸手触碰晶体。金色数据流顺手臂涌入！伏羲痛苦跪地，左眼爆发出强光。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** primordial_swamp_night
**情感:** shock, searing pain, transformation

**视觉事件:**

  1. 手指触碰晶体 (extreme close-up, eye level)
  2. 金色能量爆发涌入手臂 (extreme close-up, eye level)
  3. 跪地左眼爆发金光 (extreme close-up, low angle)

**关键帧详情:**

### S09-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考图像:** character/fuxi
- **Prompt:** `camera positioned inches from hand and crystal surface, macro framing capturing tactile moment extreme close-up of young...`

### S09-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考帧:** S09-KF1
- **Motion Prompt:** `camera following energy flow from crystal up the arm, dynamic tracking movement finger touches crystal → instant golden ...`

### S09-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** extreme close-up
- **相机角度:** low angle
- **参考帧:** S09-KF2
- **Motion Prompt:** `camera low in water looking up at face, dramatic upward framing emphasizing transformation finger touches crystal → inst...`

---

## S10 — 左瞳孔变成暗金色，深处有微小八卦图案旋转。代码视觉首次展现：看树木=绿色生长代码

**镜头时长:** 3s | **关键帧数:** 3
**地点:** primordial_swamp_night
**情感:** disorientation, wonder

**视觉事件:**

  1. 瞳孔金色变化 (extreme close-up, eye level)
  2. 代码视觉树木 (medium shot, eye level)
  3. 手部电流可视 (close-up, high angle)

**关键帧详情:**

### S10-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考图像:** character/fuxi
- **Prompt:** `macro lens positioned inches from left eye, capturing iris detail extreme close-up of left eye, pupil transformed to dar...`

### S10-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** eye level
- **参考帧:** S10-KF1
- **Motion Prompt:** `first-person POV camera panning across swamp environment, viewing trees eye close-up 1s, then POV shift — environment ov...`

### S10-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** close-up
- **相机角度:** high angle
- **参考帧:** S10-KF2
- **Motion Prompt:** `POV looking down at own hands, slight tilt movement eye close-up 1s, then POV shift — environment overlaid with data vis...`

---

## S11 — 伏羲震惊地看着自己的双手和周围的世界。

**镜头时长:** 2s | **关键帧数:** 2
**地点:** primordial_swamp_night
**情感:** shock, existential realization

**视觉事件:**

  1. 凝视双手 (medium close-up, slight low angle)
  2. 环顾世界 (medium close-up, slight low angle)

**关键帧详情:**

### S11-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** medium close-up
- **相机角度:** slight low angle
- **参考图像:** character/fuxi
- **Prompt:** `camera positioned slightly below eye level, capturing upper body and hands in shallow swamp water medium close-up of 16-...`

### S11-KF2 (i2v)

- **时间:** 1.0s (持续 0.0s)
- **类型:** i2v
- **景别:** medium close-up
- **相机角度:** slight low angle
- **参考帧:** S11-KF1
- **Motion Prompt:** `camera maintains slight low angle as subject's gaze lifts and turns to survey surroundings boy looking at hands, then sl...`

---

## S12 — 天空骤然暗下。

**镜头时长:** 2s | **关键帧数:** 2
**地点:** primordial_swamp_night
**情感:** sudden dread, atmosphere shift

**视觉事件:**

  1. 天空开始变暗 (extreme wide shot, high angle)
  2. 黑暗吞噬光明 (extreme wide shot, high angle)

**关键帧详情:**

### S12-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** extreme wide shot
- **相机角度:** high angle
- **参考图像:** location/primordial_swamp_night
- **Prompt:** `camera positioned high above swamp, capturing vast landscape with tiny figure below, bird's eye perspective on darkening...`

### S12-KF2 (i2v)

- **时间:** 1.0s (持续 0.0s)
- **类型:** i2v
- **景别:** extreme wide shot
- **相机角度:** high angle
- **参考帧:** S12-KF1
- **Motion Prompt:** `camera maintains elevated position, framing complete atmospheric transformation as supernatural darkness spreads across ...`

---

## S13 — 三个苍白几何体（正八面体）无声降下。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** primordial_swamp_night
**情感:** cold menace, mechanical threat

**视觉事件:**

  1. 几何体从天降 (extreme wide shot, low angle)
  2. 编队缓慢下降 (wide shot, low angle)
  3. 悬停威压呈现 (wide shot, low angle)

**关键帧详情:**

### S13-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** extreme wide shot
- **相机角度:** low angle
- **参考图像:** character/entropy_unit
- **Prompt:** `camera positioned at ground level in swamp, angled upward toward darkened sky, capturing vast scale of descending entiti...`

### S13-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** low angle
- **参考帧:** S13-KF1
- **Motion Prompt:** `camera maintaining low position, slowly tilting downward to follow the descending geometric entities as they approach ho...`

### S13-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** low angle
- **参考帧:** S13-KF2
- **Motion Prompt:** `camera low among swamp vegetation, framing hovering entities against sky with implied human scale reference below three ...`

---

## S14 — 黑色数据流卷向猎人乙，猎人身体开始像素化分解。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** primordial_swamp_night
**情感:** horror, helplessness

**视觉事件:**

  1. 黑色触手射出 (full shot, eye level)
  2. 触手缠绕挣扎 (full shot, low angle)
  3. 身体像素分解 (medium shot, eye level)

**关键帧详情:**

### S14-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** full shot
- **相机角度:** eye level
- **参考图像:** character/hunter_b
- **Prompt:** `handheld camera at medium distance, slight shake conveying urgency and chaos black corrupting data tendrils shooting fro...`

### S14-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** full shot
- **相机角度:** low angle
- **参考帧:** S14-KF1
- **Motion Prompt:** `handheld low angle following the coiling motion, erratic movement emphasizing struggle tendrils lashing out fast, coilin...`

### S14-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** eye level
- **参考帧:** S14-KF2
- **Motion Prompt:** `handheld tilting upward following pixelation progression from feet to torso tendrils lashing out fast, coiling around vi...`

---

## S15 — 伏羲怒吼伸手。代码视觉中看到黑色数据流的锯齿结构，本能'抓住'并扯断！

**镜头时长:** 4s | **关键帧数:** 3
**地点:** primordial_swamp_night
**情感:** rage, instinctive power

**视觉事件:**

  1. 怒吼特写 (extreme close-up, eye level)
  2. 代码视觉POV (medium shot, eye level)
  3. 能量脉冲碎裂 (medium shot, low angle)

**关键帧详情:**

### S15-KF1 (t2i)

- **时间:** 0.0s (持续 1.3333333333333333s)
- **类型:** t2i
- **景别:** extreme close-up
- **相机角度:** eye level
- **参考图像:** character/fuxi
- **Prompt:** `camera inches from face, capturing intense facial details, slight push-in to emphasize rage close-up of East Asian boy's...`

### S15-KF2 (i2v)

- **时间:** 1.3333333333333333s (持续 1.3333333333333333s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** eye level
- **参考帧:** S15-KF1
- **Motion Prompt:** `POV camera showing corrupted data stream, digital overlay effect, red-highlighted jagged structures face snap with rage,...`

### S15-KF3 (i2v)

- **时间:** 2.6666666666666665s (持续 0.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** low angle
- **参考帧:** S15-KF2
- **Motion Prompt:** `low angle capturing hand grasping tendril, camera pulls back slightly to reveal full energy explosion face snap with rag...`

---

## S16 — 熵单位判断威胁提升。更多数据触手伸出。伏羲尝试操控地面代码，让泥土变流沙，困住单

**镜头时长:** 3s | **关键帧数:** 3
**地点:** primordial_swamp_night
**情感:** escalating danger, desperate improvisation

**视觉事件:**

  1. 触手延伸逼近 (wide shot, eye level)
  2. 双手触地释能 (medium shot, low angle)
  3. 地面液化困敌 (wide shot, high angle)

**关键帧详情:**

### S16-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** wide shot
- **相机角度:** eye level
- **参考图像:** character/fuxi
- **Prompt:** `camera positioned at medium distance capturing full confrontation between boy and entities full shot of 16-year-old East...`

### S16-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** low angle
- **参考帧:** S16-KF1
- **Motion Prompt:** `camera low near ground level emphasizing boy's desperate action and golden energy burst tendrils reaching, boy drops to ...`

### S16-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** wide shot
- **相机角度:** high angle
- **参考帧:** S16-KF2
- **Motion Prompt:** `camera elevated pulling back to reveal full scope of liquefying ground effect tendrils reaching, boy drops to ground, go...`

---

## S17 — 远处山崖，一支缠绕绿光的骨箭射来！女娲（17岁）现身高喊。伏羲踉跄逃离。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** primordial_swamp_night
**情感:** urgent rescue, adrenaline

**视觉事件:**

  1. 骨箭破空而来 (wide shot, low angle)
  2. 女娲崖顶现身 (medium shot, low angle)
  3. 伏羲踉跄逃离 (medium shot, eye level)

**关键帧详情:**

### S17-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** wide shot
- **相机角度:** low angle
- **参考图像:** location/primordial_swamp_night
- **Prompt:** `camera low in swamp looking up towards distant cliff, capturing arrow trajectory across frame wide shot: glowing green b...`

### S17-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** low angle
- **参考帧:** S17-KF1
- **Motion Prompt:** `camera positioned below cliff edge looking up at figure standing heroically against stormy sky arrow flies across frame ...`

### S17-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** eye level
- **参考帧:** S17-KF2
- **Motion Prompt:** `camera retreating through swamp water as subject stumbles forward in panic arrow flies across frame trailing green light...`

---

## S18 — 几何体汇合。熵单位发出最终报告。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** primordial_swamp_night
**情感:** cold calculation, ominous promise

**视觉事件:**

  1. 几何体汇聚成阵 (medium shot, eye level)
  2. 红色裂纹同步 (medium shot, eye level)
  3. 熵单位报告 (medium shot, slightly low angle)

**关键帧详情:**

### S18-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** medium shot
- **相机角度:** eye level
- **参考图像:** character/entropy_unit
- **Prompt:** `camera positioned at medium distance facing the three octahedron entities as they begin to regroup three octahedron enti...`

### S18-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** eye level
- **参考帧:** S18-KF1
- **Motion Prompt:** `camera slowly rotating around the formation, capturing synchronized pulsing patterns entities floating together, red cra...`

### S18-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** medium shot
- **相机角度:** slightly low angle
- **参考帧:** S18-KF2
- **Motion Prompt:** `camera completing rotation arc, slight low angle emphasizing the entities' cold authority entities floating together, re...`

---

## S19 — 伏羲在雨中回头望，左眼在黑暗中发出微弱金光。惊恐、困惑、但活着。

**镜头时长:** 3s | **关键帧数:** 3
**地点:** primordial_swamp_night
**情感:** shaken survival, lingering fear, questions unanswered

**视觉事件:**

  1. 雨中停步回望 (medium close-up, eye level)
  2. 左眼金光显现 (medium close-up, eye level)
  3. 凝视后转身离去 (medium close-up, eye level)

**关键帧详情:**

### S19-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** medium close-up
- **相机角度:** eye level
- **参考图像:** character/fuxi
- **Prompt:** `camera positioned at chest height, capturing upper body and face from slight three-quarter angle as subject turns medium...`

### S19-KF2 (i2v)

- **时间:** 1.0s (持续 1.0s)
- **类型:** i2v
- **景别:** medium close-up
- **相机角度:** eye level
- **参考帧:** S19-KF1
- **Motion Prompt:** `camera steady at face level, framing turned profile with emphasis on left eye visible to camera boy stops running, turns...`

### S19-KF3 (i2v)

- **时间:** 2.0s (持续 0.0s)
- **类型:** i2v
- **景别:** medium close-up
- **相机角度:** eye level
- **参考帧:** S19-KF2
- **Motion Prompt:** `camera maintains position as subject's head turns away, golden eye glow lingering before face angles forward boy stops r...`

---

## S20 — 黑屏 + 本集终字样

**镜头时长:** 2s | **关键帧数:** 2
**地点:** black_screen
**情感:** lingering suspense

**视觉事件:**

  1. 黑屏准备 (full frame, frontal)
  2. 本集终显现 (full frame, frontal)

**关键帧详情:**

### S20-KF1 (t2i)

- **时间:** 0.0s (持续 1.0s)
- **类型:** t2i
- **景别:** full frame
- **相机角度:** frontal
- **参考图像:** location/black_screen
- **Prompt:** `fixed camera facing pure black frame, no dimensional reference pure black screen with white text fading in`

### S20-KF2 (i2v)

- **时间:** 1.0s (持续 0.0s)
- **类型:** i2v
- **景别:** full frame
- **相机角度:** frontal
- **参考帧:** S20-KF1
- **Motion Prompt:** `fixed camera facing centered text overlay on black background text fade in 1s, hold 1s`

---
