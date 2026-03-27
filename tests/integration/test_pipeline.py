"""流水线集成测试"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import tempfile
import shutil
from pathlib import Path

from src.pipeline import NovelPipeline


class TestNovelPipeline:
    """测试小说创作流水线"""
    
    @pytest.fixture
    def mock_model(self):
        model = Mock()
        model.generate = AsyncMock(return_value="生成的内容")
        return model
    
    @pytest.fixture
    def temp_dir(self):
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    @pytest.fixture
    async def pipeline(self, mock_model, temp_dir):
        pipeline = NovelPipeline(mock_model, output_dir=temp_dir)
        yield pipeline
    
    @pytest.mark.asyncio
    async def test_create_novel(self, mock_model, temp_dir):
        pipeline = NovelPipeline(mock_model, output_dir=temp_dir)
        novel_id = await pipeline.create_novel(
            title="测试小说",
            theme="测试主题",
            genre="测试类型"
        )
        
        assert novel_id is not None
        assert pipeline.novel_data["title"] == "测试小说"
        assert pipeline.novel_data["theme"] == "测试主题"
    
    @pytest.mark.asyncio
    async def test_generate_outline(self, mock_model, temp_dir):
        pipeline = NovelPipeline(mock_model, output_dir=temp_dir)
        await pipeline.create_novel("测试", "主题", "类型")
        
        result = await pipeline.generate_outline()
        
        assert "plot_outline" in result
        assert pipeline.novel_data["outline"] is not None
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self, mock_model, temp_dir):
        pipeline = NovelPipeline(mock_model, output_dir=temp_dir)
        
        # 创建小说
        novel_id = await pipeline.create_novel(
            title="完整测试",
            theme="测试",
            genre="测试",
            num_chapters=2
        )
        
        # 生成大纲
        await pipeline.generate_outline()
        
        # 生成角色
        await pipeline.generate_characters()
        
        # 生成世界观
        await pipeline.generate_world()
        
        # 写作章节
        for i in range(1, 3):
            await pipeline.write_chapter(i)
        
        assert len(pipeline.novel_data["chapters"]) == 2
        assert pipeline.novel_data["status"] == "completed"
