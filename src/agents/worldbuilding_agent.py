"""世界观构建Agent"""

from typing import Any, Dict
from .base_agent import NovelAgent


class WorldbuildingAgent(NovelAgent):
    """负责小说世界观的构建"""
    
    def __init__(self, model, config=None):
        super().__init__("WorldbuildingAgent", model, config)
    
    async def execute(self, input_data: Dict) -> Dict:
        """
        构建小说世界观
        input_data: 包含类型、时代、风格等信息
        """
        genre = input_data.get("genre", "")
        era = input_data.get("era", "")
        
        prompt = self._build_prompt(genre, era)
        world_description = await self.generate(prompt)
        
        return {
            "world_description": world_description,
            "settings": self._extract_settings(world_description),
            "rules": self._extract_rules(world_description),
            "history": self._extract_history(world_description)
        }
    
    def _build_prompt(self, genre: str, era: str) -> str:
        return f"""请为{type}类型小说构建世界观设定：
类型：{genre}
时代背景：{era}

请详细描述：
1. 地理环境
2. 社会结构
3. 政治体系
4. 经济系统
5. 文化习俗
6. 宗教信仰
7. 科技/魔法水平
8. 历史背景
"""
    
    def _extract_settings(self, text: str) -> list:
        return ["场景1", "场景2"]
    
    def _extract_rules(self, text: str) -> list:
        return ["规则1", "规则2"]
    
    def _extract_history(self, text: str) -> str:
        return "历史背景摘要"
