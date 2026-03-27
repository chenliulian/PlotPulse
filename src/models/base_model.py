"""模型基类"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List


class BaseModel(ABC):
    """AI模型基类"""
    
    def __init__(self, model_name: str, config: Optional[Dict] = None):
        self.model_name = model_name
        self.config = config or {}
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """生成文本"""
        pass
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """对话模式"""
        pass
    
    def get_name(self) -> str:
        return self.model_name
