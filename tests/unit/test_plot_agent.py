"""PlotAgent 测试用例"""

import asyncio
from unittest.mock import Mock, patch

import pytest

from src.agents.plot_agent import PlotAgent
from src.models.base_model import BaseModel


class MockModel(BaseModel):
    """模拟模型"""
    
    def __init__(self):
        super().__init__("mock_model")
    
    async def generate(self, prompt, **kwargs):
        return "测试大纲内容"
    
    async def chat(self, messages, **kwargs):
        return "模拟对话内容"


class TestPlotAgent:
    """PlotAgent 测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        self.model = MockModel()
        self.plot_agent = PlotAgent(self.model)
    
    async def test_execute(self):
        """测试执行方法"""
        # 准备输入数据
        input_data = {
            "theme": "科幻冒险",
            "genre": "科幻",
            "style": "硬科幻"
        }
        
        # 执行
        with patch.object(self.model, 'generate', return_value="测试大纲内容"):
            result = await self.plot_agent.execute(input_data)
        
        # 验证
        assert result is not None
        assert "plot_outline" in result
        assert result["plot_outline"] == "测试大纲内容"
        assert "main_conflict" in result
        assert "plot_points" in result
        assert isinstance(result["plot_points"], list)
    
    async def test_execute_with_minimal_input(self):
        """测试使用最小输入执行"""
        # 准备输入数据（只有主题）
        input_data = {
            "theme": "科幻冒险"
        }
        
        # 执行
        with patch.object(self.model, 'generate', return_value="测试大纲内容"):
            result = await self.plot_agent.execute(input_data)
        
        # 验证
        assert result is not None
        assert "plot_outline" in result
    
    async def test_build_prompt(self):
        """测试构建提示词"""
        # 准备输入数据
        input_data = {
            "theme": "科幻冒险",
            "genre": "科幻",
            "style": "硬科幻"
        }
        
        # 执行
        prompt = self.plot_agent._build_prompt(input_data)
        
        # 验证
        assert prompt is not None
        assert "科幻冒险" in prompt
        assert "科幻" in prompt
        assert "硬科幻" in prompt
        assert "主要冲突" in prompt
        assert "故事弧线" in prompt
        assert "关键情节点" in prompt
        assert "高潮设计" in prompt
        assert "结局构思" in prompt
    
    def test_extract_conflict(self):
        """测试提取冲突"""
        # 准备数据
        outline = "测试大纲内容，包含主要冲突"
        
        # 执行
        conflict = self.plot_agent._extract_conflict(outline)
        
        # 验证
        assert conflict is not None
        assert isinstance(conflict, str)
    
    def test_extract_plot_points(self):
        """测试提取情节点"""
        # 准备数据
        outline = "测试大纲内容，包含多个情节点"
        
        # 执行
        plot_points = self.plot_agent._extract_plot_points(outline)
        
        # 验证
        assert plot_points is not None
        assert isinstance(plot_points, list)
        assert len(plot_points) > 0


if __name__ == "__main__":
    pytest.main([__file__])
