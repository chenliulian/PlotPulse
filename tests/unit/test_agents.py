"""Agent单元测试"""

import pytest
from unittest.mock import Mock, AsyncMock

from src.agents import (
    PlotAgent, CharacterAgent, WorldbuildingAgent,
    WritingAgent, EditingAgent, ReviewerAgent
)


class TestPlotAgent:
    """测试情节设计Agent"""
    
    @pytest.fixture
    def mock_model(self):
        model = Mock()
        model.generate = AsyncMock(return_value="测试大纲内容")
        return model
    
    @pytest.fixture
    def agent(self, mock_model):
        return PlotAgent(mock_model)
    
    @pytest.mark.asyncio
    async def test_execute(self, agent):
        input_data = {
            "theme": "复仇",
            "genre": "武侠",
            "style": "传统"
        }
        
        result = await agent.execute(input_data)
        
        assert "plot_outline" in result
        assert "main_conflict" in result
        assert "plot_points" in result


class TestCharacterAgent:
    """测试角色设计Agent"""
    
    @pytest.fixture
    def mock_model(self):
        model = Mock()
        model.generate = AsyncMock(return_value="测试角色内容")
        return model
    
    @pytest.fixture
    def agent(self, mock_model):
        return CharacterAgent(mock_model)
    
    @pytest.mark.asyncio
    async def test_execute(self, agent):
        input_data = {
            "plot_outline": "测试大纲",
            "num_characters": 3
        }
        
        result = await agent.execute(input_data)
        
        assert "characters" in result
        assert "protagonist" in result
        assert "antagonist" in result


class TestWritingAgent:
    """测试写作Agent"""
    
    @pytest.fixture
    def mock_model(self):
        model = Mock()
        model.generate = AsyncMock(return_value="测试章节内容")
        return model
    
    @pytest.fixture
    def agent(self, mock_model):
        return WritingAgent(mock_model)
    
    @pytest.mark.asyncio
    async def test_execute(self, agent):
        input_data = {
            "chapter_num": 1,
            "outline": "测试大纲",
            "characters": [],
            "world": {}
        }
        
        result = await agent.execute(input_data)
        
        assert "chapter_num" in result
        assert "content" in result
        assert "word_count" in result
