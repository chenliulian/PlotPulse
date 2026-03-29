"""
迁移脚本：将现有小说项目迁移到新架构

使用方法:
    python migrate_to_new_architecture.py --novel-dir <小说目录>
    
功能:
    1. 读取现有小说数据
    2. 转换为StoryBrain格式
    3. 生成增强的章节规划
    4. 保存迁移后的状态
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import argparse
import json
from pathlib import Path
from typing import Dict, Any, Optional

from src.architecture_redesign.integration_adapter import StoryBrainAdapter


def find_novel_projects(base_dir: str = "novels") -> list:
    """查找所有小说项目"""
    base_path = Path(base_dir)
    if not base_path.exists():
        return []
    
    projects = []
    
    # 查找novel_data.json文件
    for data_file in base_path.rglob("novel_data.json"):
        novel_dir = data_file.parent
        
        # 读取基本信息
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            projects.append({
                "dir": novel_dir,
                "title": data.get("title", "未命名"),
                "id": data.get("id", "unknown"),
                "chapters": len(data.get("chapters", {})),
                "has_outline": bool(data.get("outline"))
            })
        except Exception as e:
            print(f"⚠️  读取 {data_file} 失败: {e}")
    
    return projects


def migrate_novel(novel_dir: Path, output_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    迁移单个小说项目
    
    Args:
        novel_dir: 小说项目目录
        output_dir: 输出目录（可选）
        
    Returns:
        迁移结果报告
    """
    print(f"\n{'='*60}")
    print(f"📚 迁移项目: {novel_dir.name}")
    print(f"{'='*60}")
    
    # 读取现有数据
    data_file = novel_dir / "novel_data.json"
    if not data_file.exists():
        return {"success": False, "error": "找不到novel_data.json"}
    
    with open(data_file, 'r', encoding='utf-8') as f:
        novel_data = json.load(f)
    
    print(f"✅ 读取数据成功")
    print(f"   标题: {novel_data.get('title', 'N/A')}")
    print(f"   章节: {len(novel_data.get('chapters', {}))}")
    print(f"   角色: {len(novel_data.get('characters', []))}")
    
    # 创建适配器
    novel_id = novel_data.get("id", novel_dir.name)
    adapter = StoryBrainAdapter(
        novel_id=novel_id,
        output_dir=str(output_dir or novel_dir)
    )
    
    # 初始化StoryBrain
    try:
        story_brain = adapter.initialize_from_legacy(novel_data)
        print(f"\n✅ StoryBrain初始化成功")
    except Exception as e:
        return {"success": False, "error": f"初始化失败: {e}"}
    
    # 为已有章节创建执行记录
    chapters = novel_data.get("chapters", {})
    if chapters:
        print(f"\n📖 处理已有章节...")
        
        for ch_num_str, ch_data in chapters.items():
            try:
                ch_num = int(ch_num_str)
                content = ch_data.get("content", "")
                
                if content:
                    # 记录章节
                    adapter.record_chapter_completion(
                        chapter_num=ch_num,
                        content=content,
                        quality_score=ch_data.get("quality_score", 0.0)
                    )
                    
                    print(f"   第{ch_num}章: {len(content)}字")
            except Exception as e:
                print(f"   ⚠️  第{ch_num_str}章处理失败: {e}")
    
    # 保存状态
    try:
        adapter.save_state()
        print(f"\n✅ StoryBrain状态已保存")
    except Exception as e:
        return {"success": False, "error": f"保存失败: {e}"}
    
    # 生成报告
    report = adapter.get_novel_report()
    
    print(f"\n📊 迁移报告:")
    print(f"   已完成章节: {report['progress']['completed_chapters']}/{report['progress']['total_chapters']}")
    print(f"   情节点: {report['plot_points']['total']}")
    print(f"   伏笔: {report['foreshadowing']['planted']}")
    
    return {
        "success": True,
        "novel_id": novel_id,
        "title": novel_data.get("title", ""),
        "report": report
    }


def batch_migrate(base_dir: str = "novels"):
    """批量迁移所有项目"""
    print("\n" + "="*60)
    print("📦 批量迁移小说项目")
    print("="*60)
    
    # 查找项目
    projects = find_novel_projects(base_dir)
    
    if not projects:
        print(f"\n⚠️  在 {base_dir} 目录下没有找到小说项目")
        return
    
    print(f"\n找到 {len(projects)} 个项目:")
    for i, proj in enumerate(projects, 1):
        print(f"  {i}. {proj['title']} ({proj['chapters']}章)")
    
    # 确认迁移
    confirm = input("\n确认迁移所有项目? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    # 批量迁移
    results = []
    for proj in projects:
        result = migrate_novel(proj["dir"])
        results.append(result)
    
    # 汇总报告
    print("\n" + "="*60)
    print("📊 批量迁移完成")
    print("="*60)
    
    success_count = sum(1 for r in results if r.get("success"))
    print(f"\n成功: {success_count}/{len(results)}")
    
    for result in results:
        status = "✅" if result.get("success") else "❌"
        print(f"  {status} {result.get('title', 'Unknown')}: {result.get('novel_id', 'N/A')}")


def interactive_migrate():
    """交互式迁移"""
    print("\n" + "="*60)
    print("🔄 StoryBrain架构迁移工具")
    print("="*60)
    
    # 查找项目
    projects = find_novel_projects()
    
    if not projects:
        print("\n⚠️  没有找到小说项目")
        print("请确保 novels/ 目录下存在小说数据")
        return
    
    print(f"\n找到 {len(projects)} 个项目:")
    for i, proj in enumerate(projects, 1):
        print(f"  {i}. {proj['title']}")
        print(f"     目录: {proj['dir']}")
        print(f"     章节: {proj['chapters']}")
    
    # 选择项目
    while True:
        choice = input("\n请选择要迁移的项目编号 (或输入 'all' 迁移全部): ").strip()
        
        if choice.lower() == 'all':
            batch_migrate()
            return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(projects):
                selected = projects[idx]
                break
            else:
                print("⚠️  无效的编号")
        except ValueError:
            print("⚠️  请输入数字或 'all'")
    
    # 迁移选中的项目
    result = migrate_novel(selected["dir"])
    
    if result["success"]:
        print("\n✅ 迁移成功！")
        print(f"\n现在可以使用增强版脚本继续创作:")
        print(f"  python interactive_create_novel_enhanced.py")
    else:
        print(f"\n❌ 迁移失败: {result.get('error', '未知错误')}")


def verify_migration(novel_id: str, base_dir: str = "novels"):
    """验证迁移结果"""
    print(f"\n{'='*60}")
    print(f"🔍 验证迁移: {novel_id}")
    print(f"{'='*60}")
    
    # 查找StoryBrain文件
    story_brain_file = Path(base_dir) / f"{novel_id}_story_brain.json"
    
    if not story_brain_file.exists():
        # 尝试在其他位置查找
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file == f"{novel_id}_story_brain.json":
                    story_brain_file = Path(root) / file
                    break
    
    if not story_brain_file.exists():
        print(f"❌ 找不到StoryBrain文件: {novel_id}_story_brain.json")
        return False
    
    # 加载并验证
    try:
        from src.architecture_redesign import StoryBrain
        
        story_brain = StoryBrain.load_from_file(str(story_brain_file))
        
        print(f"✅ StoryBrain加载成功")
        print(f"\n基本信息:")
        print(f"   标题: {story_brain.title}")
        print(f"   主题: {story_brain.theme}")
        print(f"   目标章节: {story_brain.target_chapters}")
        
        print(f"\n状态统计:")
        print(f"   角色: {len(story_brain.characters)}")
        print(f"   情节点: {len(story_brain.plot_points)} (活跃: {len(story_brain.active_plot_points)})")
        print(f"   伏笔: {len(story_brain.foreshadowing_planted)} (已回收: {len(story_brain.foreshadowing_resolved)})")
        print(f"   已完成章节: {len(story_brain.chapter_executions)}")
        
        print(f"\n角色弧线:")
        for char_name in story_brain.characters.keys():
            arc = story_brain.get_character_arc(char_name)
            print(f"   {char_name}: {len(arc)} 个状态点")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="将现有小说项目迁移到StoryBrain新架构"
    )
    
    parser.add_argument(
        "--novel-dir",
        type=str,
        help="小说项目目录"
    )
    
    parser.add_argument(
        "--batch",
        action="store_true",
        help="批量迁移所有项目"
    )
    
    parser.add_argument(
        "--verify",
        type=str,
        help="验证指定novel_id的迁移结果"
    )
    
    parser.add_argument(
        "--base-dir",
        type=str,
        default="novels",
        help="小说项目根目录 (默认: novels)"
    )
    
    args = parser.parse_args()
    
    # 验证模式
    if args.verify:
        verify_migration(args.verify, args.base_dir)
        return
    
    # 批量迁移模式
    if args.batch:
        batch_migrate(args.base_dir)
        return
    
    # 单项目迁移模式
    if args.novel_dir:
        novel_dir = Path(args.novel_dir)
        if not novel_dir.exists():
            print(f"❌ 目录不存在: {novel_dir}")
            return
        
        result = migrate_novel(novel_dir)
        
        if result["success"]:
            print("\n✅ 迁移成功！")
        else:
            print(f"\n❌ 迁移失败: {result.get('error', '未知错误')}")
        return
    
    # 交互式模式
    interactive_migrate()


if __name__ == "__main__":
    main()
