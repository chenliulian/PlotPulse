"""Agent基类"""

from typing import Any, Dict, Optional
from src.core.agent import BaseAgent as CoreBaseAgent
from src.core.memory import Memory
from src.models.base_model import BaseModel


class NovelAgent(CoreBaseAgent):
    """小说创作Agent基类"""
    
    def __init__(
        self, 
        name: str, 
        model: BaseModel,
        config: Optional[Dict] = None
    ):
        super().__init__(name, config)
        self.model = model
        self.memory = Memory()
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """调用模型生成内容"""
        return await self.model.generate(prompt, **kwargs)
    
    async def execute(self, input_data: Any) -> Any:
        """子类需要实现此方法"""
        raise NotImplementedError
