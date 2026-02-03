#!/usr/bin/env python3
"""
镜头关键帧生成 — T2I + I2I (Image-to-Image)

逻辑:
  - 第1帧 (T2I): 使用flux2_txt2img.json工作流，从prompt_visual生成
  - 第2+帧 (I2I): 使用flux2_img2img.json工作流，以第1帧为参考，使用prompt_motion

用法:
    python -m pipeline.generate_shot_keyframes ep001 S01
    python -m pipeline.generate_shot_keyframes ep001 S01 --num-candidates 3
    python -m pipeline.generate_shot_keyframes ep001 S01 --base-seed 42
"""

import json
import shutil
import time
import urllib.request
from pathlib import Path

from pipeline.utils import get_episode_dir, load_shots


COMFYUI_URL = "http://127.0.0.1:8188"
COMFYUI_INPUT = Path("/home/dz/ComfyUI/input")
COMFYUI_OUTPUT = Path("/home/dz/ComfyUI/output")
WORKFLOWS_DIR = Path("/home/dz/ComfyUI/user/default/workflows")


def load_workflow(workflow_name: str) -> dict:
    """加载ComfyUI工作流JSON文件。"""
    workflow_path = WORKFLOWS_DIR / f"{workflow_name}.json"
    if not workflow_path.exists():
        raise FileNotFoundError(f"Workflow not found: {workflow_path}")

    with open(workflow_path, "r", encoding="utf-8") as f:
        return json.load(f)


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
        # T2I工作流参数注入
        if "positive_prompt" in params and "5" in workflow:
            workflow["5"]["inputs"]["text"] = params["positive_prompt"]

        if "seed" in params and "7" in workflow:
            workflow["7"]["inputs"]["seed"] = params["seed"]

        if "denoise" in params and "8" in workflow:
            workflow["8"]["inputs"]["denoise"] = params["denoise"]

        if "filename_prefix" in params:
            # 找到SaveImage节点并更新
            for node_id, node in workflow.items():
                if node.get("class_type") == "SaveImage":
                    node["inputs"]["filename_prefix"] = params["filename_prefix"]

        # I2I工作流参数注入
        if "reference_image" in params and "4" in workflow:
            workflow["4"]["inputs"]["image"] = params["reference_image"]

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


def poll_until_done(prompt_id: str, poll_interval: float = 2.0, timeout: float = 600.0) -> dict:
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


def generate_shot_keyframes(
    episode_id: str,
    shot_id: str,
    num_candidates: int = 1,
    base_seed: int = 0,
) -> dict:
    """为指定镜头生成所有关键帧 (T2I + I2I)。

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
    print(f"镜头关键帧生成 — {episode_id}/{shot_id}")
    print(f"关键帧数: {len(shot_keyframes)}")
    print(f"{'=' * 60}\n")

    results = {}
    keyframe_dir = ep_dir / "video" / "keyframes"
    keyframe_dir.mkdir(parents=True, exist_ok=True)

    # 第一帧：T2I
    t2i_kf = shot_keyframes[0]
    print(f"[T2I] {t2i_kf['keyframe_id']}")
    print(f"  Prompt: {shot['prompt_visual'][:80]}...")

    for cand_idx in range(num_candidates):
        seed = base_seed + cand_idx * 100
        output_path = keyframe_dir / f"{t2i_kf['keyframe_id']}_seed{seed:04d}.png"

        print(f"  → Candidate {cand_idx + 1}/{num_candidates} (seed={seed})")

        try:
            # 加载T2I工作流
            workflow = load_workflow("flux2_txt2img")

            # 注入参数
            workflow = inject_parameters(workflow, {
                "positive_prompt": shot["prompt_visual"],
                "seed": seed,
                "filename_prefix": f"keyframe/{t2i_kf['keyframe_id']}_seed{seed:04d}",
            })

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
            results[t2i_kf['keyframe_id']] = output_path

        except Exception as e:
            print(f"    ❌ Error: {e}")

    # 后续帧：I2I （如有）
    if len(shot_keyframes) > 1:
        # 使用第一帧作为参考
        first_t2i_path = results.get(t2i_kf['keyframe_id'])
        if not first_t2i_path:
            print(f"\n⚠️ No T2I reference, skipping I2I frames")
        else:
            # 将参考帧复制到ComfyUI input
            ref_image_name = f"{shot_id}_ref.png"
            comfyui_ref = COMFYUI_INPUT / ref_image_name
            shutil.copy2(first_t2i_path, comfyui_ref)

            # 生成后续帧
            for i, i2i_kf in enumerate(shot_keyframes[1:], 1):
                print(f"\n[I2I-{i}] {i2i_kf['keyframe_id']}")

                # 使用prompt_motion（如有）
                motion_prompt = shot.get("prompt_motion", "")
                if motion_prompt:
                    print(f"  Prompt: {motion_prompt[:80]}...")

                for cand_idx in range(num_candidates):
                    seed = base_seed + 1000 + i * 100 + cand_idx * 10
                    output_path = keyframe_dir / f"{i2i_kf['keyframe_id']}_seed{seed:04d}.png"

                    print(f"  → Candidate {cand_idx + 1}/{num_candidates} (seed={seed})")

                    try:
                        # 加载I2I工作流 (临时使用flux2_img2img直到人物角度一致性编辑工作流转换为API格式)
                        workflow = load_workflow("flux2_img2img")

                        # 注入参数
                        workflow = inject_parameters(workflow, {
                            "positive_prompt": motion_prompt or "subtle variation",
                            "reference_image": ref_image_name,
                            "seed": seed,
                            "denoise": 0.6,  # I2I强度
                            "filename_prefix": f"keyframe/{i2i_kf['keyframe_id']}_seed{seed:04d}",
                        })

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
                        results[i2i_kf['keyframe_id']] = output_path

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
        description="生成镜头的所有关键帧 (T2I + I2I)"
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
