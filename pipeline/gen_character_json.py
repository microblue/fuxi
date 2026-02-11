"""
伏羲纪元 — 角色资产定义生成

从剧本中提取和总结每个角色的所有特征，生成 characters.json 文件。
包含：外貌、性格、声音配置、情感弧线等信息，用于后续角色资产定义工作。

使用 Claude LLM 进行智能分析。

使用方法:
    python -m pipeline.gen_character_json ep001
    python -m pipeline.gen_character_json ep001 --model sonnet
"""

import argparse
import json
import sys
from pathlib import Path

from creative_toolkit.llm import call_llm
from pipeline.utils import get_episode_dir


def generate_character_analysis_prompt(script_content: str) -> str:
    """生成Claude提示词来分析剧本中的角色。

    Args:
        script_content: 完整的剧本文本

    Returns:
        格式化的提示词字符串
    """
    return f"""你是一个资深的剧本分析师和角色设计师。请分析以下剧本，为每个角色生成详细的资产定义。

【剧本内容】
{script_content}

【输出要求】

生成一个JSON对象，包含所有主要角色的详细信息。格式如下：

{{
  "characters": {{
    "角色英文名": {{
      "zh_name": "角色中文名",
      "brief": "一句话角色描述",

      "appearance": {{
        "age": "年龄范围",
        "gender": "性别",
        "ethnicity": "民族特征",
        "height": "身高",
        "build": "体型描述",
        "face": "面部特征详述",
        "hair": "发型描述",
        "eyes": "眼睛描述",
        "distinctive_features": ["特征1", "特征2", "特征3"],
        "color_palette": ["主色调1", "主色调2", "辅色调"],
        "reference_inspiration": "参考灵感（影视、美术作品等）"
      }},

      "outfit": {{
        "primary_outfit": "主要服装描述",
        "style": "风格（科幻、古装、现代等）",
        "color_scheme": "配色方案",
        "materials": "材质（布料、光、金属等）",
        "accessories": "饰品列表",
        "armor_or_special_gear": "特殊装备（如有）"
      }},

      "personality": {{
        "core_traits": ["特质1", "特质2", "特质3"],
        "strengths": ["优点1", "优点2"],
        "weaknesses": ["缺点1", "缺点2"],
        "motivations": "动机和目标",
        "fears": "恐惧或阴影",
        "speech_patterns": "说话特点",
        "mannerisms": "动作习惯"
      }},

      "voice": {{
        "age_impression": "音色年龄感",
        "tone": "基调（温和、冷硬、热情等）",
        "tempo": "语速倾向",
        "pitch": "音高范围（高/中/低）",
        "accent": "口音或方言",
        "signature_phrases": ["标志性短语1", "标志性短语2"],
        "emotions": {{
          "angry": "生气时的特征",
          "sad": "悲伤时的特征",
          "happy": "开心时的特征",
          "determined": "坚定时的特征",
          "scared": "害怕时的特征"
        }}
      }},

      "emotion_arc": {{
        "initial_state": "初始情感状态",
        "key_moments": [
          {{"moment": "关键情节点", "emotion": "此时情感", "change": "发生的变化"}},
          {{"moment": "关键情节点2", "emotion": "情感2", "change": "变化2"}}
        ],
        "final_state": "最终情感状态",
        "character_growth": "角色成长或变化"
      }},

      "relationships": {{
        "角色名": "关系描述和互动模式",
        "角色名2": "关系描述"
      }},

      "visual_keywords": [
        "视觉关键词1",
        "视觉关键词2",
        "视觉关键词3",
        "视觉关键词4",
        "视觉关键词5"
      ],

      "tts_config": {{
        "recommended_provider": "fish或edge",
        "voice_id": "推荐的voice ID",
        "edge_voice_id": "Edge TTS备选",
        "speaking_rate": "推荐语速（0.8-1.2）",
        "pitch_adjustment": "音高调整建议",
        "emotion_dominant": "主导情感"
      }},

      "prompt_template": {{
        "style": "视觉风格（cinematic, photorealistic等）",
        "scene_types": ["适合场景类型1", "适合场景类型2"],
        "negative_traits": "应避免的特征",
        "composition_tips": "构图建议"
      }},

      "notes": "其他备注或制作建议"
    }}
  }}
}}

【重要指示】

1. 仅包含出现在剧本中的实际角色
2. 分析要基于剧本中的实际表现和对白，不要凭空发明
3. appearance 字段应包含足够的细节用于 T2I 提示词生成
4. voice 字段为 TTS 系统配置提供指导
5. emotion_arc 要追踪角色在剧本中的情感变化
6. visual_keywords 应该是能直接用于 Flux 提示词的词汇
7. 确保输出是有效的JSON，不要添加其他文字

【背景信息】

这是"伏羲纪元"项目的一部分，融合了赛博朋克、上古神话和科幻元素。
- 时间线：未来灵子文明 → 上古原始时代
- 主题：代码与生物的融合，灵魂转生，文明传承
- 目标用途：为角色资产系统和TTS系统提供完整的角色定义

输出必须是有效的JSON，格式必须能被 json.loads() 解析。"""


def analyze_script_for_characters(
    script_content: str,
    model: str = "opus",
    max_tokens: int = 16000,
) -> dict:
    """使用Claude分析剧本中的角色。

    Args:
        script_content: 剧本文本
        model: Claude模型
        max_tokens: 最大token数

    Returns:
        包含角色分析结果的字典
    """
    print("🤖 调用Claude分析角色特征...")

    prompt = generate_character_analysis_prompt(script_content)

    response_text = call_llm(
        system_prompt="You are a professional script analyst and character designer. Generate detailed character definitions in valid JSON format only.",
        user_prompt=prompt,
        model=model,
        max_tokens=max_tokens,
    )

    # 解析JSON响应
    try:
        # 尝试找到JSON代码块
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        else:
            json_str = response_text.strip()

        data = json.loads(json_str)
        return data
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        print(f"响应预览: {response_text[:500]}")
        raise


def save_characters_json(data: dict, episode_dir: Path) -> Path:
    """保存characters.json到剧集目录。

    Args:
        data: 角色数据
        episode_dir: 剧集目录

    Returns:
        保存的文件路径
    """
    output_path = episode_dir / "characters.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 保存完成: {output_path}")
    return output_path


def read_script(episode_dir: Path) -> str:
    """读取剧本文件。

    Args:
        episode_dir: 剧集目录

    Returns:
        剧本文本
    """
    script_path = episode_dir / "script.md"
    if not script_path.exists():
        raise FileNotFoundError(f"脚本未找到: {script_path}")

    with open(script_path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="从剧本中生成角色资产定义JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m pipeline.gen_character_json ep001
  python -m pipeline.gen_character_json ep001 --model sonnet
        """,
    )
    parser.add_argument("episode_id", help="剧集编号 (如 ep001)")
    parser.add_argument(
        "--model",
        default="opus",
        choices=["sonnet", "opus", "haiku"],
        help="使用的Claude模型 (默认: opus)",
    )

    args = parser.parse_args()

    try:
        # 获取剧集目录
        ep_dir = get_episode_dir(args.episode_id)
        print(f"\n📂 剧集目录: {ep_dir}")

        # 读取脚本
        print("\n📖 读取剧本...")
        script_content = read_script(ep_dir)
        print(f"✓ 脚本大小: {len(script_content)} 字符")

        # 分析角色
        print("\n" + "=" * 60)
        data = analyze_script_for_characters(
            script_content=script_content,
            model=args.model,
            max_tokens=16000,
        )

        # 统计角色
        num_characters = len(data.get("characters", {}))
        print(f"✓ 分析了 {num_characters} 个角色")

        # 保存
        save_characters_json(data, ep_dir)

        print(f"\n{'=' * 60}")
        print("✨ 角色分析完成!")
        print(f"{'=' * 60}")
        print(f"\n后续步骤:")
        print(f"  1. 审阅 {ep_dir}/characters.json")
        print(f"  2. 根据视觉关键词生成角色定妆参考图")
        print(f"  3. 在 TTS 配置中使用 tts_config 中的建议")
        print(f"  4. 在 prompt 模板中使用角色数据生成提示词")

        return 0

    except FileNotFoundError as e:
        print(f"\n❌ 文件错误: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
