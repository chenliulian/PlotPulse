"""
StoryBrain - 小说创作系统的核心架构重构

核心理念：
1. 中央状态管理 - 维护完整的故事状态、角色状态、时间线
2. 多Agent协作 - 专业Agent通过协商机制共同创作
3. 迭代式创作 - 支持回滚、重构、深度编辑
4. 一致性保证 - 实时检查跨章节一致性
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path


class StoryElementType(Enum):
    """故事元素类型"""
    PLOT_POINT = "plot_point"           # 情节点
    CHARACTER_ARC = "character_arc"     # 角色弧线
    FORESHADOWING = "foreshadowing"     # 伏笔
    THEME = "theme"                     # 主题
    SETTING = "setting"                 # 场景设定
    CONFLICT = "conflict"               # 冲突
    RESOLUTION = "resolution"           # 解决


@dataclass
class CharacterState:
    """角色动态状态（每章更新）"""
    chapter: int                                    # 当前章节
    emotional_state: str                            # 情绪状态
    goals: List[str]                                # 当前目标
    relationships: Dict[str, str]                   # 与其他角色关系状态
    knowledge: Set[str]                             # 已知信息
    development_stage: str                          # 成长阶段
    key_decisions: List[Dict]                       # 关键决策记录
    
    def to_dict(self) -> Dict:
        return {
            "chapter": self.chapter,
            "emotional_state": self.emotional_state,
            "goals": self.goals,
            "relationships": self.relationships,
            "knowledge": list(self.knowledge),
            "development_stage": self.development_stage,
            "key_decisions": self.key_decisions
        }


@dataclass
class PlotPoint:
    """情节点（可追踪状态）"""
    id: str
    description: str
    chapter_introduced: int
    chapter_resolved: Optional[int] = None
    status: str = "pending"  # pending, active, resolved, abandoned
    related_characters: List[str] = field(default_factory=list)
    foreshadowing_for: Optional[str] = None  # 为哪个后续情节点埋伏笔
    consequences: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "chapter_introduced": self.chapter_introduced,
            "chapter_resolved": self.chapter_resolved,
            "status": self.status,
            "related_characters": self.related_characters,
            "foreshadowing_for": self.foreshadowing_for,
            "consequences": self.consequences
        }


@dataclass
class ChapterPlan:
    """章节规划（写作前制定）"""
    chapter_num: int
    title: str
    objectives: List[str]                           # 本章目标
    plot_points_to_advance: List[str]               # 要推进的情节点
    character_arcs_to_develop: List[str]            # 要发展的角色弧线
    foreshadowing_to_plant: List[str]               # 要埋下的伏笔
    conflicts_to_introduce_or_resolve: List[str]    # 冲突处理
    expected_word_count: int
    key_scenes: List[Dict]                          # 关键场景规划
    emotional_tone: str                             # 情感基调
    
    def to_dict(self) -> Dict:
        return {
            "chapter_num": self.chapter_num,
            "title": self.title,
            "objectives": self.objectives,
            "plot_points_to_advance": self.plot_points_to_advance,
            "character_arcs_to_develop": self.character_arcs_to_develop,
            "foreshadowing_to_plant": self.foreshadowing_to_plant,
            "conflicts_to_introduce_or_resolve": self.conflicts_to_introduce_or_resolve,
            "expected_word_count": self.expected_word_count,
            "key_scenes": self.key_scenes,
            "emotional_tone": self.emotional_tone
        }


@dataclass
class ChapterExecution:
    """章节执行结果（写作后记录）"""
    chapter_num: int
    content: str
    word_count: int
    plot_points_advanced: List[str]                 # 实际推进的情节点
    character_states_after: Dict[str, CharacterState]  # 角色本章后的状态
    foreshadowing_planted: List[str]                # 实际埋下的伏笔
    foreshadowing_resolved: List[str]               # 实际回收的伏笔
    consistency_issues: List[Dict]                  # 一致性问题
    quality_score: float                            # 质量评分
    
    def to_dict(self) -> Dict:
        return {
            "chapter_num": self.chapter_num,
            "word_count": self.word_count,
            "plot_points_advanced": self.plot_points_advanced,
            "character_states_after": {k: v.to_dict() for k, v in self.character_states_after.items()},
            "foreshadowing_planted": self.foreshadowing_planted,
            "foreshadowing_resolved": self.foreshadowing_resolved,
            "consistency_issues": self.consistency_issues,
            "quality_score": self.quality_score
        }


class StoryBrain:
    """
    故事大脑 - 中央状态管理器
    
    职责：
    1. 维护完整的故事状态
    2. 管理角色状态机
    3. 追踪情节点和伏笔
    4. 检查一致性
    5. 为Agent提供上下文
    """
    
    def __init__(self, novel_id: str, title: str):
        self.novel_id = novel_id
        self.title = title
        
        # 基础设定
        self.theme: str = ""
        self.genre: str = ""
        self.style: str = ""
        self.target_chapters: int = 10
        
        # 角色管理
        self.characters: Dict[str, Dict] = {}           # 角色静态设定
        self.character_states: Dict[int, Dict[str, CharacterState]] = {}  # 每章角色状态
        
        # 情节管理
        self.plot_points: Dict[str, PlotPoint] = {}     # 所有情节点
        self.active_plot_points: Set[str] = set()       # 活跃情节点
        self.resolved_plot_points: Set[str] = set()     # 已解决情节点
        
        # 伏笔管理
        self.foreshadowing_planted: Dict[str, Dict] = {}    # 已埋下的伏笔
        self.foreshadowing_resolved: Dict[str, int] = {}    # 已回收的伏笔
        
        # 章节管理
        self.chapter_plans: Dict[int, ChapterPlan] = {}         # 章节规划
        self.chapter_executions: Dict[int, ChapterExecution] = {}  # 章节执行结果
        self.chapter_contents: Dict[int, str] = {}              # 章节内容
        
        # 主题追踪
        self.themes: Dict[str, Dict] = {}               # 主题及其表现
        
        # 时间线管理
        self.timeline: List[Dict] = []                  # 故事时间线事件
        
        # 一致性规则
        self.consistency_rules: List[Dict] = []         # 一致性检查规则
        
    def initialize_story(self, theme: str, genre: str, style: str, 
                        target_chapters: int, characters: List[Dict]):
        """初始化故事"""
        self.theme = theme
        self.genre = genre
        self.style = style
        self.target_chapters = target_chapters
        
        # 初始化角色
        for char in characters:
            char_id = char.get("name", "unknown")
            self.characters[char_id] = char
            # 初始状态
            initial_state = CharacterState(
                chapter=0,
                emotional_state=char.get("initial_emotion", "neutral"),
                goals=char.get("initial_goals", []),
                relationships={},
                knowledge=set(),
                development_stage="initial",
                key_decisions=[]
            )
            self.character_states[0] = {char_id: initial_state}
            
    def register_plot_point(self, plot_point: PlotPoint):
        """注册情节点"""
        self.plot_points[plot_point.id] = plot_point
        self.active_plot_points.add(plot_point.id)
        
    def update_plot_point_status(self, plot_point_id: str, status: str, 
                                 chapter: Optional[int] = None):
        """更新情节点状态"""
        if plot_point_id in self.plot_points:
            self.plot_points[plot_point_id].status = status
            if status == "resolved" and chapter:
                self.plot_points[plot_point_id].chapter_resolved = chapter
                self.active_plot_points.discard(plot_point_id)
                self.resolved_plot_points.add(plot_point_id)
                
    def update_character_state(self, chapter: int, character_id: str, 
                              state: CharacterState):
        """更新角色状态"""
        if chapter not in self.character_states:
            self.character_states[chapter] = {}
        self.character_states[chapter][character_id] = state
        
    def get_character_state(self, chapter: int, character_id: str) -> Optional[CharacterState]:
        """获取角色在特定章节的状态"""
        if chapter in self.character_states:
            return self.character_states[chapter].get(character_id)
        return None
        
    def get_character_arc(self, character_id: str) -> List[CharacterState]:
        """获取角色的完整弧线"""
        arc = []
        for chapter in sorted(self.character_states.keys()):
            if character_id in self.character_states[chapter]:
                arc.append(self.character_states[chapter][character_id])
        return arc
        
    def plant_foreshadowing(self, foreshadowing_id: str, target_plot_point: str, 
                           chapter: int, description: str):
        """埋下伏笔"""
        self.foreshadowing_planted[foreshadowing_id] = {
            "target": target_plot_point,
            "chapter_planted": chapter,
            "description": description,
            "status": "pending"
        }
        
    def resolve_foreshadowing(self, foreshadowing_id: str, chapter: int):
        """回收伏笔"""
        if foreshadowing_id in self.foreshadowing_planted:
            self.foreshadowing_planted[foreshadowing_id]["status"] = "resolved"
            self.foreshadowing_planted[foreshadowing_id]["chapter_resolved"] = chapter
            self.foreshadowing_resolved[foreshadowing_id] = chapter
            
    def create_chapter_plan(self, plan: ChapterPlan):
        """创建章节规划"""
        self.chapter_plans[plan.chapter_num] = plan
        
    def record_chapter_execution(self, execution: ChapterExecution):
        """记录章节执行结果"""
        self.chapter_executions[execution.chapter_num] = execution
        self.chapter_contents[execution.chapter_num] = execution.content
        
        # 更新情节点状态
        for plot_point_id in execution.plot_points_advanced:
            self.update_plot_point_status(plot_point_id, "active", execution.chapter_num)
            
        # 更新角色状态
        for char_id, state in execution.character_states_after.items():
            self.update_character_state(execution.chapter_num, char_id, state)
            
        # 更新伏笔状态
        for fs_id in execution.foreshadowing_planted:
            if fs_id in self.foreshadowing_planted:
                self.foreshadowing_planted[fs_id]["status"] = "planted"
        for fs_id in execution.foreshadowing_resolved:
            self.resolve_foreshadowing(fs_id, execution.chapter_num)
            
    def check_consistency(self, new_chapter_num: int, new_content: str) -> List[Dict]:
        """
        检查新章节与已有内容的一致性
        
        检查项：
        1. 角色状态一致性
        2. 时间线一致性
        3. 地点一致性
        4. 伏笔回收情况
        5. 情节点推进逻辑
        """
        issues = []
        
        # 检查角色状态一致性
        issues.extend(self._check_character_consistency(new_chapter_num, new_content))
        
        # 检查时间线一致性
        issues.extend(self._check_timeline_consistency(new_chapter_num, new_content))
        
        # 检查伏笔回收
        issues.extend(self._check_foreshadowing_consistency(new_chapter_num, new_content))
        
        # 检查情节点推进
        issues.extend(self._check_plot_consistency(new_chapter_num, new_content))
        
        return issues
        
    def _check_character_consistency(self, chapter_num: int, content: str) -> List[Dict]:
        """检查角色一致性"""
        issues = []
        
        # 获取前一章的角色状态
        prev_chapter = chapter_num - 1
        if prev_chapter in self.character_states:
            prev_states = self.character_states[prev_chapter]
            
            for char_id, prev_state in prev_states.items():
                # 检查角色是否在本章做出了与之前状态矛盾的决策
                # 这需要NLP分析，这里提供框架
                issues.append({
                    "type": "character_consistency",
                    "character": char_id,
                    "previous_state": prev_state.emotional_state,
                    "check": f"Verify {char_id}'s actions align with emotional state: {prev_state.emotional_state}",
                    "severity": "warning"
                })
                
        return issues
        
    def _check_timeline_consistency(self, chapter_num: int, content: str) -> List[Dict]:
        """检查时间线一致性"""
        issues = []
        
        # 检查本章时间标记与整体时间线是否冲突
        # 这需要从内容中提取时间信息
        
        return issues
        
    def _check_foreshadowing_consistency(self, chapter_num: int, content: str) -> List[Dict]:
        """检查伏笔一致性"""
        issues = []
        
        # 检查是否有伏笔在本章被回收但未标记
        # 检查是否有伏笔被过早回收
        
        for fs_id, fs_info in self.foreshadowing_planted.items():
            if fs_info["status"] == "pending":
                # 检查本章内容是否包含该伏笔的回收
                issues.append({
                    "type": "foreshadowing_check",
                    "foreshadowing_id": fs_id,
                    "target": fs_info["target"],
                    "planted_chapter": fs_info["chapter_planted"],
                    "check": f"Check if foreshadowing '{fs_id}' is resolved in this chapter",
                    "severity": "info"
                })
                
        return issues
        
    def _check_plot_consistency(self, chapter_num: int, content: str) -> List[Dict]:
        """检查情节一致性"""
        issues = []
        
        # 检查活跃情节点是否在本章得到推进
        for plot_id in self.active_plot_points:
            plot = self.plot_points[plot_id]
            issues.append({
                "type": "plot_advancement",
                "plot_point": plot_id,
                "description": plot.description,
                "check": f"Verify plot point '{plot_id}' is advanced or maintained",
                "severity": "warning" if plot.chapter_introduced < chapter_num - 2 else "info"
            })
            
        return issues
        
    def get_context_for_chapter_planning(self, chapter_num: int) -> Dict:
        """
        为章节规划提供完整上下文
        """
        context = {
            "novel_info": {
                "title": self.title,
                "theme": self.theme,
                "genre": self.genre,
                "style": self.style,
                "target_chapters": self.target_chapters
            },
            "current_chapter": chapter_num,
            "previous_chapters_summary": self._summarize_previous_chapters(chapter_num),
            "active_plot_points": [self.plot_points[pid].to_dict() for pid in self.active_plot_points],
            "character_states": self._get_latest_character_states(chapter_num),
            "pending_foreshadowing": [fs for fs_id, fs in self.foreshadowing_planted.items() 
                                     if fs["status"] == "pending"],
            "themes_to_develop": list(self.themes.keys()),
            "narrative_momentum": self._calculate_narrative_momentum(chapter_num)
        }
        
        return context
        
    def get_context_for_chapter_writing(self, chapter_num: int) -> Dict:
        """
        为章节写作提供完整上下文
        """
        plan = self.chapter_plans.get(chapter_num)
        
        context = {
            "novel_info": {
                "title": self.title,
                "theme": self.theme,
                "genre": self.genre,
                "style": self.style
            },
            "chapter_plan": plan.to_dict() if plan else {},
            "previous_chapter_recap": self._get_previous_chapter_recap(chapter_num),
            "character_states_at_start": self._get_latest_character_states(chapter_num),
            "active_plot_points": [self.plot_points[pid].to_dict() for pid in self.active_plot_points],
            "foreshadowing_to_resolve": self._get_foreshadowing_for_chapter(chapter_num),
            "consistency_constraints": self._generate_consistency_constraints(chapter_num)
        }
        
        return context
        
    def _summarize_previous_chapters(self, up_to_chapter: int) -> str:
        """总结前面章节的关键内容"""
        summaries = []
        for ch_num in range(1, up_to_chapter):
            if ch_num in self.chapter_executions:
                exec_result = self.chapter_executions[ch_num]
                summaries.append(f"Chapter {ch_num}: Advanced plot points: {exec_result.plot_points_advanced}")
        return "\n".join(summaries)
        
    def _get_latest_character_states(self, chapter_num: int) -> Dict[str, Dict]:
        """获取最新的角色状态"""
        # 找到最近的有记录状态的章节
        for ch in range(chapter_num - 1, -1, -1):
            if ch in self.character_states:
                return {char_id: state.to_dict() for char_id, state in self.character_states[ch].items()}
        return {}
        
    def _get_previous_chapter_recap(self, chapter_num: int) -> str:
        """获取前一章的详细回顾"""
        prev_ch = chapter_num - 1
        if prev_ch in self.chapter_contents:
            content = self.chapter_contents[prev_ch]
            # 提取最后1000字作为回顾
            return content[-1000:] if len(content) > 1000 else content
        return ""
        
    def _get_foreshadowing_for_chapter(self, chapter_num: int) -> List[Dict]:
        """获取本章应该回收的伏笔"""
        result = []
        for fs_id, fs_info in self.foreshadowing_planted.items():
            if fs_info["status"] == "pending":
                # 检查是否计划在本章回收
                plan = self.chapter_plans.get(chapter_num)
                if plan and fs_id in plan.foreshadowing_to_plant:
                    result.append(fs_info)
        return result
        
    def _generate_consistency_constraints(self, chapter_num: int) -> List[str]:
        """生成本章必须遵守的一致性约束"""
        constraints = []
        
        # 角色状态约束
        latest_states = self._get_latest_character_states(chapter_num)
        for char_id, state in latest_states.items():
            constraints.append(f"{char_id} must start with emotional state: {state['emotional_state']}")
            constraints.append(f"{char_id}'s current goals: {state['goals']}")
            
        # 活跃情节点约束
        for plot_id in self.active_plot_points:
            plot = self.plot_points[plot_id]
            constraints.append(f"Must advance or maintain plot point: {plot.description}")
            
        return constraints
        
    def _calculate_narrative_momentum(self, chapter_num: int) -> Dict:
        """计算叙事动量（用于调整节奏）"""
        # 分析最近几章的情节密度
        recent_plot_advancement = []
        for ch in range(max(1, chapter_num - 3), chapter_num):
            if ch in self.chapter_executions:
                recent_plot_advancement.append(len(self.chapter_executions[ch].plot_points_advanced))
                
        avg_advancement = sum(recent_plot_advancement) / len(recent_plot_advancement) if recent_plot_advancement else 0
        
        return {
            "recent_plot_density": avg_advancement,
            "recommended_pacing": "fast" if avg_advancement < 1 else "moderate" if avg_advancement < 3 else "slow",
            "active_conflicts": len(self.active_plot_points)
        }
        
    def save_to_file(self, filepath: str):
        """保存故事状态到文件"""
        data = {
            "novel_id": self.novel_id,
            "title": self.title,
            "theme": self.theme,
            "genre": self.genre,
            "style": self.style,
            "target_chapters": self.target_chapters,
            "characters": self.characters,
            "character_states": {str(k): {cid: s.to_dict() for cid, s in v.items()} 
                                for k, v in self.character_states.items()},
            "plot_points": {pid: pp.to_dict() for pid, pp in self.plot_points.items()},
            "active_plot_points": list(self.active_plot_points),
            "resolved_plot_points": list(self.resolved_plot_points),
            "foreshadowing_planted": self.foreshadowing_planted,
            "foreshadowing_resolved": self.foreshadowing_resolved,
            "chapter_plans": {str(k): v.to_dict() for k, v in self.chapter_plans.items()},
            "chapter_executions": {str(k): v.to_dict() for k, v in self.chapter_executions.items()},
            "themes": self.themes
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    @classmethod
    def load_from_file(cls, filepath: str) -> 'StoryBrain':
        """从文件加载故事状态"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        brain = cls(data["novel_id"], data["title"])
        brain.theme = data.get("theme", "")
        brain.genre = data.get("genre", "")
        brain.style = data.get("style", "")
        brain.target_chapters = data.get("target_chapters", 10)
        brain.characters = data.get("characters", {})
        brain.plot_points = {pid: PlotPoint(**pp) for pid, pp in data.get("plot_points", {}).items()}
        brain.active_plot_points = set(data.get("active_plot_points", []))
        brain.resolved_plot_points = set(data.get("resolved_plot_points", []))
        brain.foreshadowing_planted = data.get("foreshadowing_planted", {})
        brain.foreshadowing_resolved = data.get("foreshadowing_resolved", {})
        brain.themes = data.get("themes", {})
        
        # 恢复角色状态
        for ch_str, states in data.get("character_states", {}).items():
            ch = int(ch_str)
            brain.character_states[ch] = {}
            for cid, s in states.items():
                brain.character_states[ch][cid] = CharacterState(**s)
                
        # 恢复章节计划
        for ch_str, plan_data in data.get("chapter_plans", {}).items():
            brain.chapter_plans[int(ch_str)] = ChapterPlan(**plan_data)
            
        # 恢复章节执行
        for ch_str, exec_data in data.get("chapter_executions", {}).items():
            ch = int(ch_str)
            # 恢复CharacterState对象
            states_after = {cid: CharacterState(**s) for cid, s in exec_data.get("character_states_after", {}).items()}
            exec_data["character_states_after"] = states_after
            brain.chapter_executions[ch] = ChapterExecution(content="", **exec_data)
            
        return brain
