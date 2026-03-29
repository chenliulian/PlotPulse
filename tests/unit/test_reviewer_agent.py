"""ReviewerAgent 测试用例"""

import asyncio
from unittest.mock import Mock, patch

import pytest

from src.agents.reviewer_agent import ReviewerAgent
from src.models.base_model import BaseModel


class MockModel(BaseModel):
    """模拟模型"""
    
    def __init__(self):
        super().__init__("mock_model")
    
    async def generate(self, prompt, **kwargs):
        return "测试审阅内容"
    
    async def chat(self, messages, **kwargs):
        return "模拟对话内容"


class TestReviewerAgent:
    """ReviewerAgent 测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        self.model = MockModel()
        self.reviewer_agent = ReviewerAgent(self.model)
    
    async def test_execute_comprehensive(self):
        """测试执行综合审阅操作"""
        # 准备输入数据
        input_data = {
            "content": "测试内容",
            "review_type": "comprehensive"
        }
        
        # 执行
        with patch.object(self.model, 'generate', return_value="综合审阅内容"):
            result = await self.reviewer_agent.execute(input_data)
        
        # 验证
        assert result is not None
        assert result["review_type"] == "comprehensive"
        assert result["review_text"] == "综合审阅内容"
        assert "score" in result
        assert "suggestions" in result
        assert isinstance(result["score"], float)
        assert isinstance(result["suggestions"], list)
    
    async def test_execute_plot(self):
        """测试执行情节审阅操作"""
        # 准备输入数据
        input_data = {
            "content": "测试内容",
            "review_type": "plot"
        }
        
        # 执行
        result = await self.reviewer_agent.execute(input_data)
        
        # 验证
        assert result is not None
        assert result["review_type"] == "plot"
        assert "score" in result
    
    async def test_execute_character(self):
        """测试执行角色审阅操作"""
        # 准备输入数据
        input_data = {
            "content": "测试内容",
            "review_type": "character"
        }
        
        # 执行
        result = await self.reviewer_agent.execute(input_data)
        
        # 验证
        assert result is not None
        assert result["review_type"] == "character"
        assert "score" in result
    
    async def test_execute_default(self):
        """测试执行默认审阅操作"""
        # 准备输入数据
        input_data = {
            "content": "测试内容",
            "review_type": "unknown"
        }
        
        # 执行
        with patch.object(self.model, 'generate', return_value="默认审阅内容"):
            result = await self.reviewer_agent.execute(input_data)
        
        # 验证
        assert result is not None
        assert result["review_type"] == "comprehensive"
    
    async def test_comprehensive_review(self):
        """测试综合审阅方法"""
        # 准备数据
        content = "测试内容"
        
        # 执行
        with patch.object(self.model, 'generate', return_value="综合审阅内容"):
            result = await self.reviewer_agent._comprehensive_review(content)
        
        # 验证
        assert result is not None
        assert result["review_type"] == "comprehensive"
        assert result["review_text"] == "综合审阅内容"
        assert "score" in result
        assert "suggestions" in result
    
    async def test_review_plot(self):
        """测试情节审阅方法"""
        # 准备数据
        content = "测试内容"
        
        # 执行
        result = await self.reviewer_agent._review_plot(content)
        
        # 验证
        assert result is not None
        assert result["review_type"] == "plot"
        assert "score" in result
    
    async def test_review_characters(self):
        """测试角色审阅方法"""
        # 准备数据
        content = "测试内容"
        
        # 执行
        result = await self.reviewer_agent._review_characters(content)
        
        # 验证
        assert result is not None
        assert result["review_type"] == "character"
        assert "score" in result
    
    def test_calculate_score(self):
        """测试计算分数方法"""
        # 准备数据
        review_text = "测试审阅内容"
        
        # 执行
        score = self.reviewer_agent._calculate_score(review_text)
        
        # 验证
        assert score is not None
        assert isinstance(score, float)
    
    def test_extract_suggestions(self):
        """测试提取改进建议方法"""
        # 准备数据
        review_text = "测试审阅内容，包含改进建议"
        
        # 执行
        suggestions = self.reviewer_agent._extract_suggestions(review_text)
        
        # 验证
        assert suggestions is not None
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0


if __name__ == "__main__":
    pytest.main([__file__])
