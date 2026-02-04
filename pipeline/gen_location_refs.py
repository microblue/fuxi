"""
场景参考图批量生成 — 伏羲纪元 EP001

为每个场景的每种状态生成 4 张候选图 (不同 seed)，
输出到 episodes/ep001/assets/locations/{name}/ 目录。

用法:
    pixi run python -m pipeline.generate_location_refs
    pixi run python -m pipeline.generate_location_refs lingzi_normal swamp_storm
    pixi run python -m pipeline.generate_location_refs --seeds 100,200,300,400
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
LOCATIONS_DIR = PROJECT_ROOT / "episodes" / EPISODE_ID / "assets" / "locations"

# 横屏短剧统一用 16:9 横屏
IMG_W, IMG_H = 1344, 768  # 16:9 横屏

NUM_CANDIDATES = 4

STYLE_PREFIX = (
    "cinematic film still, photorealistic, movie quality lighting, "
    "shallow depth of field, epic atmosphere, high detail"
)

# ---------------------------------------------------------------------------
# 场景定义
# ---------------------------------------------------------------------------


@dataclass
class LocationSpec:
    name: str  # 目录名
    label: str  # 显示名
    views: list[dict] = field(default_factory=list)
    # 每个 view: {"tag": str, "positive": str}


LOCATIONS: dict[str, LocationSpec] = {}


def _register(spec: LocationSpec) -> LocationSpec:
    LOCATIONS[spec.name] = spec
    return spec


# --- 灵子文明首都 (正常状态) ---
_register(
    LocationSpec(
        name="lingzi_normal",
        label="灵子文明首都·正常",
        views=[
            {
                "tag": "city",
                "positive": (
                    f"{STYLE_PREFIX}, 16:9 horizontal framing, breathtaking futuristic city built "
                    "entirely of light, luminous crystalline architecture soaring upward, rivers "
                    "of golden-white data flowing between towers, central spire dominating skyline, "
                    "warm golden-white illumination, advanced alien civilization at peak technology, "
                    "looking up from street level, epic vertical scale, no people"
                ),
            },
        ],
    )
)

# --- 灵子文明首都 (毁灭状态) ---
_register(
    LocationSpec(
        name="lingzi_destruction",
        label="灵子文明首都·毁灭",
        views=[
            {
                "tag": "collapse",
                "positive": (
                    f"{STYLE_PREFIX}, 16:9 horizontal framing, futuristic light city collapsing, "
                    "all light sources glitching and stuttering, red alarm flashes, data streams "
                    "fragmenting and breaking apart, buildings flickering and dying, city-wide "
                    "system failure, cold silver-blue light replacing warm gold, vertical pillars "
                    "of failing light, epic destruction from below, ominous atmosphere"
                ),
            },
        ],
    )
)

# --- 火种发射 ---
_register(
    LocationSpec(
        name="lingzi_fireseed",
        label="灵子文明·火种发射",
        views=[
            {
                "tag": "pillar",
                "positive": (
                    f"{STYLE_PREFIX}, 16:9 horizontal framing, massive golden-white light pillar "
                    "erupting from center of futuristic city, pillar reaching into sky "
                    "fragmenting into billions of tiny light points scattering into cosmos "
                    "like dandelion seeds, city buildings dimming around the pillar, "
                    "cosmic scale event, epic sacrifice moment, golden radiance"
                ),
            },
        ],
    )
)

# --- 原始沼泽 (暴雨夜) ---
_register(
    LocationSpec(
        name="swamp_storm",
        label="原始沼泽·暴雨夜",
        views=[
            {
                "tag": "storm",
                "positive": (
                    f"{STYLE_PREFIX}, 16:9 horizontal framing, primordial ancient swamp at night, "
                    "torrential rain falling, dark stormy sky with dramatic lightning illumination, "
                    "twisted ancient trees framing foreground, murky shallow water reflecting "
                    "lightning below, gnarled roots, deep shadows, raw untamed wilderness, "
                    "dramatic chiaroscuro lighting, primal atmosphere, no people"
                ),
            },
        ],
    )
)

# --- 沼泽 + 火种坠落漩涡 ---
_register(
    LocationSpec(
        name="swamp_vortex",
        label="沼泽·火种坠落漩涡",
        views=[
            {
                "tag": "impact",
                "positive": (
                    f"{STYLE_PREFIX}, 16:9 horizontal framing, dark primordial swamp at night, "
                    "silver-blue geometric light streams tearing through stormy sky, structured "
                    "energy falling like cosmic rain, glowing silver-blue vortex forming in "
                    "swamp water at center, translucent crystal floating at vortex center "
                    "containing faint golden patterns, rain illuminated by silver-blue light, "
                    "otherworldly impact event in primitive landscape"
                ),
            },
        ],
    )
)

# --- 沼泽 + 熵单位降临 ---
_register(
    LocationSpec(
        name="swamp_entropy",
        label="沼泽·熵单位降临",
        views=[
            {
                "tag": "arrival",
                "positive": (
                    f"{STYLE_PREFIX}, 16:9 horizontal framing, dark swamp at night, "
                    "sky unnaturally darkened beyond normal storm, three pale white octahedron "
                    "geometric entities descending from sky in triangle formation, glowing red "
                    "cracks on their surfaces providing sole light source, pulsing red rhythm, "
                    "cold alien menace, primitive swamp below, sci-fi horror atmosphere, "
                    "ominous invasion"
                ),
            },
        ],
    )
)

# --- 远处山崖 (女娲登场) ---
_register(
    LocationSpec(
        name="cliff_nvwa",
        label="远山崖·女娲登场点",
        views=[
            {
                "tag": "cliff",
                "positive": (
                    f"{STYLE_PREFIX}, 16:9 horizontal framing, dramatic rocky cliff edge "
                    "overlooking dark swamp far below, stormy night, lightning flash revealing "
                    "cliff silhouette, rain-soaked rocks, wild vegetation clinging to cliff face, "
                    "vast depth between cliff top and swamp below, epic dramatic angle, "
                    "archer vantage point, no people"
                ),
            },
        ],
    )
)


# ---------------------------------------------------------------------------
# 生成逻辑
# ---------------------------------------------------------------------------


def generate_location(
    spec: LocationSpec,
    seeds: list[int],
    *,
    dry_run: bool = False,
) -> list[Path]:
    out_dir = LOCATIONS_DIR / spec.name
    out_dir.mkdir(parents=True, exist_ok=True)

    generated: list[Path] = []

    for view in spec.views:
        tag = view["tag"]
        positive = view["positive"]

        for i, seed in enumerate(seeds, start=1):
            filename = f"ref_{tag}_{i:03d}.png"
            dest = out_dir / filename

            print(f"[{spec.label}] {tag} #{i}  seed={seed}  {IMG_W}x{IMG_H}  → {dest}")

            if dry_run:
                print("  (dry run, skipped)")
                generated.append(dest)
                continue

            path = generate_image(
                positive_prompt=positive,
                dest_path=dest,
                seed=seed,
                filename_prefix=f"loc_{spec.name}_{tag}",
                width=IMG_W,
                height=IMG_H,
            )
            print(f"  saved {path}")
            generated.append(path)

    return generated


def run(
    location_names: list[str] | None = None,
    seeds: list[int] | None = None,
    dry_run: bool = False,
) -> dict[str, list[Path]]:
    if seeds is None:
        seeds = [random.randint(0, 2**32 - 1) for _ in range(NUM_CANDIDATES)]

    targets = location_names or list(LOCATIONS.keys())

    results: dict[str, list[Path]] = {}
    for name in targets:
        if name not in LOCATIONS:
            print(f"WARNING: unknown location '{name}', skipping")
            continue
        spec = LOCATIONS[name]
        print(f"\n{'=' * 60}")
        print(f"  场景: {spec.label} ({spec.name})")
        print(f"  Seeds: {seeds}")
        print(f"{'=' * 60}")
        results[name] = generate_location(spec, seeds, dry_run=dry_run)

    print(f"\n--- 生成完毕 ---")
    total = sum(len(v) for v in results.values())
    print(f"共生成 {total} 张场景候选图")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="为 EP001 场景生成参考图候选",
    )
    parser.add_argument(
        "locations",
        nargs="*",
        help=f"要生成的场景名 (可选: {', '.join(LOCATIONS.keys())}). 不指定则全部生成。",
    )
    parser.add_argument(
        "--seeds",
        type=str,
        default=None,
        help="逗号分隔的 seed 列表. 默认随机。",
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
        location_names=args.locations or None,
        seeds=seeds,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
