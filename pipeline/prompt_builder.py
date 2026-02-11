"""
PromptBuilder - 统一提示词生成器

伏羲项目的提示词自动化组装模块，支持：
- 角色/场景/道具提示词生成
- 组合提示词（完整镜头）
- T2I/I2I 模式切换
- 与 style_bible/prompt_templates.md 集成
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional
import json
import re


# === 数据类定义 ===

@dataclass
class CharacterPrompt:
    """角色提示词片段"""
    positive: str
    negative: str
    character_id: str


@dataclass
class ScenePrompt:
    """场景提示词片段"""
    positive: str
    lighting: str
    location_id: str


@dataclass
class PropPrompt:
    """道具提示词片段"""
    positive: str
    prop_id: str


@dataclass
class FullPrompt:
    """完整提示词输出"""
    positive_prompt: str
    negative_prompt: str
    mode: Literal["t2i", "i2i"]
    i2i_params: Optional[dict] = None
    metadata: Optional[dict] = None


@dataclass
class Shot:
    """镜头数据结构"""
    shot_id: str
    scene_id: str = ""
    location_id: str = ""
    characters: list = field(default_factory=list)
    props: list = field(default_factory=list)
    action: str = ""
    camera: dict = field(default_factory=dict)
    lighting: str = ""
    mood: str = ""
    special_effects: list = field(default_factory=list)
    i2i_config: Optional[dict] = None
    duration_sec: float = 3.0
    notes: str = ""


class PromptBuilder:
    """统一提示词生成器"""
    
    # 全局风格前缀
    STYLE_PREFIX = (
        "cinematic film still, photorealistic, 16:9 horizontal aspect ratio, "
        "movie quality lighting, shallow depth of field, "
        "epic sci-fi meets ancient mythology aesthetic, data-punk visual style"
    )
    
    # 基础负向提示词
    BASE_NEGATIVE = (
        "anatomy error, face distortion, extra limbs, extra fingers, watermark, "
        "text artifacts, oversharpen, uncanny look, blurry, low quality, cartoon, "
        "anime, illustration style, deformed face, asymmetric eyes, bad proportions, "
        "cropped, out of frame"
    )
    
    # 资产生成专用前缀
    ASSET_PREFIXES = {
        "character": "character reference sheet, full body portrait, neutral pose, white background, multiple views",
        "scene": "environment concept art, establishing shot, wide angle, atmospheric",
        "prop": "product photography, centered composition, studio lighting, white background, multiple angles"
    }
    
    # 镜头语言映射表
    CAMERA_MAPPING = {
        # 景别
        "wide": "wide shot, establishing shot",
        "medium": "medium shot",
        "close-up": "close-up shot",
        "extreme_close-up": "extreme close-up, macro shot",
        # 角度
        "eye-level": "eye level angle",
        "low-angle": "low angle, looking up",
        "high-angle": "high angle, looking down, bird's eye view",
        "dutch-angle": "dutch angle, tilted frame",
        # 运镜
        "static": "",  # 不输出
        "pan": "panning shot",
        "tilt": "tilting shot",
        "dolly": "dolly shot, tracking shot",
        "crane": "crane shot",
        "handheld": "handheld camera, documentary style"
    }
    
    # 特效模块映射
    SPECIAL_EFFECTS = {
        "code_sight": (
            "overlay of translucent golden data streams, floating code characters, "
            "matrix-like digital rain in gold, holographic data structures visible on all objects, "
            "trees showing green growth code strings, water surface showing molecular grid structure, "
            "human skin showing blue bioelectric current lines"
        ),
        "bagua_pattern": (
            "glowing dark golden bagua trigram pattern, tiny rotating octagonal symbol in pupil, "
            "ancient Chinese cosmological diagram emitting golden light, subtle glow in darkness"
        ),
        "pixelation_dissolve": (
            "body dissolving into digital pixels, voxel disintegration effect from contact point spreading outward, "
            "matter breaking apart into cubic data fragments, glitch distortion, white pixel fragments floating upward"
        ),
        "golden_data_manipulation": (
            "golden data streams flowing from hands, energy ripples on contact surface, "
            "code rewriting effect on physical matter, luminous golden veins appearing on arms"
        ),
        "dark_data_tendrils": (
            "black data tendrils extending from geometric vertices, jagged sawtooth data structure visible in code vision, "
            "dark flowing streams wrapping around target, cold mechanical precision"
        ),
        "seed_descent": (
            "silver-blue geometric light streams tearing through stormy sky, structured energy falling like cosmic rain, "
            "glowing vortex forming in water on impact, translucent crystal floating at vortex center containing golden patterns"
        ),
        "sky_pillar": (
            "massive light pillar erupting from city center, pillar reaching into sky fragmenting into billions of light points, "
            "light points scattering into cosmos like dandelion seeds, one light point containing faint bagua pattern, cosmic scale"
        )
    }
    
    # 光线模板映射
    LIGHTING_TEMPLATES = {
        "lingzi_normal": (
            "self-luminous architecture, warm golden-white ambient, "
            "data rivers providing overhead lighting, futuristic clean lighting"
        ),
        "lingzi_alert": (
            "flickering stuttering light, cold silver-blue shift, "
            "red alarm flashes, light sources dying intermittently"
        ),
        "seed_sacrifice": (
            "intense golden radiance emanating from character, overexposed golden highlights, "
            "body dissolving into light particles, epic backlighting fading to white"
        ),
        "storm_swamp": (
            "stormy night, rain, dramatic lightning illumination, "
            "near-total darkness between flashes, mud reflecting occasional light"
        ),
        "seed_fall": (
            "silver-blue geometric light tearing through dark sky, "
            "impact creating localized silver-blue glow on swamp water, crystal self-illuminating"
        ),
        "code_vision_active": (
            "golden rim lighting on character face, dark background with floating golden data overlays, "
            "dramatic contrast between golden left eye and dark surroundings"
        ),
        "entropy_descend": (
            "sky darkening unnaturally, ominous red glow from geometric cracks providing sole light source, "
            "low-key lighting, pulsing red rhythm, threatening atmosphere"
        ),
        "pixelation": (
            "white pixel fragments emitting light as body dissolves, "
            "cold clinical light from disintegration, contrasting with dark surroundings"
        ),
        "power_burst": (
            "golden energy ripple from hands illuminating ground, "
            "brief golden flash on impact, mud reflecting golden light"
        ),
        "escape_aftermath": (
            "minimal light, rain, faint golden glow from left eye in near-total darkness, "
            "distant red glow of entities behind"
        )
    }
    
    def __init__(
        self,
        characters_path: str = None,
        scenes_path: str = None,
        props_path: str = None,
        templates_path: str = None
    ):
        """
        初始化 PromptBuilder
        
        Args:
            characters_path: 角色定义文件路径
            scenes_path: 场景定义文件路径
            props_path: 道具定义文件路径
            templates_path: 提示词模板文件路径（保留，但模板已内置）
        """
        # 确定基础路径
        base_path = Path(__file__).parent.parent
        
        # 设置默认路径
        self.characters_path = Path(characters_path) if characters_path else base_path / "assets/characters/characters.json"
        self.scenes_path = Path(scenes_path) if scenes_path else base_path / "assets/locations/scenes.json"
        self.props_path = Path(props_path) if props_path else base_path / "assets/props/props.json"
        
        # 加载数据
        self.characters = self._load_json(self.characters_path)
        self.scenes = self._load_json(self.scenes_path)
        self.props = self._load_json(self.props_path)
        
        # 提取角色数据
        if "characters" in self.characters:
            self.characters = self.characters["characters"]
        
        # 提取场景数据
        if "locations" in self.scenes:
            self.locations = self.scenes["locations"]
        else:
            self.locations = self.scenes
    
    def _load_json(self, path: Path) -> dict:
        """加载 JSON 文件"""
        if not path.exists():
            raise FileNotFoundError(f"找不到文件: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # === 基础生成方法 ===
    
    def build_character_prompt(
        self,
        character_id: str,
        age_variant: Optional[int] = None,
        outfit_variant: str = "primary"
    ) -> CharacterPrompt:
        """
        生成角色提示词片段
        
        Args:
            character_id: 角色ID
            age_variant: 年龄变体（可选）
            outfit_variant: 服装变体 (primary/alternate)
            
        Returns:
            CharacterPrompt 对象
        """
        if character_id not in self.characters:
            raise ValueError(f"未找到角色: {character_id}")
        
        char = self.characters[character_id]
        positive_parts = []
        
        # 1. 优先使用预定义的 base_description
        prompt_template = char.get("prompt_template", {})
        base_desc = prompt_template.get("base_description", "")
        
        if base_desc:
            positive_parts.append(base_desc)
        else:
            # 从 appearance 各字段拼接
            appearance = char.get("appearance", {})
            
            # 性别和年龄
            gender = char.get("gender", "")
            gender_en = "male" if gender == "男" else "female" if gender == "女" else ""
            
            age = age_variant or char.get("age_start", 25)
            if gender_en:
                positive_parts.append(f"young {gender_en} age {age}")
            
            # 脸部
            if appearance.get("face"):
                positive_parts.append(self._translate_to_english(appearance["face"]))
            
            # 眼睛
            if appearance.get("eyes"):
                positive_parts.append(self._translate_to_english(appearance["eyes"]))
            
            # 头发
            if appearance.get("hair"):
                positive_parts.append(self._translate_to_english(appearance["hair"]))
            
            # 体型
            if appearance.get("build"):
                positive_parts.append(self._translate_to_english(appearance["build"]))
        
        # 2. 处理年龄变体
        if age_variant:
            # 替换年龄描述
            positive_text = ", ".join(positive_parts)
            positive_text = re.sub(r'age \d+', f'age {age_variant}', positive_text)
            positive_parts = [positive_text]
        
        # 3. 处理服装
        appearance = char.get("appearance", {})
        outfit = appearance.get("outfit", {})
        outfit_desc = outfit.get(outfit_variant, outfit.get("primary", ""))
        if outfit_desc:
            positive_parts.append(self._translate_to_english(outfit_desc))
        
        # 4. 添加特征标签
        distinctive = appearance.get("distinctive_features", [])
        if distinctive:
            features_en = [self._translate_to_english(f) for f in distinctive[:3]]
            positive_parts.extend(features_en)
        
        # 5. 添加视觉关键词
        visual_keywords = char.get("visual_keywords", [])
        if visual_keywords:
            keywords_en = [self._translate_to_english(k) for k in visual_keywords[:3]]
            positive_parts.extend(keywords_en)
        
        # 组装正向提示词
        positive = ", ".join(filter(None, positive_parts))
        
        # 获取负向提示词
        negative_traits = prompt_template.get("negative_traits", "")
        negative = self._translate_to_english(negative_traits) if negative_traits else ""
        
        return CharacterPrompt(
            positive=positive,
            negative=negative,
            character_id=character_id
        )
    
    def build_scene_prompt(
        self,
        location_id: str,
        time_of_day: Optional[str] = None,
        weather_override: Optional[str] = None
    ) -> ScenePrompt:
        """
        生成场景提示词片段
        
        Args:
            location_id: 场景ID
            time_of_day: 时间（可选）
            weather_override: 天气覆盖（可选）
            
        Returns:
            ScenePrompt 对象
        """
        if location_id not in self.locations:
            raise ValueError(f"未找到场景: {location_id}")
        
        loc = self.locations[location_id]
        positive_parts = []
        
        # 1. 氛围描述
        if loc.get("atmosphere"):
            positive_parts.append(self._translate_to_english(loc["atmosphere"]))
        
        # 2. 视觉风格
        if loc.get("visual_style"):
            positive_parts.append(self._translate_to_english(loc["visual_style"]))
        
        # 3. 建筑/地形
        if loc.get("architecture"):
            positive_parts.append(self._translate_to_english(loc["architecture"]))
        elif loc.get("terrain"):
            positive_parts.append(self._translate_to_english(loc["terrain"]))
        
        # 4. 配色方案
        color_palette = loc.get("color_palette", [])
        if color_palette:
            colors_en = [self._translate_to_english(c) for c in color_palette]
            positive_parts.append(f"{' '.join(colors_en)} color scheme")
        
        # 5. 关键特征（选择2-3个）
        key_features = loc.get("key_features", [])
        if key_features:
            features = key_features[:3]
            features_en = [self._translate_to_english(f) for f in features]
            positive_parts.extend(features_en)
        
        # 6. 天气处理
        weather = weather_override or loc.get("weather", "")
        if weather:
            positive_parts.append(self._translate_to_english(weather))
        
        # 7. 时间处理
        if time_of_day:
            time_desc = self._get_time_description(time_of_day)
            if time_desc:
                positive_parts.append(time_desc)
        
        # 组装正向提示词
        positive = ", ".join(filter(None, positive_parts))
        
        # 获取光线描述
        lighting = loc.get("lighting", "")
        lighting_en = self._translate_to_english(lighting) if lighting else ""
        
        return ScenePrompt(
            positive=positive,
            lighting=lighting_en,
            location_id=location_id
        )
    
    def build_prop_prompt(self, prop_id: str) -> PropPrompt:
        """
        生成道具提示词片段
        
        Args:
            prop_id: 道具ID
            
        Returns:
            PropPrompt 对象
        """
        if prop_id not in self.props and prop_id != "metadata":
            # 尝试用中文名查找
            for pid, pdata in self.props.items():
                if pid == "metadata":
                    continue
                if pdata.get("zh_name") == prop_id or pdata.get("en_name") == prop_id:
                    prop_id = pid
                    break
            else:
                raise ValueError(f"未找到道具: {prop_id}")
        
        prop = self.props[prop_id]
        positive_parts = []
        
        # 1. 外观描述
        if prop.get("appearance"):
            positive_parts.append(self._translate_to_english(prop["appearance"]))
        
        # 2. 材质
        materials = prop.get("materials", [])
        if materials:
            materials_en = [self._translate_to_english(m) for m in materials]
            positive_parts.append(f"made of {' and '.join(materials_en)}")
        
        # 3. 颜色
        if prop.get("color"):
            positive_parts.append(self._translate_to_english(prop["color"]))
        
        # 4. 视觉关键词
        visual_keywords = prop.get("visual_keywords", [])
        if visual_keywords:
            positive_parts.extend(visual_keywords)
        
        positive = ", ".join(filter(None, positive_parts))
        
        return PropPrompt(
            positive=positive,
            prop_id=prop_id
        )
    
    # === 组合生成方法 ===
    
    def build_shot_prompt(self, shot: Shot) -> FullPrompt:
        """
        生成完整镜头提示词（核心方法）
        
        Args:
            shot: Shot 对象，包含所有镜头信息
            
        Returns:
            FullPrompt 对象，包含正向、负向提示词及元数据
        """
        parts = []
        negative_parts = [self.BASE_NEGATIVE]
        
        # 1. 全局风格前缀
        parts.append(self.STYLE_PREFIX)
        
        # 2. 角色描述
        for char_id in shot.characters:
            try:
                char_prompt = self.build_character_prompt(char_id)
                parts.append(char_prompt.positive)
                if char_prompt.negative:
                    negative_parts.append(char_prompt.negative)
            except ValueError:
                # 角色未找到，跳过
                pass
        
        # 3. 场景描述
        if shot.location_id:
            try:
                scene_prompt = self.build_scene_prompt(shot.location_id)
                parts.append(scene_prompt.positive)
            except ValueError:
                pass
        
        # 4. 道具描述
        for prop_id in shot.props:
            try:
                prop_prompt = self.build_prop_prompt(prop_id)
                parts.append(prop_prompt.positive)
            except ValueError:
                pass
        
        # 5. 动作描述
        if shot.action:
            parts.append(self._translate_to_english(shot.action))
        
        # 6. 镜头语言
        camera_parts = []
        camera = shot.camera
        if camera.get("shot_type"):
            cam_desc = self.CAMERA_MAPPING.get(camera["shot_type"], "")
            if cam_desc:
                camera_parts.append(cam_desc)
        if camera.get("angle"):
            angle_desc = self.CAMERA_MAPPING.get(camera["angle"], "")
            if angle_desc:
                camera_parts.append(angle_desc)
        if camera.get("movement") and camera["movement"] != "static":
            movement_desc = self.CAMERA_MAPPING.get(camera["movement"], "")
            if movement_desc:
                camera_parts.append(movement_desc)
        
        if camera_parts:
            parts.append(", ".join(camera_parts))
        
        # 7. 特效模块
        for effect_id in shot.special_effects:
            effect_desc = self.get_special_effect(effect_id)
            if effect_desc:
                parts.append(effect_desc)
        
        # 8. 光线描述
        if shot.lighting:
            parts.append(self._translate_to_english(shot.lighting))
        
        # 9. 情绪氛围
        if shot.mood:
            parts.append(self._translate_to_english(shot.mood))
        
        # 确定模式
        mode = self._determine_mode(shot)
        
        # 组装完整提示词
        positive_prompt = ", ".join(filter(None, parts))
        negative_prompt = ", ".join(filter(None, negative_parts))
        
        # I2I 参数
        i2i_params = None
        if mode == "i2i" and shot.i2i_config:
            i2i_params = {
                "reference_image": shot.i2i_config.get("reference_image", ""),
                "denoise_strength": shot.i2i_config.get("denoise_strength", 0.6),
                "preserve_composition": shot.i2i_config.get("preserve_composition", True)
            }
        
        # 元数据
        metadata = {
            "shot_id": shot.shot_id,
            "characters": shot.characters,
            "location": shot.location_id,
            "generated_at": datetime.now().isoformat()
        }
        
        return FullPrompt(
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            mode=mode,
            i2i_params=i2i_params,
            metadata=metadata
        )
    
    def build_asset_prompt(
        self,
        asset_type: Literal["character", "scene", "prop"],
        asset_id: str,
        **kwargs
    ) -> FullPrompt:
        """
        生成资产参考图提示词（T2I 专用）
        
        Args:
            asset_type: 资产类型
            asset_id: 资产ID
            **kwargs: 额外参数（如角色的 age_variant）
            
        Returns:
            FullPrompt 对象
        """
        parts = [self.STYLE_PREFIX]
        negative_parts = [self.BASE_NEGATIVE]
        
        # 添加资产专用前缀
        asset_prefix = self.ASSET_PREFIXES.get(asset_type, "")
        if asset_prefix:
            parts.append(asset_prefix)
        
        # 根据类型生成
        if asset_type == "character":
            char_prompt = self.build_character_prompt(
                asset_id,
                age_variant=kwargs.get("age_variant"),
                outfit_variant=kwargs.get("outfit_variant", "primary")
            )
            parts.append(char_prompt.positive)
            if char_prompt.negative:
                negative_parts.append(char_prompt.negative)
        
        elif asset_type == "scene":
            scene_prompt = self.build_scene_prompt(
                asset_id,
                time_of_day=kwargs.get("time_of_day"),
                weather_override=kwargs.get("weather_override")
            )
            parts.append(scene_prompt.positive)
            if scene_prompt.lighting:
                parts.append(scene_prompt.lighting)
        
        elif asset_type == "prop":
            prop_prompt = self.build_prop_prompt(asset_id)
            parts.append(prop_prompt.positive)
        
        positive_prompt = ", ".join(filter(None, parts))
        negative_prompt = ", ".join(filter(None, negative_parts))
        
        metadata = {
            "asset_type": asset_type,
            "asset_id": asset_id,
            "generated_at": datetime.now().isoformat()
        }
        
        return FullPrompt(
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            mode="t2i",
            metadata=metadata
        )
    
    # === 辅助方法 ===
    
    def get_special_effect(self, effect_id: str) -> str:
        """获取特效模块提示词"""
        return self.SPECIAL_EFFECTS.get(effect_id, "")
    
    def get_lighting_template(self, scene_type: str) -> str:
        """获取光线模板"""
        return self.LIGHTING_TEMPLATES.get(scene_type, "")
    
    def get_style_prefix(self) -> str:
        """获取全局风格前缀"""
        return self.STYLE_PREFIX
    
    def get_negative_prompt(
        self,
        character_ids: Optional[list] = None
    ) -> str:
        """获取负向提示词（包含角色专用负向）"""
        parts = [self.BASE_NEGATIVE]
        
        if character_ids:
            for char_id in character_ids:
                if char_id in self.characters:
                    char = self.characters[char_id]
                    prompt_template = char.get("prompt_template", {})
                    negative = prompt_template.get("negative_traits", "")
                    if negative:
                        parts.append(self._translate_to_english(negative))
        
        return ", ".join(filter(None, parts))
    
    def _determine_mode(self, shot: Shot) -> Literal["t2i", "i2i"]:
        """判断生成模式"""
        if shot.i2i_config and shot.i2i_config.get("reference_image"):
            return "i2i"
        return "t2i"
    
    def _get_time_description(self, time_of_day: str) -> str:
        """获取时间描述"""
        time_mapping = {
            "dawn": "early morning, golden hour, soft warm light",
            "morning": "morning light, bright and clear",
            "noon": "midday sun, harsh lighting",
            "afternoon": "afternoon light, warm tones",
            "dusk": "sunset, golden hour, warm orange light",
            "evening": "evening twilight, blue hour",
            "night": "night scene, dark with artificial lights",
            "midnight": "deep night, minimal lighting"
        }
        return time_mapping.get(time_of_day.lower(), "")
    
    def _translate_to_english(self, text: str) -> str:
        """
        基础中英翻译（简单映射表）
        实际项目中可接入翻译 API
        """
        if not text:
            return ""
        
        # 常用词汇映射
        translations = {
            # 外观词汇
            "轮廓深邃": "angular face with deep features",
            "五官立体": "well-defined features",
            "眉宇间透着智慧与坚毅": "wisdom and determination in the brows",
            "金色瞳孔": "golden pupil",
            "八卦纹理": "bagua pattern",
            "旋转的八卦纹理": "rotating bagua pattern",
            "正常暗褐色": "normal dark brown",
            "黑色短发": "black short hair",
            "整洁而精干": "neat and tidy",
            "修长精干": "slender build",
            "身高约180cm": "about 180cm tall",
            "纤长灵活": "slender and agile",
            "流光长袍": "flowing translucent robe made of structured light",
            "结构光构成的半透明衣物": "translucent garment made of structured light",
            "金色数据纹路": "golden data patterns",
            "八卦符号": "bagua symbol",
            "左眼金色纹路": "golden pattern in left eye",
            "淡金光芒": "faint golden glow",
            "指尖": "fingertips",
            
            # 场景词汇
            "璀璨而诡异": "breathtaking and ethereal",
            "蓝白色的数据光芒": "blue-white data glow",
            "极度科技化": "extreme technological",
            "抽象几何化": "abstract geometric",
            "由纯粹的光与能量构成": "built entirely of light and energy",
            "流动的数据河流": "rivers of data flowing",
            "多层次的荧光": "multi-layered fluorescent lighting",
            "强烈的能量脉动感": "strong energy pulsation",
            "原始粗犷": "primordial and rugged",
            "充满危险与神秘": "dangerous and mysterious",
            "沼泽": "swamp",
            "烂泥": "mud",
            "暴雨": "heavy rain",
            "闪电": "lightning",
            "低能见度": "low visibility",
            
            # 情绪词汇
            "震惊": "shock",
            "痛苦": "pain",
            "转变": "transformation",
            "无法回头": "point of no return",
            "希望": "hope",
            "绝望": "despair",
            "恐惧": "fear",
            "愤怒": "anger",
            
            # 材质词汇
            "能量": "energy",
            "光": "light",
            "金属": "metal",
            "石头": "stone",
            "木头": "wood",
            "玉石": "jade",
            "兽皮": "animal hide",
            "纸张": "paper",
            "植物纤维": "plant fiber",
            "科技合成材料": "synthetic tech material",
            "灵子能量": "spirit particle energy",
            
            # 颜色词汇
            "蓝白": "blue-white",
            "金色": "golden",
            "银色": "silver",
            "深紫": "deep purple",
            "深褐": "dark brown",
            "深绿": "dark green",
            "灰蓝": "gray-blue",
            "土黄": "earth yellow",
            "棕红": "brown-red",
            "翠绿": "emerald green",
            "暗红": "dark red",
            "冷银": "cold silver",
            "深灰": "dark gray",
            "血色": "blood red",
            "苍翠": "verdant green",
            "银白": "silver-white",
            "纯白": "pure white"
        }
        
        result = text
        for zh, en in translations.items():
            result = result.replace(zh, en)
        
        # 如果还有中文字符，保留原文（或可接入翻译API）
        return result


# === 便捷函数 ===

def create_prompt_builder() -> PromptBuilder:
    """创建默认的 PromptBuilder 实例"""
    return PromptBuilder()


def build_character_ref_prompt(character_id: str, **kwargs) -> FullPrompt:
    """快速生成角色参考图提示词"""
    pb = create_prompt_builder()
    return pb.build_asset_prompt("character", character_id, **kwargs)


def build_scene_ref_prompt(location_id: str, **kwargs) -> FullPrompt:
    """快速生成场景参考图提示词"""
    pb = create_prompt_builder()
    return pb.build_asset_prompt("scene", location_id, **kwargs)


def build_prop_ref_prompt(prop_id: str) -> FullPrompt:
    """快速生成道具参考图提示词"""
    pb = create_prompt_builder()
    return pb.build_asset_prompt("prop", prop_id)


# === CLI 接口 ===

def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PromptBuilder - 统一提示词生成器")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # character 子命令
    char_parser = subparsers.add_parser("character", help="生成角色提示词")
    char_parser.add_argument("id", help="角色ID")
    char_parser.add_argument("--age", type=int, help="年龄变体")
    char_parser.add_argument("--outfit", default="primary", help="服装变体")
    
    # scene 子命令
    scene_parser = subparsers.add_parser("scene", help="生成场景提示词")
    scene_parser.add_argument("id", help="场景ID")
    scene_parser.add_argument("--time", help="时间")
    scene_parser.add_argument("--weather", help="天气覆盖")
    
    # prop 子命令
    prop_parser = subparsers.add_parser("prop", help="生成道具提示词")
    prop_parser.add_argument("id", help="道具ID")
    
    # list 子命令
    list_parser = subparsers.add_parser("list", help="列出可用资产")
    list_parser.add_argument("type", choices=["characters", "scenes", "props"], help="资产类型")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    pb = create_prompt_builder()
    
    if args.command == "character":
        result = pb.build_asset_prompt(
            "character",
            args.id,
            age_variant=args.age,
            outfit_variant=args.outfit
        )
        print("=== 正向提示词 ===")
        print(result.positive_prompt)
        print("\n=== 负向提示词 ===")
        print(result.negative_prompt)
    
    elif args.command == "scene":
        result = pb.build_asset_prompt(
            "scene",
            args.id,
            time_of_day=args.time,
            weather_override=args.weather
        )
        print("=== 正向提示词 ===")
        print(result.positive_prompt)
        print("\n=== 负向提示词 ===")
        print(result.negative_prompt)
    
    elif args.command == "prop":
        result = pb.build_asset_prompt("prop", args.id)
        print("=== 正向提示词 ===")
        print(result.positive_prompt)
        print("\n=== 负向提示词 ===")
        print(result.negative_prompt)
    
    elif args.command == "list":
        if args.type == "characters":
            print("可用角色:")
            for char_id in pb.characters.keys():
                char = pb.characters[char_id]
                zh_name = char.get("zh_name", char_id)
                print(f"  - {char_id}: {zh_name}")
        elif args.type == "scenes":
            print("可用场景:")
            for loc_id in pb.locations.keys():
                loc = pb.locations[loc_id]
                zh_name = loc.get("zh_name", loc_id)
                print(f"  - {loc_id}: {zh_name}")
        elif args.type == "props":
            print("可用道具:")
            for prop_id, prop in pb.props.items():
                if prop_id == "metadata":
                    continue
                zh_name = prop.get("zh_name", prop_id)
                print(f"  - {prop_id}: {zh_name}")


if __name__ == "__main__":
    main()
