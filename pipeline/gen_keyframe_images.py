#!/usr/bin/env python3
"""
镜头关键帧生成 — All Frames Multi-Reference (每帧都用原始参考图)

逻辑:
  - 所有关键帧: location 参考图 + 所有 character 参考图 + 各自的 prompt → 独立生成 (denoise=0.55)
    * 使用 creative-toolkit 的 generate_with_references() 调用 flux2_ref_generate.json
    * 每帧都基于相同的高质量原始参考图（location + characters）
    * 通过不同的 prompt 实现运镜变化（景别、角度、动作）
    * 每个镜头必须有 location 参考，有角色时必须添加所有 character 参考
  - 优势:
    * 无累积误差 - 每帧独立生成，不受前一帧影响
    * 角色一致性极佳 - 所有帧参考同一组原始图
    * 运镜自由 - 完全由 prompt 驱动，可实现大幅度变化
    * 环境一致性 - 每帧都包含完整的场景参考
  - prompt: 从 keyframes.json 读取每个关键帧的 contextual prompt，自动注入性别标识前缀
  - 资产: 从 keyframes.json 的 assets 字段读取 location_ref 和 character_refs

用法:
    python -m pipeline.gen_keyframe_images ep001 S01
    python -m pipeline.gen_keyframe_images ep001 S01 --num-candidates 3
    python -m pipeline.gen_keyframe_images ep001 S01 --base-seed 42
"""

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image
from pipeline.utils import get_episode_dir, load_shots, PROJECT_ROOT

# 添加 creative-toolkit 到路径
sys.path.insert(0, "/home/dz/creative-toolkit")
from creative_toolkit.image.comfyui import ComfyUIImageGen


COMFYUI_URL = "http://127.0.0.1:8188"
COMFYUI_INPUT = Path("/home/dz/ComfyUI/input")
COMFYUI_OUTPUT = Path("/home/dz/ComfyUI/output")
WORKFLOWS_DIR = Path("/home/dz/ComfyUI/user/default/workflows")

# 输出分辨率
OUTPUT_WIDTH = 1920
OUTPUT_HEIGHT = 1080


def load_characters_json() -> dict:
    """加载 characters.json，返回 {char_id: char_def} 字典。"""
    characters_path = PROJECT_ROOT / "assets" / "characters" / "characters.json"
    if characters_path.exists():
        with open(characters_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("characters", {})
    return {}


# 角色名别名映射（与 gen_keyframes_json.py 一致）
_CHARACTER_ALIASES = {
    "young_fuxi": "fuxi",
    "hunter_jia": "hunter",
    "hunter_yi": "hunter",
    "nuwa": "nvwa",
    "observer_ai": None,
}

# 性别 → prompt 强化前缀
_GENDER_PROMPT_PREFIX = {
    "male": "male figure, masculine features, man, ",
    "female": "female figure, feminine features, woman, ",
}


def build_gender_prefix(character_refs: list[str], characters_db: dict) -> str:
    """根据角色性别和发型生成 prompt 前缀，强化角色一致性。

    只处理有视觉形象且有明确性别的角色。
    多角色时取第一个有性别定义的角色。
    同时注入发型信息（如果定义了 hairstyle 字段）。
    """
    for char_ref in character_refs:
        # 跳过无视觉形象的角色
        if _CHARACTER_ALIASES.get(char_ref) is None and char_ref in _CHARACTER_ALIASES:
            continue

        # 在 characters_db 中查找（直接名或别名前的原名）
        char_def = characters_db.get(char_ref, {})
        gender = char_def.get("gender")
        hairstyle = char_def.get("hairstyle", "")

        if gender and gender in _GENDER_PROMPT_PREFIX:
            prefix = _GENDER_PROMPT_PREFIX[gender]
            # 添加发型信息（如果有）
            if hairstyle:
                prefix += f"{hairstyle}, "
            return prefix

    return ""


def scale_image_to_resolution(src_path: Path, dest_path: Path, width: int = OUTPUT_WIDTH, height: int = OUTPUT_HEIGHT, mode: str = "auto") -> None:
    """将图像缩放到指定分辨率。

    Args:
        mode:
          "fill" — 裁切填满（适合宽幅场景参考）
          "fit"  — 完整显示+黑边（适合正方形/竖幅角色参考，黑边由denoise填充）
          "auto" — 自动检测：如果原图宽高比接近目标则fill，否则fit
    """
    img = Image.open(src_path)
    original_w, original_h = img.size
    target_ratio = width / height       # 1920/1080 ≈ 1.78
    source_ratio = original_w / original_h

    # auto 模式：宽高比偏差 > 30% 时用 fit（避免过度裁切）
    if mode == "auto":
        ratio_diff = abs(source_ratio - target_ratio) / target_ratio
        mode = "fit" if ratio_diff > 0.3 else "fill"

    if mode == "fit":
        scale = min(width / original_w, height / original_h)
    else:
        scale = max(width / original_w, height / original_h)

    new_w = int(original_w * scale)
    new_h = int(original_h * scale)

    # 缩放图像
    img_scaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # 创建指定分辨率的新图像（黑色背景）
    canvas = Image.new('RGB', (width, height), color=(0, 0, 0))

    # 居中粘贴缩放后的图像
    x_offset = (width - new_w) // 2
    y_offset = (height - new_h) // 2
    canvas.paste(img_scaled, (x_offset, y_offset))

    # 保存到目标位置
    canvas.save(dest_path, quality=95)


def load_workflow(workflow_name: str) -> dict:
    """加载ComfyUI工作流JSON文件。支持包装格式和原生ComfyUI格式。"""
    workflow_path = WORKFLOWS_DIR / f"{workflow_name}.json"
    if not workflow_path.exists():
        raise FileNotFoundError(f"Workflow not found: {workflow_path}")

    with open(workflow_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 处理包装格式 (带name, description, parameters字段的格式)
    if "workflow" in data and isinstance(data["workflow"], dict):
        # 返回内层的workflow字典，它包含节点定义
        return data["workflow"]

    # 否则直接返回（原生ComfyUI格式）
    return data


def inject_parameters(workflow: dict, params: dict) -> dict:
    """向工作流注入参数（替换提示词、seed等）。支持两种格式：字典型和nodes数组型。"""
    workflow = json.loads(json.dumps(workflow))  # 深拷贝

    # 检查工作流格式：是否为ComfyUI图形化编辑器格式(nodes数组)
    if "nodes" in workflow and isinstance(workflow["nodes"], list):
        # 新格式：nodes数组型（Flux2_人物角度一致性编辑V1风格）
        for node in workflow["nodes"]:
            node_type = node.get("type", "")

            # CLIPTextEncode节点 - 注入prompt
            if node_type == "CLIPTextEncode" and "positive_prompt" in params:
                node["widgets_values"][0] = params["positive_prompt"]

            # RandomNoise节点 - 注入seed
            if node_type == "RandomNoise" and "seed" in params:
                node["widgets_values"][0] = params["seed"]

            # SaveImage节点 - 注入filename_prefix
            if node_type == "SaveImage" and "filename_prefix" in params:
                node["widgets_values"][0] = params["filename_prefix"]

            # LoadImage节点 - 注入reference_image
            if node_type == "LoadImage" and "reference_image" in params:
                node["widgets_values"][0] = params["reference_image"]

    else:
        # 旧格式：简单字典型（flux2_txt2img/flux2_img2img风格）
        # 动态查找节点而不是硬编码 ID

        # 查找第一个 CLIPTextEncode 节点用于正向提示词
        if "positive_prompt" in params:
            for node_id, node in workflow.items():
                if node.get("class_type") == "CLIPTextEncode" and "text" in node.get("inputs", {}):
                    # 只设置第一个（正向提示词）
                    if node["inputs"].get("text") != "anatomy error":
                        node["inputs"]["text"] = params["positive_prompt"]
                        break

        # 查找 KSampler 节点用于 seed 和 denoise
        if "seed" in params or "denoise" in params:
            for node_id, node in workflow.items():
                if node.get("class_type") == "KSampler":
                    if "seed" in params:
                        node["inputs"]["seed"] = params["seed"]
                    if "denoise" in params:
                        node["inputs"]["denoise"] = params["denoise"]
                    break

        if "filename_prefix" in params:
            # 找到SaveImage节点并更新
            for node_id, node in workflow.items():
                if node.get("class_type") == "SaveImage":
                    node["inputs"]["filename_prefix"] = params["filename_prefix"]

        # I2I工作流参数注入 - 查找 LoadImage 节点
        if "reference_image" in params:
            for node_id, node in workflow.items():
                if node.get("class_type") == "LoadImage":
                    node["inputs"]["image"] = params["reference_image"]
                    break

    return workflow


def queue_prompt(workflow: dict) -> str:
    """提交工作流到ComfyUI。"""
    payload = json.dumps({"prompt": workflow}).encode()
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        return result.get("prompt_id")


def poll_until_done(prompt_id: str, poll_interval: float = 2.0, timeout: float = 1200.0) -> dict:
    """轮询直到任务完成。"""
    import time
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise TimeoutError(f"Workflow timeout after {timeout}s")

        try:
            req = urllib.request.Request(f"{COMFYUI_URL}/history/{prompt_id}")
            with urllib.request.urlopen(req) as response:
                history = json.loads(response.read().decode())
                if prompt_id in history:
                    entry = history[prompt_id]
                    if entry.get("status", {}).get("completed", False):
                        return entry
        except Exception as e:
            print(f"  Poll error: {e}")

        time.sleep(poll_interval)


def get_output_images(entry: dict) -> list:
    """从执行结果中提取输出图像信息。"""
    images = []
    for node_out in entry.get("outputs", {}).values():
        if isinstance(node_out, dict) and "images" in node_out:
            images.extend(node_out.get("images", []))
    return images


def download_image(image_info: dict, dest_path: Path) -> Path:
    """从ComfyUI下载生成的图像。"""
    params = urllib.parse.urlencode({
        "filename": image_info.get("filename", ""),
        "subfolder": image_info.get("subfolder", ""),
        "type": image_info.get("type", "output"),
    })
    url = f"{COMFYUI_URL}/view?{params}"
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, str(dest_path))
    return dest_path


def find_location_asset_reference(location: str) -> Path:
    """找到location对应的地点参考图片。

    查找优先级:
      1. assets/locations/{location}/ 下的生成参考图 (gen_locations_refs.py生成)
      2. assets/locations/ 下的资产 (向后兼容)

    返回: Path to best reference image
    """
    # 使用共享资产目录，位于fuxi项目根目录
    project_root = Path(__file__).parent.parent
    locations_ref_dir = project_root / "assets" / "locations" / location
    locations_dir = project_root / "assets" / "locations"

    # 优先级1: 查找从gen_locations_refs.py生成的地点参考图
    if locations_ref_dir.exists():
        # 查找 {location}_ref_*.png 格式的文件（由gen_locations_refs.py生成）
        ref_files = sorted(list(locations_ref_dir.glob(f"{location}_ref_*.png")))
        if ref_files:
            # 返回第一个（最基础的参考）
            selected = ref_files[0]
            print(f"    └─ Using generated location reference: {selected.name}")
            return selected

    # 优先级2: 降级到assets/locations目录（向后兼容）
    if locations_dir.exists():
        # 尝试直接的location文件
        for ext in [".png", ".jpg", ".jpeg"]:
            location_file = locations_dir / f"{location}{ext}"
            if location_file.exists():
                print(f"    └─ Using legacy location asset: {location_file.name}")
                return location_file

        # 退而求其次，查找ref_final
        for ext in [".png", ".jpg", ".jpeg"]:
            ref_final = locations_dir / f"ref_final{ext}"
            if ref_final.exists():
                print(f"    └─ Using fallback ref_final: {ref_final.name}")
                return ref_final

    raise FileNotFoundError(
        f"No location asset reference found for '{location}'. "
        f"Expected either: {locations_ref_dir} or {locations_dir}"
    )


def find_character_asset_reference(character: str) -> Path:
    """找到character对应的角色参考图片。

    查找优先级:
      1. assets/characters/{character}/ 下的生成参考图 (gen_characters_refs.py生成)
         - {character}_ref_*.png 格式（新格式）
         - ref_final.png 格式（现有格式）
      2. assets/characters/ 下的资产 (向后兼容)

    返回: Path to best reference image
    """
    project_root = Path(__file__).parent.parent
    character_ref_dir = project_root / "assets" / "characters" / character
    characters_dir = project_root / "assets" / "characters"

    # 优先级1: 查找从gen_characters_refs.py生成的角色参考图
    if character_ref_dir.exists():
        # 查找 {character}_ref_*.png 格式的文件（新格式）
        ref_files = sorted(list(character_ref_dir.glob(f"{character}_ref_*.png")))
        if ref_files:
            selected = ref_files[0]
            print(f"    └─ Using generated character reference: {selected.name}")
            return selected

        # 查找 ref_final.png（现有格式）
        ref_final = character_ref_dir / "ref_final.png"
        if ref_final.exists():
            print(f"    └─ Using character reference: {ref_final.name}")
            return ref_final

        # 查找任何 ref_*.png 文件（其他格式兼容）
        ref_files = sorted(list(character_ref_dir.glob("ref_*.png")))
        if ref_files:
            selected = ref_files[0]
            print(f"    └─ Using character reference: {selected.name}")
            return selected

    # 优先级2: 降级到assets/characters目录（向后兼容）
    if characters_dir.exists():
        # 尝试直接的character文件
        for ext in [".png", ".jpg", ".jpeg"]:
            character_file = characters_dir / f"{character}{ext}"
            if character_file.exists():
                print(f"    └─ Using legacy character asset: {character_file.name}")
                return character_file

    raise FileNotFoundError(
        f"No character asset reference found for '{character}'. "
        f"Expected either: {character_ref_dir}/{{ref_final.png or {character}_ref_*.png}} or {characters_dir}"
    )


def select_first_frame_reference(shot: dict, keyframe: dict) -> tuple[str, Path] | None:
    """智能选择第一帧的参考图片（location或character）。

    决策逻辑:
      1. 检查keyframe中的assets字段
      2. 如果有多个characters（2+），优先使用character
      3. 否则使用location
      4. 如果参考图未找到，回退到另一个选项

    返回: (asset_type, asset_path) 或 None
    """
    # 获取keyframe和shot中的资产信息
    kf_assets = keyframe.get("assets", {})
    character_refs = kf_assets.get("character_refs", []) or shot.get("character_refs", [])
    location_ref = kf_assets.get("location_ref") or shot.get("location_ref") or shot.get("location")

    print(f"    Location: {location_ref}, Characters: {character_refs}")

    # 智能决策：如果有多个characters（2+），优先使用character
    if len(character_refs) >= 2:
        for char in character_refs:
            try:
                path = find_character_asset_reference(char)
                print(f"    └─ Selected CHARACTER '{char}' (multi-character scene)")
                return ("character", path)
            except FileNotFoundError:
                continue

    # 否则使用location
    if location_ref:
        try:
            path = find_location_asset_reference(location_ref)
            print(f"    └─ Selected LOCATION '{location_ref}'")
            return ("location", path)
        except FileNotFoundError:
            pass

    # 回退：如果location未找到但有character，尝试character
    if character_refs and len(character_refs) == 1:
        try:
            path = find_character_asset_reference(character_refs[0])
            print(f"    └─ Fallback to CHARACTER '{character_refs[0]}' (location not found)")
            return ("character", path)
        except FileNotFoundError:
            pass

    return None


def generate_shot_keyframes(
    episode_id: str,
    shot_id: str,
    num_candidates: int = 1,
    base_seed: int = 0,
) -> dict:
    """为指定镜头生成所有关键帧 (全Multi-Ref，每帧都用相同的原始参考图)。

    工作流:
      1. 所有关键帧: location + characters 参考 + 各自的 prompt → 独立生成 (denoise=0.55)
         - 每帧都使用相同的原始参考图（location + 所有 characters）
         - 通过不同的 prompt 实现运镜变化
         - 无累积误差，角色和环境一致性极佳
      2. 角色性别自动注入: 从characters.json读取gender，前缀到prompt防止性别漂移

    返回: {keyframe_id: Path, ...}
    """
    ep_dir = get_episode_dir(episode_id)
    shots_data = load_shots(episode_id)

    # 加载关键帧配置
    keyframes_path = ep_dir / "keyframes.json"
    if not keyframes_path.exists():
        raise FileNotFoundError(f"Missing keyframes.json: {keyframes_path}")

    with open(keyframes_path, "r", encoding="utf-8") as f:
        keyframes_data = json.load(f)

    # 获取该shot的所有关键帧
    shot_keyframes = [
        kf for kf in keyframes_data["keyframes"]
        if kf["shot_id"] == shot_id
    ]

    if not shot_keyframes:
        raise ValueError(f"No keyframes found for shot {shot_id}")

    # 找到对应的shot数据
    shot = next((s for s in shots_data["shots"] if s["shot_id"] == shot_id), None)
    if not shot:
        raise ValueError(f"Shot {shot_id} not found in shots.json")

    # 排序关键帧
    shot_keyframes = sorted(shot_keyframes, key=lambda x: x["frame_index"])

    print(f"\n{'=' * 60}")
    print(f"镜头关键帧生成 — {episode_id}/{shot_id} (全I2I)")

    location = shot.get("location", None)
    location_ref = shot.get("location_ref", None)
    characters = shot.get("characters", [])
    character_refs = shot.get("character_refs", [])

    print(f"Location: {location} → Location Ref: {location_ref}")
    print(f"Characters: {characters} → Character Refs: {character_refs}")
    print(f"关键帧数: {len(shot_keyframes)}")
    print(f"{'=' * 60}\n")

    # 检查黑屏镜头
    location_to_check = location_ref or location
    if location_to_check == "black_screen":
        print(f"⚠️ 黑屏镜头，跳过关键帧生成")
        return {}

    # 加载角色数据库，用于性别注入
    characters_db = load_characters_json()

    results = {}
    keyframe_dir = ep_dir / "video" / "keyframes"
    keyframe_dir.mkdir(parents=True, exist_ok=True)

    # 全Multi-Ref工作流生成所有关键帧（每帧都用相同的原始参考图）
    for kf_idx, kf in enumerate(shot_keyframes):
        keyframe_id = kf["keyframe_id"]
        kf_type = kf["type"]
        kf_prompt = kf.get("prompt", "")

        if not kf_prompt:
            print(f"⚠️ [{keyframe_id}] No prompt, skipping")
            continue

        # 注入角色性别前缀，强化一致性
        kf_character_refs = kf.get("assets", {}).get("character_refs", []) or character_refs
        gender_prefix = build_gender_prefix(kf_character_refs, characters_db)
        if gender_prefix:
            kf_prompt = gender_prefix + kf_prompt

        # denoise: 所有帧使用 0.55
        denoise = 0.55

        print(f"\n{'─' * 50}")
        print(f"[MultiRef] {keyframe_id}  (type: {kf_type}, denoise: {denoise})")
        print(f"  📝 Prompt: {kf_prompt}")

        for cand_idx in range(num_candidates):
            seed = base_seed + kf["frame_index"] * 1000 + cand_idx * 10
            # 简化文件名：去掉 seed 后缀，如果有多个候选则用 _N 后缀
            if num_candidates == 1:
                output_path = keyframe_dir / f"{keyframe_id}.png"
            else:
                output_path = keyframe_dir / f"{keyframe_id}_{cand_idx + 1}.png"

            print(f"  → Candidate {cand_idx + 1}/{num_candidates} (seed={seed})")

            try:
                # 所有关键帧：使用多参考图工作流（location + characters）
                # 从 keyframes.json assets 获取 location 和 character 参考图路径
                kf_assets = kf.get("assets", {})
                location_ref_key = kf_assets.get("location_ref")
                character_refs_keys = kf_assets.get("character_refs", [])

                # 构建参考图列表：先 location，再 characters
                ref_images = []

                # 添加 location 参考
                if location_ref_key:
                    from pipeline.gen_keyframes_json import find_location_reference
                    loc_ref_path = find_location_reference(location_ref_key)
                    if loc_ref_path:
                        ref_images.append(loc_ref_path)

                # 添加 character 参考（过滤无视觉形象的角色）
                # 多角色场景：只保留主角参考图以增强一致性
                from pipeline.gen_keyframes_json import find_character_reference, resolve_character_name

                # 先过滤掉无视觉形象的角色
                visual_char_refs = [
                    char_ref for char_ref in character_refs_keys
                    if resolve_character_name(char_ref) is not None
                ]

                # 多角色场景：只使用第一个角色（主角）的参考图
                if len(visual_char_refs) > 1:
                    main_char = visual_char_refs[0]
                    char_ref_path = find_character_reference(main_char)
                    if char_ref_path:
                        ref_images.append(char_ref_path)
                    print(f"    💡 多角色场景，仅使用主角 '{main_char}' 的参考图以增强一致性")
                else:
                    # 单角色场景：正常添加
                    for char_ref_key in visual_char_refs:
                        char_ref_path = find_character_reference(char_ref_key)
                        if char_ref_path:
                            ref_images.append(char_ref_path)

                # location 参考图是必须的
                if not ref_images:
                    print(f"    ⚠️ 无 location 参考图，跳过（location 是必须的）")
                    continue

                # 确保参考图不超过2张（1 location + 最多1 character）
                if len(ref_images) > 2:
                    ref_images = ref_images[:2]

                print(f"    [MultiRef] {len(ref_images)} refs: {[p.name for p in ref_images]}")

                # 使用 creative-toolkit 多参考图工作流
                img_gen = ComfyUIImageGen()
                img_gen.generate_with_references(
                    prompt=kf_prompt,
                    ref_images=ref_images,
                    output_path=output_path,
                    size=f"{OUTPUT_WIDTH}x{OUTPUT_HEIGHT}",
                    steps=28,
                    guidance=8.0,
                    seed=seed,
                    upload=True,
                    filename_prefix=f"keyframe/{keyframe_id}",
                )
                print(f"    ✅ {output_path.name}")
                results[keyframe_id] = output_path

            except Exception as e:
                print(f"    ❌ Error: {e}")

    print(f"\n{'=' * 60}")
    print(f"✅ 生成完成")
    print(f"   总帧数: {len(results)}")
    print(f"{'=' * 60}\n")

    return results


def generate_all_keyframes(
    episode_id: str,
    num_candidates: int = 1,
    base_seed: int = 0,
) -> dict:
    """为整个episode批量生成所有镜头的关键帧，自动跳过已完成的。

    返回: {"generated": int, "skipped": int, "failed": int, "errors": [...]}
    """
    ep_dir = get_episode_dir(episode_id)
    shots_data = load_shots(episode_id)

    keyframes_path = ep_dir / "keyframes.json"
    if not keyframes_path.exists():
        raise FileNotFoundError(f"Missing keyframes.json: {keyframes_path}")

    with open(keyframes_path, "r", encoding="utf-8") as f:
        keyframes_data = json.load(f)

    keyframe_dir = ep_dir / "video" / "keyframes"
    keyframe_dir.mkdir(parents=True, exist_ok=True)

    total = len(shots_data["shots"])
    generated = 0
    skipped = 0
    failed = 0
    errors = []

    print(f"\n{'=' * 70}")
    print(f"批量关键帧生成 — {episode_id} ({total} 镜头, {keyframes_data['total_keyframes']} 关键帧)")
    print(f"{'=' * 70}\n")

    for i, shot in enumerate(shots_data["shots"], 1):
        shot_id = shot["shot_id"]

        # 检查该shot的关键帧是否已全部生成
        shot_kfs = [kf for kf in keyframes_data["keyframes"] if kf["shot_id"] == shot_id]
        all_exist = all(
            (keyframe_dir / f"{kf['keyframe_id']}.png").exists()
            for kf in shot_kfs
        ) if shot_kfs else False

        if all_exist:
            print(f"[{i:2d}/{total}] ⏭️  {shot_id} — 已完成 ({len(shot_kfs)} 帧)")
            skipped += 1
            continue

        try:
            results = generate_shot_keyframes(
                episode_id=episode_id,
                shot_id=shot_id,
                num_candidates=num_candidates,
                base_seed=base_seed,
            )
            if results:
                generated += 1
            else:
                skipped += 1
        except KeyboardInterrupt:
            print(f"\n⚠️ 用户中断，已处理 {i-1}/{total}")
            break
        except Exception as e:
            print(f"[{i:2d}/{total}] ❌ {shot_id} — {str(e)[:80]}")
            failed += 1
            errors.append({"shot_id": shot_id, "error": str(e)[:200]})

    total_files = len(list(keyframe_dir.glob("*.png")))
    print(f"\n{'=' * 70}")
    print(f"批量生成完成 — 成功: {generated}, 跳过: {skipped}, 失败: {failed}")
    print(f"关键帧目录共 {total_files} 个文件")
    print(f"{'=' * 70}\n")

    if errors:
        print("失败的镜头:")
        for err in errors:
            print(f"  {err['shot_id']}: {err['error']}")

    return {"generated": generated, "skipped": skipped, "failed": failed, "errors": errors}


def preview_all_keyframes(
    episode_id: str,
    shot_id: str | None = None,
    base_seed: int = 0,
) -> None:
    """打印所有关键帧的参考图和prompt信息，供用户检查（不实际生成）。"""
    ep_dir = get_episode_dir(episode_id)
    shots_data = load_shots(episode_id)

    keyframes_path = ep_dir / "keyframes.json"
    with open(keyframes_path, "r", encoding="utf-8") as f:
        keyframes_data = json.load(f)

    keyframe_dir = ep_dir / "video" / "keyframes"
    characters_db = load_characters_json()

    # 筛选shots
    shots = shots_data["shots"]
    if shot_id:
        shots = [s for s in shots if s["shot_id"] == shot_id]

    print(f"\n{'=' * 70}")
    print(f"关键帧预览 — {episode_id} (dry-run)")
    print(f"{'=' * 70}")

    for shot in shots:
        sid = shot["shot_id"]
        shot_kfs = sorted(
            [kf for kf in keyframes_data["keyframes"] if kf["shot_id"] == sid],
            key=lambda x: x["frame_index"],
        )
        if not shot_kfs:
            continue

        location = shot.get("location", "")
        location_ref = shot.get("location_ref", "")
        characters = shot.get("characters", [])
        character_refs = shot.get("character_refs", [])

        print(f"\n{'━' * 70}")
        print(f"🎬 {sid}  |  location: {location} ({location_ref})  |  chars: {characters} ({character_refs})")

        for kf_idx, kf in enumerate(shot_kfs):
            keyframe_id = kf["keyframe_id"]
            kf_prompt = kf.get("prompt", "")
            kf_ref_image = kf.get("ref_image")
            denoise = 0.55 if kf_idx == 0 else 0.55
            seed = base_seed + kf["frame_index"] * 1000

            # 性别前缀（与生成时一致）
            kf_character_refs = kf.get("assets", {}).get("character_refs", []) or character_refs
            gender_prefix = build_gender_prefix(kf_character_refs, characters_db)
            if gender_prefix:
                kf_prompt = gender_prefix + kf_prompt

            # 检查是否已生成
            output_path = keyframe_dir / f"{keyframe_id}.png"
            status = "✅ 已生成" if output_path.exists() else "⏳ 待生成"

            print(f"\n  {'─' * 50}")
            print(f"  [{keyframe_id}]  type: {kf['type']}  denoise: {denoise}  seed: {seed}  {status}")
            print(f"  📝 Prompt: {kf_prompt}")

            if kf_ref_image:
                ref_path = Path(kf_ref_image)
                if ref_path.is_absolute():
                    exists = ref_path.exists()
                    print(f"  🖼️  Ref: {kf_ref_image}")
                    print(f"       {'✅ exists' if exists else '❌ NOT FOUND'}")
                else:
                    print(f"  🖼️  Ref: {kf_ref_image} (← 前一帧输出)")
            else:
                print(f"  🖼️  Ref: ⚠️ NONE — 将缺少参考图!")

    print(f"\n{'=' * 70}")
    print(f"预览完成 (dry-run，未实际生成)")
    print(f"{'=' * 70}\n")


def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="生成镜头关键帧 (全I2I，智能选择location或character资产作为首帧参考)"
    )
    parser.add_argument("episode_id", help="剧集编号, e.g. ep001")
    parser.add_argument("shot_id", nargs="?", default=None, help="镜头编号, e.g. S01 (省略则生成全部)")
    parser.add_argument(
        "--all", action="store_true",
        help="生成所有镜头的关键帧（等同于省略shot_id）"
    )
    parser.add_argument(
        "--num-candidates", type=int, default=1,
        help="每个关键帧的候选数 (default: 1)"
    )
    parser.add_argument(
        "--base-seed", type=int, default=0,
        help="基础seed (default: 0)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="仅打印每个关键帧的参考图和prompt信息，不实际生成"
    )

    args = parser.parse_args()

    try:
        if args.dry_run:
            preview_all_keyframes(
                episode_id=args.episode_id,
                shot_id=args.shot_id,
                base_seed=args.base_seed,
            )
        elif args.all or args.shot_id is None:
            generate_all_keyframes(
                episode_id=args.episode_id,
                num_candidates=args.num_candidates,
                base_seed=args.base_seed,
            )
        else:
            generate_shot_keyframes(
                episode_id=args.episode_id,
                shot_id=args.shot_id,
                num_candidates=args.num_candidates,
                base_seed=args.base_seed,
            )
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
