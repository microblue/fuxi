#!/usr/bin/env python3
"""
资产定义生成器 — 从 script.md 自动提取并生成资产库

功能：
  1. 从剧本中提取所有出现的场景/地点，生成 locations.json
  2. 从剧本中提取所有角色，生成 characters.json
  3. 从剧本中提取所有道具/物品，生成 props.json

使用 Claude LLM 进行智能提取，确保结果准确和完整。

用法:
    python -m pipeline.gen_assets_json ep001                    # 生成或更新资产定义
    python -m pipeline.gen_assets_json ep001 --force            # 强制覆盖现有文件
    python -m pipeline.gen_assets_json ep001 --merge            # 与现有文件合并
"""

import sys
import json
import argparse
from pathlib import Path

from anthropic import Anthropic
from pipeline.utils import get_episode_dir, PROJECT_ROOT


DEFAULT_MODEL = "claude-opus-4-6"


def read_script(episode_dir: Path) -> str:
    """读取 script.md 内容"""
    script_path = episode_dir / "script.md"
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    with open(script_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_assets_from_script(
    script_content: str,
    model: str = "claude-opus-4-6",
) -> dict:
    """使用 Claude API 从剧本中提取资产信息

    Args:
        script_content: 剧本文本内容
        model: Claude 模型名称

    Returns:
        {
            "locations": {...},
            "characters": {...},
            "props": {...}
        }
    """
    print("\n🤖 调用 Claude 进行资产提取...")

    client = Anthropic()

    extraction_prompt = f"""
请从以下剧本中提取资产定义信息，返回结构化的 JSON 格式。

## 任务

从剧本中识别并提取：
1. **locations** - 所有出现的场景/地点（仅静态地理/环境信息）
2. **characters** - 所有角色的**静态全局属性**（不包含剧情相关的动态变化）
3. **props** - 所有出现的道具/物品（仅静态描述）

## 关键说明

### Characters 提取规则（重要）
提取**角色的静态全局属性**，包括：
- ✓ 基本身份信息（名字、年龄、社会身份）
- ✓ 基本外貌特征（身高、体型、肤色等）
- ✓ 基本服装风格（通常穿着、民族服饰等）
- ✓ 核心性格特质（勇敢、聪明等相对不变的特征）
- ✓ 标志性的视觉特征（例如：天生的疤痕、纹身、标志性发型等）

**不应该包含**（排除剧情相关的动态变化）：
- ✗ 因剧情发展而改变的特征（例如："后来眼睛变成了金色"）
- ✗ 在故事中获得的能力（例如："获得了代码视觉能力"）
- ✗ 故事中的行为和动作（例如："射出骨箭"、"操控数据流"）
- ✗ 故事中的情感变化（例如："从恐惧到勇敢的转变"）
- ✗ 命运相关的信息（例如："最后身体消散"）

## 剧本内容

{script_content}

## 输出格式

返回纯 JSON（无额外文本），包含以下结构：

```json
{{
  "locations": {{
    "location_id_1": {{
      "zh_name": "中文名称",
      "en_name": "English Name",
      "type": "环境类型",
      "atmosphere": "氛围描述",
      "visual_style": "视觉风格",
      "color_palette": ["颜色1", "颜色2"],
      "key_features": ["特征1", "特征2"],
      "prompts": ["提示词1", "提示词2"],
      "era": "时代背景"
    }}
  }},
  "characters": {{
    "character_id": {{
      "zh_name": "中文名称",
      "en_name": "English Name",
      "role_description": "静态的角色身份和基本背景（不含剧情相关变化）",
      "appearance": "外观描述（身高、体型、肤色等静态特征，不包含后天变化）",
      "clothing": "衣着风格描述（基本风格和民族特征，不包含故事中特定时刻的穿着）",
      "personality_keywords": ["性格特征1（相对稳定的特质）"],
      "visual_keywords": ["标志性外观特征"],
      "prompts": ["提示词1", "提示词2"],
    }}
  }},
  "props": {{
    "prop_id": {{
      "zh_name": "中文名称",
      "en_name": "English Name",
      "brief": "简要描述",
      "appearance": "外观描述",
      "color": "颜色",
      "size": "尺寸",
      "functions": ["功能1"],
      "visual_keywords": ["视觉特征1"],
      "prompts": ["提示词1", "提示词2"],
    }}
  }}
}}
```

## 要求

- 位置/角色/道具 ID 使用英文蛇形命名 (如 lingzi_capital_data_core)
- 提取所有在剧本中出现的角色和场景
- 根据剧本内容推断视觉特征、氛围等信息
- **角色定义只包含静态属性，不包含任何剧情相关的动态变化**
- 返回有效的 JSON，无任何额外的 Markdown 标记或文本
"""

    response = client.messages.create(
        model=model,
        max_tokens=10000,
        messages=[{"role": "user", "content": extraction_prompt}],
    )

    # 解析响应
    response_text = response.content[0].text.strip()

    # 如果响应包含 markdown 代码块，提取 JSON 部分
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()

    assets = json.loads(response_text)

    return assets


def save_locations_json(locations: dict, output_path: Path) -> None:
    """保存 locations.json

    Args:
        locations: 场景/地点定义字典
        output_path: 输出文件路径
    """
    output_data = {
        "metadata": {
            "project": "伏羲纪元",
            "version": "1.0",
            "description": "自动从剧本生成的场景资产定义库",
            "source": "gen_assets_json.py",
        },
        "locations": locations,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Locations JSON: {output_path}")
    print(f"   场景数: {len(locations)}")


def save_characters_json(characters: dict, output_path: Path) -> None:
    """保存 characters.json

    Args:
        characters: 角色定义字典
        output_path: 输出文件路径
    """
    output_data = {
        "metadata": {
            "project": "伏羲纪元",
            "version": "1.0",
            "description": "自动从剧本生成的角色资产定义库",
            "source": "gen_assets_json.py",
        },
        "characters": characters,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Characters JSON: {output_path}")
    print(f"   角色数: {len(characters)}")


def save_props_json(props: dict, output_path: Path) -> None:
    """保存 props.json

    Args:
        props: 道具定义字典
        output_path: 输出文件路径
    """
    output_data = {
        "metadata": {
            "project": "伏羲纪元",
            "version": "1.0",
            "description": "自动从剧本生成的道具资产定义库",
            "source": "gen_assets_json.py",
        },
        **props,  # 道具直接作为顶层键
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Props JSON: {output_path}")
    print(f"   道具数: {len(props)}")


def merge_with_existing(new_data: dict, existing_path: Path) -> dict:
    """将新生成的数据与现有文件合并

    合并策略：
    - 保留现有的数据（用户手动编辑的内容）
    - 添加新发现的资产
    - 报告冲突和差异

    Args:
        new_data: 新生成的数据
        existing_path: 现有文件路径

    Returns:
        合并后的数据
    """
    if not existing_path.exists():
        return new_data

    with open(existing_path, "r", encoding="utf-8") as f:
        existing_data = json.load(f)

    # 提取资产部分（跳过 metadata）
    existing_assets = {
        k: v for k, v in existing_data.items() if k != "metadata"
    }

    # 合并逻辑：新数据为基础，保留现有的自定义内容
    merged = new_data.copy()

    for key, value in existing_assets.items():
        if key in merged:
            # 同时存在：保留现有的更详细的定义
            if isinstance(value, dict) and isinstance(merged[key], dict):
                # 合并字段（优先保留现有的）
                merged[key] = {**merged[key], **value}
        else:
            # 新增的在现有文件中但不在新数据中
            merged[key] = value

    return merged


def main():
    parser = argparse.ArgumentParser(
        description="从 script.md 自动生成资产定义 JSON (locations/characters/props)"
    )
    parser.add_argument("episode_id", help="剧集编号 (如 ep001)")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"使用的 Claude 模型 (默认: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制覆盖现有文件（不合并）",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        default=True,
        help="与现有文件合并（默认）",
    )

    args = parser.parse_args()

    try:
        # 获取剧集目录
        ep_dir = get_episode_dir(args.episode_id)
        print(f"\n📂 剧集目录: {ep_dir}")

        # 读取剧本
        print("\n📖 读取剧本...")
        script_content = read_script(ep_dir)
        print(f"✓ 剧本大小: {len(script_content)} 字符")

        # 提取资产
        print("\n" + "=" * 60)
        assets = extract_assets_from_script(
            script_content=script_content,
            model=args.model,
        )
        print("=" * 60)

        locations = assets.get("locations", {})
        characters = assets.get("characters", {})
        props = assets.get("props", {})

        print(f"\n提取结果:")
        print(f"  🏞️  场景: {len(locations)} 个")
        print(f"  👤 角色: {len(characters)} 个")
        print(f"  🎭 道具: {len(props)} 个")

        # 准备输出路径
        assets_dir = PROJECT_ROOT / "assets"
        locations_path = assets_dir / "locations" / "locations.json"
        characters_path = assets_dir / "characters" / "characters.json"
        props_path = assets_dir / "props" / "props.json"

        # 合并或覆盖
        if args.merge and not args.force:
            print("\n🔗 与现有文件合并...")

            if locations_path.exists():
                locations = merge_with_existing(locations, locations_path)
            if characters_path.exists():
                characters = merge_with_existing(characters, characters_path)
            if props_path.exists():
                props = merge_with_existing(props, props_path)

            print("✓ 合并完成")

        # 保存
        print("\n💾 保存资产文件...")
        save_locations_json(locations, locations_path)
        save_characters_json(characters, characters_path)
        save_props_json(props, props_path)

        print(f"\n{'=' * 60}")
        print(f"✨ 资产定义生成完成!")
        print(f"{'=' * 60}")
        print(f"\n后续步骤:")
        print(f"  1. 审阅生成的资产定义（可手工调整细节）")
        print(f"  2. 运行: python -m pipeline.gen_shots {args.episode_id}")
        print(f"  3. 自动关联 location_ref、character_refs 等")

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
