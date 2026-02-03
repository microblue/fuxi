"""
角色参考图批量生成 — 伏羲纪元 EP001

为每个角色生成 4 张候选定妆参考图 (不同 seed)，
输出到 episodes/ep001/assets/characters/{name}/ 目录。

用法:
    python -m pipeline.generate_character_refs                # 全部角色
    python -m pipeline.generate_character_refs xihe fuxi      # 指定角色
    python -m pipeline.generate_character_refs --seeds 100,200,300,400
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass, field
from pathlib import Path

from pipeline.comfyui_api import generate_image
from pipeline.utils import PROJECT_ROOT

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

EPISODE_ID = "ep001"
CHARACTERS_DIR = PROJECT_ROOT / "episodes" / EPISODE_ID / "assets" / "characters"

import json as _json


def _json_prompt(data: dict) -> str:
    """将结构化 dict 转为 FLUX.2 JSON prompt 字符串。"""
    return _json.dumps(data, ensure_ascii=False)


NUM_CANDIDATES = 4

# ---------------------------------------------------------------------------
# 角色定义
# ---------------------------------------------------------------------------


@dataclass
class CharacterSpec:
    """一个角色的生成规格。"""

    name: str  # 目录名 (英文)
    label: str  # 显示名 (中文)
    views: list[dict] = field(default_factory=list)
    # 每个 view: {"tag": str, "positive": str}


CHARACTERS: dict[str, CharacterSpec] = {}


def _register(spec: CharacterSpec) -> CharacterSpec:
    CHARACTERS[spec.name] = spec
    return spec


# --- 羲和 ---
_register(
    CharacterSpec(
        name="xihe",
        label="羲和（伏羲前世）",
        views=[
            {
                "tag": "body",
                "positive": _json_prompt(
                    {
                        "scene": "character reference sheet, full body front view, head to toe, neutral gray background",
                        "subjects": [
                            {
                                "description": (
                                    "East Asian man age 30, Chinese facial features, deep-set mature "
                                    "refined face, high cheekbones, angular sharp jawline, short black "
                                    "hair neatly swept back, tall scholarly build, golden ornate markings "
                                    "around left eye"
                                ),
                                "outfit": (
                                    "floor-length flowing robe made entirely of structured light, "
                                    "semi-transparent luminous fabric with golden circuit data patterns "
                                    "streaming and pulsing across surface like a living hologram, "
                                    "futuristic sci-fi alien civilization robe, NOT traditional clothing, "
                                    "the robe itself glows and emits soft light, advanced technology "
                                    "woven into every thread"
                                ),
                                "pose": "standing upright, composed dignified posture, arms at sides",
                                "temperament": "composed, wise, gentle resolve",
                            }
                        ],
                        "style": "photorealistic, cinematic",
                        "lighting": "studio lighting, rim light",
                        "camera": {
                            "angle": "front view",
                            "lens": "85mm",
                            "depth_of_field": "shallow",
                        },
                    }
                ),
            },
            {
                "tag": "face",
                "positive": _json_prompt(
                    {
                        "scene": "character portrait, face close-up, neutral gray background",
                        "subjects": [
                            {
                                "description": (
                                    "East Asian man age 30, Chinese facial features, deep-set mature "
                                    "refined face, high cheekbones, angular sharp jawline, short black "
                                    "hair neatly swept back, golden ornate markings around left eye, "
                                    "composed wise expression"
                                ),
                                "outfit": "high collar of luminous flowing robe made of structured light with golden circuit patterns, futuristic sci-fi",
                            }
                        ],
                        "style": "photorealistic, cinematic, high detail",
                        "lighting": "studio lighting, gentle fill light",
                        "camera": {
                            "angle": "front view",
                            "lens": "85mm f/1.8",
                            "depth_of_field": "shallow",
                        },
                    }
                ),
            },
        ],
    )
)

# --- 少年伏羲 (觉醒前) ---
_register(
    CharacterSpec(
        name="fuxi",
        label="少年伏羲",
        views=[
            {
                "tag": "body",
                "positive": _json_prompt(
                    {
                        "scene": "character reference sheet, full body front view, head to toe, neutral gray background",
                        "subjects": [
                            {
                                "description": (
                                    "East Asian teenage boy age 16, Chinese facial features, angular face "
                                    "with lingering boyishness, high cheekbones, long black hair half-tied "
                                    "with upper portion in topknot and lower half loose and messy, lean agile "
                                    "hunter build 168cm, both eyes normal black"
                                ),
                                "outfit": (
                                    "crude dark brown animal hide short tunic exposing right arm and shoulder, "
                                    "rough rope belt at waist, barefoot, primitive tribal appearance, "
                                    "no modern elements"
                                ),
                                "pose": "standing, alert hunter stance, weight on one leg",
                                "temperament": "wild, naive, stubborn, youthful energy",
                            }
                        ],
                        "style": "photorealistic, cinematic",
                        "lighting": "studio lighting",
                        "camera": {
                            "angle": "front view",
                            "lens": "85mm",
                            "depth_of_field": "shallow",
                        },
                    }
                ),
            },
            {
                "tag": "face_awakened",
                "positive": _json_prompt(
                    {
                        "scene": "character portrait, face close-up, neutral gray background",
                        "subjects": [
                            {
                                "description": (
                                    "East Asian teenage boy age 16, Chinese facial features, angular face "
                                    "with lingering boyishness, high cheekbones, long black hair half-tied, "
                                    "left eye dark golden with tiny glowing bagua trigram pattern inside iris, "
                                    "right eye normal black, intense determined gaze, faint golden glow "
                                    "around left eye"
                                ),
                            }
                        ],
                        "style": "photorealistic, cinematic, high detail",
                        "lighting": "studio lighting, dramatic accent light on left eye",
                        "camera": {
                            "angle": "front view",
                            "lens": "85mm f/1.8",
                            "depth_of_field": "shallow",
                        },
                    }
                ),
            },
        ],
    )
)

# --- 女娲 ---
_register(
    CharacterSpec(
        name="nvwa",
        label="女娲",
        views=[
            {
                "tag": "body",
                "positive": _json_prompt(
                    {
                        "scene": "character reference sheet, full body front view, head to toe, neutral gray background",
                        "subjects": [
                            {
                                "description": (
                                    "East Asian young woman age 18, Chinese facial features, oval face, "
                                    "elongated almond eyes, wild natural beauty, long dark brown hair in "
                                    "side braid woven with green vine decorations, slender agile archer "
                                    "build 165cm, extremely long elegant legs"
                                ),
                                "outfit": (
                                    "emerald green leaf-woven armor covering shoulders and torso, "
                                    "vine arm guards wrapped around forearms, white bone bow strapped "
                                    "on back, bone arrow quiver at waist"
                                ),
                                "pose": "standing with legs crossed elegantly, one foot slightly forward, graceful stance",
                                "temperament": "wild, agile, decisive, guardian, vitality",
                            }
                        ],
                        "style": "photorealistic, cinematic",
                        "lighting": "studio lighting",
                        "camera": {
                            "angle": "front view",
                            "lens": "85mm",
                            "depth_of_field": "shallow",
                        },
                    }
                ),
            },
        ],
    )
)

# --- 熵单位 ---
_register(
    CharacterSpec(
        name="entropy_unit",
        label="熵单位",
        views=[
            {
                "tag": "front",
                "positive": _json_prompt(
                    {
                        "scene": "concept art, single entity floating in dark void",
                        "subjects": [
                            {
                                "description": (
                                    "pale white octahedron geometric entity, 2-3x human size, "
                                    "glowing red cracks pulsing across entire surface, floating silently, "
                                    "dark black data tendrils extending from vertices, cold mechanical "
                                    "alien presence, absolutely no face or organic features"
                                ),
                            }
                        ],
                        "style": "3D rendered, photorealistic, sci-fi horror aesthetic",
                        "color_palette": ["#e0e0e0", "#ff1a1a", "#0a0a0a"],
                        "lighting": "red glow from cracks as sole light source, dark ambient",
                    }
                ),
            },
        ],
    )
)

# --- 华胥氏族猎人 ---
_register(
    CharacterSpec(
        name="hunter",
        label="华胥氏族猎人",
        views=[
            {
                "tag": "body",
                "positive": _json_prompt(
                    {
                        "scene": "character reference sheet, full body front view, head to toe, neutral gray background",
                        "subjects": [
                            {
                                "description": (
                                    "East Asian adult male age 25, Chinese facial features, rugged face, "
                                    "sun-tanned bronze skin, muscular stocky build, rough short black hair"
                                ),
                                "outfit": (
                                    "crude dark brown animal hide clothing with unfinished edges, "
                                    "leather strap across chest, leather ankle wraps, carrying bone-tipped "
                                    "spear in right hand"
                                ),
                                "pose": "standing upright, spear held vertically, warrior stance",
                                "temperament": "rugged, loyal, brave",
                            }
                        ],
                        "style": "photorealistic, cinematic",
                        "lighting": "studio lighting",
                        "camera": {
                            "angle": "front view",
                            "lens": "85mm",
                            "depth_of_field": "shallow",
                        },
                    }
                ),
            },
        ],
    )
)


# ---------------------------------------------------------------------------
# 生成逻辑
# ---------------------------------------------------------------------------


def generate_character(
    spec: CharacterSpec,
    seeds: list[int],
    *,
    dry_run: bool = False,
) -> list[Path]:
    """为一个角色的所有 views 生成候选图。返回所有生成文件路径。"""
    out_dir = CHARACTERS_DIR / spec.name
    out_dir.mkdir(parents=True, exist_ok=True)

    generated: list[Path] = []

    for view in spec.views:
        tag = view["tag"]
        positive = view["positive"]

        for i, seed in enumerate(seeds, start=1):
            filename = f"ref_{tag}_{i:03d}.png"
            dest = out_dir / filename

            print(f"[{spec.label}] {tag} #{i}  seed={seed}  → {dest}")

            if dry_run:
                print("  (dry run, skipped)")
                generated.append(dest)
                continue

            path = generate_image(
                positive_prompt=positive,
                dest_path=dest,
                seed=seed,
                filename_prefix=f"{spec.name}_{tag}",
            )
            print(f"  ✓ saved {path}")
            generated.append(path)

    return generated


def run(
    character_names: list[str] | None = None,
    seeds: list[int] | None = None,
    dry_run: bool = False,
) -> dict[str, list[Path]]:
    """主入口。返回 {角色名: [生成文件路径]}。"""
    if seeds is None:
        seeds = [random.randint(0, 2**32 - 1) for _ in range(NUM_CANDIDATES)]

    targets = character_names or list(CHARACTERS.keys())

    results: dict[str, list[Path]] = {}
    for name in targets:
        if name not in CHARACTERS:
            print(f"WARNING: unknown character '{name}', skipping")
            continue
        spec = CHARACTERS[name]
        print(f"\n{'=' * 60}")
        print(f"  角色: {spec.label} ({spec.name})")
        print(f"  Seeds: {seeds}")
        print(f"{'=' * 60}")
        results[name] = generate_character(spec, seeds, dry_run=dry_run)

    print(f"\n--- 生成完毕 ---")
    total = sum(len(v) for v in results.values())
    print(f"共生成 {total} 张候选图")
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="为 EP001 角色生成定妆参考图候选",
    )
    parser.add_argument(
        "characters",
        nargs="*",
        help=f"要生成的角色名 (可选: {', '.join(CHARACTERS.keys())}). 不指定则全部生成。",
    )
    parser.add_argument(
        "--seeds",
        type=str,
        default=None,
        help="逗号分隔的 seed 列表 (如 100,200,300,400). 默认随机。",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅打印要生成的内容，不实际调用 ComfyUI。",
    )
    args = parser.parse_args()

    seeds = None
    if args.seeds:
        seeds = [int(s.strip()) for s in args.seeds.split(",")]

    run(
        character_names=args.characters or None,
        seeds=seeds,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
