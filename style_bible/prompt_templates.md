# Prompt 模板规范 — 伏羲纪元

## 模块化 Prompt 结构

每个镜头的生成 Prompt 必须按以下模块拼接：

```
[STYLE PREFIX]     — 全局风格前缀（每集统一）
[CHARACTER PREFIX]  — 角色外貌描述（从角色卡复制）
[LOCATION PREFIX]   — 场景环境描述（从场景卡复制）
[SHOT ACTION]       — 当前镜头的具体动作/画面
[CAMERA LANGUAGE]   — 景别、角度、运镜
[LIGHTING]          — 光线描述
[MOOD]              — 情绪氛围
```

## 全局风格前缀（Style Prefix）

```
cinematic film still, photorealistic, 16:9 horizontal aspect ratio, movie quality lighting, shallow depth of field, epic sci-fi meets ancient mythology aesthetic, data-punk visual style
```

## 负向 Prompt（每张必加）

```
anatomy error, face distortion, extra limbs, extra fingers, watermark, text artifacts, oversharpen, uncanny look, blurry, low quality, cartoon, anime, illustration style, deformed face, asymmetric eyes, bad proportions, cropped, out of frame
```

---

## 特效叠加 Prompt 模块

### 代码视觉（Code Sight）— 第一集觉醒场景
```
overlay of translucent golden data streams, floating code characters, matrix-like digital rain in gold, holographic data structures visible on all objects, trees showing green growth code strings, water surface showing molecular grid structure, human skin showing blue bioelectric current lines
```

### 八卦图案（Bagua Pattern）— 左眼标识
```
glowing dark golden bagua trigram pattern, tiny rotating octagonal symbol in pupil, ancient Chinese cosmological diagram emitting golden light, subtle glow in darkness
```

### 像素化分解（Pixelation Dissolve）— 熵的格式化攻击
```
body dissolving into digital pixels, voxel disintegration effect from contact point spreading outward, matter breaking apart into cubic data fragments, glitch distortion, white pixel fragments floating upward
```

### 金色数据流操控（Golden Data Manipulation）— 伏羲能力
```
golden data streams flowing from hands, energy ripples on contact surface, code rewriting effect on physical matter, luminous golden veins appearing on arms
```

### 黑色数据触手（Dark Data Tendrils）— 熵单位攻击
```
black data tendrils extending from geometric vertices, jagged sawtooth data structure visible in code vision, dark flowing streams wrapping around target, cold mechanical precision
```

### 火种降临（Seed Descent）— 第一集核心事件
```
silver-blue geometric light streams tearing through stormy sky, structured energy falling like cosmic rain, glowing vortex forming in water on impact, translucent crystal floating at vortex center containing golden patterns
```

### 通天光柱（Sky Pillar）— 火种协议发射
```
massive light pillar erupting from city center, pillar reaching into sky fragmenting into billions of light points, light points scattering into cosmos like dandelion seeds, one light point containing faint bagua pattern, cosmic scale
```

---

## 场景光线模板

| 场景 | 光线描述 |
|------|----------|
| 灵子文明（正常） | `self-luminous architecture, warm golden-white ambient, data rivers providing overhead lighting, futuristic clean lighting` |
| 灵子文明（警报） | `flickering stuttering light, cold silver-blue shift, red alarm flashes, light sources dying intermittently` |
| 火种牺牲 | `intense golden radiance emanating from character, overexposed golden highlights, body dissolving into light particles, epic backlighting fading to white` |
| 暴雨夜沼泽 | `stormy night, rain, dramatic lightning illumination, near-total darkness between flashes, mud reflecting occasional light` |
| 火种坠落 | `silver-blue geometric light tearing through dark sky, impact creating localized silver-blue glow on swamp water, crystal self-illuminating` |
| 代码视觉激活 | `golden rim lighting on character face, dark background with floating golden data overlays, dramatic contrast between golden left eye and dark surroundings` |
| 熵单位降临 | `sky darkening unnaturally, ominous red glow from geometric cracks providing sole light source, low-key lighting, pulsing red rhythm, threatening atmosphere` |
| 像素化格式化 | `white pixel fragments emitting light as body dissolves, cold clinical light from disintegration, contrasting with dark surroundings` |
| 力量爆发 | `golden energy ripple from hands illuminating ground, brief golden flash on impact, mud reflecting golden light` |
| 逃离余震 | `minimal light, rain, faint golden glow from left eye in near-total darkness, distant red glow of entities behind` |

---

## Prompt 拼接示例

### 示例 1：S01 — 灵子文明开场

```
[STYLE] cinematic film still, photorealistic, 16:9 horizontal aspect ratio, movie quality lighting, shallow depth of field, epic sci-fi meets ancient mythology aesthetic
[LOCATION] breathtaking futuristic city built entirely of light, luminous architecture, rivers of data flowing through sky between buildings
[ACTION] suddenly all light begins glitching and stuttering, piercing alarm, city-scale emergency
[CAMERA] wide shot, crane down revealing full city, epic scale
[LIGHTING] self-luminous architecture transitioning to flickering alarm state, warm gold shifting cold
[MOOD] awe turning to dread, cosmic scale destruction imminent
```

### 示例 2：S09 — 伏羲触碰晶体觉醒

```
[STYLE] cinematic film still, photorealistic, 16:9 horizontal aspect ratio, movie quality lighting
[CHARACTER] young male age 16, angular face, long black hair half-tied, dark brown fur vest, barefoot
[LOCATION] dark swamp at night, rain, glowing silver-blue vortex in water
[ACTION] hand touching translucent crystal, golden data streams erupting from crystal flowing up arm like glowing veins, face contorted in pain kneeling in water, left eye erupting with golden light
[CAMERA] extreme close-up hand → face, dynamic cut
[LIGHTING] golden energy burst from crystal illuminating face from below, rain catching golden light
[MOOD] shock, searing pain, transformation, point of no return
```

### 示例 3：S13 — 熵单位降临

```
[STYLE] cinematic film still, photorealistic, 16:9 horizontal aspect ratio, ominous atmosphere
[CHARACTER] three pale white octahedron geometric entities, glowing red cracks, 2-3x human size
[LOCATION] dark swamp, sky unnaturally darkened beyond normal storm
[ACTION] three entities descending silently from sky in triangle formation, hovering above swamp
[CAMERA] low angle, slow tilt down from sky, threatening perspective
[LIGHTING] near darkness, red cracks sole light source, pulsing in sync
[MOOD] cold menace, mechanical threat, alien invasion
```

### 示例 4：S17 — 女娲首次登场

```
[STYLE] cinematic film still, photorealistic, 16:9 horizontal aspect ratio, dramatic action
[CHARACTER] young female age 17, oval face, wild beauty, dark brown side braid with vine, emerald leaf armor, white bone bow
[LOCATION] distant cliff overlooking swamp, stormy night
[ACTION] girl standing on cliff edge, shouting, glowing green bone arrow streaking through rain toward geometric entities below, boy in swamp stumbling and running
[CAMERA] wide shot, dramatic angle, arrow trajectory crossing frame
[LIGHTING] lightning flash revealing cliff figure, green arrow trail providing dynamic light streak
[MOOD] urgent rescue, adrenaline, hope amid chaos
```
