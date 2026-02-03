"""
分镜视频生成 — LTX-2 I2V via ComfyUI API

用法:
    pixi run python -m pipeline.generate_shot_video ep001 S01 --prompt "..." --input-image path.png
    pixi run python -m pipeline.generate_shot_video ep001 S01 --prompt-file prompts/S01.txt
    pixi run python -m pipeline.generate_shot_video ep001 S01 --seed1 256 --seed2 2560 --frames 121
"""

from __future__ import annotations

import argparse
import json
import shutil
import time
import urllib.request
from pathlib import Path

from pipeline.utils import PROJECT_ROOT, get_episode_dir

COMFYUI_URL = "http://127.0.0.1:8188"
COMFYUI_INPUT = Path("/home/dz/ComfyUI/input")
COMFYUI_OUTPUT = Path("/home/dz/ComfyUI/output")

DEFAULT_FRAMES = 121  # ~4.84s @ 25fps
DEFAULT_FPS = 25
DEFAULT_NEGATIVE = (
    "pink, purple, magenta, overexposed, blown out highlights, "
    "dark scene, blackout, mechanical structures, "
    "worst quality, blurry, jittery"
)


def build_ltx2_i2v_workflow(
    image_name: str,
    video_prompt: str,
    negative_prompt: str = DEFAULT_NEGATIVE,
    frame_count: int = DEFAULT_FRAMES,
    seed1: int = 42,
    seed2: int = 420,
    filename_prefix: str = "video/shot",
) -> dict:
    """构建 CybEye LTX-2 I2V 工作流 (API format)."""
    return {
        # --- 输入图片 ---
        "98": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "102": {
            "class_type": "ResizeImageMaskNode",
            "inputs": {
                "input": ["98", 0],
                "resize_type": "scale dimensions",
                "resize_type.width": 1344,
                "resize_type.height": 768,
                "resize_type.crop": "center",
                "scale_method": "lanczos",
            },
        },
        # --- 模型加载 ---
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "ltx-2-19b-dev-fp8.safetensors"},
        },
        "48": {
            "class_type": "LTXVAudioVAELoader",
            "inputs": {"ckpt_name": "ltx-2-19b-dev-fp8.safetensors"},
        },
        "60": {
            "class_type": "LTXAVTextEncoderLoader",
            "inputs": {
                "text_encoder": "gemma_3_12B_it_fp8_scaled.safetensors",
                "ckpt_name": "ltx-2-19b-dev-fp8.safetensors",
                "device": "cpu",
            },
        },
        "76": {
            "class_type": "LatentUpscaleModelLoader",
            "inputs": {"model_name": "ltx-2-spatial-upscaler-x2-1.0.safetensors"},
        },
        # --- 文本编码 ---
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["60", 0], "text": video_prompt},
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["60", 0], "text": negative_prompt},
        },
        "22": {
            "class_type": "LTXVConditioning",
            "inputs": {
                "positive": ["3", 0],
                "negative": ["4", 0],
                "frame_rate": DEFAULT_FPS,
            },
        },
        # --- Latent (半分辨率) ---
        "105": {"class_type": "GetImageSize", "inputs": {"image": ["102", 0]}},
        "89": {
            "class_type": "EmptyImage",
            "inputs": {
                "width": ["105", 0],
                "height": ["105", 1],
                "batch_size": 1,
                "color": 0,
            },
        },
        "90": {
            "class_type": "ImageScaleBy",
            "inputs": {
                "image": ["89", 0],
                "upscale_method": "lanczos",
                "scale_by": 0.5,
            },
        },
        "91": {"class_type": "GetImageSize", "inputs": {"image": ["90", 0]}},
        "43": {
            "class_type": "EmptyLTXVLatentVideo",
            "inputs": {
                "width": ["91", 0],
                "height": ["91", 1],
                "length": frame_count,
                "batch_size": 1,
            },
        },
        "51": {
            "class_type": "LTXVEmptyLatentAudio",
            "inputs": {
                "audio_vae": ["48", 0],
                "frames_number": frame_count,
                "frame_rate": DEFAULT_FPS,
                "batch_size": 1,
            },
        },
        # --- I2V 预处理 ---
        "106": {
            "class_type": "ResizeImagesByLongerEdge",
            "inputs": {"images": ["102", 0], "longer_edge": 1536},
        },
        "99": {
            "class_type": "LTXVPreprocess",
            "inputs": {"image": ["106", 0], "img_compression": 33},
        },
        "107": {
            "class_type": "LTXVImgToVideoInplace",
            "inputs": {
                "vae": ["1", 2],
                "image": ["99", 0],
                "latent": ["43", 0],
                "strength": 1.0,
                "bypass": False,
            },
        },
        "56": {
            "class_type": "LTXVConcatAVLatent",
            "inputs": {"video_latent": ["107", 0], "audio_latent": ["51", 0]},
        },
        # --- Stage 1: euler, 20 steps, CFG=4 ---
        "11": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed1}},
        "8": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "9": {
            "class_type": "LTXVScheduler",
            "inputs": {
                "latent": ["56", 0],
                "steps": 20,
                "max_shift": 2.05,
                "base_shift": 0.95,
                "stretch": True,
                "terminal": 0.1,
            },
        },
        "47": {
            "class_type": "CFGGuider",
            "inputs": {
                "model": ["1", 0],
                "positive": ["22", 0],
                "negative": ["22", 1],
                "cfg": 4.0,
            },
        },
        "41": {
            "class_type": "SamplerCustomAdvanced",
            "inputs": {
                "noise": ["11", 0],
                "guider": ["47", 0],
                "sampler": ["8", 0],
                "sigmas": ["9", 0],
                "latent_image": ["56", 0],
            },
        },
        # --- 中间: 分离 + 裁剪 + 上采样 ---
        "80": {
            "class_type": "LTXVSeparateAVLatent",
            "inputs": {"av_latent": ["41", 0]},
        },
        "81": {
            "class_type": "LTXVCropGuides",
            "inputs": {
                "positive": ["22", 0],
                "negative": ["22", 1],
                "latent": ["80", 0],
            },
        },
        "84": {
            "class_type": "LTXVLatentUpsampler",
            "inputs": {
                "samples": ["81", 2],
                "upscale_model": ["76", 0],
                "vae": ["1", 2],
            },
        },
        # --- Stage 2 I2V ---
        "108": {
            "class_type": "LTXVImgToVideoInplace",
            "inputs": {
                "vae": ["1", 2],
                "image": ["99", 0],
                "latent": ["84", 0],
                "strength": 1.0,
                "bypass": False,
            },
        },
        "83": {
            "class_type": "LTXVConcatAVLatent",
            "inputs": {"video_latent": ["108", 0], "audio_latent": ["80", 1]},
        },
        # --- Stage 2: gradient_estimation + distilled LoRA ---
        "68": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "model": ["1", 0],
                "lora_name": "ltx-2-19b-distilled-lora-384.safetensors",
                "strength_model": 1.0,
            },
        },
        "67": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed2}},
        "66": {
            "class_type": "KSamplerSelect",
            "inputs": {"sampler_name": "gradient_estimation"},
        },
        "73": {
            "class_type": "ManualSigmas",
            "inputs": {"sigmas": "0.909375, 0.725, 0.421875, 0.0"},
        },
        "82": {
            "class_type": "CFGGuider",
            "inputs": {
                "model": ["68", 0],
                "positive": ["81", 0],
                "negative": ["81", 1],
                "cfg": 1.0,
            },
        },
        "70": {
            "class_type": "SamplerCustomAdvanced",
            "inputs": {
                "noise": ["67", 0],
                "guider": ["82", 0],
                "sampler": ["66", 0],
                "sigmas": ["73", 0],
                "latent_image": ["83", 0],
            },
        },
        # --- 解码 + 保存 ---
        "94": {
            "class_type": "LTXVSeparateAVLatent",
            "inputs": {"av_latent": ["70", 1]},
        },
        "95": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["94", 0], "vae": ["1", 2]},
        },
        "96": {
            "class_type": "LTXVAudioVAEDecode",
            "inputs": {"samples": ["94", 1], "audio_vae": ["48", 0]},
        },
        "97": {
            "class_type": "CreateVideo",
            "inputs": {
                "images": ["95", 0],
                "audio": ["96", 0],
                "fps": float(DEFAULT_FPS),
            },
        },
        "75": {
            "class_type": "SaveVideo",
            "inputs": {
                "video": ["97", 0],
                "filename_prefix": filename_prefix,
                "format": "auto",
                "codec": "auto",
            },
        },
    }


def queue_prompt(workflow: dict) -> str:
    payload = json.dumps({"prompt": workflow}).encode()
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["prompt_id"]


def poll_until_done(prompt_id: str, timeout: float = 600.0) -> dict:
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        time.sleep(5)
        elapsed = time.monotonic() - start
        try:
            url = f"{COMFYUI_URL}/history/{prompt_id}"
            with urllib.request.urlopen(url, timeout=30) as resp:
                history = json.loads(resp.read())
        except Exception:
            continue
        if prompt_id not in history:
            print(f"  [{elapsed:.0f}s] running...")
            continue
        entry = history[prompt_id]
        status = entry.get("status", {})
        if status.get("status_str") == "error":
            msgs = status.get("messages", [])
            err_msg = "unknown"
            for msg in msgs:
                if msg[0] == "execution_error":
                    err_msg = msg[1].get("exception_message", err_msg)
            raise RuntimeError(f"ComfyUI error: {err_msg}")
        outputs = entry.get("outputs", {})
        for node_out in outputs.values():
            if any(k in node_out for k in ("gifs", "animated", "videos")):
                print(f"  done in {elapsed:.0f}s")
                return entry
        if status.get("status_str") == "success":
            return entry
    raise TimeoutError(f"Timeout after {timeout}s")


def get_output_video(entry: dict) -> str | None:
    for node_out in entry.get("outputs", {}).values():
        # SaveVideo 输出可能在 "gifs", "animated", 或 "videos" key 下
        for key in ("gifs", "animated", "videos"):
            for item in node_out.get(key, []):
                if not isinstance(item, dict):
                    continue
                sf = item.get("subfolder", "")
                return (
                    str(COMFYUI_OUTPUT / sf / item["filename"])
                    if sf
                    else str(COMFYUI_OUTPUT / item["filename"])
                )
    return None


def parse_prompt_file(path: Path) -> dict:
    """解析 prompt 文件，返回 {video_prompt, negative, input_image, ...}."""
    result = {}
    current_key = None
    current_lines = []

    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and "]" in stripped:
            if current_key and current_lines:
                result[current_key] = "\n".join(current_lines).strip()
            bracket_end = stripped.index("]")
            current_key = stripped[1:bracket_end].lower().replace(" ", "_")
            rest = stripped[bracket_end + 1 :].strip()
            current_lines = [rest] if rest else []
        elif current_key:
            current_lines.append(line.rstrip())

    if current_key and current_lines:
        result[current_key] = "\n".join(current_lines).strip()

    return result


def generate_shot_video(
    episode_id: str,
    shot_id: str,
    *,
    video_prompt: str | None = None,
    negative_prompt: str | None = None,
    input_image: str | None = None,
    frames: int = DEFAULT_FRAMES,
    seed1: int = 42,
    seed2: int = 420,
    version: str = "",
) -> Path:
    """生成一个分镜的视频。返回输出路径。"""
    # 动态创建 episode 路径
    episode_dir = get_episode_dir(episode_id)
    video_dir = episode_dir / "video"
    prompts_dir = episode_dir / "prompts"
    assets_dir = episode_dir / "assets"

    # 如果没有直接传参，从 prompt 文件读取
    if video_prompt is None or input_image is None:
        prompt_file = prompts_dir / f"{shot_id}.txt"
        if prompt_file.exists():
            parsed = parse_prompt_file(prompt_file)
            if video_prompt is None:
                # 尝试多种 key
                for k in [
                    "video_prompt_—_ltx-2_i2v,_5s_/_121_frames_@_25fps",
                    "video_prompt",
                    "positive_prompt",
                ]:
                    if k in parsed:
                        video_prompt = parsed[k]
                        break
            if input_image is None and "input_image" in parsed:
                input_image = parsed["input_image"]
            if negative_prompt is None and "negative" in parsed:
                negative_prompt = parsed["negative"]

    if video_prompt is None:
        raise ValueError(f"No video prompt for {shot_id}")
    if input_image is None:
        raise ValueError(f"No input image for {shot_id}")

    if negative_prompt is None:
        negative_prompt = DEFAULT_NEGATIVE

    # 解析 input_image 路径 (可以是相对 assets 的路径)
    img_path = Path(input_image)
    if not img_path.is_absolute():
        img_path = episode_dir.parent / input_image  # 相对 episode 目录
        if not img_path.exists():
            img_path = assets_dir / input_image

    # 拷贝到 ComfyUI input
    comfy_name = f"{shot_id}_input.png"
    shutil.copy2(img_path, COMFYUI_INPUT / comfy_name)

    suffix = f"_{version}" if version else ""
    prefix = f"video/{shot_id}{suffix}"

    print(f"\n{'=' * 60}")
    print(f"  Shot: {shot_id}{suffix}")
    print(f"  Input: {img_path.name}")
    print(f"  Frames: {frames} @ {DEFAULT_FPS}fps = {frames / DEFAULT_FPS:.1f}s")
    print(f"  Seeds: {seed1} / {seed2}")
    print(f"{'=' * 60}")
    print(f"  Prompt: {video_prompt[:100]}...")
    print(f"  Negative: {negative_prompt[:80]}...")

    workflow = build_ltx2_i2v_workflow(
        image_name=comfy_name,
        video_prompt=video_prompt,
        negative_prompt=negative_prompt,
        frame_count=frames,
        seed1=seed1,
        seed2=seed2,
        filename_prefix=prefix,
    )

    prompt_id = queue_prompt(workflow)
    print(f"  queued: {prompt_id}")

    entry = poll_until_done(prompt_id)
    output_path = get_output_video(entry)

    if output_path:
        dest = video_dir / f"{shot_id}.mp4"
        shutil.copy2(output_path, dest)
        print(f"  saved: {dest}")
        return dest
    else:
        raise RuntimeError(f"No video output for {shot_id}")


def main():
    parser = argparse.ArgumentParser(description="生成分镜视频 (LTX-2 I2V)")
    parser.add_argument("episode_id", help="剧集编号, e.g. ep001")
    parser.add_argument("shot_id", help="镜头编号, e.g. S01")
    parser.add_argument(
        "--prompt", type=str, default=None, help="视频提示词 (覆盖 prompt 文件)"
    )
    parser.add_argument("--negative", type=str, default=None, help="负向提示词")
    parser.add_argument("--input-image", type=str, default=None, help="输入图片路径")
    parser.add_argument("--frames", type=int, default=DEFAULT_FRAMES, help="帧数")
    parser.add_argument("--seed1", type=int, default=42, help="Stage 1 seed")
    parser.add_argument("--seed2", type=int, default=420, help="Stage 2 seed")
    parser.add_argument("--version", type=str, default="", help="版本后缀, e.g. v7")
    args = parser.parse_args()

    generate_shot_video(
        args.episode_id,
        args.shot_id,
        video_prompt=args.prompt,
        negative_prompt=args.negative,
        input_image=args.input_image,
        frames=args.frames,
        seed1=args.seed1,
        seed2=args.seed2,
        version=args.version,
    )


if __name__ == "__main__":
    main()
