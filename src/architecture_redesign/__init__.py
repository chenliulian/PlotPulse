"""
PlotPulse 架构重构模块

这个模块提供了全新的小说创作系统架构，解决了原架构的以下问题：
1. 缺乏全局故事状态管理
2. 章节间缺乏记忆机制
3. 大纲与执行脱节
4. 角色状态追踪缺失
5. 缺乏一致性检查机制
6. 写作流程缺乏迭代深度
7. 编辑Agent功能过于简单

新架构核心组件：
- StoryBrain: 中央状态管理器
- CollaborativeAgents: 多Agent协作系统
- IterativePipeline: 迭代式创作流程
"""

from .story_brain import (
    StoryBrain,
    CharacterState,
    PlotPoint,
    ChapterPlan,
    ChapterExecution,
    StoryElementType
)

from .collaborative_agents import (
    BaseCollaborativeAgent,
    PlotDesignerAgent,
    CharacterDeveloperAgent,
    ScenePlannerAgent,
    WriterAgent,
    ConsistencyCheckerAgent,
    EditorAgent,
    QualityAssessorAgent,
    AgentRole,
    AgentProposal,
    CollaborationResult
)

from .iterative_pipeline import (
    IterativeNovelPipeline,
    DeepEditor,
    PipelineStage,
    StageResult,
    HumanDecision
)

__all__ = [
    # StoryBrain
    'StoryBrain',
    'CharacterState',
    'PlotPoint',
    'ChapterPlan',
    'ChapterExecution',
    'StoryElementType',
    
    # Collaborative Agents
    'BaseCollaborativeAgent',
    'PlotDesignerAgent',
    'CharacterDeveloperAgent',
    'ScenePlannerAgent',
    'WriterAgent',
    'ConsistencyCheckerAgent',
    'EditorAgent',
    'QualityAssessorAgent',
    'AgentRole',
    'AgentProposal',
    'CollaborationResult',
    
    # Iterative Pipeline
    'IterativeNovelPipeline',
    'DeepEditor',
    'PipelineStage',
    'StageResult',
    'HumanDecision'
]
