"""基础Agent类"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAgent(ABC):
    """所有Agent的基类"""
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        self.name = name
        self.config = config or {}
    
    @abstractmethod
    async def execute(self, input_data: Any) -> Any:
        """执行Agent的主要任务"""
        pass
    
    def get_name(self) -> str:
        return self.name
