#!/usr/bin/env python3
"""
伏羲纪元 — 根据关键帧生成镜头视频

工作流：kf_to_video (ComfyUI)
  - 加载关键帧序列（从gen_keyframe_images.py生成）
  - 通过kf_to_video工作流生成中间帧
  - 输出完整镜头视频

使用：
  # 生成单个镜头视频
  pixi run python -m pipeline.gen_shot_video ep001 S01

  # 生成多个镜头
  pixi run python -m pipeline.gen_shot_video ep001 S01 S02 S03

  # 生成整集视频
  pixi run python -m pipeline.gen_shot_video ep001

  # 指定输出质量
  pixi run python -m pipeline.gen_shot_video ep001 S01 --quality high
"""

import argparse
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from pipeline.utils import ensure_episode_dirs, get_episode_dir, load_shots


COMFYUI_URL = "http://127.0.0.1:8188"
COMFYUI_INPUT = Path("/home/dz/ComfyUI/input")
COMFYUI_OUTPUT = Path("/home/dz/ComfyUI/output")
WORKFLOWS_DIR = Path("/home/dz/ComfyUI/user/default/workflows")

# 输出视频参数
OUTPUT_WIDTH = 1920
OUTPUT_HEIGHT = 1080
OUTPUT_FPS = 24


def load_workflow(workflow_name: str) -> dict:
    """加载ComfyUI工作流JSON文件"""
    workflow_path = WORKFLOWS_DIR / f"{workflow_name}.json"
    if not workflow_path.exists():
        raise FileNotFoundError(f"Workflow not found: {workflow_path}")

    with open(workflow_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 处理包装格式
    if "workflow" in data and isinstance(data["workflow"], dict):
        return data["workflow"]

    return data


def inject_parameters(workflow: dict, params: dict) -> dict:
    """向工作流注入参数（提示词、种子、图片路径等）"""
    workflow_copy = json.loads(json.dumps(workflow))

    for node_id, node in workflow_copy.items():
        if not isinstance(node, dict):
            continue

        # 注入提示词
        if "prompt" in node and "prompt" in params:
            node["inputs"]["text"] = params["prompt"]

        # 注入种子
        if "seed" in node and "seed" in params:
            node["inputs"]["seed"] = params["seed"]

        # 注入关键帧图片路径
        if "image" in node and "keyframes" in params:
            # 假设node有image_list或images字段
            if "images" in node["inputs"]:
                node["inputs"]["images"] = params["keyframes"]
            elif "image" in node["inputs"]:
                node["inputs"]["image"] = params["keyframes"][0] if params["keyframes"] else ""

        # 注入其他参数
        for param_key, param_value in params.items():
            if param_key in ["prompt", "seed", "keyframes"]:
                continue
            if param_key in node.get("inputs", {}):
                node["inputs"][param_key] = param_value

    return workflow_copy


def submit_workflow(workflow: dict) -> str:
    """提交工作流到ComfyUI并返回任务ID"""
    try:
        payload = json.dumps(workflow).encode("utf-8")
        req = urllib.request.Request(
            f"{COMFYUI_URL}/prompt",
            data=payload,
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            prompt_id = result.get("prompt_id")
            if not prompt_id:
                raise ValueError("No prompt_id in response")
            return prompt_id

    except Exception as e:
        raise RuntimeError(f"Failed to submit workflow: {e}")


def wait_for_completion(prompt_id: str, timeout_s: int = 600) -> dict:
    """等待工作流完成"""
    start_time = time.time()

    while time.time() - start_time < timeout_s:
        try:
            req = urllib.request.Request(f"{COMFYUI_URL}/history/{prompt_id}")
            with urllib.request.urlopen(req) as response:
                history = json.loads(response.read().decode())

                if prompt_id not in history:
                    time.sleep(1)
                    continue

                result = history[prompt_id]

                # 检查是否有错误
                if "error" in result or "status" in result:
                    if "status" in result and result["status"].get("status") == "error":
                        raise RuntimeError(f"Workflow error: {result['status']}")

                # 如果有输出，认为完成
                if "outputs" in result and result["outputs"]:
                    return result

                time.sleep(1)

        except Exception as e:
            if "HTTP Error 404" in str(e):
                time.sleep(1)
                continue
            raise

    raise TimeoutError(f"Workflow {prompt_id} timed out after {timeout_s}s")


def copy_workflow_outputs(
    source_dir: Path,
    dest_path: Path,
    file_pattern: str = "*.mp4",
) -> bool:
    """从ComfyUI输出目录复制生成的视频"""
    try:
        import shutil
        import glob

        # 查找匹配的输出文件
        output_files = glob.glob(str(source_dir / file_pattern))

        if not output_files:
            return False

        # 使用最新的文件
        latest_file = max(output_files, key=lambda p: Path(p).stat().st_mtime)
        shutil.copy(latest_file, dest_path)

        return True

    except Exception as e:
        print(f"  ✗ 复制输出失败: {e}")
        return False


def generate_shot_video(
    episode_id: str,
    shot_id: str,
    keyframes_dir: Path | None = None,
    output_path: Path | None = None,
    quality: str = "high",
) -> Path | None:
    """生成单个镜头视频

    Args:
        episode_id: 剧集ID (e.g., "ep001")
        shot_id: 镜头ID (e.g., "S01")
        keyframes_dir: 关键帧图片目录（默认: episodes/{ep}/keyframes/{shot_id}）
        output_path: 输出视频路径（默认: episodes/{ep}/video/{shot_id}_video.mp4）
        quality: 输出质量 ("low", "medium", "high")

    Returns:
        生成的视频路径，失败返回None
    """
    ep_dir = get_episode_dir(episode_id)

    # 默认路径
    if keyframes_dir is None:
        keyframes_dir = ep_dir / "keyframes" / shot_id

    if output_path is None:
        output_path = ep_dir / "video" / f"{shot_id}_video.mp4"

    # 检查关键帧目录
    if not keyframes_dir.exists():
        print(f"  ✗ 关键帧目录不存在: {keyframes_dir}")
        return None

    # 列出关键帧图片
    keyframe_images = sorted(keyframes_dir.glob("*.png"))
    if not keyframe_images:
        print(f"  ✗ 未找到关键帧图片: {keyframes_dir}")
        return None

    print(f"  → {shot_id}: {len(keyframe_images)} 关键帧")

    # 加载kf_to_video工作流
    try:
        workflow = load_workflow("kf_to_video")
    except FileNotFoundError:
        print(f"  ✗ 工作流缺失: kf_to_video.json")
        print(f"     需要在 {WORKFLOWS_DIR}/kf_to_video.json")
        return None

    # 准备关键帧列表（复制到ComfyUI input目录）
    input_dir = COMFYUI_INPUT / shot_id
    input_dir.mkdir(parents=True, exist_ok=True)

    keyframe_names = []
    for i, kf_path in enumerate(keyframe_images):
        dest = input_dir / f"keyframe_{i:03d}.png"
        # 符号链接或复制
        if not dest.exists():
            import shutil
            shutil.copy(kf_path, dest)
        keyframe_names.append(dest.name)

    # 注入参数
    params = {
        "keyframes": keyframe_names,
        "quality": quality,
        "output_width": OUTPUT_WIDTH,
        "output_height": OUTPUT_HEIGHT,
        "output_fps": OUTPUT_FPS,
    }

    try:
        workflow = inject_parameters(workflow, params)
    except Exception as e:
        print(f"  ✗ 参数注入失败: {e}")
        return None

    # 提交工作流
    try:
        print(f"    提交工作流...")
        prompt_id = submit_workflow(workflow)
        print(f"    任务ID: {prompt_id}")
    except Exception as e:
        print(f"  ✗ 提交失败: {e}")
        return None

    # 等待完成
    try:
        print(f"    等待完成...", end="", flush=True)
        result = wait_for_completion(prompt_id, timeout_s=600)
        print(" ✓")
    except TimeoutError:
        print(f" ✗ (超时)")
        return None
    except Exception as e:
        print(f" ✗ ({e})")
        return None

    # 复制输出
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if copy_workflow_outputs(COMFYUI_OUTPUT, output_path, "*.mp4"):
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"  ✓ {shot_id} → {output_path.name} ({size_mb:.1f} MB)")
            return output_path
        else:
            print(f"  ✗ 复制输出失败")
            return None

    except Exception as e:
        print(f"  ✗ 错误: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="根据关键帧生成镜头视频 (kf_to_video工作流)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成单个镜头视频
  pixi run python -m pipeline.gen_shot_video ep001 S01

  # 生成多个镜头
  pixi run python -m pipeline.gen_shot_video ep001 S01 S02 S03

  # 生成整集视频
  pixi run python -m pipeline.gen_shot_video ep001

  # 指定质量
  pixi run python -m pipeline.gen_shot_video ep001 --quality high
        """,
    )

    parser.add_argument("episode_id", help="剧集ID (e.g., ep001)")
    parser.add_argument(
        "shot_ids",
        nargs="*",
        help="镜头IDs (不指定则处理全部)",
    )
    parser.add_argument(
        "--quality",
        choices=["low", "medium", "high"],
        default="high",
        help="输出质量 (默认: high)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="单个镜头超时时间(秒，默认600)",
    )

    args = parser.parse_args()

    episode_id = args.episode_id
    ep_dir = get_episode_dir(episode_id)
    ensure_episode_dirs(episode_id)

    print(f"\n{'=' * 70}")
    print(f"关键帧→视频生成 — {episode_id}")
    print(f"工作流: kf_to_video")
    print(f"质量: {args.quality.upper()}")
    print(f"{'=' * 70}\n")

    # 加载shots.json
    try:
        shots_data = load_shots(episode_id)
    except FileNotFoundError:
        print(f"❌ 错误: 找不到 {episode_id}/shots.json")
        sys.exit(1)

    shots = shots_data["shots"]

    # 过滤镜头
    if args.shot_ids:
        shot_filter = set(args.shot_ids)
        shots = [s for s in shots if s["shot_id"] in shot_filter]
        if not shots:
            print(f"❌ 未找到指定的镜头: {args.shot_ids}")
            sys.exit(1)

    print(f"处理 {len(shots)} 个镜头:\n")

    success_count = 0
    for shot in shots:
        shot_id = shot["shot_id"]

        result = generate_shot_video(
            episode_id=episode_id,
            shot_id=shot_id,
            quality=args.quality,
        )

        if result:
            success_count += 1

    print(f"\n{'=' * 70}")
    print(f"✓ 成功: {success_count}/{len(shots)} 个镜头")
    print(f"{'=' * 70}\n")

    if success_count < len(shots):
        sys.exit(1)


if __name__ == "__main__":
    main()
