"""
增强版交互式小说创作脚本

集成StoryBrain的新架构，同时保持与原有系统的兼容性。

使用方法:
    python interactive_create_novel_enhanced.py
    
新特性:
    - 完整的故事状态管理
    - 角色状态自动追踪
    - 情节点和伏笔管理
    - 自动一致性检查
    - 增强的上下文生成
"""

import asyncio
import os
import json
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加新架构到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline.interactive_pipeline import (
    InteractiveNovelPipeline, 
    CreationStep, 
    HumanFeedback
)
from src.models.dashscope_model import DashScopeModel

# 导入新架构适配器
from src.architecture_redesign.integration_adapter import (
    StoryBrainAdapter,
    integrate_with_pipeline
)

# 全局变量保存pipeline状态
_global_pipeline = None
_global_novel_id = None
_global_story_brain_adapter = None


def get_human_feedback(step: CreationStep) -> HumanFeedback:
    """
    获取人类创作者的反馈（增强版）
    
    增加了StoryBrain相关的信息和选项
    """
    global _global_story_brain_adapter
    
    print("\n" + "="*60)
    print("📝 人类审核阶段")
    print("="*60)

    print(f"\n当前步骤：{step.title}")
    print(f"状态：{step.status}")
    
    # 显示StoryBrain状态（如果有）
    if _global_story_brain_adapter and _global_story_brain_adapter.story_brain:
        sb = _global_story_brain_adapter.story_brain
        print(f"\n📊 StoryBrain状态:")
        print(f"   已完成章节: {len(sb.chapter_executions)}/{sb.target_chapters}")
        print(f"   活跃情节点: {len(sb.active_plot_points)}")
        print(f"   待回收伏笔: {len([f for f in sb.foreshadowing_planted.values() if f['status'] == 'pending'])}")

    # 特殊处理：章节创作模式选择
    if step.title == "章节创作模式选择":
        print("\n📄 请选择：")
        print("-" * 60)
        if "options" in step.agent_output:
            for option in step.agent_output["options"]:
                print(f"  {option}")
        print("-" * 60)

        while True:
            choice = input("\n请输入选项 (1/2): ").strip()
            if choice in ["1", "2"]:
                return HumanFeedback(
                    approved=True,
                    feedback=choice,
                    modifications={"chapter_mode": choice}
                )
            else:
                print("⚠ 无效的选项，请重新选择")

    # 显示AI生成的内容摘要
    if step.agent_output:
        print("\n📄 AI生成的内容摘要：")
        print("-" * 60)

        if "plot_outline" in step.agent_output:
            content = step.agent_output["plot_outline"]
            print(content[:1000] if len(content) > 1000 else content)
            if len(content) > 1000:
                print("...")

        elif "characters" in step.agent_output:
            characters = step.agent_output.get("characters", [])
            print(f"共 {len(characters)} 个角色")
            for char in characters[:3]:
                print(f"  - {char.get('name', '未命名')}: {char.get('description', '')[:50]}...")

        elif "world_description" in step.agent_output:
            content = step.agent_output["world_description"]
            print(content[:800] if len(content) > 800 else content)
            if len(content) > 800:
                print("...")

        elif "edited_content" in step.agent_output or "content" in step.agent_output:
            content = step.agent_output.get("edited_content") or step.agent_output.get("content", "")
            print(content[:1200] if len(content) > 1200 else content)
            if len(content) > 1200:
                print("...")
                print(f"\n总字数：{len(content)}")
                
            # 显示一致性检查结果（如果有）
            if _global_story_brain_adapter and "consistency_issues" in step.agent_output:
                issues = step.agent_output["consistency_issues"]
                if issues:
                    print(f"\n⚠️  一致性问题: {len(issues)}个")
                    for issue in issues[:3]:
                        print(f"   - {issue.get('type', '')}: {issue.get('check', '')[:50]}...")

        elif "review_text" in step.agent_output:
            print(f"评分：{step.agent_output.get('score', 'N/A')}/10")
            print(step.agent_output["review_text"][:800])

        print("-" * 60)
    
    # 交互式选择
    while True:
        print("\n请选择操作：")
        print("  1. ✅ 批准 - 满意，进入下一步")
        print("  2. 🔄 修改 - 提供修改意见，让AI重新生成")
        print("  3. 👀 查看完整内容 - 显示AI生成的完整内容")
        print("  4. 📊 查看StoryBrain报告 - 显示故事状态")
        print("  5. 💾 保存并退出 - 保存当前进度，下次继续")
        
        choice = input("\n请输入选项 (1/2/3/4/5): ").strip()
        
        if choice == "1":
            print("\n✅ 已批准，进入下一步...")
            return HumanFeedback(approved=True, feedback="人类创作者批准")
            
        elif choice == "2":
            print("\n📝 请输入您的修改意见（直接回车表示无具体意见）：")
            feedback_text = input("> ").strip()
            
            print("\n💡 是否需要提供具体的修改参数？")
            print("  例如：修改主题、调整风格、增加角色等")
            print("  格式：key=value，多个参数用逗号分隔")
            print("  直接回车表示不添加参数")
            
            modifications = {}
            mod_input = input("> ").strip()
            if mod_input:
                try:
                    for pair in mod_input.split(","):
                        if "=" in pair:
                            key, value = pair.split("=", 1)
                            modifications[key.strip()] = value.strip()
                    print(f"✓ 已添加修改参数：{modifications}")
                except Exception as e:
                    print(f"⚠ 参数解析失败：{e}")
            
            return HumanFeedback(
                approved=False, 
                feedback=feedback_text or "需要修改",
                modifications=modifications
            )
            
        elif choice == "3":
            print("\n" + "="*60)
            print("📄 完整内容")
            print("="*60)
            
            if "plot_outline" in step.agent_output:
                print(step.agent_output["plot_outline"])
            elif "world_description" in step.agent_output:
                print(step.agent_output["world_description"])
            elif "edited_content" in step.agent_output:
                print(step.agent_output["edited_content"])
            elif "content" in step.agent_output:
                print(step.agent_output["content"])
            elif "review_text" in step.agent_output:
                print(step.agent_output["review_text"])
            elif "raw_content" in step.agent_output:
                print(step.agent_output["raw_content"])
            
            print("="*60)
            input("\n按回车键继续...")
            
        elif choice == "4":
            if _global_story_brain_adapter:
                print_story_brain_report()
            else:
                print("\n⚠️ StoryBrain尚未初始化")
            input("\n按回车键继续...")
            
        elif choice == "5":
            print("\n💾 保存进度并退出...")
            save_progress()
            exit(0)
            
        else:
            print("\n⚠ 无效的选项，请重新选择")


def print_story_brain_report():
    """打印StoryBrain报告"""
    global _global_story_brain_adapter
    
    if not _global_story_brain_adapter or not _global_story_brain_adapter.story_brain:
        print("\n⚠️ StoryBrain尚未初始化")
        return
    
    report = _global_story_brain_adapter.get_novel_report()
    sb = _global_story_brain_adapter.story_brain
    
    print("\n" + "="*60)
    print("📊 StoryBrain状态报告")
    print("="*60)
    
    print(f"\n小说: {report.get('title', 'N/A')}")
    print(f"ID: {report.get('novel_id', 'N/A')}")
    
    progress = report.get('progress', {})
    print(f"\n【进度】")
    print(f"  已完成: {progress.get('completed_chapters', 0)}/{progress.get('total_chapters', 0)} 章")
    print(f"  完成率: {progress.get('completion_rate', 0):.1f}%")
    
    plot_points = report.get('plot_points', {})
    print(f"\n【情节点】")
    print(f"  总数: {plot_points.get('total', 0)}")
    print(f"  活跃: {plot_points.get('active', 0)}")
    print(f"  已解决: {plot_points.get('resolved', 0)}")
    
    foreshadowing = report.get('foreshadowing', {})
    print(f"\n【伏笔】")
    print(f"  已埋下: {foreshadowing.get('planted', 0)}")
    print(f"  已回收: {foreshadowing.get('resolved', 0)}")
    
    print(f"\n【角色弧线】")
    for char_name, char_info in report.get('characters', {}).items():
        print(f"  {char_name}: {char_info.get('arc_length', 0)} 个状态点")
    
    print("\n" + "="*60)


def save_progress():
    """保存创作进度（增强版）"""
    global _global_pipeline, _global_novel_id, _global_story_brain_adapter
    
    if _global_pipeline is None or _global_novel_id is None:
        print("⚠ 没有可保存的进度")
        return
    
    try:
        # 保存完整的进度数据
        save_data = {
            "novel_id": _global_novel_id,
            "title": _global_pipeline.novel_data.get("title", ""),
            "theme": _global_pipeline.novel_data.get("theme", ""),
            "genre": _global_pipeline.novel_data.get("genre", ""),
            "style": _global_pipeline.novel_data.get("style", ""),
            "num_chapters": _global_pipeline.novel_data.get("num_chapters", 0),
            "current_stage": _global_pipeline.current_stage.value if _global_pipeline.current_stage else "init",
            "creation_history": [],
            "enhanced": True,  # 标记为增强版
            "story_brain_enabled": _global_story_brain_adapter is not None
        }
        
        # 保存关键创作数据
        if "outline" in _global_pipeline.novel_data:
            save_data["outline"] = _global_pipeline.novel_data["outline"]
        if "characters" in _global_pipeline.novel_data:
            save_data["characters"] = _global_pipeline.novel_data["characters"]
        if "world_setting" in _global_pipeline.novel_data:
            save_data["world_setting"] = _global_pipeline.novel_data["world_setting"]
        if "chapters" in _global_pipeline.novel_data:
            save_data["chapters"] = _global_pipeline.novel_data["chapters"]
        
        # 保存创作历史
        for step in _global_pipeline.creation_history:
            step_data = {
                "stage": step.stage.value,
                "title": step.title,
                "description": step.description,
                "status": step.status,
                "agent_output_keys": list(step.agent_output.keys()) if step.agent_output else []
            }
            if step.human_feedback:
                step_data["human_feedback"] = {
                    "approved": step.human_feedback.approved,
                    "feedback": step.human_feedback.feedback
                }
            save_data["creation_history"].append(step_data)
        
        # 保存StoryBrain状态
        if _global_story_brain_adapter:
            _global_story_brain_adapter.save_state()
        
        # 保存到文件
        save_dir = Path("saves")
        save_dir.mkdir(exist_ok=True)
        save_file = save_dir / f"novel_{_global_novel_id}.json"
        
        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 进度已保存: {save_file}")
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")


async def create_novel_with_story_brain():
    """
    使用StoryBrain增强的创作流程
    """
    global _global_pipeline, _global_novel_id, _global_story_brain_adapter
    
    print("\n" + "="*60)
    print("🚀 增强版交互式小说创作")
    print("="*60)
    print("\n本版本集成了StoryBrain新架构，提供：")
    print("  ✅ 完整的故事状态管理")
    print("  ✅ 角色状态自动追踪")
    print("  ✅ 情节点和伏笔管理")
    print("  ✅ 自动一致性检查")
    print("  ✅ 增强的上下文生成")
    print("="*60)
    
    # 初始化模型
    api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("LLM_API_KEY")
    if not api_key:
        print("\n❌ 错误：未设置API密钥环境变量")
        print("请在.env文件中设置 DASHSCOPE_API_KEY 或 LLM_API_KEY")
        return
    
    model = DashScopeModel(api_key=api_key)
    
    # 创建pipeline
    pipeline = InteractiveNovelPipeline(
        model=model,
        output_dir="novels/enhanced",
        feedback_callback=get_human_feedback
    )
    
    _global_pipeline = pipeline
    
    # 创建项目
    print("\n📚 创建新小说项目")
    print("-" * 60)
    
    title = input("请输入小说标题（直接回车让AI生成）: ").strip()
    theme = input("请输入主题（直接回车让AI生成）: ").strip()
    genre = input("请输入类型（直接回车让AI生成）: ").strip()
    style = input("请输入风格（直接回车让AI生成）: ").strip()
    
    try:
        num_chapters = input("请输入章节数（默认10）: ").strip()
        num_chapters = int(num_chapters) if num_chapters else 10
    except ValueError:
        num_chapters = 10
    
    human_input = {
        "title": title,
        "theme": theme,
        "genre": genre,
        "style": style
    }
    
    # 创建项目
    novel_id = await pipeline.create_project(
        title=title or "",
        theme=theme or "",
        genre=genre or "",
        style=style or "",
        num_chapters=num_chapters,
        language="中文",
        human_input=human_input
    )
    
    _global_novel_id = novel_id
    print(f"\n✅ 项目创建成功！ID: {novel_id}")
    
    # 初始化StoryBrain适配器
    print("\n🧠 初始化StoryBrain...")
    _global_story_brain_adapter = integrate_with_pipeline(pipeline, pipeline.novel_data)
    
    # 运行创作流程
    print("\n" + "="*60)
    print("🎬 开始创作流程")
    print("="*60)
    
    try:
        # 阶段1：生成大纲
        print("\n📖 阶段1：生成故事大纲")
        outline_result = await pipeline.generate_outline_interactive()
        outline = outline_result.get("plot_outline", "")
        
        # 更新StoryBrain的大纲信息
        if _global_story_brain_adapter:
            _global_story_brain_adapter._convert_outline_to_plot_points(outline)
        
        # 阶段2：生成角色
        print("\n👥 阶段2：生成角色设定")
        await pipeline.generate_characters_interactive()
        
        # 更新StoryBrain的角色信息
        if _global_story_brain_adapter:
            _global_story_brain_adapter.story_brain.characters = pipeline.novel_data.get("characters", {})
        
        # 阶段3：生成世界观
        print("\n🌍 阶段3：生成世界观")
        await pipeline.generate_world_interactive()
        
        # 阶段4：章节创作
        print("\n✍️ 阶段4：章节创作")
        
        # 询问创作模式
        print("\n请选择章节创作模式：")
        print("  1. 全自动模式 - AI自动完成所有章节")
        print("  2. 协作模式 - 每章完成后由您审核")
        
        while True:
            mode = input("\n请输入选项 (1/2): ").strip()
            if mode in ["1", "2"]:
                break
            print("⚠ 无效的选项")
        
        if mode == "1":
            pipeline._skip_chapter_review = True
        
        # 逐章创作
        for chapter_num in range(1, num_chapters + 1):
            print(f"\n{'='*60}")
            print(f"📖 创作第 {chapter_num}/{num_chapters} 章")
            print(f"{'='*60}")
            
            # 使用StoryBrain创建增强的上下文
            if _global_story_brain_adapter:
                enhanced_context = _global_story_brain_adapter.create_enhanced_chapter_plan(chapter_num)
                
                # 将增强上下文传递给pipeline
                if "chapters" not in pipeline.novel_data:
                    pipeline.novel_data["chapters"] = {}
                
                # 存储增强上下文供后续使用
                pipeline.novel_data["enhanced_context"] = enhanced_context
            
            # 创作章节
            chapter_result = await pipeline.write_chapter_interactive(chapter_num, skip_review=pipeline._skip_chapter_review)
            
            # 使用StoryBrain检查一致性
            if _global_story_brain_adapter and chapter_result:
                content = chapter_result.get("content", "")
                issues = _global_story_brain_adapter.check_chapter_consistency(chapter_num, content)
                
                # 将一致性问题添加到结果中
                if issues:
                    chapter_result["consistency_issues"] = issues
            
            # 记录到StoryBrain
            if _global_story_brain_adapter and chapter_result:
                content = chapter_result.get("content", "")
                quality = chapter_result.get("quality_score", 0.0)
                _global_story_brain_adapter.record_chapter_completion(
                    chapter_num, content, quality
                )
            
            # 保存进度
            save_progress()
        
        # 阶段5：最终审阅
        print("\n🔍 阶段5：最终审阅")
        await pipeline.review_novel_interactive()
        
        # 导出小说
        print("\n📤 导出小说...")
        output_path = await pipeline.export_novel()
        
        print("\n" + "="*60)
        print("🎉 创作完成！")
        print("="*60)
        print(f"\n小说已保存到: {output_path}")
        
        # 显示最终报告
        if _global_story_brain_adapter:
            print_story_brain_report()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 创作被中断")
        save_progress()
        print("进度已保存，下次可以继续")
        
    except Exception as e:
        print(f"\n❌ 创作过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        save_progress()
        print("进度已保存")


async def continue_writing(pipeline, save_data):
    """继续创作章节"""
    global _global_story_brain_adapter
    
    # 确定当前进度
    current_stage = save_data.get('current_stage', 'init')
    num_chapters = save_data.get('num_chapters', 10)
    
    # 根据当前阶段决定从哪一步开始
    if current_stage == 'init':
        print("\n📖 从大纲生成开始...")
        start_stage = 1
    elif current_stage == 'outline':
        print("\n👥 从角色生成开始...")
        start_stage = 2
    elif current_stage == 'characters':
        print("\n🌍 从世界观生成开始...")
        start_stage = 3
    elif current_stage == 'world':
        print("\n✍️ 从章节创作开始...")
        start_stage = 4
    elif current_stage == 'writing':
        # 已经在章节创作阶段，确定当前章节
        chapters = save_data.get('chapters', [])
        completed_chapters = len([c for c in chapters if c.get('content') or c.get('edited_content')])
        if completed_chapters >= num_chapters:
            print("\n✅ 所有章节已完成！进入审阅阶段...")
            start_stage = 5
        else:
            print(f"\n✍️ 从第 {completed_chapters + 1} 章开始创作...")
            start_stage = 4
    elif current_stage == 'review':
        print("\n🔍 从最终审阅开始...")
        start_stage = 5
    elif current_stage == 'completed':
        print("\n✅ 小说创作已全部完成！")
        return
    else:
        # 未知状态，尝试从章节数量判断
        chapters = save_data.get('chapters', [])
        completed_chapters = len([c for c in chapters if c.get('content') or c.get('edited_content')])
        if completed_chapters >= num_chapters:
            print("\n✅ 所有章节已完成！进入审阅阶段...")
            start_stage = 5
        else:
            print(f"\n✍️ 从第 {completed_chapters + 1} 章开始创作...")
            start_stage = 4
    
    try:
        # 阶段1：大纲（如果需要）
        if start_stage <= 1:
            print("\n📖 阶段1：生成故事大纲")
            outline_result = await pipeline.generate_outline_interactive()
            outline = outline_result.get("plot_outline", "")
            if _global_story_brain_adapter:
                _global_story_brain_adapter._convert_outline_to_plot_points(outline)
            save_progress()
        
        # 阶段2：角色（如果需要）
        if start_stage <= 2:
            print("\n👥 阶段2：生成角色设定")
            await pipeline.generate_characters_interactive()
            if _global_story_brain_adapter:
                _global_story_brain_adapter.story_brain.characters = pipeline.novel_data.get("characters", {})
            save_progress()
        
        # 阶段3：世界观（如果需要）
        if start_stage <= 3:
            print("\n🌍 阶段3：生成世界观")
            await pipeline.generate_world_interactive()
            save_progress()
        
        # 阶段4：章节创作
        print("\n✍️ 阶段4：章节创作")
        
        # 询问创作模式
        print("\n请选择章节创作模式：")
        print("  1. 全自动模式 - AI自动完成所有章节")
        print("  2. 协作模式 - 每章完成后由您审核")
        
        while True:
            mode = input("\n请输入选项 (1/2): ").strip()
            if mode in ["1", "2"]:
                break
            print("⚠ 无效的选项")
        
        skip_review = (mode == "1")
        
        # 确定起始章节
        chapters = save_data.get('chapters', [])
        start_chapter = len([c for c in chapters if c.get('content') or c.get('edited_content')]) + 1
        
        # 逐章创作
        for chapter_num in range(start_chapter, num_chapters + 1):
            print(f"\n{'='*60}")
            print(f"📖 创作第 {chapter_num}/{num_chapters} 章")
            print(f"{'='*60}")
            
            # 使用StoryBrain创建增强的上下文
            if _global_story_brain_adapter:
                enhanced_context = _global_story_brain_adapter.create_enhanced_chapter_plan(chapter_num)
                if "chapters" not in pipeline.novel_data:
                    pipeline.novel_data["chapters"] = {}
                pipeline.novel_data["enhanced_context"] = enhanced_context
            
            # 创作章节
            chapter_result = await pipeline.write_chapter_interactive(chapter_num, skip_review=skip_review)
            
            # 使用StoryBrain检查一致性
            if _global_story_brain_adapter and chapter_result:
                content = chapter_result.get("content", "")
                issues = _global_story_brain_adapter.check_chapter_consistency(chapter_num, content)
                if issues:
                    chapter_result["consistency_issues"] = issues
            
            # 记录到StoryBrain
            if _global_story_brain_adapter and chapter_result:
                content = chapter_result.get("content", "")
                quality = chapter_result.get("quality_score", 0.0)
                _global_story_brain_adapter.record_chapter_completion(chapter_num, content, quality)
            
            save_progress()
        
        # 阶段5：最终审阅
        print("\n🔍 阶段5：最终审阅")
        await pipeline.review_novel_interactive()
        
        # 导出小说
        print("\n📤 导出小说...")
        output_path = await pipeline.export_novel()
        
        print("\n" + "="*60)
        print("🎉 创作完成！")
        print("="*60)
        print(f"\n小说已保存到: {output_path}")
        
        if _global_story_brain_adapter:
            print_story_brain_report()
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 创作被中断")
        save_progress()
        print("进度已保存，下次可以继续")
    except Exception as e:
        print(f"\n❌ 创作过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        save_progress()
        print("进度已保存")


async def load_and_continue():
    """加载保存的进度并继续创作"""
    global _global_pipeline, _global_novel_id, _global_story_brain_adapter
    
    print("\n📂 加载保存的进度")
    print("-" * 60)
    
    # 查找保存的文件
    save_dir = Path("saves")
    if not save_dir.exists():
        print("⚠️ 没有找到保存的文件")
        return
    
    save_files = list(save_dir.glob("novel_*.json"))
    if not save_files:
        print("⚠️ 没有找到保存的文件")
        return
    
    # 显示可用的保存文件
    print("\n可用的保存文件：")
    for i, save_file in enumerate(save_files, 1):
        with open(save_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"  {i}. {data.get('title', '未命名')} ({data.get('novel_id', 'unknown')})")
        print(f"     进度: {data.get('current_stage', 'unknown')}")
        if data.get('enhanced'):
            print(f"     [增强版]")
    
    # 选择文件
    while True:
        choice = input("\n请选择要加载的文件编号: ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(save_files):
                selected_file = save_files[idx]
                break
            else:
                print("⚠️ 无效的编号")
        except ValueError:
            print("⚠️ 请输入数字")
    
    # 加载数据
    with open(selected_file, 'r', encoding='utf-8') as f:
        save_data = json.load(f)
    
    novel_id = save_data.get('novel_id')
    _global_novel_id = novel_id
    
    print(f"\n✅ 已加载: {save_data.get('title', '未命名')}")
    
    # 检查是否是增强版
    if save_data.get('enhanced') and save_data.get('story_brain_enabled'):
        print("🧠 加载StoryBrain状态...")
        
        # 初始化模型
        api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("LLM_API_KEY")
        model = DashScopeModel(api_key=api_key)
        
        # 创建pipeline
        pipeline = InteractiveNovelPipeline(
            model=model,
            output_dir="novels/enhanced",
            feedback_callback=get_human_feedback
        )
        
        _global_pipeline = pipeline
        
        # 将保存的数据加载到pipeline
        pipeline.novel_data = save_data.copy()
        pipeline.novel_id = novel_id
        
        # 加载StoryBrain状态
        _global_story_brain_adapter = StoryBrainAdapter(novel_id, output_dir="novels/enhanced")
        _global_story_brain_adapter.load_state()
        
        print("✅ StoryBrain状态已恢复")
        
        # 询问用户接下来要做什么
        print("\n" + "="*60)
        print("🎬 继续创作")
        print("="*60)
        print("\n1. 继续创作下一章")
        print("2. 查看StoryBrain报告")
        print("3. 返回主菜单")
        
        while True:
            action = input("\n请选择: ").strip()
            if action == "1":
                # 继续创作
                await continue_writing(pipeline, save_data)
                break
            elif action == "2":
                print_story_brain_report()
                # 显示报告后重新显示菜单
                print("\n" + "="*60)
                print("🎬 继续创作")
                print("="*60)
                print("\n1. 继续创作下一章")
                print("2. 查看StoryBrain报告")
                print("3. 返回主菜单")
                continue
            elif action == "3":
                break
            else:
                print("⚠️ 无效的选项")
    else:
        print("\n⚠️ 这不是增强版项目，无法使用StoryBrain功能")
        print("目前可以查看StoryBrain报告：")
        print_story_brain_report()


def main():
    """主函数"""
    print("\n" + "="*60)
    print("📚 PlotPulse 增强版交互式小说创作")
    print("="*60)
    print("\n1. 🚀 开始新创作")
    print("2. 📂 加载并继续")
    print("3. ❌ 退出")
    
    while True:
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            asyncio.run(create_novel_with_story_brain())
            break
        elif choice == "2":
            asyncio.run(load_and_continue())
            break
        elif choice == "3":
            print("\n再见！")
            break
        else:
            print("⚠️ 无效的选项")


if __name__ == "__main__":
    main()
