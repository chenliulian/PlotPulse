#!/usr/bin/env python3
"""
继续创作小说脚本

用法：
    python scripts/continue_writing.py --novel-id <ID> --from-chapter <N>
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import NovelPipeline
from src.models.openai_model import OpenAIModel
from src.tools import Storage


async def main():
    parser = argparse.ArgumentParser(description="继续创作小说")
    parser.add_argument("--novel-id", required=True, help="小说项目ID")
    parser.add_argument("--from-chapter", type=int, help="从第几章开始")
    parser.add_argument("--model", default="gpt-4", help="使用的模型")
    
    args = parser.parse_args()
    
    # 加载已有项目
    storage = Storage()
    metadata = storage.load_json(
        "metadata.json",
        f"novels/in_progress/novel_{args.novel_id}"
    )
    
    if not metadata:
        print(f"❌ 未找到小说项目: {args.novel_id}")
        return
    
    print(f"📚 继续创作: {metadata['title']}")
    print(f"   当前状态: {metadata['status']}")
    print(f"   已完成章节: {len(metadata['chapters'])}/{metadata['num_chapters']}")
    
    # 初始化模型和流水线
    model = OpenAIModel(model_name=args.model)
    pipeline = NovelPipeline(model)
    pipeline.novel_id = args.novel_id
    pipeline.novel_data = metadata
    
    # 确定开始章节
    start_chapter = args.from_chapter or len(metadata['chapters']) + 1
    
    if start_chapter > metadata['num_chapters']:
        print("✅ 所有章节已完成!")
        return
    
    print(f"\n📝 从第 {start_chapter} 章开始创作...")
    
    # 写作剩余章节
    for i in range(start_chapter, metadata['num_chapters'] + 1):
        print(f"\n写作第 {i} 章...")
        chapter = await pipeline.write_chapter(i)
        print(f"✅ 第 {i} 章完成，字数: {chapter['word_count']}")
    
    print("\n✅ 全部章节创作完成!")
    
    # 询问是否导出
    response = input("\n是否导出完整小说? (y/n): ")
    if response.lower() == 'y':
        filepath = await pipeline.export_novel()
        print(f"✅ 小说已导出: {filepath}")


if __name__ == "__main__":
    asyncio.run(main())
