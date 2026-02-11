#!/usr/bin/env python3
"""
镜头关键帧生成 — 全I2I (Image-to-Image) with Intelligent First-Frame Reference Selection

逻辑:
  - 第一帧 (i2i_first): 智能选择 location 或 character 资产 + visual prompt → 初始场景 (denoise=0.7)
    * 多角色场景（2+）优先选择 character 资产
    * 单角色或环境聚焦场景选择 location 资产
  - 后续帧 (i2i_seq): 前一帧结果 + motion prompt → 运动变化 (denoise=0.5)
  - 工作流: 所有关键帧都使用 flux2_i2i.json
  - prompt: 从 keyframes.json 读取每个关键帧的 contextual prompt
  - 资产: 从 keyframes.json 的 assets 字段读取 location_ref 和 character_refs

用法:
    python -m pipeline.gen_keyframe_images ep001 S01
    python -m pipeline.gen_keyframe_images ep001 S01 --num-candidates 3
    python -m pipeline.gen_keyframe_images ep001 S01 --base-seed 42
"""

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image
from pipeline.utils import get_episode_dir, load_shots


COMFYUI_URL = "http://127.0.0.1:8188"
COMFYUI_INPUT = Path("/home/dz/ComfyUI/input")
COMFYUI_OUTPUT = Path("/home/dz/ComfyUI/output")
WORKFLOWS_DIR = Path("/home/dz/ComfyUI/user/default/workflows")

# 输出分辨率
OUTPUT_WIDTH = 1920
OUTPUT_HEIGHT = 1080


def scale_image_to_resolution(src_path: Path, dest_path: Path, width: int = OUTPUT_WIDTH, height: int = OUTPUT_HEIGHT) -> None:
    """将图像缩放到指定分辨率（保持宽高比，填充空白）。"""
    img = Image.open(src_path)
    original_w, original_h = img.size

    # 计算缩放比例（保持宽高比）
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
    """为指定镜头生成所有关键帧 (全I2I，第一帧智能选择location或character资产，后续帧使用前一帧)。

    工作流:
      1. 第一帧 (i2i_first): 智能选择location或character参考 + visual prompt → 初始场景 (denoise=0.7)
         - 多角色场景（2+）优先选择character资产
         - 单角色或环境聚焦场景选择location资产
      2. 后续帧 (i2i_seq): 前一帧结果 + motion prompt → 运动变化 (denoise=0.5)

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

    results = {}
    keyframe_dir = ep_dir / "video" / "keyframes"
    keyframe_dir.mkdir(parents=True, exist_ok=True)

    # 用于跟踪每个candidate的最后一帧，以供下一帧作为参考
    last_frame_per_candidate = {}

    # 全I2I工作流生成所有关键帧
    for kf_idx, kf in enumerate(shot_keyframes):
        keyframe_id = kf["keyframe_id"]
        kf_type = kf["type"]
        kf_prompt = kf.get("prompt", "")
        kf_ref_image = kf.get("ref_image")  # 从keyframes.json读取ref_image

        if not kf_prompt:
            print(f"⚠️ [{keyframe_id}] No prompt, skipping")
            continue

        print(f"[I2I] {keyframe_id}")
        print(f"  Type: {kf_type}")
        print(f"  Prompt: {kf_prompt[:80]}...")

        for cand_idx in range(num_candidates):
            seed = base_seed + kf["frame_index"] * 1000 + cand_idx * 10
            output_path = keyframe_dir / f"{keyframe_id}_seed{seed:04d}.png"

            print(f"  → Candidate {cand_idx + 1}/{num_candidates} (seed={seed})")

            try:
                # 加载I2I工作流（所有关键帧都使用I2I）
                workflow = load_workflow("flux2_i2i")
                denoise = 0.7 if kf_idx == 0 else 0.5  # 首帧0.7，后续0.5

                # 构建工作流参数
                params = {
                    "positive_prompt": kf_prompt,
                    "seed": seed,
                    "denoise": denoise,
                    "filename_prefix": f"keyframe/{keyframe_id}_seed{seed:04d}",
                }

                # 处理参考图像
                if kf_ref_image:
                    # 检查ref_image是否为文件路径或keyframe_id
                    ref_path = Path(kf_ref_image)

                    if ref_path.is_absolute() and ref_path.exists():
                        # 文件路径：缩放并复制到ComfyUI input
                        ref_image_name = f"{keyframe_id}_ref.png"
                        comfyui_ref = COMFYUI_INPUT / ref_image_name
                        scale_image_to_resolution(ref_path, comfyui_ref)
                        params["reference_image"] = ref_image_name
                        print(f"    [I2I] Using reference image: {ref_path.name}")

                    elif cand_idx in last_frame_per_candidate and kf_ref_image.startswith(shot_id):
                        # 前一帧：使用前一个候选的输出
                        prev_frame_path = last_frame_per_candidate[cand_idx]
                        ref_image_name = f"{keyframe_id}_ref_c{cand_idx}.png"
                        comfyui_ref = COMFYUI_INPUT / ref_image_name
                        scale_image_to_resolution(prev_frame_path, comfyui_ref)
                        params["reference_image"] = ref_image_name
                        print(f"    [I2I] Using previous frame reference")

                # 注入参数
                workflow = inject_parameters(workflow, params)

                # 执行工作流
                prompt_id = queue_prompt(workflow)
                print(f"    queued {prompt_id}, waiting...")

                entry = poll_until_done(prompt_id)
                images = get_output_images(entry)

                if not images:
                    print(f"    ⚠️ No output images")
                    continue

                # 下载图像
                output_path = download_image(images[0], output_path)
                print(f"    ✅ {output_path.name}")
                results[keyframe_id] = output_path

                # 记录此candidate的最后一帧，供下一帧使用
                last_frame_per_candidate[cand_idx] = output_path

            except Exception as e:
                print(f"    ❌ Error: {e}")

    print(f"\n{'=' * 60}")
    print(f"✅ 生成完成")
    print(f"   总帧数: {len(results)}")
    print(f"{'=' * 60}\n")

    return results


def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="生成镜头的所有关键帧 (全I2I，智能选择location或character资产作为首帧参考)"
    )
    parser.add_argument("episode_id", help="剧集编号, e.g. ep001")
    parser.add_argument("shot_id", help="镜头编号, e.g. S01")
    parser.add_argument(
        "--num-candidates",
        type=int,
        default=1,
        help="每个关键帧的候选数 (default: 1)"
    )
    parser.add_argument(
        "--base-seed",
        type=int,
        default=0,
        help="基础seed (default: 0)"
    )

    args = parser.parse_args()

    try:
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
