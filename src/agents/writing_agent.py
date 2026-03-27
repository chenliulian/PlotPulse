"""写作Agent"""

from typing import Any, Dict
from .base_agent import NovelAgent


class WritingAgent(NovelAgent):
    """负责具体章节写作"""
    
    def __init__(self, model, config=None):
        super().__init__("WritingAgent", model, config)
    
    async def execute(self, input_data: Dict) -> Dict:
        """
        写作章节内容
        input_data: 包含大纲、角色、世界观等信息
        """
        chapter_num = input_data.get("chapter_num", 1)
        outline = input_data.get("outline", "")
        characters = input_data.get("characters", [])
        world = input_data.get("world", {})
        
        prompt = self._build_chapter_prompt(
            chapter_num, outline, characters, world
        )
        chapter_content = await self.generate(prompt)
        
        return {
            "chapter_num": chapter_num,
            "content": chapter_content,
            "word_count": len(chapter_content),
            "scenes": self._extract_scenes(chapter_content)
        }
    
    def _build_chapter_prompt(
        self, 
        chapter_num: int, 
        outline: str,
        characters: list,
        world: dict
    ) -> str:
        return f"""请创作第{chapter_num}章内容：

章节大纲：
{outline}

角色信息：
{characters}

世界观设定：
{world}

写作要求：
1. 使用生动的描写
2. 保持人物性格一致性
3. 推进情节发展
4. 适当加入对话
5. 营造氛围和情绪

请直接输出章节正文：
"""
    
    def _extract_scenes(self, content: str) -> list:
        # 提取场景信息
        return ["场景1", "场景2"]
