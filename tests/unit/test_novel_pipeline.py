"""NovelPipeline 测试用例"""

import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.pipeline.novel_pipeline import NovelPipeline
from src.models.base_model import BaseModel


class MockModel(BaseModel):
    """模拟模型"""
    
    def __init__(self):
        super().__init__("mock_model")
    
    async def generate(self, prompt, **kwargs):
        return "模拟生成内容"
    
    async def chat(self, messages, **kwargs):
        return "模拟对话内容"


class TestNovelPipeline:
    """NovelPipeline 测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.model = MockModel()
        self.pipeline = NovelPipeline(
            model=self.model,
            output_dir=os.path.join(self.temp_dir, "novels", "in_progress")
        )
        # 设置storage的base_dir为临时目录
        self.pipeline.storage.base_dir = Path(self.temp_dir)
    
    def teardown_method(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    async def test_create_novel(self):
        """测试创建小说项目"""
        # 执行
        novel_id = await self.pipeline.create_novel(
            title="测试小说",
            theme="科幻冒险",
            genre="科幻",
            style="硬科幻",
            num_chapters=5
        )
        
        # 验证
        assert novel_id is not None
        assert len(novel_id) == 8
        assert self.pipeline.novel_id == novel_id
        assert self.pipeline.novel_data["title"] == "测试小说"
        assert self.pipeline.novel_data["theme"] == "科幻冒险"
        assert self.pipeline.novel_data["genre"] == "科幻"
        assert self.pipeline.novel_data["style"] == "硬科幻"
        assert self.pipeline.novel_data["num_chapters"] == 5
        assert self.pipeline.novel_data["status"] == "planning"
        
        # 验证目录创建
        novel_dir = Path(self.temp_dir) / "novels" / "in_progress" / f"novel_{novel_id}"
        assert novel_dir.exists()
        assert (novel_dir / "chapters").exists()
        assert (novel_dir / "final").exists()
    
    async def test_generate_outline(self):
        """测试生成小说大纲"""
        # 先创建小说项目
        await self.pipeline.create_novel(
            title="测试小说",
            theme="科幻冒险",
            genre="科幻",
            num_chapters=5
        )
        
        # 执行
        with patch.object(self.model, 'generate', return_value="测试大纲内容"):
            outline = await self.pipeline.generate_outline()
        
        # 验证
        assert outline is not None
        assert "plot_outline" in outline
        assert "main_conflict" in outline
        assert "plot_points" in outline
        assert self.pipeline.novel_data["status"] == "outlined"
        assert self.pipeline.novel_data["outline"] == outline
    
    async def test_generate_characters(self):
        """测试生成角色设定"""
        # 先创建小说项目并生成大纲
        await self.pipeline.create_novel(
            title="测试小说",
            theme="科幻冒险",
            genre="科幻",
            num_chapters=5
        )
        
        with patch.object(self.model, 'generate', return_value="测试角色内容"):
            await self.pipeline.generate_outline()
            characters = await self.pipeline.generate_characters()
        
        # 验证
        assert characters is not None
        assert "characters" in characters
        assert "protagonist" in characters
        assert "antagonist" in characters
        assert self.pipeline.novel_data["characters"] == characters
    
    async def test_generate_world(self):
        """测试生成世界观设定"""
        # 先创建小说项目
        await self.pipeline.create_novel(
            title="测试小说",
            theme="科幻冒险",
            genre="科幻",
            num_chapters=5
        )
        
        # 执行
        with patch.object(self.model, 'generate', return_value="测试世界观内容"):
            world = await self.pipeline.generate_world()
        
        # 验证
        assert world is not None
        assert "world_description" in world
        assert "settings" in world
        assert "rules" in world
        assert "history" in world
        assert self.pipeline.novel_data["world"] == world
    
    async def test_write_chapter(self):
        """测试写作单章"""
        # 先创建小说项目并完成前期准备
        await self.pipeline.create_novel(
            title="测试小说",
            theme="科幻冒险",
            genre="科幻",
            num_chapters=5
        )
        
        # 模拟数据
        self.pipeline.novel_data["outline"] = {"plot_outline": "测试大纲"}
        self.pipeline.novel_data["characters"] = {"characters": []}
        self.pipeline.novel_data["world"] = {"world_description": "测试世界观"}
        
        # 执行
        with patch.object(self.model, 'generate', side_effect=[
            "测试章节内容",  # 写作
            "测试编辑内容"   # 编辑
        ]):
            chapter = await self.pipeline.write_chapter(1)
        
        # 验证
        assert chapter is not None
        assert chapter["chapter_num"] == 1
        assert "content" in chapter
        assert "edited_content" in chapter
        assert "word_count" in chapter
        assert "scenes" in chapter
        assert len(self.pipeline.novel_data["chapters"]) == 1
        
        # 验证文件保存
        novel_dir = Path(self.temp_dir) / "novels" / "in_progress" / f"novel_{self.pipeline.novel_id}"
        chapter_file = novel_dir / "chapters" / "chapter_01.md"
        assert chapter_file.exists()
    
    async def test_write_all_chapters(self):
        """测试写作所有章节"""
        # 先创建小说项目并完成前期准备
        await self.pipeline.create_novel(
            title="测试小说",
            theme="科幻冒险",
            genre="科幻",
            num_chapters=2
        )
        
        # 模拟数据
        self.pipeline.novel_data["outline"] = {"plot_outline": "测试大纲"}
        self.pipeline.novel_data["characters"] = {"characters": []}
        self.pipeline.novel_data["world"] = {"world_description": "测试世界观"}
        
        # 执行
        with patch.object(self.model, 'generate', side_effect=[
            "测试章节1内容", "测试编辑1内容",  # 第一章
            "测试章节2内容", "测试编辑2内容"   # 第二章
        ]):
            await self.pipeline.write_all_chapters()
        
        # 验证
        assert len(self.pipeline.novel_data["chapters"]) == 2
        assert self.pipeline.novel_data["status"] == "completed"
        
        # 验证文件保存
        novel_dir = Path(self.temp_dir) / "novels" / "in_progress" / f"novel_{self.pipeline.novel_id}"
        chapter1_file = novel_dir / "chapters" / "chapter_01.md"
        chapter2_file = novel_dir / "chapters" / "chapter_02.md"
        assert chapter1_file.exists()
        assert chapter2_file.exists()
    
    async def test_review_novel(self):
        """测试审阅整部小说"""
        # 先创建小说项目并完成前期准备
        await self.pipeline.create_novel(
            title="测试小说",
            theme="科幻冒险",
            genre="科幻",
            num_chapters=1
        )
        
        # 模拟数据
        self.pipeline.novel_data["outline"] = {"plot_outline": "测试大纲"}
        self.pipeline.novel_data["characters"] = {"characters": []}
        self.pipeline.novel_data["world"] = {"world_description": "测试世界观"}
        self.pipeline.novel_data["chapters"] = [{
            "chapter_num": 1,
            "content": "测试章节内容",
            "edited_content": "测试编辑内容"
        }]
        
        # 执行
        with patch.object(self.model, 'generate', return_value="测试审阅内容"):
            review = await self.pipeline.review_novel()
        
        # 验证
        assert review is not None
        assert "review_type" in review
        assert "review_text" in review
        assert "score" in review
        assert "suggestions" in review
        assert self.pipeline.novel_data["review"] == review
    
    async def test_export_novel(self):
        """测试导出完整小说"""
        # 先创建小说项目并完成前期准备
        await self.pipeline.create_novel(
            title="测试小说",
            theme="科幻冒险",
            genre="科幻",
            num_chapters=1
        )
        
        # 模拟数据
        self.pipeline.novel_data["chapters"] = [{
            "chapter_num": 1,
            "content": "测试章节内容",
            "edited_content": "测试编辑内容"
        }]
        
        # 执行
        export_path = await self.pipeline.export_novel()
        
        # 验证
        assert export_path is not None
        assert os.path.exists(export_path)
        
        # 验证文件内容
        with open(export_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert "# 测试小说" in content
        assert "## 第1章" in content
        assert "测试编辑内容" in content
    
    async def test_generate_outline_without_novel(self):
        """测试未创建小说项目时生成大纲"""
        with pytest.raises(ValueError, match="No novel project created"):
            await self.pipeline.generate_outline()
    
    async def test_generate_characters_without_outline(self):
        """测试未生成大纲时生成角色"""
        await self.pipeline.create_novel(
            title="测试小说",
            theme="科幻冒险",
            genre="科幻",
            num_chapters=5
        )
        
        with pytest.raises(ValueError, match="Outline not generated yet"):
            await self.pipeline.generate_characters()


if __name__ == "__main__":
    pytest.main([__file__])
