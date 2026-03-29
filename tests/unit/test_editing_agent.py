"""EditingAgent 测试用例"""

import asyncio
from unittest.mock import Mock, patch

import pytest

from src.agents.editing_agent import EditingAgent
from src.models.base_model import BaseModel


class MockModel(BaseModel):
    """模拟模型"""
    
    def __init__(self):
        super().__init__("mock_model")
    
    async def generate(self, prompt, **kwargs):
        return "修改后的内容"
    
    async def chat(self, messages, **kwargs):
        return "模拟对话内容"


class TestEditingAgent:
    """EditingAgent 测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        self.model = MockModel()
        self.editing_agent = EditingAgent(self.model)
    
    async def test_execute_polish(self):
        """测试执行润色操作"""
        # 准备输入数据
        input_data = {
            "content": "测试内容",
            "edit_type": "polish"
        }
        
        # 执行
        with patch.object(self.model, 'generate', return_value="润色后的内容"):
            result = await self.editing_agent.execute(input_data)
        
        # 验证
        assert result is not None
        assert result["original"] == "测试内容"
        assert result["edited"] == "润色后的内容"
        assert "changes" in result
        assert isinstance(result["changes"], list)
    
    async def test_execute_grammar(self):
        """测试执行语法检查操作"""
        # 准备输入数据
        input_data = {
            "content": "测试内容",
            "edit_type": "grammar"
        }
        
        # 执行
        with patch.object(self.model, 'generate', return_value="语法修正后的内容"):
            result = await self.editing_agent.execute(input_data)
        
        # 验证
        assert result is not None
        assert result["original"] == "测试内容"
        assert result["edited"] == "语法修正后的内容"
    
    async def test_execute_style(self):
        """测试执行文风改进操作"""
        # 准备输入数据
        input_data = {
            "content": "测试内容",
            "edit_type": "style"
        }
        
        # 执行
        with patch.object(self.model, 'generate', return_value="文风改进后的内容"):
            result = await self.editing_agent.execute(input_data)
        
        # 验证
        assert result is not None
        assert result["original"] == "测试内容"
        assert result["edited"] == "文风改进后的内容"
    
    async def test_execute_default(self):
        """测试执行默认操作"""
        # 准备输入数据
        input_data = {
            "content": "测试内容",
            "edit_type": "unknown"
        }
        
        # 执行
        result = await self.editing_agent.execute(input_data)
        
        # 验证
        assert result is not None
        assert result["original"] == "测试内容"
        assert result["edited"] == "测试内容"
    
    async def test_polish(self):
        """测试润色方法"""
        # 准备数据
        content = "测试内容"
        
        # 执行
        with patch.object(self.model, 'generate', return_value="润色后的内容"):
            result = await self.editing_agent._polish(content)
        
        # 验证
        assert result == "润色后的内容"
    
    async def test_check_grammar(self):
        """测试语法检查方法"""
        # 准备数据
        content = "测试内容"
        
        # 执行
        with patch.object(self.model, 'generate', return_value="语法修正后的内容"):
            result = await self.editing_agent._check_grammar(content)
        
        # 验证
        assert result == "语法修正后的内容"
    
    async def test_improve_style(self):
        """测试文风改进方法"""
        # 准备数据
        content = "测试内容"
        
        # 执行
        with patch.object(self.model, 'generate', return_value="文风改进后的内容"):
            result = await self.editing_agent._improve_style(content)
        
        # 验证
        assert result == "文风改进后的内容"
    
    def test_identify_changes(self):
        """测试识别修改内容方法"""
        # 准备数据
        original = "原始内容"
        edited = "修改后的内容"
        
        # 执行
        changes = self.editing_agent._identify_changes(original, edited)
        
        # 验证
        assert changes is not None
        assert isinstance(changes, list)
        assert len(changes) > 0


if __name__ == "__main__":
    pytest.main([__file__])
