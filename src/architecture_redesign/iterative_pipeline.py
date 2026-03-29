"""
迭代式小说创作流程

核心理念：
1. 规划 → 写作 → 检查 → 评估 → （迭代优化）→ 确认
2. 支持回滚到任意阶段重新创作
3. 深度编辑而不仅是表面润色
4. 人类在关键决策点深度参与
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
from pathlib import Path

from .story_brain import StoryBrain, ChapterPlan, ChapterExecution, CharacterState, PlotPoint
from .collaborative_agents import (
    PlotDesignerAgent, CharacterDeveloperAgent, ScenePlannerAgent,
    WriterAgent, ConsistencyCheckerAgent, EditorAgent, QualityAssessorAgent,
    AgentRole, AgentProposal, CollaborationResult
)


class PipelineStage(Enum):
    """流程阶段"""
    INIT = "init"
    STRUCTURE_DESIGN = "structure_design"
    CHAPTER_PLANNING = "chapter_planning"
    SCENE_PLANNING = "scene_planning"
    WRITING = "writing"
    CONSISTENCY_CHECK = "consistency_check"
    EDITING = "editing"
    QUALITY_ASSESSMENT = "quality_assessment"
    HUMAN_REVIEW = "human_review"
    COMPLETED = "completed"


@dataclass
class StageResult:
    """阶段结果"""
    stage: PipelineStage
    success: bool
    output: Any
    issues: List[str]
    next_stage: Optional[PipelineStage] = None


@dataclass
class HumanDecision:
    """人类决策"""
    decision: str  # "approve", "revise", "rollback", "abort"
    feedback: str
    rollback_to: Optional[PipelineStage] = None
    specific_changes: Optional[Dict] = None


class IterativeNovelPipeline:
    """
    迭代式小说创作流程
    
    与旧架构的关键区别：
    1. 每章经过完整流程：规划→写作→检查→编辑→评估→人类审核
    2. 发现问题可回滚到任意阶段
    3. 深度编辑可重构情节，不仅是润色语言
    4. StoryBrain维护完整状态，确保连贯性
    """
    
    def __init__(
        self,
        model: Any,
        story_brain: StoryBrain,
        output_dir: str = "novels/iterative",
        human_feedback_callback: Optional[Callable] = None
    ):
        self.model = model
        self.story_brain = story_brain
        self.output_dir = Path(output_dir)
        self.human_feedback_callback = human_feedback_callback
        
        # 初始化所有Agent
        self.plot_designer = PlotDesignerAgent(model, story_brain)
        self.character_developer = CharacterDeveloperAgent(model, story_brain)
        self.scene_planner = ScenePlannerAgent(model, story_brain)
        self.writer = WriterAgent(model, story_brain)
        self.consistency_checker = ConsistencyCheckerAgent(model, story_brain)
        self.editor = EditorAgent(model, story_brain)
        self.quality_assessor = QualityAssessorAgent(model, story_brain)
        
        # 当前状态
        self.current_stage: PipelineStage = PipelineStage.INIT
        self.current_chapter: int = 0
        self.stage_history: List[StageResult] = []
        
    async def run_full_pipeline(self) -> str:
        """
        运行完整创作流程
        """
        print(f"\n{'='*70}")
        print(f"🎭 迭代式小说创作流程")
        print(f"{'='*70}")
        print(f"小说：{self.story_brain.title}")
        print(f"目标章节数：{self.story_brain.target_chapters}")
        print(f"{'='*70}\n")
        
        # 阶段1：设计整体结构
        result = await self._design_structure()
        if not result.success:
            print(f"❌ 结构设计失败: {result.issues}")
            return ""
            
        # 逐章创作
        for chapter_num in range(1, self.story_brain.target_chapters + 1):
            success = await self._create_chapter(chapter_num)
            if not success:
                print(f"❌ 第{chapter_num}章创作失败")
                # 询问人类是否继续
                if self.human_feedback_callback:
                    decision = self.human_feedback_callback(
                        f"第{chapter_num}章创作失败，是否继续？",
                        ["继续下一章", "重新创作本章", "停止创作"]
                    )
                    if decision == "停止创作":
                        break
                    elif decision == "重新创作本章":
                        chapter_num -= 1  # 重新创作本章
                        continue
                        
        # 导出完整小说
        return await self._export_novel()
        
    async def _design_structure(self) -> StageResult:
        """设计整体故事结构"""
        print(f"\n📚 阶段：设计整体结构")
        
        proposal = await self.plot_designer.generate_proposal(
            context={},
            task="design_overall_structure"
        )
        
        structure = proposal.content
        
        # 注册情节点到StoryBrain
        for pp_data in structure.get("plot_points", []):
            plot_point = PlotPoint(
                id=pp_data["id"],
                description=pp_data["description"],
                chapter_introduced=pp_data["chapter_introduced"],
                chapter_resolved=pp_data.get("chapter_resolved"),
                related_characters=pp_data.get("related_characters", []),
                foreshadowing_for=pp_data.get("foreshadowing_for")
            )
            self.story_brain.register_plot_point(plot_point)
            
        print(f"✅ 已设计 {len(structure.get('plot_points', []))} 个情节点")
        print(f"   三幕结构：{structure.get('act_structure', {})}")
        
        return StageResult(
            stage=PipelineStage.STRUCTURE_DESIGN,
            success=True,
            output=structure,
            issues=[]
        )
        
    async def _create_chapter(self, chapter_num: int) -> bool:
        """
        创作单章（完整迭代流程）
        """
        print(f"\n{'='*70}")
        print(f"📖 创作第{chapter_num}章")
        print(f"{'='*70}")
        
        self.current_chapter = chapter_num
        max_iterations = 3
        
        for iteration in range(1, max_iterations + 1):
            print(f"\n🔄 迭代 {iteration}/{max_iterations}")
            
            # 步骤1：规划章节
            plan_result = await self._plan_chapter(chapter_num)
            if not plan_result.success:
                print(f"❌ 章节规划失败")
                continue
                
            # 步骤2：规划场景
            scene_result = await self._plan_scenes(chapter_num)
            if not scene_result.success:
                print(f"❌ 场景规划失败")
                continue
                
            # 步骤3：写作
            write_result = await self._write_chapter(chapter_num)
            if not write_result.success:
                print(f"❌ 写作失败")
                continue
                
            chapter_content = write_result.output
            
            # 步骤4：一致性检查
            consistency_result = await self._check_consistency(chapter_num, chapter_content)
            if consistency_result.issues:
                print(f"⚠️  发现 {len(consistency_result.issues)} 个一致性问题")
                for issue in consistency_result.issues[:3]:  # 只显示前3个
                    print(f"   - {issue.get('type')}: {issue.get('description', '')[:50]}...")
                    
                # 如果问题严重，直接重写
                high_severity = [i for i in consistency_result.issues 
                               if i.get('severity') == 'high']
                if high_severity and iteration < max_iterations:
                    print(f"   存在严重问题，将重新创作")
                    continue
                    
            # 步骤5：编辑润色
            edit_result = await self._edit_chapter(chapter_num, chapter_content)
            if edit_result.success:
                chapter_content = edit_result.output
                
            # 步骤6：质量评估
            quality_result = await self._assess_quality(chapter_num, chapter_content)
            quality_score = quality_result.output.get("overall_score", 0)
            print(f"   质量评分: {quality_score}/10")
            
            # 步骤7：人类审核（如果提供了回调）
            if self.human_feedback_callback:
                human_decision = await self._get_human_feedback(
                    chapter_num, chapter_content, quality_result.output
                )
                
                if human_decision.decision == "approve":
                    print(f"✅ 人类审核通过")
                    # 记录执行结果
                    await self._finalize_chapter(chapter_num, chapter_content, quality_result.output)
                    return True
                    
                elif human_decision.decision == "revise":
                    print(f"📝 根据人类反馈修改")
                    # 根据反馈修改
                    chapter_content = await self._revise_based_on_feedback(
                        chapter_num, chapter_content, human_decision.feedback
                    )
                    # 重新评估
                    continue
                    
                elif human_decision.decision == "rollback":
                    print(f"⏮️  回滚到 {human_decision.rollback_to}")
                    # 实现回滚逻辑
                    if human_decision.rollback_to == PipelineStage.CHAPTER_PLANNING:
                        continue  # 重新规划
                    elif human_decision.rollback_to == PipelineStage.WRITING:
                        pass  # 保持当前内容，重新编辑
                        
                elif human_decision.decision == "abort":
                    print(f"🛑 中止本章创作")
                    return False
            else:
                # 自动模式：质量足够就通过
                if quality_score >= 7.0:
                    print(f"✅ 质量达标，自动通过")
                    await self._finalize_chapter(chapter_num, chapter_content, quality_result.output)
                    return True
                elif iteration < max_iterations:
                    print(f"   质量未达标，继续迭代")
                    continue
                else:
                    print(f"⚠️  达到最大迭代次数，使用当前版本")
                    await self._finalize_chapter(chapter_num, chapter_content, quality_result.output)
                    return True
                    
        return False
        
    async def _plan_chapter(self, chapter_num: int) -> StageResult:
        """规划章节"""
        print(f"   📋 规划章节...")
        
        proposal = await self.plot_designer.generate_proposal(
            context={"chapter_num": chapter_num},
            task="plan_chapter_arc"
        )
        
        chapter_plan = proposal.content
        self.story_brain.create_chapter_plan(chapter_plan)
        
        print(f"   ✅ 章节规划完成: {chapter_plan.title}")
        print(f"      目标: {len(chapter_plan.objectives)} 个")
        print(f"      推进情节点: {chapter_plan.plot_points_to_advance}")
        
        return StageResult(
            stage=PipelineStage.CHAPTER_PLANNING,
            success=True,
            output=chapter_plan,
            issues=[]
        )
        
    async def _plan_scenes(self, chapter_num: int) -> StageResult:
        """规划场景"""
        print(f"   🎬 规划场景...")
        
        proposal = await self.scene_planner.generate_proposal(
            context={"chapter_num": chapter_num},
            task="plan_scenes"
        )
        
        print(f"   ✅ 场景规划完成")
        
        return StageResult(
            stage=PipelineStage.SCENE_PLANNING,
            success=True,
            output=proposal.content,
            issues=[]
        )
        
    async def _write_chapter(self, chapter_num: int) -> StageResult:
        """写作章节"""
        print(f"   ✍️  写作章节...")
        
        # 先发展角色状态
        for char_id in self.story_brain.characters.keys():
            char_proposal = await self.character_developer.generate_proposal(
                context={"character_id": char_id, "chapter_num": chapter_num},
                task="develop_character_arc"
            )
            # 角色状态暂存，等章节确认后再正式更新
            
        proposal = await self.writer.generate_proposal(
            context={"chapter_num": chapter_num},
            task="write_chapter"
        )
        
        content = proposal.content
        word_count = len(content)
        
        print(f"   ✅ 写作完成: {word_count} 字")
        
        return StageResult(
            stage=PipelineStage.WRITING,
            success=True,
            output=content,
            issues=[]
        )
        
    async def _check_consistency(self, chapter_num: int, content: str) -> StageResult:
        """检查一致性"""
        print(f"   🔍 检查一致性...")
        
        proposal = await self.consistency_checker.generate_proposal(
            context={"chapter_num": chapter_num, "chapter_content": content},
            task="check_consistency"
        )
        
        check_result = proposal.content
        issues = check_result.get("issues", [])
        
        if issues:
            print(f"   ⚠️  发现 {len(issues)} 个问题")
        else:
            print(f"   ✅ 一致性检查通过")
            
        return StageResult(
            stage=PipelineStage.CONSISTENCY_CHECK,
            success=True,
            output=check_result,
            issues=issues
        )
        
    async def _edit_chapter(self, chapter_num: int, content: str) -> StageResult:
        """编辑章节"""
        print(f"   📝 编辑润色...")
        
        proposal = await self.editor.generate_proposal(
            context={
                "chapter_num": chapter_num,
                "chapter_content": content,
                "edit_focus": "comprehensive"
            },
            task="edit_chapter"
        )
        
        edited_content = proposal.content
        
        print(f"   ✅ 编辑完成")
        
        return StageResult(
            stage=PipelineStage.EDITING,
            success=True,
            output=edited_content,
            issues=[]
        )
        
    async def _assess_quality(self, chapter_num: int, content: str) -> StageResult:
        """评估质量"""
        print(f"   ⭐ 质量评估...")
        
        proposal = await self.quality_assessor.generate_proposal(
            context={"chapter_num": chapter_num, "chapter_content": content},
            task="assess_quality"
        )
        
        assessment = proposal.content
        
        return StageResult(
            stage=PipelineStage.QUALITY_ASSESSMENT,
            success=True,
            output=assessment,
            issues=[]
        )
        
    async def _get_human_feedback(
        self, 
        chapter_num: int, 
        content: str, 
        assessment: Dict
    ) -> HumanDecision:
        """获取人类反馈"""
        print(f"   👤 等待人类审核...")
        
        if not self.human_feedback_callback:
            return HumanDecision(decision="approve", feedback="")
            
        # 构建反馈请求
        feedback_request = {
            "chapter_num": chapter_num,
            "content_preview": content[:1500] + "..." if len(content) > 1500 else content,
            "word_count": len(content),
            "quality_score": assessment.get("overall_score", 0),
            "strengths": assessment.get("strengths", []),
            "weaknesses": assessment.get("weaknesses", []),
            "improvement_suggestions": assessment.get("improvement_suggestions", [])
        }
        
        # 调用人类反馈回调
        result = self.human_feedback_callback(feedback_request)
        
        # 解析结果
        if isinstance(result, dict):
            return HumanDecision(
                decision=result.get("decision", "approve"),
                feedback=result.get("feedback", ""),
                rollback_to=result.get("rollback_to"),
                specific_changes=result.get("specific_changes")
            )
        else:
            # 简化处理
            return HumanDecision(decision=str(result), feedback="")
            
    async def _revise_based_on_feedback(
        self, 
        chapter_num: int, 
        content: str, 
        feedback: str
    ) -> str:
        """根据反馈修改"""
        print(f"   🔄 根据反馈修改...")
        
        proposal = await self.writer.generate_proposal(
            context={
                "chapter_num": chapter_num,
                "original_content": content,
                "revision_notes": feedback
            },
            task="revise_chapter"
        )
        
        return proposal.content
        
    async def _finalize_chapter(
        self, 
        chapter_num: int, 
        content: str, 
        assessment: Dict
    ):
        """完成章节，更新StoryBrain"""
        
        # 提取执行信息
        plan = self.story_brain.chapter_plans.get(chapter_num)
        
        # 识别实际推进的情节点（需要NLP分析，简化处理）
        plot_points_advanced = plan.plot_points_to_advance if plan else []
        
        # 识别实际埋下的伏笔
        foreshadowing_planted = plan.foreshadowing_to_plant if plan else []
        
        # 构建执行结果
        execution = ChapterExecution(
            chapter_num=chapter_num,
            content=content,
            word_count=len(content),
            plot_points_advanced=plot_points_advanced,
            character_states_after={},  # 需要实际分析
            foreshadowing_planted=foreshadowing_planted,
            foreshadowing_resolved=[],
            consistency_issues=[],
            quality_score=assessment.get("overall_score", 0)
        )
        
        # 记录到StoryBrain
        self.story_brain.record_chapter_execution(execution)
        
        # 保存到文件
        await self._save_chapter(chapter_num, content)
        
        print(f"   ✅ 第{chapter_num}章已完成并保存")
        
    async def _save_chapter(self, chapter_num: int, content: str):
        """保存章节到文件"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 构建文件名：第一章_标题.md 格式
        chapter_prefix = f"第{chapter_num}章"
        plan = self.story_brain.chapter_plans.get(chapter_num)
        if plan and plan.title:
            safe_title = self._sanitize_filename(plan.title)
            chapter_file = self.output_dir / f"{chapter_prefix}_{safe_title}.md"
        else:
            chapter_file = self.output_dir / f"{chapter_prefix}.md"
        
        title = plan.title if plan else f"第{chapter_num}章"
        
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n{content}\n")
    
    def _sanitize_filename(self, name: str) -> str:
        """清理文件名，移除不安全字符"""
        import re
        # 替换不安全的字符
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
        # 移除前后空白
        safe_name = safe_name.strip()
        # 限制长度
        if len(safe_name) > 50:
            safe_name = safe_name[:50]
        return safe_name
            
    async def _export_novel(self) -> str:
        """导出完整小说"""
        print(f"\n{'='*70}")
        print(f"📚 导出完整小说")
        print(f"{'='*70}")
        
        full_content = f"# {self.story_brain.title}\n\n"
        
        for chapter_num in range(1, self.story_brain.target_chapters + 1):
            if chapter_num in self.story_brain.chapter_contents:
                plan = self.story_brain.chapter_plans.get(chapter_num)
                title = plan.title if plan else f"第{chapter_num}章"
                
                full_content += f"## {title}\n\n"
                full_content += self.story_brain.chapter_contents[chapter_num]
                full_content += "\n\n"
                
        # 保存完整小说
        output_file = self.output_dir / "full_novel.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_content)
            
        # 保存StoryBrain状态
        brain_file = self.output_dir / "story_brain.json"
        self.story_brain.save_to_file(str(brain_file))
        
        print(f"✅ 小说已导出: {output_file}")
        print(f"✅ StoryBrain状态已保存: {brain_file}")
        
        return str(output_file)
        
    async def rollback_to_chapter(self, chapter_num: int):
        """
        回滚到指定章节重新创作
        
        这会：
        1. 删除该章节及之后的所有章节
        2. 恢复该章节开始时的StoryBrain状态
        3. 从该章节重新开始创作
        """
        print(f"\n⏮️  回滚到第{chapter_num}章")
        
        # 删除后续章节的记录
        chapters_to_remove = [ch for ch in self.story_brain.chapter_executions.keys() 
                             if ch >= chapter_num]
        for ch in chapters_to_remove:
            del self.story_brain.chapter_executions[ch]
            if ch in self.story_brain.chapter_contents:
                del self.story_brain.chapter_contents[ch]
                
        # 恢复角色状态
        if chapter_num - 1 in self.story_brain.character_states:
            # 保留到前一章的状态
            states_to_remove = [ch for ch in self.story_brain.character_states.keys() 
                               if ch >= chapter_num]
            for ch in states_to_remove:
                del self.story_brain.character_states[ch]
                
        # 恢复情节点状态
        for plot_id, plot in self.story_brain.plot_points.items():
            if plot.chapter_resolved and plot.chapter_resolved >= chapter_num:
                plot.status = "active"
                plot.chapter_resolved = None
                self.story_brain.active_plot_points.add(plot_id)
                self.story_brain.resolved_plot_points.discard(plot_id)
                
        print(f"✅ 已回滚到第{chapter_num}章")
        print(f"   活跃情节点: {len(self.story_brain.active_plot_points)}")
        print(f"   已解决情节点: {len(self.story_brain.resolved_plot_points)}")
        
        # 从该章节重新开始
        for ch in range(chapter_num, self.story_brain.target_chapters + 1):
            success = await self._create_chapter(ch)
            if not success:
                print(f"❌ 第{ch}章创作失败")
                break


class DeepEditor:
    """
    深度编辑器
    
    与表面润色不同，深度编辑可以：
    1. 重构情节（添加/删除场景）
    2. 调整角色行为
    3. 修改对话以更好地展现性格
    4. 添加或删除伏笔
    5. 调整节奏
    """
    
    def __init__(self, model: Any, story_brain: StoryBrain):
        self.model = model
        self.story_brain = story_brain
        
    async def deep_edit_chapter(
        self, 
        chapter_num: int, 
        edit_instructions: Dict
    ) -> str:
        """
        深度编辑章节
        
        edit_instructions可以包含：
        - add_scenes: 添加场景
        - remove_scenes: 删除场景
        - modify_character_actions: 修改角色行为
        - adjust_pacing: 调整节奏
        - add_foreshadowing: 添加伏笔
        - resolve_plot_point: 解决情节点
        """
        
        original_content = self.story_brain.chapter_contents.get(chapter_num, "")
        plan = self.story_brain.chapter_plans.get(chapter_num)
        
        prompt = f"""作为深度编辑，请对第{chapter_num}章进行结构性修改：

原章节内容：
{original_content}

原章节规划：
{plan.to_dict() if plan else {}}

修改指令：
{edit_instructions}

请进行以下深度编辑：
1. 根据指令重构情节
2. 确保修改后的内容仍符合整体故事逻辑
3. 保持角色一致性
4. 维持指定的情感基调
5. 确保与前后章节的连贯性

请输出修改后的完整章节内容。
"""
        
        edited_content = await self.model.generate(prompt, max_tokens=4000)
        
        # 更新StoryBrain中的记录
        if chapter_num in self.story_brain.chapter_executions:
            self.story_brain.chapter_executions[chapter_num].content = edited_content
            self.story_brain.chapter_contents[chapter_num] = edited_content
            
        return edited_content
        
    async def add_subplot(
        self, 
        start_chapter: int, 
        end_chapter: int, 
        subplot_description: str
    ):
        """
        在指定章节范围内添加副情节
        """
        # 创建新的情节点
        new_plot_point = PlotPoint(
            id=f"subplot_{start_chapter}_{end_chapter}",
            description=subplot_description,
            chapter_introduced=start_chapter,
            chapter_resolved=end_chapter,
            status="active"
        )
        
        self.story_brain.register_plot_point(new_plot_point)
        
        # 修改相关章节以融入副情节
        for ch in range(start_chapter, end_chapter + 1):
            if ch in self.story_brain.chapter_plans:
                plan = self.story_brain.chapter_plans[ch]
                plan.plot_points_to_advance.append(new_plot_point.id)
                
                # 重新创作该章节
                # 这里需要调用pipeline重新写作
                
    async def merge_chapters(self, chapter_nums: List[int]) -> int:
        """
        合并多个章节为一个
        
        返回合并后的新章节号
        """
        # 实现章节合并逻辑
        pass
        
    async def split_chapter(self, chapter_num: int, split_points: List[int]) -> List[int]:
        """
        将一个章节拆分为多个
        
        split_points: 拆分位置（字数位置）
        返回新章节号列表
        """
        # 实现章节拆分逻辑
        pass
