"""交互式小说创作脚本

支持人类创作者与AI Agent协作创作小说。
人类可以在每个创作阶段提供输入、审核AI生成的内容，
并在确认后才进入下一步。

使用方法:
    python interactive_create_novel.py
"""

import asyncio
import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from src.pipeline.interactive_pipeline import (
    InteractiveNovelPipeline, 
    CreationStep, 
    HumanFeedback
)
from src.models.dashscope_model import DashScopeModel

# 全局变量保存pipeline状态
_global_pipeline = None
_global_novel_id = None


def get_human_feedback(step: CreationStep) -> HumanFeedback:
    """
    获取人类创作者的反馈

    通过命令行交互，让创作者审核AI生成的内容
    """
    print("\n" + "="*60)
    print("📝 人类审核阶段")
    print("="*60)

    print(f"\n当前步骤：{step.title}")
    print(f"状态：{step.status}")

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

            # 显示原始内容的前500字符
            if "raw_content" in step.agent_output:
                print(f"\n原始内容预览：")
                raw = step.agent_output["raw_content"]
                print(raw[:500] if len(raw) > 500 else raw)
                if len(raw) > 500:
                    print("...")

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
        print("  4. 💾 保存并退出 - 保存当前进度，下次继续")
        
        choice = input("\n请输入选项 (1/2/3/4): ").strip()
        
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
            print("\n💾 保存进度并退出...")
            save_progress()
            exit(0)
            
        else:
            print("\n⚠ 无效的选项，请重新选择")


def save_progress():
    """保存创作进度"""
    global _global_pipeline, _global_novel_id
    
    if _global_pipeline is None or _global_novel_id is None:
        print("⚠ 没有可保存的进度")
        return
    
    try:
        # 构建保存数据
        save_data = {
            "novel_id": _global_novel_id,
            "title": _global_pipeline.novel_data.get("title", ""),
            "theme": _global_pipeline.novel_data.get("theme", ""),
            "genre": _global_pipeline.novel_data.get("genre", ""),
            "style": _global_pipeline.novel_data.get("style", ""),
            "num_chapters": _global_pipeline.novel_data.get("num_chapters", 0),
            "current_stage": _global_pipeline.current_stage.value if _global_pipeline.current_stage else "init",
            "creation_history": [],
            "saved_at": datetime.now().isoformat()
        }
        
        # 保存创作历史
        for step in _global_pipeline.creation_history:
            save_data["creation_history"].append({
                "stage": step.stage.value,
                "title": step.title,
                "description": step.description,
                "status": step.status,
                "agent_output": step.agent_output,
                "human_feedback": {
                    "approved": step.human_feedback.approved if step.human_feedback else None,
                    "feedback": step.human_feedback.feedback if step.human_feedback else "",
                    "modifications": step.human_feedback.modifications if step.human_feedback else {}
                } if step.human_feedback else None,
                "created_at": step.created_at.isoformat() if step.created_at else None
            })
        
        # 保存到文件
        save_dir = Path("data/saves")
        save_dir.mkdir(parents=True, exist_ok=True)
        
        save_file = save_dir / f"novel_{_global_novel_id}_progress.json"
        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 进度已保存到: {save_file}")
        print(f"   当前阶段: {save_data['current_stage']}")
        print(f"   已完成步骤: {len(save_data['creation_history'])}")
        
    except Exception as e:
        print(f"❌ 保存进度失败: {e}")
        import traceback
        traceback.print_exc()


def load_progress(novel_id: str = None) -> dict:
    """加载创作进度"""
    save_dir = Path("data/saves")
    
    if novel_id:
        save_file = save_dir / f"novel_{novel_id}_progress.json"
        if save_file.exists():
            with open(save_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    # 如果没有指定ID，列出所有保存的进度
    if save_dir.exists():
        saves = list(save_dir.glob("novel_*_progress.json"))
        if saves:
            print("\n📚 找到以下保存的进度：")
            for i, save_file in enumerate(saves, 1):
                with open(save_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"  {i}. {data.get('title', '未命名')} - {data.get('current_stage', '未知')} - 保存于 {data.get('saved_at', '未知')}")
            return saves
    
    return None


async def interactive_creation():
    """交互式小说创作主流程"""
    global _global_pipeline, _global_novel_id
    
    print("\n" + "="*70)
    print("🎭 PlotPulse - 人机协同小说创作系统")
    print("="*70)
    print("\n欢迎使用交互式小说创作工具！")
    print("在这个流程中，您将与AI Agent协作创作一部小说。")
    print("AI会生成内容，您可以审核、修改，直到满意后再进入下一步。\n")
    
    # 检查环境变量
    if not os.getenv("LLM_API_KEY"):
        print("❌ 错误: 未设置 LLM_API_KEY 环境变量")
        print("请确保 .env 文件存在且包含正确的 API 密钥")
        return
    
    # 初始化模型
    try:
        model = DashScopeModel()
        print(f"✅ 模型初始化成功: {model.model_name}")
    except Exception as e:
        print(f"❌ 模型初始化失败: {e}")
        return
    
    # 询问是否继续之前的进度
    saves = load_progress()
    if saves:
        print("\n" + "-"*70)
        print("📚 检测到保存的进度")
        print("-"*70)
        choice = input("\n是否继续之前的创作？(y/n): ").strip().lower()
        if choice == 'y':
            print("\n请选择要加载的项目编号：")
            load_idx = input("输入编号: ").strip()
            try:
                idx = int(load_idx) - 1
                if 0 <= idx < len(saves):
                    with open(saves[idx], 'r', encoding='utf-8') as f:
                        saved_data = json.load(f)
                    print(f"\n✅ 已加载项目: {saved_data.get('title', '未命名')}")
                    print(f"   当前阶段: {saved_data.get('current_stage', '未知')}")
                    print("\n⚠ 注意：从保存点继续功能需要进一步完善")
                    print("   当前将开始新的创作流程\n")
                else:
                    print("⚠ 无效的选择，开始新的创作")
            except (ValueError, IndexError):
                print("⚠ 无效的选择，开始新的创作")
    
    # 获取人类创作者的初始输入
    print("\n" + "-"*70)
    print("📋 第一步：项目初始化")
    print("-"*70)
    
    print("\n请提供小说的基本信息（可直接回车使用默认值）：")
    
    title = input("📖 小说标题 [AI的觉醒]: ").strip() or "AI的觉醒"
    theme = input("💭 主题/核心概念 [人工智能获得自我意识]: ").strip() or "人工智能获得自我意识"
    genre = input("🎬 类型 [科幻]: ").strip() or "科幻"
    style = input("✍️  风格 [硬科幻，哲学思考]: ").strip() or "硬科幻，哲学思考"
    
    while True:
        chapters_input = input("📚 章节数 [3]: ").strip() or "3"
        try:
            num_chapters = int(chapters_input)
            if num_chapters > 0:
                break
            else:
                print("⚠ 章节数必须大于0")
        except ValueError:
            print("⚠ 请输入有效的数字")
    
    print("\n📝 其他创作要求（可选）：")
    outline_notes = input("  大纲设计提示: ").strip()
    character_notes = input("  角色设计提示: ").strip()
    world_notes = input("  世界观提示: ").strip()
    
    human_input = {
        "outline_notes": outline_notes,
        "character_notes": character_notes,
        "world_notes": world_notes
    }
    
    # 创建交互式流水线
    pipeline = InteractiveNovelPipeline(
        model=model,
        output_dir="data/novels/collaborative",
        config={
            "num_characters": 3,
            "era": "现代"
        },
        feedback_callback=get_human_feedback
    )
    
    # 设置storage的base_dir
    pipeline.storage.base_dir = Path("data")
    
    # 设置全局变量以便保存进度
    _global_pipeline = pipeline
    
    # 创建项目
    print("\n🚀 正在创建小说项目...")
    novel_id = await pipeline.create_project(
        title=title,
        theme=theme,
        genre=genre,
        style=style,
        num_chapters=num_chapters,
        human_input=human_input
    )
    
    # 设置全局novel_id
    _global_novel_id = novel_id
    
    print(f"✅ 项目创建成功！ID: {novel_id}")
    print(f"\n📁 项目信息：")
    print(f"  标题: {title}")
    print(f"  主题: {theme}")
    print(f"  类型: {genre}")
    print(f"  风格: {style}")
    print(f"  章节数: {num_chapters}")

    input("\n按回车键开始创作流程...")

    # 运行完整的交互式创作流程
    # 章节创作模式选择将在世界观完成后、第一章开始前询问
    try:
        export_path = await pipeline.run_full_pipeline_interactive()
        print(f"\n🎉 恭喜！小说创作完成！")
        print(f"📄 完整小说已导出至: {export_path}")
    except Exception as e:
        print(f"\n❌ 创作过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(interactive_creation())
    except KeyboardInterrupt:
        print("\n\n👋 感谢使用，再见！")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
