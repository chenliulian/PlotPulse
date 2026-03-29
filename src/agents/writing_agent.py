"""写作Agent"""

from typing import Any, Dict, List
from .base_agent import NovelAgent


class WritingAgent(NovelAgent):
    """负责具体章节写作"""

    def __init__(self, model, config=None):
        super().__init__("WritingAgent", model, config)

    async def execute(self, input_data: Dict) -> Dict:
        """
        写作章节内容
        input_data: 包含大纲、角色、世界观等信息
        """
        chapter_num = input_data.get("chapter_num", 1)
        outline = input_data.get("outline", {})
        characters = input_data.get("characters", {})
        world = input_data.get("world", {})
        human_notes = input_data.get("human_notes", "")
        previous_chapter = input_data.get("previous_chapter", "")

        prompt = self._build_chapter_prompt(
            chapter_num, outline, characters, world, human_notes, previous_chapter
        )
        chapter_content = await self.generate(prompt)

        return {
            "chapter_num": chapter_num,
            "content": chapter_content,
            "word_count": len(chapter_content),
            "scenes": self._extract_scenes(chapter_content)
        }

    def _build_chapter_prompt(
        self,
        chapter_num: int,
        outline: Dict,
        characters: Dict,
        world: Dict,
        human_notes: str,
        previous_chapter: str
    ) -> str:
        """构建优化的章节创作提示词"""

        # 提取当前章节信息
        current_chapter_info = self._extract_current_chapter_info(outline, chapter_num)

        # 格式化角色信息
        characters_info = self._format_characters(characters)

        # 格式化世界观信息
        world_info = self._format_world(world)

        # 构建前情提要
        recap = self._build_recap(previous_chapter, chapter_num)

        prompt = f"""# 小说章节创作任务

## 当前章节信息
- **章节编号**：第{chapter_num}章
- **章节标题**：{current_chapter_info.get('title', '未命名')}
- **字数要求**：{current_chapter_info.get('target_words', '3000-4000字')}

## 章节目标
{current_chapter_info.get('summary', '暂无摘要')}

### 关键事件
{self._format_key_events(current_chapter_info.get('key_events', []))}

### 场景设置
{self._format_scenes(current_chapter_info.get('scenes', []))}

{recap}

## 角色信息
{characters_info}

## 世界观设定
{world_info}

{self._format_human_notes(human_notes)}

## 写作要求

### 内容要求
1. **紧扣大纲**：严格按照本章目标和关键事件进行创作
2. **情节推进**：推动故事发展，设置合理的冲突和转折
3. **人物塑造**：保持角色性格一致性，展现角色成长和变化
4. **场景描写**：营造符合世界观和情节的氛围
5. **对话设计**：对话要符合角色身份，推动情节或展现性格

### 技术要求
1. **章节开头**：用吸引人的场景或对话开篇
2. **节奏控制**：张弛有度，避免平铺直叙
3. **结尾设计**：留下悬念或自然过渡到下一章
4. **字数控制**：{current_chapter_info.get('target_words', '3000-4000字')}

### 风格要求
- 使用生动的描写，调动读者的感官
- 适当运用修辞手法，增强文学性
- 保持叙事视角的一致性
- 注意段落和章节的结构安排

请直接输出第{chapter_num}章的正文内容：
"""
        return prompt

    def _extract_current_chapter_info(self, outline: Dict, chapter_num: int) -> Dict:
        """提取当前章节的详细信息"""
        chapter_outlines = outline.get("chapter_outlines", [])

        if isinstance(chapter_outlines, list) and len(chapter_outlines) >= chapter_num:
            ch = chapter_outlines[chapter_num - 1]
            if isinstance(ch, dict):
                return {
                    "title": ch.get("title", ""),
                    "summary": ch.get("summary", ""),
                    "key_events": ch.get("key_events", []),
                    "scenes": ch.get("scenes", []),
                    "target_words": ch.get("target_words", "3000-4000字"),
                    "characters_involved": ch.get("characters_involved", [])
                }

        # 如果没有找到，返回默认值
        return {
            "title": "",
            "summary": outline.get("plot_outline", "")[:500] if isinstance(outline, dict) else "",
            "key_events": [],
            "scenes": [],
            "target_words": "3000-4000字",
            "characters_involved": []
        }

    def _format_key_events(self, key_events: List) -> str:
        """格式化关键事件"""
        if not key_events:
            return "（本章无特定关键事件要求）"

        result = []
        for i, event in enumerate(key_events, 1):
            if isinstance(event, dict):
                desc = event.get("description", str(event))
                importance = event.get("importance", "")
                result.append(f"{i}. {desc}{f'（重要性：{importance}）' if importance else ''}")
            else:
                result.append(f"{i}. {event}")
        return "\n".join(result)

    def _format_scenes(self, scenes: List) -> str:
        """格式化场景设置"""
        if not scenes:
            return "（场景设置自由发挥）"

        result = []
        for i, scene in enumerate(scenes, 1):
            if isinstance(scene, dict):
                location = scene.get("location", "未指定")
                time = scene.get("time", "未指定")
                description = scene.get("description", "")
                result.append(f"**场景{i}**：{location} | {time}")
                if description:
                    result.append(f"  - {description}")
            else:
                result.append(f"**场景{i}**：{scene}")
        return "\n".join(result)

    def _build_recap(self, previous_chapter: str, current_chapter_num: int) -> str:
        """构建前情提要"""
        if current_chapter_num == 1:
            return ""  # 第一章不需要前情提要

        if not previous_chapter:
            return "## 前情提要\n（前一章内容未提供）\n"

        # 提取前一章的最后500字作为前情提要
        recap_text = previous_chapter[-500:] if len(previous_chapter) > 500 else previous_chapter

        return f"""## 前情提要
> 前一章结尾内容：
> 
> {recap_text}
>
> 请确保本章与上述内容自然衔接。
"""

    def _format_characters(self, characters: Dict) -> str:
        """格式化角色信息"""
        if not characters:
            return "（暂无角色信息）"

        result = []

        # 主角信息
        protagonist = characters.get("protagonist", {})
        if protagonist:
            result.append("### 主角")
            result.append(self._format_single_character(protagonist))

        # 反派信息
        antagonist = characters.get("antagonist", {})
        if antagonist:
            result.append("\n### 反派")
            result.append(self._format_single_character(antagonist))

        # 其他角色
        other_chars = characters.get("characters", [])
        if other_chars:
            result.append(f"\n### 其他重要角色（共{len(other_chars)}人）")
            for char in other_chars[:5]:  # 最多显示5个角色
                result.append(self._format_single_character(char, brief=True))

        return "\n".join(result)

    def _format_single_character(self, char: Dict, brief: bool = False) -> str:
        """格式化单个角色信息"""
        if not isinstance(char, dict):
            return str(char)

        name = char.get("name", "未命名")

        if brief:
            # 简要格式
            age = char.get("age", "")
            personality = char.get("personality", "")[:50]
            return f"- **{name}**{f'（{age}）' if age else ''}：{personality}..."
        else:
            # 详细格式
            lines = [f"**{name}**"]
            if char.get("age"):
                lines.append(f"- 年龄：{char['age']}")
            if char.get("appearance"):
                lines.append(f"- 外貌：{char['appearance'][:100]}...")
            if char.get("personality"):
                lines.append(f"- 性格：{char['personality'][:100]}...")
            if char.get("background"):
                lines.append(f"- 背景：{char['background'][:100]}...")
            if char.get("motivation"):
                lines.append(f"- 动机：{char['motivation'][:100]}...")
            if char.get("arc"):
                lines.append(f"- 角色弧线：{char['arc'][:100]}...")
            return "\n".join(lines)

    def _format_world(self, world: Dict) -> str:
        """格式化世界观信息"""
        if not world:
            return "（暂无世界观信息）"

        world_desc = world.get("world_description", "")

        if not world_desc:
            return "（世界观描述未提供）"

        # 提取关键信息（前800字）
        summary = world_desc[:800]
        if len(world_desc) > 800:
            summary += "..."

        return f"""### 世界观概述
{summary}

### 重要提示
- 保持与已建立的世界观设定一致
- 注意时代背景和社会环境
- 遵循已有的规则和设定
"""

    def _format_human_notes(self, notes: str) -> str:
        """格式化人类创作提示"""
        if not notes:
            return ""

        return f"""## 人类创作者提示
> {notes}

"""

    def _extract_scenes(self, content: str) -> list:
        """提取场景信息"""
        # 简单的场景提取逻辑
        scenes = []
        import re

        # 尝试匹配场景标记（如 "## 一"、"### 场景1" 等）
        scene_patterns = [
            r'##\s*[一二三四五六七八九十\d]+[、.\s]',
            r'###\s*场景\s*\d+',
            r'\n\n[一二三四五六七八九十][、.\s]',
        ]

        for pattern in scene_patterns:
            matches = re.findall(pattern, content)
            if matches:
                scenes = [f"场景{i+1}" for i in range(len(matches))]
                break

        if not scenes:
            # 如果没有找到场景标记，按段落数估算
            paragraphs = [p for p in content.split('\n\n') if len(p) > 100]
            scenes = [f"场景{i+1}" for i in range(min(len(paragraphs), 5))]

        return scenes if scenes else ["场景1"]
