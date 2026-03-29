"""WorldbuildingAgent 测试用例"""

import asyncio
from unittest.mock import Mock, patch

import pytest

from src.agents.worldbuilding_agent import WorldbuildingAgent
from src.models.base_model import BaseModel


class MockModel(BaseModel):
    """模拟模型"""
    
    def __init__(self):
        super().__init__("mock_model")
    
    async def generate(self, prompt, **kwargs):
        return "测试世界观内容"
    
    async def chat(self, messages, **kwargs):
        return "模拟对话内容"


class TestWorldbuildingAgent:
    """WorldbuildingAgent 测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        self.model = MockModel()
        self.world_agent = WorldbuildingAgent(self.model)
    
    async def test_execute(self):
        """测试执行方法"""
        # 准备输入数据
        input_data = {
            "genre": "科幻",
            "era": "未来"
        }
        
        # 执行
        with patch.object(self.model, 'generate', return_value="测试世界观内容"):
            result = await self.world_agent.execute(input_data)
        
        # 验证
        assert result is not None
        assert "world_description" in result
        assert result["world_description"] == "测试世界观内容"
        assert "settings" in result
        assert "rules" in result
        assert "history" in result
        assert isinstance(result["settings"], list)
        assert isinstance(result["rules"], list)
        assert isinstance(result["history"], str)
    
    async def test_execute_with_default_era(self):
        """测试使用默认时代执行"""
        # 准备输入数据（不指定时代）
        input_data = {
            "genre": "科幻"
        }
        
        # 执行
        with patch.object(self.model, 'generate', return_value="测试世界观内容"):
            result = await self.world_agent.execute(input_data)
        
        # 验证
        assert result is not None
        assert "world_description" in result
    
    def test_build_prompt(self):
        """测试构建提示词"""
        # 准备数据
        genre = "科幻"
        era = "未来"
        
        # 执行
        prompt = self.world_agent._build_prompt(genre, era)
        
        # 验证
        assert prompt is not None
        assert "科幻" in prompt
        assert "未来" in prompt
        assert "地理环境" in prompt
        assert "社会结构" in prompt
        assert "政治体系" in prompt
        assert "经济系统" in prompt
        assert "文化习俗" in prompt
        assert "宗教信仰" in prompt
        assert "科技/魔法水平" in prompt
        assert "历史背景" in prompt
    
    def test_extract_settings(self):
        """测试提取设置"""
        # 准备数据
        text = "测试世界观内容"
        
        # 执行
        settings = self.world_agent._extract_settings(text)
        
        # 验证
        assert settings is not None
        assert isinstance(settings, list)
        assert len(settings) > 0
    
    def test_extract_rules(self):
        """测试提取规则"""
        # 准备数据
        text = "测试世界观内容"
        
        # 执行
        rules = self.world_agent._extract_rules(text)
        
        # 验证
        assert rules is not None
        assert isinstance(rules, list)
        assert len(rules) > 0
    
    def test_extract_history(self):
        """测试提取历史背景"""
        # 准备数据
        text = "测试世界观内容"
        
        # 执行
        history = self.world_agent._extract_history(text)
        
        # 验证
        assert history is not None
        assert isinstance(history, str)


if __name__ == "__main__":
    pytest.main([__file__])
