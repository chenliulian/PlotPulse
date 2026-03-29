"""情节设计Agent"""

from typing import Any, Dict, List
from .base_agent import NovelAgent


class PlotAgent(NovelAgent):
    """负责小说情节设计"""
    
    def __init__(self, model, config=None):
        super().__init__("PlotAgent", model, config)
    
    async def execute(self, input_data: Dict) -> Dict:
        """
        设计小说情节
        input_data: 包含主题、类型、风格等信息
        """
        # 第一步：生成整体情节大纲
        outline_prompt = self._build_prompt(input_data)
        plot_outline = await self.generate(outline_prompt)
        
        # 第二步：生成详细章节大纲
        num_chapters = input_data.get("num_chapters", 10)
        chapter_prompt = self._build_chapter_prompt(input_data, plot_outline, num_chapters)
        chapter_outlines_raw = await self.generate(chapter_prompt)
        chapter_outlines = self._parse_chapter_outlines(chapter_outlines_raw, num_chapters)
        
        return {
            "plot_outline": plot_outline,
            "chapter_outlines": chapter_outlines,
            "main_conflict": self._extract_conflict(plot_outline),
            "plot_points": self._extract_plot_points(plot_outline)
        }
    
    def _build_prompt(self, input_data: Dict) -> str:
        theme = input_data.get("theme", "")
        genre = input_data.get("genre", "")
        style = input_data.get("style", "")
        
        return f"""请为以下小说设计情节大纲：
主题：{theme}
类型：{genre}
风格：{style}

请提供：
1. 主要冲突
2. 故事弧线（分三幕结构）
3. 关键情节点
4. 高潮设计
5. 结局构思

要求：
- 故事结构完整，有清晰的起承转合
- 情节要有张力和悬念
- 适合后续扩展为{input_data.get("num_chapters", 10)}章的详细大纲
"""
    
    def _build_chapter_prompt(self, input_data: Dict, plot_outline: str, num_chapters: int) -> str:
        """构建章节大纲生成的prompt"""
        theme = input_data.get("theme", "")
        genre = input_data.get("genre", "")
        style = input_data.get("style", "")
        
        return f"""基于以下整体情节大纲，设计详细的章节大纲。

主题：{theme}
类型：{genre}
风格：{style}
总章节数：{num_chapters}

整体情节大纲：
{plot_outline}

请为每一章设计以下内容：
1. 章节标题
2. 章节概要（200-300字）
3. 主要场景
4. 关键情节转折（如有）
5. 本章结尾钩子（吸引读者继续阅读）

请严格按照以下格式输出，共{num_chapters}章：

## 第1章 [章节标题]
**概要**：[章节概要]
**场景**：[主要场景]
**转折**：[关键转折，无则写"无"]
**钩子**：[结尾钩子]

## 第2章 [章节标题]
...

（以此类推，直到第{num_chapters}章）

注意：
- 每章内容要连贯，前后章节有逻辑衔接
- 保持整体故事弧线的三幕结构
- 在适当位置埋下伏笔和悬念
- 高潮部分应该分布在第{int(num_chapters * 0.7)}-{num_chapters}章
"""
    
    def _parse_chapter_outlines(self, raw_text: str, num_chapters: int) -> List[Dict]:
        """解析AI生成的章节大纲文本"""
        chapters = []
        
        # 按章节分割文本
        import re
        chapter_pattern = r'## 第(\d+)章\s*(.+?)\n\*\*概要\*\*：(.+?)(?=\n\*\*|$)'
        matches = re.findall(chapter_pattern, raw_text, re.DOTALL)
        
        for i in range(1, num_chapters + 1):
            chapter_data = {
                "chapter_num": i,
                "title": f"第{i}章",
                "summary": "",
                "scenes": [],
                "twist": "",
                "hook": ""
            }
            
            # 查找对应章节的内容
            for match in matches:
                if int(match[0]) == i:
                    chapter_data["title"] = match[1].strip() if match[1] else f"第{i}章"
                    chapter_data["summary"] = match[2].strip() if match[2] else ""
                    break
            
            # 如果没有匹配到，尝试从原始文本中提取
            if not chapter_data["summary"]:
                # 简单提取：找到第X章后面的内容
                simple_pattern = rf'第{i}章.*?(?:第{i+1}章|$)'
                simple_match = re.search(simple_pattern, raw_text, re.DOTALL)
                if simple_match:
                    chapter_data["summary"] = simple_match.group(0)[:500]
            
            chapters.append(chapter_data)
        
        return chapters
    
    def _extract_conflict(self, outline: str) -> str:
        # 简单提取，实际可用更复杂的NLP
        return "主要冲突内容"
    
    def _extract_plot_points(self, outline: str) -> list:
        return ["情节点1", "情节点2", "情节点3"]
