#!/usr/bin/env python3
"""
从 script.md 解析生成 shots.json 的分镜规划脚本

使用 Claude（最强的创意LLM）分析脚本，生成结构化的镜头规划。

通过 creative_toolkit 调用 LLM 功能，确保所有模型调用集中在 toolkit 中。

用法:
    python -m pipeline.gen_shots ep001
    python -m pipeline.gen_shots ep001 --interactive  # 交互模式验证
    python -m pipeline.gen_shots ep001 --auto          # 完全自动，无交互
"""

import sys
import argparse
from pathlib import Path

from creative_toolkit.storyboard import (
    parse_script_to_shots,
    build_shots_json as toolkit_build_shots_json,
)
from pipeline.utils import get_episode_dir


# Default Claude model for creative tasks
DEFAULT_MODEL = "opus"  # Aliases: "sonnet", "opus", "haiku"


def build_shots_json(
    script_content: str,
    episode_id: str,
    model: str = "opus",
    max_tokens: int = 50000,
    title: str | None = None,
    source: str | None = None,
) -> dict:
    """Build complete shots.json structure from screenplay.

    This encapsulates the full workflow:
    1. Parse screenplay to extract shot planning using Claude
    2. Build complete shots.json structure with metadata and scene grouping

    Args:
        script_content: The screenplay text
        episode_id: Episode identifier (e.g. "ep001")
        model: Claude model to use
        max_tokens: Maximum tokens for Claude response
        title: Episode title (optional)
        source: Source description (optional)

    Returns:
        Complete shots.json data structure
    """
    # 1. Parse screenplay to get shots list
    shots_list = parse_script_to_shots(
        script_content=script_content,
        model=model,
        max_tokens=max_tokens,
    )

    # 2. Build complete shots.json structure using toolkit
    shots_data = toolkit_build_shots_json(
        shots_list=shots_list,
        episode_id=episode_id,
        title=title,
        source=source,
    )

    return shots_data


def read_script(episode_dir: Path) -> str:
    """读取 script.md 内容"""
    script_path = episode_dir / "script.md"
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    with open(script_path, "r", encoding="utf-8") as f:
        return f.read()


def interactive_review(shots_data: dict) -> dict:
    """交互式审阅和编辑"""
    print("\n" + "=" * 60)
    print("📋 分镜审阅 (交互模式)")
    print("=" * 60)

    shots = shots_data["shots"]
    total_duration = sum(s.get("duration_s", 3) for s in shots)

    print(f"\n✓ 生成了 {len(shots)} 个镜头")
    print(f"✓ 总时长: {total_duration:.1f}秒")
    print()

    for i, shot in enumerate(shots, 1):
        print(f"\n[{i}/{len(shots)}] {shot.get('shot_id', '?')}")
        print(f"  场景: {shot.get('scene', '?')}")
        print(f"  时长: {shot.get('duration_s', 3)}s")
        print(f"  地点: {shot.get('location', '?')}")
        print(f"  景别: {shot.get('camera', '?')}")
        print(f"  情感: {shot.get('emotion', '?')}")

        response = input("  编辑此镜头? (y/n/skip): ").strip().lower()
        if response == "y":
            print("\n  可编辑的字段: duration_s, location, camera, action, emotion, dialogue")
            field = input("  要编辑的字段: ").strip()
            if field in shot:
                new_value = input(f"  新值 (当前: {shot[field]}): ").strip()
                shot[field] = new_value
                print(f"  ✓ 已更新 {field}")
        elif response == "skip":
            continue

    return shots_data


def save_shots_json(shots_data: dict, episode_dir: Path) -> Path:
    """保存shots.json

    Args:
        shots_data: 完整的shots.json数据结构（已调用build_shots_json生成）
        episode_dir: 剧集目录
    """
    import json

    output_path = episode_dir / "shots.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(shots_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 保存完成: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="从 script.md 生成 shots.json 分镜规划"
    )
    parser.add_argument("episode_id", help="剧集编号 (如 ep001)")
    parser.add_argument(
        "--interactive",
        action="store_true",
        default=True,
        help="交互模式，逐个审阅镜头 (默认)",
    )
    parser.add_argument(
        "--auto", action="store_true", help="自动模式，无交互直接保存"
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"使用的Claude模型 (默认: {DEFAULT_MODEL})",
    )

    args = parser.parse_args()

    try:
        # 获取剧集目录
        ep_dir = get_episode_dir(args.episode_id)
        print(f"\n📂 剧集目录: {ep_dir}")

        # 读取脚本
        print("\n📖 读取脚本...")
        script_content = read_script(ep_dir)
        print(f"✓ 脚本大小: {len(script_content)} 字符")

        # 调用 creative_toolkit 的 LLM 函数生成分镜
        print("\n" + "=" * 60)
        print(f"🤖 调用Claude-{args.model}进行分镜规划...")
        print("=" * 60)

        # build_shots_json 内部处理: 解析脚本 + 构建完整结构
        shots_data = build_shots_json(
            script_content=script_content,
            episode_id=args.episode_id,
            model=args.model,
            max_tokens=50000,
        )
        print(f"✓ 解析成功，得到 {len(shots_data['shots'])} 个镜头")

        # 交互审阅（除非--auto）
        if args.auto:
            print("\n⚡ 自动模式，跳过交互审阅")
        else:
            shots_data = interactive_review(shots_data)

        # 保存
        save_shots_json(shots_data, ep_dir)

        print(f"\n{'=' * 60}")
        print(f"✨ 分镜规划完成!")
        print(f"{'=' * 60}")
        print(f"\n后续步骤:")
        print(f"  1. 审阅 {ep_dir}/shots.json")
        print(f"  2. 手工调整 prompt_visual 和 prompt_motion")
        print(f"  3. 运行: python -m pipeline.gen_keyframes {args.episode_id}")

    except FileNotFoundError as e:
        print(f"\n❌ 文件错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
