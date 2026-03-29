"""小说创作主流程"""

from typing import Dict, Any, Optional
from pathlib import Path

from src.agents import (
    PlotAgent, CharacterAgent, WorldbuildingAgent,
    WritingAgent, EditingAgent, ReviewerAgent
)
from src.models import BaseModel
from src.tools import Storage


class NovelPipeline:
    """小说创作完整流程"""
    
    def __init__(
        self,
        model: BaseModel,
        output_dir: str = "novels/in_progress",
        config: Optional[Dict] = None
    ):
        self.model = model
        self.output_dir = Path(output_dir)
        self.config = config or {}
        self.storage = Storage()
        
        # 初始化所有Agent
        self.plot_agent = PlotAgent(model)
        self.character_agent = CharacterAgent(model)
        self.world_agent = WorldbuildingAgent(model)
        self.writing_agent = WritingAgent(model)
        self.editing_agent = EditingAgent(model)
        self.reviewer_agent = ReviewerAgent(model)
        
        # 创作状态
        self.novel_id: Optional[str] = None
        self.novel_data: Dict[str, Any] = {}
    
    async def create_novel(
        self,
        title: str,
        theme: str,
        genre: str,
        style: str = "",
        num_chapters: int = 10
    ) -> str:
        """
        创建新小说项目
        
        Returns:
            novel_id: 小说项目ID
        """
        import uuid
        from datetime import datetime
        
        self.novel_id = str(uuid.uuid4())[:8]
        self.novel_data = {
            "id": self.novel_id,
            "title": title,
            "theme": theme,
            "genre": genre,
            "style": style,
            "num_chapters": num_chapters,
            "created_at": datetime.now().isoformat(),
            "status": "planning",
            "outline": None,
            "characters": None,
            "world": None,
            "chapters": []
        }
        
        # 创建小说目录
        novel_dir = self.output_dir / f"novel_{self.novel_id}"
        novel_dir.mkdir(parents=True, exist_ok=True)
        (novel_dir / "chapters").mkdir(exist_ok=True)
        (novel_dir / "final").mkdir(exist_ok=True)
        
        return self.novel_id
    
    async def generate_outline(self) -> Dict:
        """生成小说大纲"""
        if not self.novel_id:
            raise ValueError("No novel project created")
        
        plot_data = await self.plot_agent.execute({
            "theme": self.novel_data["theme"],
            "genre": self.novel_data["genre"],
            "style": self.novel_data["style"]
        })
        
        self.novel_data["outline"] = plot_data
        self.novel_data["status"] = "outlined"
        
        await self._save_progress()
        return plot_data
    
    async def generate_characters(self) -> Dict:
        """生成角色设定"""
        if not self.novel_data.get("outline"):
            raise ValueError("Outline not generated yet")
        
        character_data = await self.character_agent.execute({
            "plot_outline": self.novel_data["outline"]["plot_outline"],
            "num_characters": self.config.get("num_characters", 5)
        })
        
        self.novel_data["characters"] = character_data
        await self._save_progress()
        return character_data
    
    async def generate_world(self) -> Dict:
        """生成世界观设定"""
        world_data = await self.world_agent.execute({
            "genre": self.novel_data["genre"],
            "era": self.config.get("era", "现代")
        })
        
        self.novel_data["world"] = world_data
        await self._save_progress()
        return world_data
    
    async def write_chapter(self, chapter_num: int) -> Dict:
        """写作单章"""
        chapter_data = await self.writing_agent.execute({
            "chapter_num": chapter_num,
            "outline": self.novel_data["outline"],
            "characters": self.novel_data["characters"],
            "world": self.novel_data["world"]
        })
        
        # 编辑润色
        edited = await self.editing_agent.execute({
            "content": chapter_data["content"],
            "edit_type": "polish"
        })
        chapter_data["edited_content"] = edited["edited"]
        
        # 保存章节
        self.novel_data["chapters"].append(chapter_data)
        await self._save_chapter(chapter_num, chapter_data)
        await self._save_progress()
        
        return chapter_data
    
    async def write_all_chapters(self):
        """写作所有章节"""
        for i in range(1, self.novel_data["num_chapters"] + 1):
            print(f"Writing chapter {i}...")
            await self.write_chapter(i)
        
        self.novel_data["status"] = "completed"
        await self._save_progress()
    
    async def review_novel(self) -> Dict:
        """审阅整部小说"""
        # 合并所有章节
        full_text = "\n\n".join([
            ch["edited_content"] for ch in self.novel_data["chapters"]
        ])
        
        review = await self.reviewer_agent.execute({
            "content": full_text,
            "review_type": "comprehensive"
        })
        
        self.novel_data["review"] = review
        await self._save_progress()
        return review
    
    async def _save_progress(self):
        """保存创作进度"""
        novel_dir = self.output_dir / f"novel_{self.novel_id}"
        self.storage.save_json(
            "metadata.json",
            self.novel_data,
            str(novel_dir.relative_to(self.storage.base_dir))
        )
    
    async def _save_chapter(self, chapter_num: int, chapter_data: Dict):
        """保存章节文件"""
        novel_dir = self.output_dir / f"novel_{self.novel_id}"
        
        # 构建文件名：第一章_标题.md 格式
        chapter_prefix = f"第{chapter_num}章"
        chapter_title = chapter_data.get('title', '')
        if chapter_title:
            safe_title = self._sanitize_filename(chapter_title)
            filename = f"{chapter_prefix}_{safe_title}.md"
        else:
            filename = f"{chapter_prefix}.md"
        
        content = f"""# 第{chapter_num}章

{chapter_data.get('edited_content', chapter_data['content'])}
"""
        self.storage.save_text(
            filename,
            content,
            str(novel_dir / "chapters")
        )
    
    def _sanitize_filename(self, name: str) -> str:
        """清理文件名，移除不安全字符"""
        import re
        # 替换不安全的字符
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
        # 移除前后空白
        safe_name = safe_name.strip()
        # 限制长度
        if len(safe_name) > 50:
            safe_name = safe_name[:50]
        return safe_name
    
    async def export_novel(self, format: str = "markdown") -> str:
        """导出完整小说"""
        novel_dir = self.output_dir / f"novel_{self.novel_id}"
        
        # 合并所有章节
        full_content = f"# {self.novel_data['title']}\n\n"
        
        for chapter in self.novel_data["chapters"]:
            full_content += f"## 第{chapter['chapter_num']}章\n\n"
            full_content += chapter.get("edited_content", chapter["content"])
            full_content += "\n\n"
        
        # 保存完整版本
        self.storage.save_text(
            "full_novel.md",
            full_content,
            str(novel_dir / "final")
        )
        
        return str(novel_dir / "final" / "full_novel.md")
