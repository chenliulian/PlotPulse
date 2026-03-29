"""CharacterAgent 测试用例"""

import asyncio
from unittest.mock import Mock, patch

import pytest

from src.agents.character_agent import CharacterAgent
from src.models.base_model import BaseModel


class MockModel(BaseModel):
    """模拟模型"""
    
    def __init__(self):
        super().__init__("mock_model")
    
    async def generate(self, prompt, **kwargs):
        return "测试角色内容"
    
    async def chat(self, messages, **kwargs):
        return "模拟对话内容"


class TestCharacterAgent:
    """CharacterAgent 测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        self.model = MockModel()
        self.character_agent = CharacterAgent(self.model)
    
    async def test_execute(self):
        """测试执行方法"""
        # 准备输入数据
        input_data = {
            "plot_outline": "测试情节大纲",
            "num_characters": 3
        }
        
        # 执行
        with patch.object(self.model, 'generate', return_value="测试角色内容"):
            result = await self.character_agent.execute(input_data)
        
        # 验证
        assert result is not None
        assert "characters" in result
        assert "protagonist" in result
        assert "antagonist" in result
        assert isinstance(result["characters"], list)
    
    async def test_execute_with_default_num_characters(self):
        """测试使用默认角色数量执行"""
        # 准备输入数据（不指定角色数量）
        input_data = {
            "plot_outline": "测试情节大纲"
        }
        
        # 执行
        with patch.object(self.model, 'generate', return_value="测试角色内容"):
            result = await self.character_agent.execute(input_data)
        
        # 验证
        assert result is not None
        assert "characters" in result
    
    def test_build_prompt(self):
        """测试构建提示词"""
        # 准备数据
        plot_outline = "测试情节大纲"
        num_characters = 3
        
        # 执行
        prompt = self.character_agent._build_prompt(plot_outline, num_characters)
        
        # 验证
        assert prompt is not None
        assert "测试情节大纲" in prompt
        assert "3个主要角色" in prompt
        assert "姓名" in prompt
        assert "年龄、外貌特征" in prompt
        assert "性格特点" in prompt
        assert "背景故事" in prompt
        assert "动机和目标" in prompt
        assert "角色弧线" in prompt
        assert "与其他角色的关系" in prompt
    
    def test_parse_characters(self):
        """测试解析角色信息"""
        # 准备数据
        text = "测试角色内容"
        
        # 执行
        characters = self.character_agent._parse_characters(text)
        
        # 验证
        assert characters is not None
        assert isinstance(characters, list)
        assert len(characters) > 0
        assert "name" in characters[0]
        assert "description" in characters[0]
    
    def test_identify_protagonist(self):
        """测试识别主角"""
        # 准备数据
        text = "测试角色内容"
        
        # 执行
        protagonist = self.character_agent._identify_protagonist(text)
        
        # 验证
        assert protagonist is not None
        assert "name" in protagonist
        assert "role" in protagonist
        assert protagonist["role"] == "protagonist"
    
    def test_identify_antagonist(self):
        """测试识别反派"""
        # 准备数据
        text = "测试角色内容"
        
        # 执行
        antagonist = self.character_agent._identify_antagonist(text)
        
        # 验证
        assert antagonist is not None
        assert "name" in antagonist
        assert "role" in antagonist
        assert antagonist["role"] == "antagonist"


if __name__ == "__main__":
    pytest.main([__file__])
