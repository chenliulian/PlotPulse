"""工作流管理"""

from typing import List, Any, Dict
from .agent import BaseAgent


class Workflow:
    """工作流编排器"""
    
    def __init__(self, name: str):
        self.name = name
        self.agents: List[BaseAgent] = []
        self.context: Dict[str, Any] = {}
    
    def add_agent(self, agent: BaseAgent):
        """添加Agent到工作流"""
        self.agents.append(agent)
    
    async def execute(self, initial_input: Any) -> Any:
        """按顺序执行所有Agent"""
        result = initial_input
        for agent in self.agents:
            result = await agent.execute(result)
            self.context[agent.get_name()] = result
        return result
