"""角色设计Agent"""

from typing import Any, Dict, List
from .base_agent import NovelAgent


class CharacterAgent(NovelAgent):
    """负责角色设计和开发"""
    
    def __init__(self, model, config=None):
        super().__init__("CharacterAgent", model, config)
    
    async def execute(self, input_data: Dict) -> Dict:
        """
        设计小说角色
        input_data: 包含情节大纲、角色数量要求等
        """
        plot_outline = input_data.get("plot_outline", "")
        num_characters = input_data.get("num_characters", 3)
        
        prompt = self._build_prompt(plot_outline, num_characters)
        characters_text = await self.generate(prompt)
        
        return {
            "characters": self._parse_characters(characters_text),
            "protagonist": self._identify_protagonist(characters_text),
            "antagonist": self._identify_antagonist(characters_text)
        }
    
    def _build_prompt(self, plot_outline: str, num_characters: int) -> str:
        return f"""基于以下情节大纲，设计{num_characters}个主要角色：

情节大纲：
{plot_outline}

请为每个角色提供：
1. 姓名
2. 年龄、外貌特征
3. 性格特点
4. 背景故事
5. 动机和目标
6. 角色弧线
7. 与其他角色的关系
"""
    
    def _parse_characters(self, text: str) -> List[Dict]:
        # 解析角色信息
        return [{"name": "角色名", "description": "描述"}]
    
    def _identify_protagonist(self, text: str) -> Dict:
        return {"name": "主角", "role": "protagonist"}
    
    def _identify_antagonist(self, text: str) -> Dict:
        return {"name": "反派", "role": "antagonist"}
