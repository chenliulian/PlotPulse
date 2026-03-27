"""Agent相关路由"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/agents", tags=["agents"])


class AgentExecuteRequest(BaseModel):
    agent_type: str
    input_data: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None


@router.get("/")
async def list_agents():
    """列出所有可用Agent"""
    return {
        "agents": [
            {"name": "plot", "description": "情节设计Agent"},
            {"name": "character", "description": "角色设计Agent"},
            {"name": "worldbuilding", "description": "世界观构建Agent"},
            {"name": "writing", "description": "写作Agent"},
            {"name": "editing", "description": "编辑Agent"},
            {"name": "reviewer", "description": "审阅Agent"}
        ]
    }


@router.post("/execute")
async def execute_agent(request: AgentExecuteRequest):
    """执行指定Agent"""
    # TODO: 实现Agent执行
    return {
        "agent": request.agent_type,
        "status": "executed",
        "result": {}
    }


@router.get("/{agent_name}/config")
async def get_agent_config(agent_name: str):
    """获取Agent配置"""
    # TODO: 实现配置获取
    return {
        "agent": agent_name,
        "config": {}
    }
