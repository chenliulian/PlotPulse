"""
协作式Agent架构

核心理念：
1. 专业Agent各司其职
2. 通过StoryBrain共享状态
3. 协商机制解决冲突
4. 迭代优化而非一次性生成
"""

from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import json

from .story_brain import StoryBrain, ChapterPlan, ChapterExecution, CharacterState, PlotPoint


class AgentRole(Enum):
    """Agent角色类型"""
    PLOT_DESIGNER = "plot_designer"        # 情节设计师
    CHARACTER_DEVELOPER = "character_dev"  # 角色发展师
    SCENE_PLANNER = "scene_planner"        # 场景规划师
    WRITER = "writer"                      # 写作执行者
    CONSISTENCY_CHECKER = "consistency"    # 一致性检查员
    EDITOR = "editor"                      # 编辑润色师
    QUALITY_ASSESSOR = "quality"           # 质量评估师


@dataclass
class AgentProposal:
    """Agent提案"""
    agent_role: AgentRole
    proposal_type: str
    content: Any
    rationale: str
    priority: int = 5  # 1-10, 越高越重要
    
    
@dataclass
class CollaborationResult:
    """协作结果"""
    success: bool
    final_output: Any
    agent_contributions: Dict[AgentRole, Any]
    iterations: int
    issues_resolved: List[str]
    issues_remaining: List[str]


class BaseCollaborativeAgent(ABC):
    """协作Agent基类"""
    
    def __init__(self, role: AgentRole, model: Any, story_brain: StoryBrain):
        self.role = role
        self.model = model
        self.story_brain = story_brain
        
    @abstractmethod
    async def generate_proposal(self, context: Dict, task: str) -> AgentProposal:
        """生成提案"""
        pass
        
    @abstractmethod
    async def evaluate_proposal(self, proposal: AgentProposal, context: Dict) -> Dict:
        """评估其他Agent的提案"""
        pass
        
    async def generate(self, prompt: str, **kwargs) -> str:
        """调用模型生成内容"""
        return await self.model.generate(prompt, **kwargs)


class PlotDesignerAgent(BaseCollaborativeAgent):
    """
    情节设计师
    
    职责：
    1. 设计整体故事结构
    2. 规划情节点和转折点
    3. 管理故事节奏
    4. 协调多条情节线
    """
    
    def __init__(self, model: Any, story_brain: StoryBrain):
        super().__init__(AgentRole.PLOT_DESIGNER, model, story_brain)
        
    async def generate_proposal(self, context: Dict, task: str) -> AgentProposal:
        """生成情节设计方案"""
        
        if task == "design_overall_structure":
            return await self._design_overall_structure(context)
        elif task == "plan_chapter_arc":
            return await self._plan_chapter_arc(context)
        elif task == "design_plot_points":
            return await self._design_plot_points(context)
        else:
            raise ValueError(f"Unknown task: {task}")
            
    async def _design_overall_structure(self, context: Dict) -> AgentProposal:
        """设计整体故事结构"""
        
        prompt = f"""作为情节设计师，请为以下小说设计完整的三幕结构：

小说信息：
- 标题：{self.story_brain.title}
- 主题：{self.story_brain.theme}
- 类型：{self.story_brain.genre}
- 风格：{self.story_brain.style}
- 目标章节数：{self.story_brain.target_chapters}

角色设定：
{json.dumps(self.story_brain.characters, ensure_ascii=False, indent=2)}

请提供：
1. 三幕结构划分（每幕包含哪些章节）
2. 每幕的核心冲突和主题发展
3. 关键转折点位置
4. 高潮设计
5. 结局构思
6. 主要情节点列表（每个情节点包含：ID、描述、引入章节、计划解决章节、相关角色）

输出格式为JSON：
{{
    "act_structure": {{
        "act1": {{"chapters": [1, 2, 3], "focus": "..."}},
        "act2": {{"chapters": [4, 5, 6, 7], "focus": "..."}},
        "act3": {{"chapters": [8, 9, 10], "focus": "..."}}
    }},
    "plot_points": [
        {{"id": "pp1", "description": "...", "chapter_introduced": 1, "chapter_resolved": 5, "related_characters": ["..."], "foreshadowing_for": null}},
        ...
    ],
    "turning_points": [{{"chapter": 3, "description": "..."}}, ...],
    "climax": {{"chapter": 9, "description": "..."}},
    "ending": {{"type": "...", "description": "..."}}
}}
"""
        
        response = await self.generate(prompt)
        
        try:
            structure = json.loads(response)
        except json.JSONDecodeError:
            # 如果返回的不是JSON，包装为结构化格式
            structure = {
                "act_structure": {"act1": {}, "act2": {}, "act3": {}},
                "plot_points": [],
                "raw_response": response
            }
            
        return AgentProposal(
            agent_role=self.role,
            proposal_type="overall_structure",
            content=structure,
            rationale="基于主题和角色设定设计的三幕结构，确保情节张力和主题深度"
        )
        
    async def _plan_chapter_arc(self, context: Dict) -> AgentProposal:
        """规划单章情节弧线"""
        chapter_num = context.get("chapter_num")
        
        # 获取StoryBrain中的相关信息
        story_context = self.story_brain.get_context_for_chapter_planning(chapter_num)
        
        prompt = f"""作为情节设计师，请为第{chapter_num}章设计详细的情节弧线：

小说信息：
- 标题：{self.story_brain.title}
- 主题：{self.story_brain.theme}

前文摘要：
{story_context['previous_chapters_summary']}

活跃情节点：
{json.dumps(story_context['active_plot_points'], ensure_ascii=False, indent=2)}

角色当前状态：
{json.dumps(story_context['character_states'], ensure_ascii=False, indent=2)}

待回收伏笔：
{json.dumps(story_context['pending_foreshadowing'], ensure_ascii=False, indent=2)}

请为第{chapter_num}章设计：
1. 章节标题
2. 本章目标（2-3个）
3. 要推进的情节点ID列表
4. 要发展的角色弧线
5. 要埋下的新伏笔（为未来章节铺垫）
6. 要回收的旧伏笔ID列表
7. 冲突处理（引入新冲突/推进现有冲突/解决冲突）
8. 关键场景列表（每个场景：地点、时间、参与角色、场景目标）
9. 情感基调
10. 预期字数

输出格式为JSON，与ChapterPlan结构一致。
"""
        
        response = await self.generate(prompt)
        
        try:
            plan_data = json.loads(response)
            chapter_plan = ChapterPlan(
                chapter_num=chapter_num,
                title=plan_data.get("title", f"第{chapter_num}章"),
                objectives=plan_data.get("objectives", []),
                plot_points_to_advance=plan_data.get("plot_points_to_advance", []),
                character_arcs_to_develop=plan_data.get("character_arcs_to_develop", []),
                foreshadowing_to_plant=plan_data.get("foreshadowing_to_plant", []),
                conflicts_to_introduce_or_resolve=plan_data.get("conflicts_to_introduce_or_resolve", []),
                expected_word_count=plan_data.get("expected_word_count", 3000),
                key_scenes=plan_data.get("key_scenes", []),
                emotional_tone=plan_data.get("emotional_tone", "neutral")
            )
        except Exception as e:
            # 创建默认规划
            chapter_plan = ChapterPlan(
                chapter_num=chapter_num,
                title=f"第{chapter_num}章",
                objectives=["推进主线情节"],
                plot_points_to_advance=[],
                character_arcs_to_develop=[],
                foreshadowing_to_plant=[],
                conflicts_to_introduce_or_resolve=[],
                expected_word_count=3000,
                key_scenes=[],
                emotional_tone="neutral"
            )
            
        return AgentProposal(
            agent_role=self.role,
            proposal_type="chapter_plan",
            content=chapter_plan,
            rationale=f"基于活跃情节点和角色状态设计的第{chapter_num}章规划"
        )
        
    async def _design_plot_points(self, context: Dict) -> AgentProposal:
        """设计具体情节点"""
        # 实现情节点详细设计
        pass
        
    async def evaluate_proposal(self, proposal: AgentProposal, context: Dict) -> Dict:
        """评估其他Agent的提案"""
        
        evaluation = {
            "approved": True,
            "concerns": [],
            "suggestions": []
        }
        
        if proposal.proposal_type == "chapter_plan":
            plan = proposal.content
            
            # 检查是否推进了活跃情节点
            active_plots = self.story_brain.active_plot_points
            plots_addressed = set(plan.plot_points_to_advance)
            
            unaddressed = active_plots - plots_addressed
            if unaddressed:
                evaluation["concerns"].append(
                    f"未处理活跃情节点: {unaddressed}"
                )
                evaluation["suggestions"].append(
                    f"建议在本章推进或至少提及这些情节点"
                )
                
        return evaluation


class CharacterDeveloperAgent(BaseCollaborativeAgent):
    """
    角色发展师
    
    职责：
    1. 确保角色行为一致性
    2. 设计角色成长弧线
    3. 管理角色关系演变
    4. 验证角色决策合理性
    """
    
    def __init__(self, model: Any, story_brain: StoryBrain):
        super().__init__(AgentRole.CHARACTER_DEVELOPER, model, story_brain)
        
    async def generate_proposal(self, context: Dict, task: str) -> AgentProposal:
        """生成角色发展方案"""
        
        if task == "develop_character_arc":
            return await self._develop_character_arc(context)
        elif task == "validate_character_actions":
            return await self._validate_character_actions(context)
        else:
            raise ValueError(f"Unknown task: {task}")
            
    async def _develop_character_arc(self, context: Dict) -> AgentProposal:
        """发展角色弧线"""
        character_id = context.get("character_id")
        chapter_num = context.get("chapter_num")
        
        # 获取角色历史状态
        character_arc = self.story_brain.get_character_arc(character_id)
        current_state = character_arc[-1] if character_arc else None
        
        prompt = f"""作为角色发展师，请为角色'{character_id}'设计第{chapter_num}章的发展：

角色设定：
{json.dumps(self.story_brain.characters.get(character_id, {}), ensure_ascii=False, indent=2)}

角色历史状态：
{json.dumps([s.to_dict() for s in character_arc], ensure_ascii=False, indent=2)}

请设计：
1. 本章开始时的情绪状态
2. 本章目标（基于角色动机）
3. 关键决策点
4. 本章结束时的状态变化
5. 与其他角色的关系变化
6. 成长阶段推进

输出为JSON格式，与CharacterState结构一致。
"""
        
        response = await self.generate(prompt)
        
        try:
            state_data = json.loads(response)
            new_state = CharacterState(
                chapter=chapter_num,
                emotional_state=state_data.get("emotional_state", "neutral"),
                goals=state_data.get("goals", []),
                relationships=state_data.get("relationships", {}),
                knowledge=set(state_data.get("knowledge", [])),
                development_stage=state_data.get("development_stage", "initial"),
                key_decisions=state_data.get("key_decisions", [])
            )
        except:
            new_state = CharacterState(
                chapter=chapter_num,
                emotional_state="neutral",
                goals=[],
                relationships={},
                knowledge=set(),
                development_stage="initial",
                key_decisions=[]
            )
            
        return AgentProposal(
            agent_role=self.role,
            proposal_type="character_state",
            content=new_state,
            rationale=f"基于角色历史弧线设计的第{chapter_num}章状态"
        )
        
    async def _validate_character_actions(self, context: Dict) -> AgentProposal:
        """验证角色行为合理性"""
        chapter_content = context.get("chapter_content")
        chapter_num = context.get("chapter_num")
        
        # 提取所有角色行为
        # 这里需要NLP分析，简化处理
        
        validation_results = []
        for char_id in self.story_brain.characters.keys():
            prev_state = self.story_brain.get_character_state(chapter_num - 1, char_id)
            if prev_state:
                validation_results.append({
                    "character": char_id,
                    "previous_emotional_state": prev_state.emotional_state,
                    "actions_in_chapter": "需要NLP提取",
                    "consistency_check": "需要NLP分析"
                })
                
        return AgentProposal(
            agent_role=self.role,
            proposal_type="character_validation",
            content=validation_results,
            rationale="验证角色行为与之前状态的一致性"
        )
        
    async def evaluate_proposal(self, proposal: AgentProposal, context: Dict) -> Dict:
        """评估其他Agent的提案"""
        return {"approved": True, "concerns": [], "suggestions": []}


class ScenePlannerAgent(BaseCollaborativeAgent):
    """
    场景规划师
    
    职责：
    1. 设计具体场景结构
    2. 规划场景节奏和转换
    3. 确保场景服务于情节和角色
    4. 管理场景间的过渡
    """
    
    def __init__(self, model: Any, story_brain: StoryBrain):
        super().__init__(AgentRole.SCENE_PLANNER, model, story_brain)
        
    async def generate_proposal(self, context: Dict, task: str) -> AgentProposal:
        """生成场景规划"""
        
        if task == "plan_scenes":
            return await self._plan_scenes(context)
        else:
            raise ValueError(f"Unknown task: {task}")
            
    async def _plan_scenes(self, context: Dict) -> AgentProposal:
        """规划章节内的场景"""
        chapter_num = context.get("chapter_num")
        chapter_plan = self.story_brain.chapter_plans.get(chapter_num)
        
        if not chapter_plan:
            raise ValueError(f"第{chapter_num}章尚未规划")
            
        prompt = f"""作为场景规划师，请为第{chapter_num}章设计详细的场景序列：

章节规划：
- 标题：{chapter_plan.title}
- 目标：{chapter_plan.objectives}
- 情感基调：{chapter_plan.emotional_tone}
- 关键场景大纲：{chapter_plan.key_scenes}

角色状态：
{json.dumps(self.story_brain._get_latest_character_states(chapter_num), ensure_ascii=False, indent=2)}

请设计：
1. 场景列表（每个场景包含）：
   - 场景编号和标题
   - 地点和时间
   - 参与角色
   - 场景目标（推动哪个情节点/角色弧线）
   - 场景冲突
   - 场景结果
   - 预计字数
2. 场景间的过渡设计
3. 节奏控制（紧张-放松的交替）
4. 视角选择（如果是多视角叙事）

输出为详细的场景规划文档。
"""
        
        response = await self.generate(prompt)
        
        return AgentProposal(
            agent_role=self.role,
            proposal_type="scene_plan",
            content={
                "chapter_num": chapter_num,
                "scenes": response,
                "scene_count": len(chapter_plan.key_scenes)
            },
            rationale=f"基于章节目标和角色状态设计的场景序列"
        )
        
    async def evaluate_proposal(self, proposal: AgentProposal, context: Dict) -> Dict:
        """评估其他Agent的提案"""
        return {"approved": True, "concerns": [], "suggestions": []}


class WriterAgent(BaseCollaborativeAgent):
    """
    写作执行者
    
    职责：
    1. 根据规划执行具体写作
    2. 确保执行符合规划
    3. 在约束条件下发挥创意
    4. 保持风格一致性
    """
    
    def __init__(self, model: Any, story_brain: StoryBrain):
        super().__init__(AgentRole.WRITER, model, story_brain)
        
    async def generate_proposal(self, context: Dict, task: str) -> AgentProposal:
        """生成写作内容"""
        
        if task == "write_chapter":
            return await self._write_chapter(context)
        elif task == "revise_chapter":
            return await self._revise_chapter(context)
        else:
            raise ValueError(f"Unknown task: {task}")
            
    async def _write_chapter(self, context: Dict) -> AgentProposal:
        """写作章节"""
        chapter_num = context.get("chapter_num")
        
        # 获取完整上下文
        writing_context = self.story_brain.get_context_for_chapter_writing(chapter_num)
        
        prompt = f"""作为写作执行者，请创作第{chapter_num}章：

小说信息：
- 标题：{writing_context['novel_info']['title']}
- 主题：{writing_context['novel_info']['theme']}
- 类型：{writing_context['novel_info']['genre']}
- 风格：{writing_context['novel_info']['style']}

章节规划：
{json.dumps(writing_context['chapter_plan'], ensure_ascii=False, indent=2)}

前情提要：
{writing_context['previous_chapter_recap'][:800]}...

角色起始状态：
{json.dumps(writing_context['character_states_at_start'], ensure_ascii=False, indent=2)}

活跃情节点：
{json.dumps(writing_context['active_plot_points'], ensure_ascii=False, indent=2)}

一致性约束（必须遵守）：
{chr(10).join(writing_context['consistency_constraints'])}

写作要求：
1. 严格遵守一致性约束
2. 推进章节规划中指定的情节点
3. 展现角色的情绪状态和目标
4. 保持指定的情感基调
5. 适当回收伏笔
6. 为后续章节埋下新伏笔
7. 字数要求：{writing_context['chapter_plan'].get('expected_word_count', 3000)}字

请直接输出章节正文内容，不要包含说明文字。
"""
        
        content = await self.generate(prompt, max_tokens=4000)
        
        return AgentProposal(
            agent_role=self.role,
            proposal_type="chapter_content",
            content=content,
            rationale=f"基于完整上下文创作的第{chapter_num}章"
        )
        
    async def _revise_chapter(self, context: Dict) -> AgentProposal:
        """修改章节"""
        chapter_num = context.get("chapter_num")
        original_content = context.get("original_content")
        revision_notes = context.get("revision_notes")
        
        prompt = f"""作为写作执行者，请根据修改意见修订第{chapter_num}章：

原文：
{original_content}

修改意见：
{revision_notes}

请输出修订后的完整章节内容。
"""
        
        revised_content = await self.generate(prompt, max_tokens=4000)
        
        return AgentProposal(
            agent_role=self.role,
            proposal_type="revised_chapter",
            content=revised_content,
            rationale=f"根据修改意见修订的第{chapter_num}章"
        )
        
    async def evaluate_proposal(self, proposal: AgentProposal, context: Dict) -> Dict:
        """评估其他Agent的提案"""
        return {"approved": True, "concerns": [], "suggestions": []}


class ConsistencyCheckerAgent(BaseCollaborativeAgent):
    """
    一致性检查员
    
    职责：
    1. 检查跨章节一致性
    2. 验证角色行为一致性
    3. 检查时间线逻辑
    4. 验证伏笔回收情况
    """
    
    def __init__(self, model: Any, story_brain: StoryBrain):
        super().__init__(AgentRole.CONSISTENCY_CHECKER, model, story_brain)
        
    async def generate_proposal(self, context: Dict, task: str) -> AgentProposal:
        """生成一致性检查报告"""
        
        if task == "check_consistency":
            return await self._check_consistency(context)
        else:
            raise ValueError(f"Unknown task: {task}")
            
    async def _check_consistency(self, context: Dict) -> AgentProposal:
        """检查一致性"""
        chapter_num = context.get("chapter_num")
        chapter_content = context.get("chapter_content")
        
        # 使用StoryBrain的基础检查
        issues = self.story_brain.check_consistency(chapter_num, chapter_content)
        
        # 使用LLM进行深度检查
        prompt = f"""作为一致性检查员，请深度检查第{chapter_num}章的一致性：

本章内容：
{chapter_content[:2000]}...

前文关键信息：
{self.story_brain._summarize_previous_chapters(chapter_num)}

角色历史状态：
{json.dumps(self.story_brain._get_latest_character_states(chapter_num), ensure_ascii=False, indent=2)}

活跃情节点：
{[self.story_brain.plot_points[pid].description for pid in self.story_brain.active_plot_points]}

请检查：
1. 角色行为是否与之前的状态一致
2. 时间线是否连贯
3. 地点转换是否合理
4. 情节点是否得到适当推进
5. 伏笔是否被正确回收或延续
6. 对话是否符合角色性格
7. 是否有逻辑漏洞

输出格式：
{{
    "issues": [
        {{"type": "...", "description": "...", "severity": "high/medium/low", "suggestion": "..."}}
    ],
    "passed": true/false
}}
"""
        
        response = await self.generate(prompt)
        
        try:
            check_result = json.loads(response)
        except:
            check_result = {"issues": issues, "passed": len(issues) == 0}
            
        return AgentProposal(
            agent_role=self.role,
            proposal_type="consistency_report",
            content=check_result,
            rationale=f"第{chapter_num}章的一致性检查报告"
        )
        
    async def evaluate_proposal(self, proposal: AgentProposal, context: Dict) -> Dict:
        """评估其他Agent的提案"""
        return {"approved": True, "concerns": [], "suggestions": []}


class EditorAgent(BaseCollaborativeAgent):
    """
    编辑润色师
    
    职责：
    1. 语言润色
    2. 结构调整
    3. 删除冗余
    4. 增强表现力
    """
    
    def __init__(self, model: Any, story_brain: StoryBrain):
        super().__init__(AgentRole.EDITOR, model, story_brain)
        
    async def generate_proposal(self, context: Dict, task: str) -> AgentProposal:
        """生成编辑方案"""
        
        if task == "edit_chapter":
            return await self._edit_chapter(context)
        else:
            raise ValueError(f"Unknown task: {task}")
            
    async def _edit_chapter(self, context: Dict) -> AgentProposal:
        """编辑章节"""
        chapter_num = context.get("chapter_num")
        original_content = context.get("chapter_content")
        edit_focus = context.get("edit_focus", "comprehensive")
        
        prompt = f"""作为编辑润色师，请编辑第{chapter_num}章：

原文：
{original_content}

编辑重点：{edit_focus}

请进行以下编辑：
1. 删除冗余和重复内容
2. 优化段落结构
3. 增强描写的表现力
4. 改进对话的自然度
5. 确保节奏张弛有度
6. 修正语言错误

请直接输出编辑后的完整章节，不要包含编辑说明。
"""
        
        edited_content = await self.generate(prompt, max_tokens=4000)
        
        return AgentProposal(
            agent_role=self.role,
            proposal_type="edited_chapter",
            content=edited_content,
            rationale=f"对第{chapter_num}章的综合编辑"
        )
        
    async def evaluate_proposal(self, proposal: AgentProposal, context: Dict) -> Dict:
        """评估其他Agent的提案"""
        return {"approved": True, "concerns": [], "suggestions": []}


class QualityAssessorAgent(BaseCollaborativeAgent):
    """
    质量评估师
    
    职责：
    1. 评估章节质量
    2. 识别改进空间
    3. 对比规划检查完成度
    4. 提供改进建议
    """
    
    def __init__(self, model: Any, story_brain: StoryBrain):
        super().__init__(AgentRole.QUALITY_ASSESSOR, model, story_brain)
        
    async def generate_proposal(self, context: Dict, task: str) -> AgentProposal:
        """生成质量评估"""
        
        if task == "assess_quality":
            return await self._assess_quality(context)
        else:
            raise ValueError(f"Unknown task: {task}")
            
    async def _assess_quality(self, context: Dict) -> AgentProposal:
        """评估质量"""
        chapter_num = context.get("chapter_num")
        chapter_content = context.get("chapter_content")
        chapter_plan = self.story_brain.chapter_plans.get(chapter_num)
        
        prompt = f"""作为质量评估师，请评估第{chapter_num}章的质量：

章节规划目标：
{json.dumps(chapter_plan.to_dict() if chapter_plan else {}, ensure_ascii=False, indent=2)}

实际内容：
{chapter_content[:2000]}...

请评估：
1. 目标完成度（是否达成规划目标）
2. 情节推进效果
3. 角色塑造质量
4. 对话质量
5. 描写质量
6. 整体文学性
7. 改进建议

输出格式：
{{
    "overall_score": 8.5,
    "dimension_scores": {{
        "plot_advancement": 9,
        "character_development": 8,
        "dialogue": 7,
        "description": 8,
        "literary_quality": 9
    }},
    "objectives_achieved": ["..."],
    "objectives_missed": ["..."],
    "strengths": ["..."],
    "weaknesses": ["..."],
    "improvement_suggestions": ["..."]
}}
"""
        
        response = await self.generate(prompt)
        
        try:
            assessment = json.loads(response)
        except:
            assessment = {
                "overall_score": 7.0,
                "dimension_scores": {},
                "improvement_suggestions": ["需要进一步评估"]
            }
            
        return AgentProposal(
            agent_role=self.role,
            proposal_type="quality_assessment",
            content=assessment,
            rationale=f"第{chapter_num}章的质量评估报告"
        )
        
    async def evaluate_proposal(self, proposal: AgentProposal, context: Dict) -> Dict:
        """评估其他Agent的提案"""
        return {"approved": True, "concerns": [], "suggestions": []}
