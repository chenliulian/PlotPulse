#!/usr/bin/env python3
"""
导出小说脚本

用法：
    python scripts/export_novel.py --novel-id <ID> --format <format>
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools import Storage


def export_to_txt(novel_data: dict) -> str:
    """导出为TXT格式"""
    lines = [
        novel_data['title'],
        "=" * 40,
        "",
        f"主题: {novel_data['theme']}",
        f"类型: {novel_data['genre']}",
        "",
        "=" * 40,
        ""
    ]
    
    for chapter in novel_data['chapters']:
        lines.append(f"第{chapter['chapter_num']}章")
        lines.append("-" * 40)
        lines.append("")
        lines.append(chapter.get('edited_content', chapter['content']))
        lines.append("")
        lines.append("")
    
    return "\n".join(lines)


def export_to_html(novel_data: dict) -> str:
    """导出为HTML格式"""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{novel_data['title']}</title>
    <style>
        body {{ font-family: serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ text-align: center; }}
        h2 {{ margin-top: 40px; }}
        .meta {{ color: #666; text-align: center; margin-bottom: 40px; }}
        .chapter {{ margin-bottom: 40px; }}
    </style>
</head>
<body>
    <h1>{novel_data['title']}</h1>
    <div class="meta">
        <p>主题: {novel_data['theme']}</p>
        <p>类型: {novel_data['genre']}</p>
    </div>
"""
    
    for chapter in novel_data['chapters']:
        content = chapter.get('edited_content', chapter['content'])
        html += f"""
    <div class="chapter">
        <h2>第{chapter['chapter_num']}章</h2>
        <p>{content.replace(chr(10), '</p><p>')}</p>
    </div>
"""
    
    html += "</body></html>"
    return html


def main():
    parser = argparse.ArgumentParser(description="导出小说")
    parser.add_argument("--novel-id", required=True, help="小说项目ID")
    parser.add_argument("--format", choices=["md", "txt", "html"], 
                       default="md", help="导出格式")
    parser.add_argument("--output", help="输出文件路径")
    
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
    
    print(f"📚 导出小说: {metadata['title']}")
    
    # 根据格式导出
    if args.format == "txt":
        content = export_to_txt(metadata)
        ext = "txt"
    elif args.format == "html":
        content = export_to_html(metadata)
        ext = "html"
    else:
        # Markdown格式
        content = f"# {metadata['title']}\n\n"
        for chapter in metadata['chapters']:
            content += f"## 第{chapter['chapter_num']}章\n\n"
            content += chapter.get('edited_content', chapter['content'])
            content += "\n\n"
        ext = "md"
    
    # 确定输出路径
    if args.output:
        output_path = args.output
    else:
        output_path = f"novels/published/{metadata['title']}.{ext}"
    
    # 保存文件
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 导出成功: {output_path}")


if __name__ == "__main__":
    main()
