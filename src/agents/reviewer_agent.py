"""审阅Agent"""

from typing import Any, Dict
from .base_agent import NovelAgent


class ReviewerAgent(NovelAgent):
    """负责内容审阅和质量评估"""
    
    def __init__(self, model, config=None):
        super().__init__("ReviewerAgent", model, config)
    
    async def execute(self, input_data: Dict) -> Dict:
        """
        审阅内容
        input_data: 包含待审阅的文本
        """
        content = input_data.get("content", "")
        review_type = input_data.get("review_type", "comprehensive")
        
        if review_type == "comprehensive":
            review = await self._comprehensive_review(content)
        elif review_type == "plot":
            review = await self._review_plot(content)
        elif review_type == "character":
            review = await self._review_characters(content)
        else:
            review = await self._comprehensive_review(content)
        
        return review
    
    async def _comprehensive_review(self, content: str) -> Dict:
        """综合审阅"""
        prompt = f"""请对以下小说内容进行全面审阅：

{content}

请从以下方面进行评估：
1. 情节连贯性和吸引力
2. 角色塑造和发展
3. 对话质量
4. 描写技巧
5. 节奏把控
6. 主题表达
7. 改进建议

请提供详细的审阅报告。
"""
        review_text = await self.generate(prompt)
        
        return {
            "review_type": "comprehensive",
            "review_text": review_text,
            "score": self._calculate_score(review_text),
            "suggestions": self._extract_suggestions(review_text)
        }
    
    async def _review_plot(self, content: str) -> Dict:
        """审阅情节"""
        return {"review_type": "plot", "score": 8.0}
    
    async def _review_characters(self, content: str) -> Dict:
        """审阅角色"""
        return {"review_type": "character", "score": 8.5}
    
    def _calculate_score(self, review_text: str) -> float:
        # 基于审阅文本计算分数
        return 8.0
    
    def _extract_suggestions(self, review_text: str) -> list:
        # 提取改进建议
        return ["建议1", "建议2"]
