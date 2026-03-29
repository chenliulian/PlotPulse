"""WritingAgent 测试用例"""

import asyncio
from unittest.mock import Mock, patch

import pytest

from src.agents.writing_agent import WritingAgent
from src.models.base_model import BaseModel


class MockModel(BaseModel):
    """模拟模型"""
    
    def __init__(self):
        super().__init__("mock_model")
    
    async def generate(self, prompt, **kwargs):
        return "测试章节内容"
    
    async def chat(self, messages, **kwargs):
        return "模拟对话内容"


class TestWritingAgent:
    """WritingAgent 测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        self.model = MockModel()
        self.writing_agent = WritingAgent(self.model)
    
    async def test_execute(self):
        """测试执行方法"""
        # 准备输入数据
        input_data = {
            "chapter_num": 1,
            "outline": "测试大纲",
            "characters": [{"name": "角色1", "description": "描述1"}],
            "world": {"world_description": "测试世界观"}
        }
        
        # 执行
        with patch.object(self.model, 'generate', return_value="测试章节内容"):
            result = await self.writing_agent.execute(input_data)
        
        # 验证
        assert result is not None
        assert result["chapter_num"] == 1
        assert result["content"] == "测试章节内容"
        assert "word_count" in result
        assert isinstance(result["word_count"], int)
        assert "scenes" in result
        assert isinstance(result["scenes"], list)
    
    async def test_execute_with_default_chapter_num(self):
        """测试使用默认章节号执行"""
        # 准备输入数据（不指定章节号）
        input_data = {
            "outline": "测试大纲",
            "characters": [{"name": "角色1", "description": "描述1"}],
            "world": {"world_description": "测试世界观"}
        }
        
        # 执行
        with patch.object(self.model, 'generate', return_value="测试章节内容"):
            result = await self.writing_agent.execute(input_data)
        
        # 验证
        assert result is not None
        assert result["chapter_num"] == 1
    
    def test_build_chapter_prompt(self):
        """测试构建章节提示词"""
        # 准备数据
        chapter_num = 1
        outline = "测试大纲"
        characters = [{"name": "角色1", "description": "描述1"}]
        world = {"world_description": "测试世界观"}
        
        # 执行
        prompt = self.writing_agent._build_chapter_prompt(
            chapter_num, outline, characters, world
        )
        
        # 验证
        assert prompt is not None
        assert "第1章内容" in prompt
        assert "测试大纲" in prompt
        assert "角色1" in prompt
        assert "测试世界观" in prompt
        assert "使用生动的描写" in prompt
        assert "保持人物性格一致性" in prompt
        assert "推进情节发展" in prompt
        assert "适当加入对话" in prompt
        assert "营造氛围和情绪" in prompt
    
    def test_extract_scenes(self):
        """测试提取场景信息"""
        # 准备数据
        content = "测试章节内容，包含多个场景"
        
        # 执行
        scenes = self.writing_agent._extract_scenes(content)
        
        # 验证
        assert scenes is not None
        assert isinstance(scenes, list)
        assert len(scenes) > 0


if __name__ == "__main__":
    pytest.main([__file__])
