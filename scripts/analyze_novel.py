#!/usr/bin/env python3
"""
分析小说脚本

用法：
    python scripts/analyze_novel.py --novel-id <ID>
"""

import argparse
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools import Storage, TextUtils


def analyze_novel(novel_data: dict) -> dict:
    """分析小说数据"""
    analysis = {
        "basic_info": {
            "title": novel_data['title'],
            "theme": novel_data['theme'],
            "genre": novel_data['genre'],
            "status": novel_data['status'],
            "created_at": novel_data['created_at']
        },
        "statistics": {
            "total_chapters": len(novel_data['chapters']),
            "planned_chapters": novel_data['num_chapters'],
            "total_words": 0,
            "avg_chapter_length": 0
        },
        "content_analysis": {
            "dialogue_ratio": 0,
            "paragraph_count": 0
        }
    }
    
    total_words = 0
    total_paragraphs = 0
    total_dialogues = 0
    
    for chapter in novel_data['chapters']:
        content = chapter.get('edited_content', chapter['content'])
        
        # 字数统计
        word_count = TextUtils.count_words(content)
        total_words += word_count
        
        # 段落统计
        paragraphs = TextUtils.split_into_paragraphs(content)
        total_paragraphs += len(paragraphs)
        
        # 对话统计
        dialogues = TextUtils.extract_dialogue(content)
        total_dialogues += len(dialogues)
    
    # 计算平均值
    if novel_data['chapters']:
        analysis['statistics']['total_words'] = total_words
        analysis['statistics']['avg_chapter_length'] = total_words // len(novel_data['chapters'])
        analysis['content_analysis']['paragraph_count'] = total_paragraphs
        analysis['content_analysis']['dialogue_ratio'] = round(
            total_dialogues / total_paragraphs * 100, 2
        ) if total_paragraphs > 0 else 0
    
    return analysis


def print_analysis(analysis: dict):
    """打印分析报告"""
    print("\n" + "=" * 50)
    print("📊 小说分析报告")
    print("=" * 50)
    
    print("\n【基本信息】")
    for key, value in analysis['basic_info'].items():
        print(f"  {key}: {value}")
    
    print("\n【统计数据】")
    stats = analysis['statistics']
    print(f"  已完成章节: {stats['total_chapters']}/{stats['planned_chapters']}")
    print(f"  总字数: {stats['total_words']:,}")
    print(f"  平均每章字数: {stats['avg_chapter_length']:,}")
    
    print("\n【内容分析】")
    content = analysis['content_analysis']
    print(f"  总段落数: {content['paragraph_count']}")
    print(f"  对话占比: {content['dialogue_ratio']}%")
    
    print("\n" + "=" * 50)


def main():
    parser = argparse.ArgumentParser(description="分析小说")
    parser.add_argument("--novel-id", required=True, help="小说项目ID")
    
    args = parser.parse_args()
    
    # 加载小说数据
    storage = Storage()
    metadata = storage.load_json(
        "metadata.json",
        f"novels/in_progress/novel_{args.novel_id}"
    )
    
    if not metadata:
        print(f"❌ 未找到小说项目: {args.novel_id}")
        return
    
    # 分析
    analysis = analyze_novel(metadata)
    print_analysis(analysis)


if __name__ == "__main__":
    main()
