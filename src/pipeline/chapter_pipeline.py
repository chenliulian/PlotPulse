"""章节创作流程"""

from typing import Dict, Any, Optional

from src.agents import WritingAgent, EditingAgent, ReviewerAgent
from src.models import BaseModel


class ChapterPipeline:
    """单章创作流程"""
    
    def __init__(
        self,
        model: BaseModel,
        config: Optional[Dict] = None
    ):
        self.model = model
        self.config = config or {}
        
        self.writing_agent = WritingAgent(model)
        self.editing_agent = EditingAgent(model)
        self.reviewer_agent = ReviewerAgent(model)
    
    async def write_chapter(
        self,
        chapter_num: int,
        outline: Dict,
        characters: Dict,
        world: Dict,
        previous_chapter: Optional[str] = None
    ) -> Dict:
        """
        创作单章完整流程
        
        Args:
            chapter_num: 章节编号
            outline: 大纲信息
            characters: 角色信息
            world: 世界观信息
            previous_chapter: 前一章内容（用于连贯性）
        
        Returns:
            包含章节内容和元数据的字典
        """
        # 1. 初稿写作
        print(f"Writing chapter {chapter_num} draft...")
        draft = await self.writing_agent.execute({
            "chapter_num": chapter_num,
            "outline": outline,
            "characters": characters,
            "world": world,
            "previous_chapter": previous_chapter
        })
        
        # 2. 润色
        print(f"Polishing chapter {chapter_num}...")
        polished = await self.editing_agent.execute({
            "content": draft["content"],
            "edit_type": "polish"
        })
        
        # 3. 语法检查
        print(f"Checking grammar for chapter {chapter_num}...")
        corrected = await self.editing_agent.execute({
            "content": polished["edited"],
            "edit_type": "grammar"
        })
        
        # 4. 审阅
        print(f"Reviewing chapter {chapter_num}...")
        review = await self.reviewer_agent.execute({
            "content": corrected["edited"],
            "review_type": "comprehensive"
        })
        
        # 5. 根据审阅意见改进（可选）
        if review["score"] < 7.0:
            print(f"Improving chapter {chapter_num} based on review...")
            improved = await self.editing_agent.execute({
                "content": corrected["edited"],
                "edit_type": "style"
            })
            final_content = improved["edited"]
        else:
            final_content = corrected["edited"]
        
        return {
            "chapter_num": chapter_num,
            "draft": draft["content"],
            "final_content": final_content,
            "word_count": len(final_content),
            "review": review,
            "scenes": draft.get("scenes", [])
        }
    
    async def revise_chapter(
        self,
        chapter_content: str,
        feedback: str
    ) -> str:
        """
        根据反馈修改章节
        
        Args:
            chapter_content: 当前章节内容
            feedback: 修改意见
        
        Returns:
            修改后的内容
        """
        # 构建修改提示
        prompt = f"""请根据以下反馈修改章节内容：

反馈：
{feedback}

当前内容：
{chapter_content}

请输出修改后的完整章节内容：
"""
        
        revised = await self.model.generate(prompt)
        return revised
