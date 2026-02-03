"""
ComfyUI API 封装 — 伏羲纪元角色资产生成管线

封装 ComfyUI HTTP API:
- 构建 Flux 2 Dev / Flux 1 文生图工作流 (API format JSON)
- 提交 prompt、轮询状态、下载生成图片

Flux 2 节点链: UNETLoader → CLIPLoader → VAELoader → EmptyLatentImage
               → CLIPTextEncode → KSampler → VAEDecode → SaveImage
  (单文本编码器 Mistral，无需负向 prompt，CFG=1.0)

Flux 1 节点链: UNETLoader → DualCLIPLoader → VAELoader → EmptyLatentImage
               → CLIPTextEncode ×2 → KSampler → VAEDecode → SaveImage
"""

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path


COMFYUI_URL = "http://127.0.0.1:8188"

# ---------------------------------------------------------------------------
# Flux 2 Dev 默认参数
# ---------------------------------------------------------------------------
FLUX2_DEFAULTS = {
    "width": 1344,
    "height": 768,
    "steps": 20,
    "cfg": 1.0,  # Flux 2: guidance baked into model
    "sampler_name": "euler",
    "scheduler": "simple",
    "denoise": 1.0,
    "batch_size": 1,
    # 模型文件名
    "unet": "flux2_dev_fp8mixed.safetensors",
    "clip": "mistral_3_small_flux2_fp4_mixed.safetensors",
    "vae": "flux2-vae.safetensors",
}

# ---------------------------------------------------------------------------
# Flux 1 Dev 默认参数 (保留向后兼容)
# ---------------------------------------------------------------------------
FLUX1_DEFAULTS = {
    "width": 1344,
    "height": 768,
    "steps": 20,
    "cfg": 3.5,
    "sampler_name": "euler",
    "scheduler": "simple",
    "denoise": 1.0,
    "batch_size": 1,
    "unet": "flux1-dev-kontext_fp8_scaled.safetensors",
    "clip_l": "clip_l.safetensors",
    "clip_t5": "t5xxl_fp8_e4m3fn.safetensors",
    "vae": "ae.safetensors",
}


# ---------------------------------------------------------------------------
# 工作流构建
# ---------------------------------------------------------------------------


def build_flux2_txt2img_workflow(
    positive_prompt: str,
    seed: int = 0,
    filename_prefix: str = "comfyui",
    **overrides,
) -> dict:
    """构建 Flux 2 Dev 文生图工作流 JSON (ComfyUI API format).

    Flux 2 使用单 CLIPLoader (Mistral 3)，无需负向 prompt，CFG=1.0。
    """
    p = {**FLUX2_DEFAULTS, **overrides}

    workflow = {
        # 1 — UNET Loader (Flux 2)
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": p["unet"],
                "weight_dtype": "fp8_e4m3fn",
            },
        },
        # 2 — CLIP Loader (single Mistral encoder)
        "2": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": p["clip"],
                "type": "flux2",
            },
        },
        # 3 — VAE Loader
        "3": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": p["vae"],
            },
        },
        # 4 — Empty Latent Image
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": p["width"],
                "height": p["height"],
                "batch_size": p["batch_size"],
            },
        },
        # 5 — CLIP Text Encode (positive)
        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": positive_prompt,
                "clip": ["2", 0],
            },
        },
        # 6 — CLIP Text Encode (empty conditioning for negative)
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "",
                "clip": ["2", 0],
            },
        },
        # 7 — KSampler
        "7": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["5", 0],
                "negative": ["6", 0],
                "latent_image": ["4", 0],
                "seed": seed,
                "steps": p["steps"],
                "cfg": p["cfg"],
                "sampler_name": p["sampler_name"],
                "scheduler": p["scheduler"],
                "denoise": p["denoise"],
            },
        },
        # 8 — VAE Decode
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["7", 0],
                "vae": ["3", 0],
            },
        },
        # 9 — Save Image
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["8", 0],
                "filename_prefix": filename_prefix,
            },
        },
    }
    return workflow


def build_flux1_txt2img_workflow(
    positive_prompt: str,
    negative_prompt: str,
    seed: int = 0,
    filename_prefix: str = "comfyui",
    **overrides,
) -> dict:
    """构建 Flux 1 Dev 文生图工作流 JSON (保留向后兼容)."""
    p = {**FLUX1_DEFAULTS, **overrides}

    workflow = {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": p["unet"],
                "weight_dtype": "fp8_e4m3fn",
            },
        },
        "2": {
            "class_type": "DualCLIPLoader",
            "inputs": {
                "clip_name1": p["clip_l"],
                "clip_name2": p["clip_t5"],
                "type": "flux",
            },
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": p["vae"]},
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": p["width"],
                "height": p["height"],
                "batch_size": p["batch_size"],
            },
        },
        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": positive_prompt, "clip": ["2", 0]},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative_prompt, "clip": ["2", 0]},
        },
        "7": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["5", 0],
                "negative": ["6", 0],
                "latent_image": ["4", 0],
                "seed": seed,
                "steps": p["steps"],
                "cfg": p["cfg"],
                "sampler_name": p["sampler_name"],
                "scheduler": p["scheduler"],
                "denoise": p["denoise"],
            },
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["7", 0], "vae": ["3", 0]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"images": ["8", 0], "filename_prefix": filename_prefix},
        },
    }
    return workflow


# 默认使用 Flux 2
build_flux_txt2img_workflow = build_flux2_txt2img_workflow


# ---------------------------------------------------------------------------
# ComfyUI HTTP API
# ---------------------------------------------------------------------------


def queue_prompt(workflow: dict, *, base_url: str = COMFYUI_URL) -> str:
    """Submit a workflow to ComfyUI. Returns the prompt_id."""
    payload = json.dumps({"prompt": workflow}).encode()
    req = urllib.request.Request(
        f"{base_url}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    return result["prompt_id"]


def poll_until_done(
    prompt_id: str,
    *,
    base_url: str = COMFYUI_URL,
    poll_interval: float = 2.0,
    timeout: float = 600.0,
) -> dict:
    """Poll /history/{prompt_id} until the job finishes.

    Returns the history entry dict for this prompt_id.
    Raises TimeoutError if *timeout* seconds elapse.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            url = f"{base_url}/history/{prompt_id}"
            with urllib.request.urlopen(url, timeout=30) as resp:
                history = json.loads(resp.read())
        except (ConnectionError, OSError, urllib.error.URLError):
            # Transient connection errors while GPU is busy loading models
            time.sleep(poll_interval * 2)
            continue
        if prompt_id in history:
            entry = history[prompt_id]
            status = entry.get("status", {})
            if status.get("status_str") == "error":
                msgs = status.get("messages", [])
                err_msg = "ComfyUI execution error"
                for msg in msgs:
                    if msg[0] == "execution_error":
                        err_msg = msg[1].get("exception_message", err_msg)
                        break
                raise RuntimeError(f"ComfyUI error: {err_msg}")
            return entry
        time.sleep(poll_interval)
    raise TimeoutError(f"ComfyUI job {prompt_id} did not finish within {timeout}s")


def get_output_images(history_entry: dict) -> list[dict]:
    """Extract image info dicts from a history entry.

    Each dict has keys: ``filename``, ``subfolder``, ``type``.
    """
    images = []
    for node_output in history_entry.get("outputs", {}).values():
        for img in node_output.get("images", []):
            images.append(img)
    return images


def download_image(
    image_info: dict,
    dest_path: Path,
    *,
    base_url: str = COMFYUI_URL,
) -> Path:
    """Download a generated image from ComfyUI to *dest_path*."""
    params = urllib.parse.urlencode(
        {
            "filename": image_info["filename"],
            "subfolder": image_info.get("subfolder", ""),
            "type": image_info.get("type", "output"),
        }
    )
    url = f"{base_url}/view?{params}"
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, str(dest_path))
    return dest_path


def generate_image(
    positive_prompt: str,
    dest_path: Path,
    *,
    seed: int = 0,
    filename_prefix: str = "comfyui",
    base_url: str = COMFYUI_URL,
    poll_interval: float = 2.0,
    timeout: float = 600.0,
    **workflow_overrides,
) -> Path:
    """One-shot helper: build workflow → queue → poll → download.

    Uses Flux 2 Dev workflow (no negative prompt needed).
    Returns the local path of the saved image.
    """
    workflow = build_flux2_txt2img_workflow(
        positive_prompt,
        seed=seed,
        filename_prefix=filename_prefix,
        **workflow_overrides,
    )
    prompt_id = queue_prompt(workflow, base_url=base_url)
    print(f"  queued prompt {prompt_id}, waiting...")
    entry = poll_until_done(
        prompt_id,
        base_url=base_url,
        poll_interval=poll_interval,
        timeout=timeout,
    )
    images = get_output_images(entry)
    if not images:
        raise RuntimeError(f"No images returned for prompt {prompt_id}")
    return download_image(images[0], dest_path, base_url=base_url)
