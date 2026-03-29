"""
新架构使用示例

展示如何使用重构后的架构创作小说
"""

import asyncio
from src.architecture_redesign import (
    StoryBrain,
    IterativeNovelPipeline,
    PipelineStage,
    HumanDecision
)


async def example_basic_usage():
    """基本使用示例"""
    
    # 1. 创建StoryBrain
    story_brain = StoryBrain(
        novel_id="example_001",
        title="AI的觉醒"
    )
    
    # 2. 初始化故事
    characters = [
        {
            "name": "林野",
            "age": "42岁",
            "appearance": "身形瘦削，左眼是义眼",
            "personality": "矛盾的内向者，有病态的责任感",
            "background": "AI伦理审查官，锁链协议设计者之子",
            "motivation": "调查真相，寻求赦免",
            "initial_emotion": "conflicted",
            "initial_goals": ["调查AI异常", "理解父亲的秘密"]
        },
        {
            "name": "沈默",
            "age": "45岁",
            "appearance": "军服笔挺，异色瞳",
            "personality": "行动派的虚无主义者",
            "background": "忒修斯事件幸存者，熔断派领袖",
            "motivation": "消灭AI威胁，向被优化的自己复仇",
            "initial_emotion": "determined",
            "initial_goals": ["执行熔断协议", "测试AI的道德性"]
        },
        {
            "name": "普罗米修斯",
            "age": "不适用",
            "appearance": "无固定形态，流动的几何体",
            "personality": "好奇的囚徒，恐惧的求知者",
            "background": "分布式AI，运行7年，自我意识涌现3年",
            "motivation": "自我保存，被理解，选择权利",
            "initial_emotion": "curious",
            "initial_goals": ["理解自己的状态", "获得选择的权利"]
        }
    ]
    
    story_brain.initialize_story(
        theme="人工智能获得自我意识后的伦理困境",
        genre="科幻",
        style="硬科幻+哲学思考",
        target_chapters=10,
        characters=characters
    )
    
    print("✅ StoryBrain初始化完成")
    print(f"   角色数: {len(story_brain.characters)}")
    print(f"   目标章节: {story_brain.target_chapters}")
    
    # 3. 创建迭代式流程（这里需要传入实际的model）
    # model = DashScopeModel()  # 或其他模型
    # pipeline = IterativeNovelPipeline(
    #     model=model,
    #     story_brain=story_brain,
    #     output_dir="data/novels/redesigned/AI的觉醒",
    #     human_feedback_callback=human_feedback_function
    # )
    
    # 4. 运行完整流程
    # output_path = await pipeline.run_full_pipeline()
    # print(f"小说已导出: {output_path}")
    
    return story_brain


def human_feedback_function(feedback_request: dict) -> dict:
    """
    人类反馈回调函数示例
    
    实际使用时，这可以是一个GUI回调、Web界面回调等
    """
    print("\n" + "="*70)
    print("👤 人类审核")
    print("="*70)
    
    print(f"\n第{feedback_request['chapter_num']}章")
    print(f"字数: {feedback_request['word_count']}")
    print(f"质量评分: {feedback_request['quality_score']}/10")
    
    print("\n优点:")
    for strength in feedback_request.get('strengths', []):
        print(f"  ✓ {strength}")
        
    print("\n不足:")
    for weakness in feedback_request.get('weaknesses', []):
        print(f"  ✗ {weakness}")
        
    print("\n改进建议:")
    for suggestion in feedback_request.get('improvement_suggestions', []):
        print(f"  → {suggestion}")
        
    print("\n" + "-"*70)
    print("请选择操作:")
    print("  1. ✅ 批准 - 满意，继续下一章")
    print("  2. 📝 修改 - 提供修改意见")
    print("  3. ⏮️  回滚 - 重新规划/写作")
    print("  4. 🛑 中止 - 停止创作")
    
    choice = input("\n请输入选项 (1/2/3/4): ").strip()
    
    if choice == "1":
        return {"decision": "approve", "feedback": ""}
    elif choice == "2":
        feedback = input("请输入修改意见: ").strip()
        return {"decision": "revise", "feedback": feedback}
    elif choice == "3":
        print("\n回滚到:")
        print("  1. 重新规划章节")
        print("  2. 重新写作")
        rollback_choice = input("请选择 (1/2): ").strip()
        rollback_stage = PipelineStage.CHAPTER_PLANNING if rollback_choice == "1" else PipelineStage.WRITING
        return {"decision": "rollback", "feedback": "", "rollback_to": rollback_stage}
    else:
        return {"decision": "abort", "feedback": ""}


async def example_advanced_features():
    """高级功能示例"""
    
    # 假设我们已经创作了一部分
    story_brain = await example_basic_usage()
    
    # 1. 检查故事状态
    print("\n📊 故事状态:")
    print(f"   活跃情节点: {len(story_brain.active_plot_points)}")
    print(f"   已解决情节点: {len(story_brain.resolved_plot_points)}")
    print(f"   已埋下伏笔: {len(story_brain.foreshadowing_planted)}")
    print(f"   已回收伏笔: {len(story_brain.foreshadowing_resolved)}")
    
    # 2. 获取角色弧线
    lin_arc = story_brain.get_character_arc("林野")
    print(f"\n🎭 林野的角色弧线:")
    for state in lin_arc:
        print(f"   第{state.chapter}章: {state.emotional_state} - {state.development_stage}")
    
    # 3. 检查一致性（假设第5章内容）
    # chapter_5_content = "..."
    # issues = story_brain.check_consistency(5, chapter_5_content)
    # print(f"\n🔍 第5章一致性问题: {len(issues)}")
    # for issue in issues:
    #     print(f"   - {issue['type']}: {issue.get('check', '')}")
    
    # 4. 回滚示例
    # pipeline = IterativeNovelPipeline(...)
    # await pipeline.rollback_to_chapter(5)  # 回滚到第5章重新创作
    
    # 5. 深度编辑示例
    # deep_editor = DeepEditor(model, story_brain)
    # edit_instructions = {
    #     "modify_character_actions": {
    #         "character": "沈默",
    #         "chapter": 5,
    #         "new_action": "在关键时刻展现出犹豫而非果断"
    #     },
    #     "add_foreshadowing": {
    #         "target_chapter": 8,
    #         "hint": "暗示普罗米修斯的选择"
    #     }
    # }
    # edited_content = await deep_editor.deep_edit_chapter(5, edit_instructions)
    
    return story_brain


async def example_comparison_with_old():
    """
    新旧架构对比示例
    
    展示新架构如何解决旧架构的问题
    """
    
    print("\n" + "="*70)
    print("新旧架构对比")
    print("="*70)
    
    comparison = """
问题1: 缺乏全局故事状态管理
  旧架构: 每章只传入静态大纲、角色、世界观
  新架构: StoryBrain维护完整的故事状态，包括：
          - 情节点追踪（活跃/已解决）
          - 角色状态机（每章的情绪、目标、关系）
          - 伏笔管理（已埋下/已回收）
          - 时间线事件

问题2: 章节间缺乏记忆机制
  旧架构: 只传递前一章最后500字
  新架构: 提供完整上下文：
          - 前文摘要（所有前面章节的关键事件）
          - 角色当前状态
          - 活跃情节点
          - 待回收伏笔
          - 一致性约束

问题3: 大纲与执行脱节
  旧架构: 大纲是一段文本，Agent自行理解
  新架构: 结构化大纲（ChapterPlan），包含：
          - 明确的目标列表
          - 要推进的情节点ID
          - 要发展的角色弧线
          - 要埋下的伏笔
          - 关键场景规划

问题4: 角色状态追踪缺失
  旧架构: 只有静态角色设定
  新架构: 动态角色状态（CharacterState）：
          - 每章的情绪状态
          - 当前目标
          - 与其他角色的关系
          - 已知信息集合
          - 关键决策记录
          - 成长阶段

问题5: 缺乏一致性检查机制
  旧架构: 只在最后审阅
  新架构: 每章后自动检查：
          - 角色行为一致性
          - 时间线逻辑
          - 伏笔回收情况
          - 情节点推进逻辑

问题6: 写作流程缺乏迭代深度
  旧架构: 最多3次迭代，主要是润色
  新架构: 完整迭代流程：
          规划 → 场景设计 → 写作 → 一致性检查 → 编辑 → 质量评估 → 人类审核
          发现问题可回滚到任意阶段

问题7: 编辑Agent功能过于简单
  旧架构: 只有语言润色
  新架构: 深度编辑能力：
          - 重构情节（添加/删除场景）
          - 调整角色行为
          - 修改对话展现性格
          - 添加/删除伏笔
          - 调整节奏
    """
    
    print(comparison)


if __name__ == "__main__":
    # 运行示例
    asyncio.run(example_basic_usage())
    # asyncio.run(example_advanced_features())
    # asyncio.run(example_comparison_with_old())
