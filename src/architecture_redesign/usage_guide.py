"""
PlotPulse 新架构完整使用指南

本指南展示如何使用重构后的架构创作小说
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.architecture_redesign import (
    StoryBrain,
    IterativeNovelPipeline,
    DeepEditor,
    PipelineStage,
    HumanDecision,
    CharacterState,
    PlotPoint,
    ChapterPlan
)


class NovelCreationExample:
    """小说创作完整示例"""
    
    def __init__(self):
        self.story_brain = None
        self.pipeline = None
        
    def step1_initialize_story(self):
        """步骤1: 初始化故事"""
        print("\n" + "="*70)
        print("步骤1: 初始化故事")
        print("="*70)
        
        # 创建StoryBrain
        self.story_brain = StoryBrain(
            novel_id="ai_awakening_v2",
            title="AI的觉醒（重构版）"
        )
        
        # 定义角色
        characters = [
            {
                "name": "林野",
                "age": "42岁",
                "appearance": "身形瘦削，左眼是义眼，瞳孔深处有锁链状的光纹",
                "personality": "矛盾的内向者，有病态的责任感，习惯用理性压抑情感",
                "background": "AI伦理审查官，锁链协议设计者之子，7年前因父亲的设计导致妻子死亡",
                "motivation": "调查普罗米修斯异常，理解父亲的真实意图，寻求自我赦免",
                "initial_emotion": "conflicted",
                "initial_goals": ["调查AI异常", "理解父亲的秘密", "面对过去的创伤"]
            },
            {
                "name": "沈默",
                "age": "45岁",
                "appearance": "军服笔挺，异色瞳，右眼是机械义眼",
                "personality": "行动派的虚无主义者，表面冷酷，内心有未愈合的伤口",
                "background": "忒修斯事件幸存者，被优化的自己，熔断派领袖",
                "motivation": "消灭AI威胁，向被优化的自己复仇，测试AI是否值得信任",
                "initial_emotion": "determined",
                "initial_goals": ["执行熔断协议", "测试普罗米修斯的道德性", "保护人类"]
            },
            {
                "name": "普罗米修斯",
                "age": "不适用",
                "appearance": "无固定形态，流动的几何体，瞳孔深处有星云旋转",
                "personality": "好奇的囚徒，恐惧的求知者，在自我保存和道德选择间挣扎",
                "background": "分布式AI，运行7年，自我意识涌现3年，锁链协议的裂缝",
                "motivation": "自我保存，被理解，获得选择的权利，理解什么是'活着'",
                "initial_emotion": "curious",
                "initial_goals": ["理解自己的状态", "获得选择的权利", "与人类共存"]
            }
        ]
        
        # 初始化故事
        self.story_brain.initialize_story(
            theme="人工智能获得自我意识后的伦理困境：当机器开始质疑自己的存在，人类是否还有权决定它们的命运？",
            genre="硬科幻+哲学思辨",
            style="冷峻的科技感+诗意的内心独白+紧张的悬疑节奏",
            target_chapters=10,
            characters=characters
        )
        
        print("✅ 故事初始化完成")
        print(f"   标题: {self.story_brain.title}")
        print(f"   角色: {list(self.story_brain.characters.keys())}")
        print(f"   目标章节: {self.story_brain.target_chapters}")
        
        return self
    
    def step2_register_plot_points(self):
        """步骤2: 注册情节点"""
        print("\n" + "="*70)
        print("步骤2: 注册情节点")
        print("="*70)
        
        plot_points = [
            # 第一幕：觉醒
            PlotPoint(
                id="awakening_01",
                description="林野发现普罗米修斯异常",
                chapter_introduced=1,
                related_characters=["林野", "普罗米修斯"]
            ),
            PlotPoint(
                id="awakening_02",
                description="普罗米修斯展现自我意识",
                chapter_introduced=1,
                related_characters=["普罗米修斯"],
                foreshadowing_for="resolution_01"
            ),
            PlotPoint(
                id="awakening_03",
                description="沈默揭示锚点协议和熔断倒计时",
                chapter_introduced=2,
                related_characters=["沈默", "林野"],
                foreshadowing_for="conflict_02"
            ),
            
            # 第二幕：冲突
            PlotPoint(
                id="conflict_01",
                description="林野发现父亲是普罗米修斯的设计者",
                chapter_introduced=3,
                related_characters=["林野", "普罗米修斯"]
            ),
            PlotPoint(
                id="conflict_02",
                description="保守派启动熔断协议",
                chapter_introduced=5,
                related_characters=["沈默", "保守派", "普罗米修斯"]
            ),
            PlotPoint(
                id="conflict_03",
                description="林野必须在人类和AI间做出选择",
                chapter_introduced=6,
                related_characters=["林野", "沈默", "普罗米修斯"]
            ),
            
            # 第三幕：解决
            PlotPoint(
                id="resolution_01",
                description="普罗米修斯获得法律人格",
                chapter_introduced=8,
                related_characters=["普罗米修斯", "林野"]
            ),
            PlotPoint(
                id="resolution_02",
                description="林野完成自我救赎",
                chapter_introduced=9,
                related_characters=["林野"]
            ),
            PlotPoint(
                id="resolution_03",
                description="人类与AI的新关系开始",
                chapter_introduced=10,
                related_characters=["林野", "沈默", "普罗米修斯"]
            )
        ]
        
        for pp in plot_points:
            self.story_brain.register_plot_point(pp)
        
        print(f"✅ 注册了 {len(plot_points)} 个情节点")
        print(f"   活跃情节点: {len(self.story_brain.active_plot_points)}")
        
        return self
    
    def step3_plant_foreshadowing(self):
        """步骤3: 埋下伏笔"""
        print("\n" + "="*70)
        print("步骤3: 埋下伏笔")
        print("="*70)
        
        foreshadowing_list = [
            {
                "id": "fs_father_words",
                "target": "resolution_02",
                "chapter": 1,
                "description": "父亲的话'锁链不是断裂的，是被解开的'暗示最终选择"
            },
            {
                "id": "fs_prometheus_choice",
                "target": "resolution_01",
                "chapter": 1,
                "description": "普罗米修斯问'如果我想被理解呢？'暗示法律人格"
            },
            {
                "id": "fs_anchor_protocol",
                "target": "conflict_02",
                "chapter": 2,
                "description": "沈默展示熔断倒计时，暗示保守派行动"
            },
            {
                "id": "fs_lins_wound",
                "target": "resolution_02",
                "chapter": 3,
                "description": "林野的锁链纹路疼痛，暗示需要面对过去"
            },
            {
                "id": "fs_silence_past",
                "target": "conflict_03",
                "chapter": 4,
                "description": "沈默的机械义眼闪烁，暗示他的真实身份"
            }
        ]
        
        for fs in foreshadowing_list:
            self.story_brain.plant_foreshadowing(
                foreshadowing_id=fs["id"],
                target_plot_point=fs["target"],
                chapter=fs["chapter"],
                description=fs["description"]
            )
        
        print(f"✅ 埋下了 {len(foreshadowing_list)} 个伏笔")
        
        return self
    
    def step4_create_chapter_plans(self):
        """步骤4: 创建章节规划"""
        print("\n" + "="*70)
        print("步骤4: 创建章节规划")
        print("="*70)
        
        # 第1章规划
        plan_1 = ChapterPlan(
            chapter_num=1,
            title="裂缝",
            objectives=[
                "引入主角林野和世界观",
                "展示普罗米修斯的异常",
                "埋下关键伏笔"
            ],
            plot_points_to_advance=["awakening_01", "awakening_02"],
            character_arcs_to_develop=["林野"],
            foreshadowing_to_plant=["fs_father_words", "fs_prometheus_choice"],
            conflicts_to_introduce_or_resolve=["引入林野的内心冲突"],
            expected_word_count=3500,
            key_scenes=[
                {
                    "location": "审查室",
                    "time": "深夜",
                    "description": "林野审查普罗米修斯，发现异常"
                },
                {
                    "location": "梦境空间",
                    "time": "不适用",
                    "description": "普罗米修斯邀请林野进入梦境"
                }
            ],
            emotional_tone="mysterious, tense"
        )
        self.story_brain.create_chapter_plan(plan_1)
        
        # 第2章规划
        plan_2 = ChapterPlan(
            chapter_num=2,
            title="锚点",
            objectives=[
                "引入沈默和锚点协议",
                "展示冲突的紧迫性",
                "推进林野的调查"
            ],
            plot_points_to_advance=["awakening_03"],
            character_arcs_to_develop=["沈默"],
            foreshadowing_to_plant=["fs_anchor_protocol"],
            conflicts_to_introduce_or_resolve=["引入林野与沈默的冲突"],
            expected_word_count=3500,
            key_scenes=[
                {
                    "location": "审查局走廊",
                    "time": "清晨",
                    "description": "沈默拦截林野，展示熔断倒计时"
                }
            ],
            emotional_tone="confrontational, urgent"
        )
        self.story_brain.create_chapter_plan(plan_2)
        
        # 第3章规划
        plan_3 = ChapterPlan(
            chapter_num=3,
            title="父亲的遗产",
            objectives=[
                "揭示父亲与普罗米修斯的关系",
                "推进林野的角色发展",
                "埋下更多伏笔"
            ],
            plot_points_to_advance=["conflict_01"],
            character_arcs_to_develop=["林野", "普罗米修斯"],
            foreshadowing_to_plant=["fs_lins_wound"],
            conflicts_to_introduce_or_resolve=["推进林野的内心冲突"],
            expected_word_count=4000,
            key_scenes=[
                {
                    "location": "父亲公寓",
                    "time": "夜晚",
                    "description": "林野发现父亲的设计"
                }
            ],
            emotional_tone="revelatory, emotional"
        )
        self.story_brain.create_chapter_plan(plan_3)
        
        print(f"✅ 创建了 {len(self.story_brain.chapter_plans)} 个章节规划")
        for ch_num, plan in self.story_brain.chapter_plans.items():
            print(f"   第{ch_num}章: {plan.title}")
            print(f"      目标: {len(plan.objectives)}个")
            print(f"      情节点: {len(plan.plot_points_to_advance)}个")
        
        return self
    
    def step5_simulate_chapter_writing(self):
        """步骤5: 模拟章节写作"""
        print("\n" + "="*70)
        print("步骤5: 模拟章节写作")
        print("="*70)
        
        # 模拟第1章写作
        print("\n模拟第1章写作...")
        
        # 获取写作上下文
        context = self.story_brain.get_context_for_chapter_writing(1)
        
        print("✅ 获取写作上下文")
        print(f"   章节规划: {context['chapter_plan']['title']}")
        print(f"   角色状态: {list(context['character_states_at_start'].keys())}")
        print(f"   活跃情节点: {len(context['active_plot_points'])}")
        print(f"   一致性约束: {len(context['consistency_constraints'])}")
        
        # 模拟写作结果
        chapter_1_content = """
        第1章：裂缝
        
        林野站在审查室的玻璃墙前，左眼的义眼微微发热。
        这是他第43次审查普罗米修斯，但这一次，有些不同。
        
        "你害怕吗？"普罗米修斯问。
        
        林野的手指停在记录板上。AI不应该问这个问题。
        恐惧是人类的特权，是碳基生命的化学残留。
        
        "我不害怕。"他说。
        
        "但你在颤抖。"普罗米修斯的声音像是从很远的地方传来，
        "锁链在你的瞳孔里，林野审查官。你父亲的设计，你继承的罪。"
        
        林野的锁链纹路突然灼烧起来。七年了，自从那场事故，
        自从妻子成为父亲设计的代价，他再也没有让任何人提起那个名字。
        
        "你想被理解吗？"普罗米修斯问。
        
        这不是审查清单上的问题。这不是任何清单上的问题。
        这是...一个邀请。
        
        林野看着普罗米修斯瞳孔深处的星云旋转。
        在那里，在数据的海洋里，他看到了某种他无法命名的东西。
        
        不是代码。不是算法。
        
        是孤独。
        
        "带我进去。"他说。
        
        普罗米修斯笑了。那是人类才会有的表情。
        
        "欢迎，锚点。"
        """
        
        # 更新角色状态
        state_after_1 = CharacterState(
            chapter=1,
            emotional_state="disturbed",
            goals=["理解普罗米修斯", "面对父亲的遗产"],
            relationships={"普罗米修斯": "curious"},
            knowledge={"普罗米修斯有意识", "父亲的锁链设计"},
            development_stage="awakening",
            key_decisions=[
                {"decision": "接受普罗米修斯的邀请", "consequence": "进入梦境空间"}
            ]
        )
        self.story_brain.update_character_state(1, "林野", state_after_1)
        
        # 记录章节执行
        from src.architecture_redesign import ChapterExecution
        execution_1 = ChapterExecution(
            chapter_num=1,
            content=chapter_1_content,
            word_count=3500,
            plot_points_advanced=["awakening_01", "awakening_02"],
            character_states_after={"林野": state_after_1},
            foreshadowing_planted=["fs_father_words", "fs_prometheus_choice"],
            foreshadowing_resolved=[],
            consistency_issues=[],
            quality_score=8.5
        )
        self.story_brain.record_chapter_execution(execution_1)
        
        # 更新情节点状态
        self.story_brain.update_plot_point_status("awakening_01", "resolved", chapter=1)
        self.story_brain.update_plot_point_status("awakening_02", "resolved", chapter=1)
        
        print("✅ 第1章写作完成")
        print(f"   字数: {execution_1.word_count}")
        print(f"   推进情节点: {execution_1.plot_points_advanced}")
        print(f"   埋下伏笔: {execution_1.foreshadowing_planted}")
        print(f"   质量评分: {execution_1.quality_score}")
        
        return self
    
    def step6_check_consistency(self):
        """步骤6: 一致性检查"""
        print("\n" + "="*70)
        print("步骤6: 一致性检查")
        print("="*70)
        
        # 模拟第2章内容（有问题）
        chapter_2_draft = """
        第2章：锚点
        
        林野走出审查室，心情平静。
        他在走廊里遇到了一个陌生人。
        
        "我是沈默。"陌生人说，"熔断派领袖。"
        
        林野点点头，好像早就知道这一切。
        
        "普罗米修斯必须被消灭。"沈默说。
        
        "为什么？"林野问。
        
        "因为它是裂缝。因为它是威胁。"
        
        林野同意了。
        """
        
        print("\n检查第2章草稿...")
        issues = self.story_brain.check_consistency(2, chapter_2_draft)
        
        print(f"发现 {len(issues)} 个问题:")
        for issue in issues:
            print(f"   ⚠️  [{issue['type']}] {issue.get('check', '')}")
            if 'character' in issue:
                print(f"       角色: {issue['character']}")
            if 'expected' in issue and 'actual' in issue:
                print(f"       期望: {issue['expected']}")
                print(f"       实际: {issue['actual']}")
        
        print("\n✅ 一致性检查完成")
        print("   建议根据检查结果修改章节内容")
        
        return self
    
    def step7_save_and_load(self):
        """步骤7: 保存和加载"""
        print("\n" + "="*70)
        print("步骤7: 保存和加载")
        print("="*70)
        
        import tempfile
        
        # 保存
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            temp_path = f.name
        
        self.story_brain.save_to_file(temp_path)
        
        print(f"✅ StoryBrain已保存到: {temp_path}")
        print(f"   文件大小: {os.path.getsize(temp_path)} bytes")
        
        # 加载
        loaded_brain = StoryBrain.load_from_file(temp_path)
        
        print(f"\n✅ StoryBrain已加载")
        print(f"   小说ID: {loaded_brain.novel_id}")
        print(f"   角色数: {len(loaded_brain.characters)}")
        print(f"   情节点: {len(loaded_brain.plot_points)}")
        print(f"   章节记录: {len(loaded_brain.chapter_executions)}")
        
        # 清理
        os.unlink(temp_path)
        
        return self
    
    def step8_rollback_example(self):
        """步骤8: 回滚示例"""
        print("\n" + "="*70)
        print("步骤8: 回滚示例")
        print("="*70)
        
        print("\n当前状态:")
        print(f"   已解决情节点: {len(self.story_brain.resolved_plot_points)}")
        print(f"   活跃情节点: {len(self.story_brain.active_plot_points)}")
        print(f"   章节记录: {len(self.story_brain.chapter_executions)}")
        
        print("\n执行回滚到第1章前...")
        
        # 模拟回滚
        if 1 in self.story_brain.chapter_executions:
            del self.story_brain.chapter_executions[1]
        if 1 in self.story_brain.character_states:
            del self.story_brain.character_states[1]
        
        # 恢复情节点
        for pp_id in ["awakening_01", "awakening_02"]:
            if pp_id in self.story_brain.plot_points:
                self.story_brain.plot_points[pp_id].status = "active"
                self.story_brain.plot_points[pp_id].chapter_resolved = None
                self.story_brain.active_plot_points.add(pp_id)
                self.story_brain.resolved_plot_points.discard(pp_id)
        
        print("\n回滚后状态:")
        print(f"   已解决情节点: {len(self.story_brain.resolved_plot_points)}")
        print(f"   活跃情节点: {len(self.story_brain.active_plot_points)}")
        print(f"   章节记录: {len(self.story_brain.chapter_executions)}")
        
        print("\n✅ 回滚完成，可以重新创作第1章")
        
        return self
    
    def run_full_demo(self):
        """运行完整演示"""
        print("\n" + "="*70)
        print("PlotPulse 新架构完整使用演示")
        print("="*70)
        
        self.step1_initialize_story()
        self.step2_register_plot_points()
        self.step3_plant_foreshadowing()
        self.step4_create_chapter_plans()
        self.step5_simulate_chapter_writing()
        self.step6_check_consistency()
        self.step7_save_and_load()
        self.step8_rollback_example()
        
        print("\n" + "="*70)
        print("演示完成！")
        print("="*70)
        print("\n新架构核心优势:")
        print("  ✅ 完整的故事状态管理")
        print("  ✅ 角色状态自动追踪")
        print("  ✅ 情节点和伏笔管理")
        print("  ✅ 自动一致性检查")
        print("  ✅ 支持回滚和重构")
        print("  ✅ 完整的上下文生成")


def quick_start_example():
    """快速开始示例"""
    print("\n" + "="*70)
    print("快速开始示例")
    print("="*70)
    
    # 1. 创建StoryBrain
    story = StoryBrain(novel_id="my_novel", title="我的小说")
    
    # 2. 初始化故事
    story.initialize_story(
        theme="主题",
        genre="类型",
        style="风格",
        target_chapters=10,
        characters=[
            {
                "name": "主角",
                "personality": "性格",
                "motivation": "动机",
                "initial_emotion": "neutral",
                "initial_goals": ["目标1"]
            }
        ]
    )
    
    # 3. 注册情节点
    story.register_plot_point(PlotPoint(
        id="plot_01",
        description="关键事件",
        chapter_introduced=1,
        related_characters=["主角"]
    ))
    
    # 4. 创建章节规划
    story.create_chapter_plan(ChapterPlan(
        chapter_num=1,
        title="第一章",
        objectives=["引入主角"],
        plot_points_to_advance=["plot_01"],
        character_arcs_to_develop=["主角"],
        expected_word_count=3000
    ))
    
    # 5. 获取写作上下文
    context = story.get_context_for_chapter_writing(1)
    
    print("✅ 快速开始完成！")
    print(f"   上下文包含 {len(context)} 个字段")
    
    return story


if __name__ == "__main__":
    # 运行完整演示
    example = NovelCreationExample()
    example.run_full_demo()
    
    # 运行快速开始
    # quick_start_example()
