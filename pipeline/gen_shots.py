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
import json
import argparse
from pathlib import Path

from pipeline.utils import get_episode_dir, PROJECT_ROOT


# Default Claude model for creative tasks
DEFAULT_MODEL = "opus"  # Aliases: "sonnet", "opus", "haiku"


def build_shots_json(
    script_content: str,
    episode_id: str,
    model: str = "opus",
    max_tokens: int = 100000,
    title: str | None = None,
    source: str | None = None,
    locations: dict | None = None,
    characters: dict | None = None,
    props: dict | None = None,
) -> dict:
    """Build complete shots.json structure from screenplay with automatic asset linking.

    Workflow:
    1. Load asset definitions (locations, characters, props)
    2. Pass screenplay + assets to Claude in single call
    3. Claude generates complete shots.json with asset refs (location_ref, character_refs, prop_refs)

    Args:
        script_content: The screenplay text
        episode_id: Episode identifier (e.g. "ep001")
        model: Claude model to use
        max_tokens: Maximum tokens for Claude response
        title: Episode title (optional)
        source: Source description (optional)
        locations: Locations asset definitions dict (optional, auto-loaded if None)
        characters: Characters asset definitions dict (optional, auto-loaded if None)
        props: Props asset definitions dict (optional, auto-loaded if None)

    Returns:
        Complete shots.json data structure with linked assets
    """
    from anthropic import Anthropic

    # 1. Load asset definitions if not provided
    if locations is None or characters is None or props is None:
        loaded_locations, loaded_characters, loaded_props = load_asset_definitions()
        locations = locations or loaded_locations
        characters = characters or loaded_characters
        props = props or loaded_props

    print("\n📖 从剧本生成分镜并关联资产...")

    client = Anthropic()

    # 2. Prepare asset context for Claude
    assets_context = f"""
## 可用的位置资产 (locations)

{json.dumps({k: v.get('zh_name', k) for k, v in locations.items()}, ensure_ascii=False, indent=2)}

## 可用的角色资产 (characters)

{json.dumps({k: v.get('zh_name', k) for k, v in characters.items()}, ensure_ascii=False, indent=2)}

## 可用的道具资产 (props)

{json.dumps({k: v.get('zh_name', k) for k, v in props.items()}, ensure_ascii=False, indent=2)}
"""

    # 3. Create comprehensive prompt for shots generation with asset linking
    title_note = f"\n\n剧集标题：{title}" if title else ""
    source_note = f"\n剧本来源：{source}" if source else ""

    generation_prompt = f"""
你是一个专业的电影分镜规划师。根据以下剧本、可用资产和要求，生成完整的 shots.json 分镜规划。

## 剧本内容
{title_note}{source_note}

{script_content}

{assets_context}

## 任务

为这个剧集生成完整的分镜规划 (shots.json)，包括：

1. **分镜基本信息**
   - shot_id: S01, S02, S03... (按顺序)
   - scene: 场景分组 ID (e.g., "1-1", "1-2")
   - duration_s: 镜头时长（秒）
   - camera: 景别和镜头运动
   - action: 镜头动作描述
   - dialogue: 对白（如有）
   - emotion: 情感基调

2. **提示词**
   - prompt_visual: 详细的 T2I 视觉提示词（用于生成关键帧）
   - prompt_motion: 详细的 I2V 运动提示词（用于生成视频）

3. **资产关联** ⭐ 重要
   - location_ref: 从上面的 locations 中选择最匹配的资产 ID（必填）
   - character_refs: 从上面的 characters 中选择所有出现的角色 ID（数组）
   - prop_refs: 从上面的 props 中选择所有出现的道具 ID（数组）

4. **转场和音效**
   - transition_out: 转场方式 (cut, fade, dissolve 等)
   - transition_duration_s: 转场时长
   - transition_note: 转场说明
   - sfx_bgm: 音效和背景音乐描述

## 输出格式

返回一个完整的 JSON 对象，结构如下：

```json
{{
  "episode": "{episode_id}",
  "total_duration_s": 0,  // 计算所有镜头的时长
  "total_shots": 0,  // 镜头总数
  "format": {{
    "resolution": "1920x1080",
    "aspect_ratio": "16:9",
    "fps": 24
  }},
  "shots": [
    {{
      "shot_id": "S01",
      "scene": "1-1",
      "duration_s": 4,
      "location": "场景描述名称",
      "location_ref": "对应的资产ID",
      "characters": ["角色1", "角色2"],
      "character_refs": ["character_id_1", "character_id_2"],
      "prop_refs": ["prop_id_1"],
      "camera": "景别和镜头运动",
      "action": "镜头动作描述",
      "dialogue": [
        {{
          "character": "角色名",
          "text": "对白文本",
          "emotion": "情感",
          "speed": 1.0
        }}
      ],
      "emotion": "情感基调",
      "prompt_visual": "详细的 T2I 视觉提示词...",
      "prompt_motion": "详细的 I2V 运动提示词...",
      "transition_out": "cut",
      "transition_duration_s": 0,
      "transition_note": "转场说明",
      "sfx_bgm": "音效描述",
      "notes": "补充说明"
    }}
  ]
}}
```

## 关键要求

- ✅ 每个 shot 必须有 location_ref（指向 locations 中的一个资产）
- ✅ 每个 shot 的 character_refs 必须是实际出现的角色
- ✅ 每个 shot 的 prop_refs 包含涉及的道具
- ✅ 提示词要详细、具体、包含美学和情感信息
- ✅ 转场应该根据叙事节奏选择
- ✅ 总时长应该接近 60-90 秒
- ✅ 返回有效的 JSON，无任何额外文本或 Markdown
- ✅ **JSON 格式严格要求**:
  - 所有字符串值中的双引号必须转义为 \"
  - 所有换行符必须转义为 \\n
  - 所有反斜杠必须转义为 \\\\
  - 不能包含任何无效的 JSON 语法

开始生成：
"""

    # 4. Call Claude API with assets context
    # Map model aliases to actual model names
    model_map = {
        "opus": "claude-opus-4-6",
        "sonnet": "claude-sonnet-4-5-20250929",
        "haiku": "claude-haiku-4-5-20251001",
    }
    actual_model = model_map.get(model, "claude-opus-4-6")

    print(f"🤖 调用 Claude ({actual_model}) 进行分镜规划和资产关联...")

    response = client.messages.create(
        model=actual_model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": generation_prompt}],
    )

    response_text = response.content[0].text.strip()

    # 5. Extract JSON from response
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()

    try:
        shots_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON 解析失败: {e}")
        # 显示错误位置周围的上下文
        error_pos = e.pos
        start = max(0, error_pos - 200)
        end = min(len(response_text), error_pos + 200)
        print(f"\n📝 错误位置周围的上下文 (位置 {error_pos}):")
        print("="*60)
        print(response_text[start:end])
        print("="*60)
        print(f"\n完整响应长度: {len(response_text)} 字符")
        raise

    print(f"✓ 成功生成 {len(shots_data.get('shots', []))} 个镜头（已包含资产关联）")

    return shots_data


def read_script(episode_dir: Path) -> str:
    """读取 script.md 内容"""
    script_path = episode_dir / "script.md"
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    with open(script_path, "r", encoding="utf-8") as f:
        return f.read()


def load_asset_definitions() -> tuple[dict, dict, dict]:
    """从资产 JSON 文件中加载位置、角色、道具定义。

    Returns:
        (locations_dict, characters_dict, props_dict)
    """
    locations = {}
    characters = {}
    props = {}

    try:
        locations_path = PROJECT_ROOT / "assets" / "locations" / "locations.json"
        if locations_path.exists():
            with open(locations_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                locations = data.get("locations", {})
    except Exception as e:
        print(f"⚠️  无法加载 locations.json: {e}")

    try:
        characters_path = PROJECT_ROOT / "assets" / "characters" / "characters.json"
        if characters_path.exists():
            with open(characters_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                characters = data.get("characters", {})
    except Exception as e:
        print(f"⚠️  无法加载 characters.json: {e}")

    try:
        props_path = PROJECT_ROOT / "assets" / "props" / "props.json"
        if props_path.exists():
            with open(props_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # props.json 的结构直接是 {prop_key: prop_info, ...}，除了 metadata
                props = {k: v for k, v in data.items() if k != "metadata"}
    except Exception as e:
        print(f"⚠️  无法加载 props.json: {e}")

    return locations, characters, props





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

        # build_shots_json 内部处理: 解析脚本 + 加载资产 + 在一次API调用中生成包含资产关联的完整shots.json
        shots_data = build_shots_json(
            script_content=script_content,
            episode_id=args.episode_id,
            model=args.model,
            max_tokens=20000,
        )
        print(f"✓ 解析成功，得到 {len(shots_data['shots'])} 个镜头")
        print(f"✓ 自动关联了资产定义（location_ref, character_refs 等）")

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
