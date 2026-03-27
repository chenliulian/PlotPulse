#!/usr/bin/env python3
"""
创建新小说项目脚本

用法：
    python scripts/create_novel.py --title "小说标题" --theme "主题" --genre "类型"
"""

import argparse
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import NovelPipeline
from src.models.openai_model import OpenAIModel


async def main():
    parser = argparse.ArgumentParser(description="创建新小说项目")
    parser.add_argument("--title", required=True, help="小说标题")
    parser.add_argument("--theme", required=True, help="小说主题")
    parser.add_argument("--genre", required=True, help="小说类型")
    parser.add_argument("--style", default="", help="写作风格")
    parser.add_argument("--chapters", type=int, default=10, help="章节数量")
    parser.add_argument("--model", default="gpt-4", help="使用的模型")
    
    args = parser.parse_args()
    
    print(f"🚀 创建小说项目: {args.title}")
    print(f"   主题: {args.theme}")
    print(f"   类型: {args.genre}")
    print(f"   章节数: {args.chapters}")
    
    # 初始化模型
    try:
        model = OpenAIModel(model_name=args.model)
    except ValueError as e:
        print(f"❌ 错误: {e}")
        print("请确保设置了 OPENAI_API_KEY 环境变量")
        return
    
    # 创建流水线
    pipeline = NovelPipeline(model)
    
    # 创建项目
    novel_id = await pipeline.create_novel(
        title=args.title,
        theme=args.theme,
        genre=args.genre,
        style=args.style,
        num_chapters=args.chapters
    )
    
    print(f"\n✅ 小说项目创建成功!")
    print(f"   项目ID: {novel_id}")
    print(f"   项目目录: novels/in_progress/novel_{novel_id}")
    
    # 询问是否立即生成大纲
    response = input("\n是否立即生成大纲? (y/n): ")
    if response.lower() == 'y':
        print("\n📝 正在生成大纲...")
        outline = await pipeline.generate_outline()
        print("✅ 大纲生成完成!")
        print(f"\n大纲预览:\n{outline['plot_outline'][:500]}...")


if __name__ == "__main__":
    asyncio.run(main())
