# PromptBuilder 需求文档

> 伏羲项目 — 统一提示词生成器规范  
> 版本：1.0  
> 日期：2025-02-05  
> 作者：Director Chen  
> 实现者：Arc

---

## 1. 概述

### 1.1 背景

伏羲项目需要生成大量图像资产，包括角色参考图、场景参考图、道具图以及关键帧镜头。目前提示词的组装是手工完成的，效率低且容易出错。需要一个统一的 PromptBuilder 来自动化这个过程。

### 1.2 使用场景

| 场景 | 模式 | 说明 |
|------|------|------|
| **资产定义** | T2I（纯文生图） | 生成角色参考图、场景参考图、道具图 |
| **关键帧生成** | I2I（图生图 + 提示词） | 基于参考图 + 动作描述生成具体镜头 |

### 1.3 核心目标

- 统一提示词格式，确保一致的视觉风格
- 自动化组装，减少人工错误
- 支持 T2I 和 I2I 两种模式的无缝切换
- 与现有 `style_bible/prompt_templates.md` 完全兼容

---

## 2. 输入数据源

### 2.1 characters.json 结构

**路径**: `/home/dz/fuxi/assets/characters/characters.json`

```json
{
  "metadata": { ... },
  "characters": {
    "<character_id>": {
      "zh_name": "string",          // 中文名
      "aliases": ["string"],        // 别名列表
      "title": "string",            // 头衔
      "brief": "string",            // 简介
      "age_start": number,          // 起始年龄
      "age_end": number,            // 结束年龄
      "gender": "string",           // 性别
      
      "appearance": {
        "face": "string",           // 脸部描述
        "eyes": "string",           // 眼睛描述
        "hair": "string",           // 发型描述
        "build": "string",          // 体型描述
        "distinctive_features": ["string"],  // 特征标签
        "color_palette": ["string"],         // 配色方案
        "outfit": {
          "primary": "string",      // 主要服装
          "alternate": "string",    // 备选服装
          "accessories": "string"   // 配饰
        },
        "reference_inspiration": "string"    // 参考灵感
      },
      
      "visual_keywords": ["string"],         // 视觉关键词列表
      
      "prompt_template": {
        "style": "string",                   // 风格标签
        "base_description": "string",        // 基础描述（核心提示词）
        "scene_types": ["string"],           // 场景类型建议
        "negative_traits": "string",         // 负向提示建议
        "composition_tips": "string"         // 构图提示
      }
    }
  }
}
```

**必须提取的字段**:
- `appearance.face`, `eyes`, `hair`, `build` — 拼接角色外貌
- `appearance.outfit.primary` — 服装描述
- `appearance.distinctive_features` — 特征标签
- `appearance.color_palette` — 配色关键词
- `prompt_template.base_description` — 预定义的核心提示词（优先使用）
- `visual_keywords` — 补充关键词

### 2.2 scenes.json 结构

**路径**: `/home/dz/fuxi/assets/locations/scenes.json`

```json
{
  "metadata": { ... },
  "locations": {
    "<location_id>": {
      "zh_name": "string",          // 中文名
      "en_name": "string",          // 英文名
      "type": "string",             // 场景类型
      "era": "string",              // 时代
      "atmosphere": "string",       // 氛围描述
      "visual_style": "string",     // 视觉风格
      "color_palette": ["string"],  // 配色方案
      "architecture": "string",     // 建筑风格（如适用）
      "terrain": "string",          // 地形描述（如适用）
      "weather": "string",          // 天气（如适用）
      "lighting": "string",         // 光线描述
      "key_features": ["string"],   // 关键视觉元素
      "special_effects_required": ["string"]  // 特效需求
    }
  },
  "environmental_effects": {
    "weather": { ... },
    "lighting_styles": { ... }
  }
}
```

**必须提取的字段**:
- `atmosphere` — 氛围描述
- `visual_style` — 视觉风格
- `color_palette` — 配色方案
- `architecture` 或 `terrain` — 环境描述
- `lighting` — 光线描述
- `key_features` — 关键特征（选择性拼接）

### 2.3 props.json 结构

**路径**: `/home/dz/fuxi/assets/props/props.json`

```json
{
  "metadata": { ... },
  "<prop_id>": {
    "zh_name": "string",            // 中文名
    "en_name": "string",            // 英文名
    "brief": "string",              // 简介
    "appearance": "string",         // 外观描述
    "materials": ["string"],        // 材质列表
    "color": "string",              // 颜色
    "size": "string",               // 尺寸
    "functions": ["string"],        // 功能列表
    "visual_keywords": ["string"],  // 视觉关键词
    "tech_level": "string",         // 科技等级
    "notes": "string"               // 备注
  }
}
```

**必须提取的字段**:
- `appearance` — 外观描述
- `materials` — 材质（转为英文描述）
- `color` — 颜色
- `visual_keywords` — 视觉关键词

### 2.4 shots.json 结构（待定义）

**建议路径**: `/home/dz/fuxi/episodes/<ep_id>/shots.json`

```json
{
  "metadata": {
    "episode_id": "ep001",
    "episode_title": "数据洪流",
    "total_shots": 25
  },
  "shots": [
    {
      "shot_id": "ep001_s001",
      "scene_id": "1_1",                    // 关联 scenes.json 的场景
      "location_id": "lingzi_capital_data_core",  // 关联位置
      "characters": ["fuxi", "observer_ai"],      // 角色ID列表
      "props": ["通讯器", "能量护盾"],            // 道具列表
      
      "action": "string",                   // 动作描述
      "camera": {
        "shot_type": "wide|medium|close-up|extreme_close-up",
        "angle": "eye-level|low-angle|high-angle|dutch-angle",
        "movement": "static|pan|tilt|dolly|crane|handheld"
      },
      "lighting": "string",                 // 光线覆盖（可选，不填则用场景默认）
      "mood": "string",                     // 情绪氛围
      "special_effects": ["string"],        // 特效需求（关联 prompt_templates.md 的特效模块）
      
      "i2i_config": {                       // I2I 模式专用
        "reference_image": "path/to/ref.png",
        "denoise_strength": 0.6,
        "preserve_composition": true
      },
      
      "duration_sec": 3.5,                  // 镜头时长
      "notes": "string"                     // 备注
    }
  ]
}
```

---

## 3. 输出格式

### 3.1 正向提示词结构

采用模块化拼接，按以下顺序组装：

```
[STYLE PREFIX]      — 全局风格前缀（固定）
[CHARACTER PREFIX]  — 角色外貌描述（从角色卡提取）
[LOCATION PREFIX]   — 场景环境描述（从场景卡提取）
[PROPS]             — 道具描述（如有）
[SHOT ACTION]       — 当前镜头的具体动作/画面
[CAMERA LANGUAGE]   — 景别、角度、运镜
[SPECIAL EFFECTS]   — 特效叠加（如适用）
[LIGHTING]          — 光线描述
[MOOD]              — 情绪氛围
```

**示例输出**:

```
cinematic film still, photorealistic, 16:9 horizontal aspect ratio, movie quality lighting, shallow depth of field, epic sci-fi meets ancient mythology aesthetic, data-punk visual style, young male age 20, angular face with deep features, left eye golden with rotating bagua pattern in pupil, right eye normal dark brown, long black hair half-tied, flowing translucent robe made of structured light with golden data patterns, breathtaking futuristic city built entirely of light, luminous architecture, rivers of data flowing through sky, hand reaching toward translucent crystal, golden data streams erupting from crystal flowing up arm like glowing veins, extreme close-up transitioning to face, golden energy burst from crystal illuminating face from below, shock and transformation
```

### 3.2 负向提示词

**基础负向提示词**（所有图像必加）:

```
anatomy error, face distortion, extra limbs, extra fingers, watermark, text artifacts, oversharpen, uncanny look, blurry, low quality, cartoon, anime, illustration style, deformed face, asymmetric eyes, bad proportions, cropped, out of frame
```

**角色专用负向提示词**（从 `prompt_template.negative_traits` 提取并追加）:
```
# 示例：伏羲的负向提示
..., cold emotionless god, too young childish look, overly beautified idol appearance
```

### 3.3 I2I 专用参数

| 参数 | 说明 | 建议值范围 |
|------|------|-----------|
| `denoise_strength` | 去噪强度，控制与原图的偏离程度 | 0.3 ~ 0.8 |
| `preserve_composition` | 是否保持构图 | true/false |
| `reference_weight` | 参考图权重（ControlNet） | 0.5 ~ 1.0 |

**denoise_strength 建议值**:

| 用途 | denoise_strength | 说明 |
|------|------------------|------|
| 微调光线/颜色 | 0.3 ~ 0.4 | 保持原图结构，仅调整氛围 |
| 添加特效叠加 | 0.4 ~ 0.5 | 保持角色不变，添加特效 |
| 动作变化 | 0.5 ~ 0.6 | 改变姿势但保持角色一致性 |
| 场景转换 | 0.6 ~ 0.7 | 较大改变，保留角色特征 |
| 创意变体 | 0.7 ~ 0.8 | 大幅变化，仅保留基本特征 |

---

## 4. 功能需求

### 4.1 角色提示词生成

**输入**: `character_id`, `age_variant` (可选), `outfit_variant` (可选)

**处理逻辑**:
1. 检查 `prompt_template.base_description` 是否存在
   - 若存在，优先使用（已预先优化）
   - 若不存在，从 `appearance` 各字段拼接
2. 根据 `age_variant` 调整年龄描述
3. 根据 `outfit_variant` 选择服装（primary/alternate）
4. 追加 `distinctive_features` 和 `visual_keywords`
5. 返回组装好的角色描述片段

**输出示例**:
```python
{
    "positive": "young male age 20, angular face with deep features, left eye golden with rotating bagua pattern in pupil, right eye normal dark brown, black short hair neat and tidy, slender build about 180cm, flowing translucent robe made of structured light with golden data patterns flowing on surface, waist belt with bagua symbol, golden faint glow at fingertips",
    "negative": "cold emotionless god, too young childish look, overly beautified"
}
```

### 4.2 场景提示词生成

**输入**: `location_id`, `time_of_day` (可选), `weather_override` (可选)

**处理逻辑**:
1. 从 `locations[location_id]` 提取核心字段
2. 拼接 `atmosphere` + `visual_style` + `architecture/terrain`
3. 从 `key_features` 选择 2-3 个关键元素
4. 根据 `time_of_day` 调整光线描述
5. 如有 `weather_override`，覆盖默认天气

**输出示例**:
```python
{
    "positive": "breathtaking futuristic city built entirely of light, luminous architecture, rivers of data flowing through sky between buildings, extreme technological abstract geometric visual style, blue-white golden silver color scheme, multi-layered fluorescent lighting with strong energy pulsation",
    "lighting": "self-luminous architecture, warm golden-white ambient, data rivers providing overhead lighting"
}
```

### 4.3 道具提示词生成

**输入**: `prop_id`

**处理逻辑**:
1. 提取 `appearance` 描述
2. 拼接 `materials` (转英文) + `color`
3. 追加 `visual_keywords`

**输出示例**:
```python
{
    "positive": "mystical talisman with glowing runes, made of jade and wood, multi-colored glow changing with energy, magical ancient appearance"
}
```

### 4.4 组合提示词（完整镜头）

**输入**: `shot` 对象（包含角色、场景、动作等全部信息）

**处理逻辑**:
1. 加载全局 STYLE PREFIX
2. 调用角色提示词生成（支持多角色）
3. 调用场景提示词生成
4. 调用道具提示词生成（如有）
5. 解析 `action` 描述
6. 解析 `camera` 对象，转换为镜头语言
7. 查找并追加特效模块（从 `prompt_templates.md` 映射）
8. 追加 `lighting` 和 `mood`
9. 按标准顺序拼接
10. 组装负向提示词
11. 如果是 I2I 模式，附加 I2I 参数

**输出结构**:
```python
{
    "positive_prompt": "string",      # 完整正向提示词
    "negative_prompt": "string",      # 完整负向提示词
    "mode": "t2i" | "i2i",           # 生成模式
    "i2i_params": {                   # 仅 I2I 模式
        "reference_image": "path",
        "denoise_strength": 0.6,
        "preserve_composition": true
    },
    "metadata": {
        "shot_id": "ep001_s001",
        "characters": ["fuxi"],
        "location": "lingzi_capital_data_core",
        "generated_at": "2025-02-05T10:30:00Z"
    }
}
```

### 4.5 T2I 模式 vs I2I 模式切换

**模式判断逻辑**:
```python
def determine_mode(shot):
    if shot.get("i2i_config") and shot["i2i_config"].get("reference_image"):
        return "i2i"
    return "t2i"
```

**模式差异**:

| 特性 | T2I 模式 | I2I 模式 |
|------|----------|----------|
| 参考图 | 无 | 必须提供 |
| denoise_strength | 不适用 | 必须指定 |
| 角色描述详细度 | 完整描述 | 可简化（依赖参考图） |
| 场景描述详细度 | 完整描述 | 可简化 |
| 特效描述 | 详细 | 详细（叠加到参考图上） |

### 4.6 与 style_bible/prompt_templates.md 的集成

**特效模块映射表**:

| 特效ID | 中文名 | 用途 |
|--------|--------|------|
| `code_sight` | 代码视觉 | 伏羲觉醒后的视觉能力 |
| `bagua_pattern` | 八卦图案 | 伏羲左眼标识 |
| `pixelation_dissolve` | 像素化分解 | 熵的格式化攻击 |
| `golden_data_manipulation` | 金色数据流操控 | 伏羲能力展示 |
| `dark_data_tendrils` | 黑色数据触手 | 熵单位攻击 |
| `seed_descent` | 火种降临 | 第一集核心事件 |
| `sky_pillar` | 通天光柱 | 火种协议发射 |

**光线模板映射**:

从 `prompt_templates.md` 的光线模板表自动匹配，支持以下场景关键词：
- `lingzi_normal` — 灵子文明（正常）
- `lingzi_alert` — 灵子文明（警报）
- `seed_sacrifice` — 火种牺牲
- `storm_swamp` — 暴雨夜沼泽
- `seed_fall` — 火种坠落
- `code_vision_active` — 代码视觉激活
- `entropy_descend` — 熵单位降临
- `pixelation` — 像素化格式化
- `power_burst` — 力量爆发
- `escape_aftermath` — 逃离余震

---

## 5. API 设计建议

### 5.1 类设计

```python
class PromptBuilder:
    """统一提示词生成器"""
    
    def __init__(self, 
                 characters_path: str = "assets/characters/characters.json",
                 scenes_path: str = "assets/locations/scenes.json",
                 props_path: str = "assets/props/props.json",
                 templates_path: str = "style_bible/prompt_templates.md"):
        """
        初始化 PromptBuilder
        
        Args:
            characters_path: 角色定义文件路径
            scenes_path: 场景定义文件路径
            props_path: 道具定义文件路径
            templates_path: 提示词模板文件路径
        """
        pass
    
    # === 基础生成方法 ===
    
    def build_character_prompt(self,
                               character_id: str,
                               age_variant: Optional[int] = None,
                               outfit_variant: str = "primary") -> CharacterPrompt:
        """生成角色提示词片段"""
        pass
    
    def build_scene_prompt(self,
                           location_id: str,
                           time_of_day: Optional[str] = None,
                           weather_override: Optional[str] = None) -> ScenePrompt:
        """生成场景提示词片段"""
        pass
    
    def build_prop_prompt(self, prop_id: str) -> PropPrompt:
        """生成道具提示词片段"""
        pass
    
    # === 组合生成方法 ===
    
    def build_shot_prompt(self, shot: Shot) -> FullPrompt:
        """
        生成完整镜头提示词（核心方法）
        
        Args:
            shot: Shot 对象，包含所有镜头信息
            
        Returns:
            FullPrompt 对象，包含正向、负向提示词及元数据
        """
        pass
    
    def build_asset_prompt(self,
                           asset_type: Literal["character", "scene", "prop"],
                           asset_id: str,
                           **kwargs) -> FullPrompt:
        """
        生成资产参考图提示词（T2I 专用）
        
        Args:
            asset_type: 资产类型
            asset_id: 资产ID
            **kwargs: 额外参数（如角色的 age_variant）
            
        Returns:
            FullPrompt 对象
        """
        pass
    
    # === 辅助方法 ===
    
    def get_special_effect(self, effect_id: str) -> str:
        """获取特效模块提示词"""
        pass
    
    def get_lighting_template(self, scene_type: str) -> str:
        """获取光线模板"""
        pass
    
    def get_style_prefix(self) -> str:
        """获取全局风格前缀"""
        pass
    
    def get_negative_prompt(self, 
                            character_ids: Optional[List[str]] = None) -> str:
        """获取负向提示词（包含角色专用负向）"""
        pass


# === 数据类定义 ===

@dataclass
class CharacterPrompt:
    positive: str
    negative: str
    character_id: str
    
@dataclass
class ScenePrompt:
    positive: str
    lighting: str
    location_id: str
    
@dataclass
class PropPrompt:
    positive: str
    prop_id: str

@dataclass
class FullPrompt:
    positive_prompt: str
    negative_prompt: str
    mode: Literal["t2i", "i2i"]
    i2i_params: Optional[dict] = None
    metadata: Optional[dict] = None
```

### 5.2 调用示例

#### 示例 1：生成角色参考图（T2I）

```python
from prompt_builder import PromptBuilder

pb = PromptBuilder()

# 生成伏羲的角色参考图提示词
result = pb.build_asset_prompt(
    asset_type="character",
    asset_id="fuxi",
    age_variant=20,
    outfit_variant="primary"
)

print(result.positive_prompt)
# cinematic film still, photorealistic, character reference sheet, ...
# young male age 20, angular face with deep features, left eye golden with 
# rotating bagua pattern in pupil, ...

print(result.negative_prompt)
# anatomy error, face distortion, extra limbs, ...
# cold emotionless god, too young childish look, ...
```

#### 示例 2：生成场景参考图（T2I）

```python
result = pb.build_asset_prompt(
    asset_type="scene",
    asset_id="eight_trigram_city",
    time_of_day="night"
)

print(result.positive_prompt)
# cinematic film still, photorealistic, environment concept art, ...
# eight trigram layout circular city divided into eight districts, ...
# golden white emerald deep blue color scheme, ...
# night scene with golden and blue lights flickering across entire city
```

#### 示例 3：生成完整镜头（I2I）

```python
from prompt_builder import Shot

shot = Shot(
    shot_id="ep001_s009",
    scene_id="1_3",
    location_id="vortex_edge",
    characters=["fuxi"],
    props=[],
    action="hand touching translucent crystal, golden data streams erupting from crystal flowing up arm like glowing veins, face contorted in pain kneeling in water, left eye erupting with golden light",
    camera={
        "shot_type": "extreme_close-up",
        "angle": "low-angle",
        "movement": "static"
    },
    lighting="golden energy burst from crystal illuminating face from below, rain catching golden light",
    mood="shock, searing pain, transformation, point of no return",
    special_effects=["code_sight", "bagua_pattern"],
    i2i_config={
        "reference_image": "assets/characters/fuxi/ref_001.png",
        "denoise_strength": 0.55,
        "preserve_composition": True
    }
)

result = pb.build_shot_prompt(shot)

print(result.mode)  # "i2i"

print(result.positive_prompt)
# cinematic film still, photorealistic, 16:9 horizontal aspect ratio, ...
# young male age 16, angular face, ... [角色描述]
# dark swamp at night, rain, glowing silver-blue vortex in water [场景描述]
# hand touching translucent crystal, golden data streams erupting ... [动作]
# extreme close-up, low angle [镜头]
# overlay of translucent golden data streams, floating code characters ... [特效]
# glowing dark golden bagua trigram pattern, tiny rotating octagonal symbol in pupil ... [特效]
# golden energy burst from crystal illuminating face from below ... [光线]
# shock, searing pain, transformation [情绪]

print(result.i2i_params)
# {'reference_image': 'assets/characters/fuxi/ref_001.png', 
#  'denoise_strength': 0.55, 
#  'preserve_composition': True}
```

#### 示例 4：批量生成镜头

```python
import json

# 加载镜头列表
with open("episodes/ep001/shots.json") as f:
    shots_data = json.load(f)

pb = PromptBuilder()

# 批量生成
results = []
for shot_data in shots_data["shots"]:
    shot = Shot(**shot_data)
    result = pb.build_shot_prompt(shot)
    results.append({
        "shot_id": shot.shot_id,
        "positive": result.positive_prompt,
        "negative": result.negative_prompt,
        "mode": result.mode,
        "i2i_params": result.i2i_params
    })

# 保存结果
with open("episodes/ep001/prompts.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
```

---

## 6. 验收标准

### 6.1 功能验收

| 编号 | 测试项 | 预期结果 | 优先级 |
|------|--------|----------|--------|
| F-01 | 加载所有数据文件 | 无报错，数据正确解析 | P0 |
| F-02 | 生成角色提示词 | 输出包含所有外观特征 | P0 |
| F-03 | 生成场景提示词 | 输出包含氛围、风格、光线 | P0 |
| F-04 | 生成道具提示词 | 输出包含外观、材质、颜色 | P1 |
| F-05 | 组合提示词生成 | 按标准顺序正确拼接 | P0 |
| F-06 | T2I/I2I 模式切换 | 正确识别模式并输出对应格式 | P0 |
| F-07 | 特效模块追加 | 正确查找并追加特效描述 | P1 |
| F-08 | 光线模板匹配 | 根据场景关键词正确匹配 | P1 |
| F-09 | 负向提示词组装 | 包含基础 + 角色专用负向 | P0 |
| F-10 | 批量处理 | 支持批量生成，无内存泄漏 | P1 |

### 6.2 质量验收

#### 6.2.1 提示词质量标准

**合格的正向提示词应满足**:
- ✅ 以全局风格前缀开头
- ✅ 角色描述完整（外貌、服装、特征）
- ✅ 场景描述包含氛围和视觉风格
- ✅ 动作描述具体且可视化
- ✅ 镜头语言明确（景别、角度）
- ✅ 光线描述与场景匹配
- ✅ 情绪氛围与剧情一致
- ✅ 无中文（全英文输出）
- ✅ 长度在 75-200 tokens 之间（SDXL 最佳范围）

**不合格示例**:
```
❌ 太短: "fuxi in swamp"
❌ 中英混杂: "cinematic film, 伏羲 in 沼泽"
❌ 缺少风格: "young male with golden eye touching crystal"
❌ 顺序错误: "golden eye, cinematic, swamp, photorealistic" (风格应在前)
```

#### 6.2.2 I2I 参数质量标准

- ✅ `denoise_strength` 在 0.3-0.8 范围内
- ✅ `reference_image` 路径有效
- ✅ 特效场景的 denoise 建议为 0.4-0.5
- ✅ 动作变化场景的 denoise 建议为 0.5-0.6

### 6.3 性能验收

| 指标 | 目标 |
|------|------|
| 单个提示词生成时间 | < 50ms |
| 批量 100 个镜头生成 | < 5s |
| 内存占用（加载后） | < 100MB |
| 启动加载时间 | < 2s |

### 6.4 集成验收

- ✅ 可作为 Python 模块导入
- ✅ 可通过 CLI 命令调用
- ✅ 输出可直接传入 ComfyUI API
- ✅ 与现有 `creative-toolkit` 工作流兼容

---

## 7. 附录

### 7.1 镜头语言映射表

| 输入值 | 输出描述 |
|--------|----------|
| `wide` | wide shot, establishing shot |
| `medium` | medium shot |
| `close-up` | close-up shot |
| `extreme_close-up` | extreme close-up, macro shot |
| `eye-level` | eye level angle |
| `low-angle` | low angle, looking up |
| `high-angle` | high angle, looking down, bird's eye view |
| `dutch-angle` | dutch angle, tilted frame |
| `static` | (不输出) |
| `pan` | panning shot |
| `tilt` | tilting shot |
| `dolly` | dolly shot, tracking shot |
| `crane` | crane shot |
| `handheld` | handheld camera, documentary style |

### 7.2 全局风格前缀

```
cinematic film still, photorealistic, 16:9 horizontal aspect ratio, movie quality lighting, shallow depth of field, epic sci-fi meets ancient mythology aesthetic, data-punk visual style
```

### 7.3 资产生成专用前缀

| 资产类型 | 前缀 |
|----------|------|
| 角色参考图 | `character reference sheet, full body portrait, neutral pose, white background, multiple views` |
| 场景参考图 | `environment concept art, establishing shot, wide angle, atmospheric` |
| 道具参考图 | `product photography, centered composition, studio lighting, white background, multiple angles` |

---

## 8. 变更日志

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|----------|
| 1.0 | 2025-02-05 | Director Chen | 初始版本 |

---

*文档结束*
