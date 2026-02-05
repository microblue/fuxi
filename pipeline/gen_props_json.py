#!/usr/bin/env python3
"""
伏羲纪元 — 道具资产库生成

从完整30集剧本中提取并分析所有道具，生成structured props.json
包含：视觉描述、材质、颜色、尺寸、出现场景、技术水平等

使用：
  pixi run python -m pipeline.gen_props_json --model opus
  pixi run python -m pipeline.gen_props_json --model sonnet
"""

import argparse
import json
import sys
from pathlib import Path

import anthropic

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPT_FILE = PROJECT_ROOT / "doc" / "script_full_30eps.md"
OUTPUT_FILE = PROJECT_ROOT / "assets" / "props" / "props.json"


def read_script() -> str:
    """读取完整30集剧本"""
    if not SCRIPT_FILE.exists():
        raise FileNotFoundError(f"脚本文件不存在: {SCRIPT_FILE}")

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def generate_props_json(script_content: str, model: str = "opus") -> dict:
    """使用Claude从剧本中提取道具并生成JSON定义

    Args:
        script_content: 完整剧本内容
        model: Claude模型 ("opus", "sonnet", "haiku")

    Returns:
        props.json的字典结构
    """
    client = anthropic.Anthropic()

    prompt = """分析以下30集剧本，提取所有出现的道具（物品、工具、装饰品等）。

对于每个道具，生成以下结构的JSON定义：
{
  "prop_id": {
    "zh_name": "中文名称",
    "en_name": "英文名称（可选）",
    "brief": "简短描述（一句话）",
    "appearance": "外观描述（颜色、形状、大小、材质等）",
    "materials": ["材料1", "材料2"],  // e.g., ["金属", "玻璃", "布料"]
    "color": "主要颜色",
    "size": "相对大小（微小/小/中等/大/超大）",
    "functions": ["功能1", "功能2"],  // 道具的用途
    "scenes": ["S01", "S02", ...],    // 出现的场景ID (可选)
    "episodes": [1, 2, 3, ...],       // 出现的集数
    "era": "灵子文明/上古原始/新兴文明",  // 所属时代
    "visual_keywords": ["关键词1", "关键词2", ...],  // 用于T2I生成
    "tech_level": "原始/代码/混合/科技",  // 技术水平
    "reusability": "高/中/低",  // 可复用性
    "notes": "其他备注"
  }
}

要求：
1. 详细分析每个道具的外观特征
2. 标注道具出现的所有剧集
3. 为T2I生成提供准确的视觉关键词
4. 标注时代归属和技术水平
5. 按出现频率和重要性排序
6. 至少提取100+个道具

开始分析：

""" + script_content

    print(f"\n{'=' * 70}")
    print(f"道具库生成 — 使用 {model.upper()}")
    print(f"{'=' * 70}\n")

    print("→ 分析剧本中的道具...")
    print(f"   脚本大小: {len(script_content):,} 字符")
    print()

    try:
        # 使用streaming模式处理长请求
        response_text = ""

        # 映射模型名称到实际的API模型ID
        model_map = {
            "opus": "claude-opus-4-1",
            "sonnet": "claude-3-5-sonnet-20241022",
            "haiku": "claude-3-5-haiku-20241022",
        }
        api_model = model_map.get(model, "claude-opus-4-1")

        with client.messages.stream(
            model=api_model,
            max_tokens=100000,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        ) as stream:
            for text in stream.text_stream:
                response_text += text
                # 显示进度
                if len(response_text) % 5000 == 0:
                    print(f"   已接收: {len(response_text):,} 字符...", end="\r")

        print(f"   已接收: {len(response_text):,} 字符 ✓")

        # 提取JSON块
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1

        if json_start == -1 or json_end <= json_start:
            raise ValueError("响应中找不到有效的JSON")

        json_str = response_text[json_start:json_end]
        props_data = json.loads(json_str)

        return props_data

    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        print(f"   响应: {response_text[:500]}")
        sys.exit(1)

    except anthropic.APIError as e:
        print(f"❌ API错误: {e}")
        sys.exit(1)


def save_props_json(props_data: dict, output_path: Path) -> None:
    """保存props.json到文件"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(props_data, f, ensure_ascii=False, indent=2)

    print(f"✓ 道具库已保存: {output_path}")
    print(f"  • 道具总数: {len(props_data)}")


def main():
    parser = argparse.ArgumentParser(
        description="从剧本生成道具资产库 (props.json)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用Opus生成（推荐，最精准）
  pixi run python -m pipeline.gen_props_json --model opus

  # 使用Sonnet生成（较快）
  pixi run python -m pipeline.gen_props_json --model sonnet

  # 使用Haiku生成（最快，但可能不够精准）
  pixi run python -m pipeline.gen_props_json --model haiku
        """,
    )

    parser.add_argument(
        "--model",
        choices=["opus", "sonnet", "haiku"],
        default="opus",
        help="Claude模型选择 (默认: opus)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_FILE,
        help="输出文件路径",
    )

    args = parser.parse_args()

    try:
        # 读取脚本
        print("读取剧本...")
        script_content = read_script()

        # 生成道具库
        props_data = generate_props_json(script_content, model=args.model)

        # 保存到文件
        print()
        save_props_json(props_data, args.output)

        print(f"\n{'=' * 70}")
        print("✓ 道具库生成完成")
        print(f"{'=' * 70}\n")

    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 未预期的错误: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
