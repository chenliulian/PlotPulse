"""人机协同创作流程

支持人类创作者与AI Agent协作创作小说，人类可以在每个阶段提供输入、
审核Agent生成的内容，并在确认后才进入下一步。
"""

import asyncio
import re
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

from src.agents import (
    PlotAgent, CharacterAgent, WorldbuildingAgent,
    WritingAgent, EditingAgent, ReviewerAgent
)
from src.models import BaseModel
from src.tools import Storage


def sanitize_filename(name: str) -> str:
    """将字符串转换为安全的文件名
    
    移除或替换不安全的字符，限制长度
    """
    # 替换不安全的字符
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # 移除前后空白
    safe_name = safe_name.strip()
    # 限制长度
    if len(safe_name) > 50:
        safe_name = safe_name[:50]
    # 确保不为空
    if not safe_name:
        safe_name = "untitled"
    return safe_name


class CreationStage(Enum):
    """创作阶段"""
    INIT = "init"
    OUTLINE = "outline"
    CHARACTERS = "characters"
    WORLD = "world"
    WRITING = "writing"
    REVIEW = "review"
    COMPLETED = "completed"


@dataclass
class HumanFeedback:
    """人类反馈"""
    approved: bool
    feedback: str = ""
    modifications: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CreationStep:
    """创作步骤"""
    stage: CreationStage
    title: str
    description: str
    agent_input: Dict[str, Any] = field(default_factory=dict)
    agent_output: Dict[str, Any] = field(default_factory=dict)
    human_feedback: Optional[HumanFeedback] = None
    status: str = "pending"  # pending, generating, reviewing, approved, rejected


class InteractiveNovelPipeline:
    """人机协同小说创作流程"""
    
    def __init__(
        self,
        model: BaseModel,
        output_dir: str = "novels/collaborative",
        config: Optional[Dict] = None,
        feedback_callback: Optional[Callable[[CreationStep], HumanFeedback]] = None
    ):
        self.model = model
        self.output_dir = Path(output_dir)
        self.config = config or {}
        self.storage = Storage()
        self.feedback_callback = feedback_callback or self._default_feedback_callback
        
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
        self.current_stage: CreationStage = CreationStage.INIT
        self.creation_history: List[CreationStep] = []
        self._novel_dir: Optional[Path] = None  # 缓存小说目录路径
        self._skip_chapter_review: bool = False  # 是否跳过章节审核
    
    def _get_novel_dir(self) -> Path:
        """获取小说目录路径
        
        如果缓存的目录不存在（例如从保存的进度恢复），则重新构建路径
        """
        if self._novel_dir is not None and self._novel_dir.exists():
            return self._novel_dir
        
        # 重新构建目录路径
        if self.novel_id and self.novel_data.get("title"):
            safe_title = sanitize_filename(self.novel_data["title"])
            self._novel_dir = self.output_dir / f"{safe_title}_{self.novel_id[:8]}"
            return self._novel_dir
        
        # 回退到旧格式
        return self.output_dir / f"novel_{self.novel_id}"
    
    def _default_feedback_callback(self, step: CreationStep) -> HumanFeedback:
        """默认反馈回调（自动通过，用于非交互模式）"""
        return HumanFeedback(approved=True, feedback="自动通过")
    
    async def create_project(
        self,
        title: str = "",
        theme: str = "",
        genre: str = "",
        style: str = "",
        num_chapters: int = 10,
        human_input: Optional[Dict] = None
    ) -> str:
        """
        创建新小说项目
        
        Args:
            title: 小说标题（人类可提供）
            theme: 主题（人类可提供）
            genre: 类型（人类可提供）
            style: 风格（人类可提供）
            num_chapters: 章节数
            human_input: 人类的其他输入
        """
        import uuid
        from datetime import datetime
        
        self.novel_id = str(uuid.uuid4())[:8]
        
        # 如果人类提供了输入，优先使用
        self.novel_data = {
            "id": self.novel_id,
            "title": title or "未命名小说",
            "theme": theme or "",
            "genre": genre or "",
            "style": style or "",
            "num_chapters": num_chapters,
            "created_at": datetime.now().isoformat(),
            "status": "planning",
            "human_input": human_input or {},
            "outline": None,
            "characters": None,
            "world": None,
            "chapters": []
        }
        
        # 创建小说目录 - 使用小说名称命名
        safe_title = sanitize_filename(title)
        self._novel_dir = self.output_dir / f"{safe_title}_{self.novel_id[:8]}"
        self._novel_dir.mkdir(parents=True, exist_ok=True)
        (self._novel_dir / "chapters").mkdir(exist_ok=True)
        (self._novel_dir / "final").mkdir(exist_ok=True)
        
        self.current_stage = CreationStage.INIT
        await self._save_progress()
        
        return self.novel_id
    
    async def generate_outline_interactive(self) -> Dict:
        """
        交互式生成小说大纲
        
        流程：
        1. Agent根据人类提供的主题/类型生成大纲
        2. 展示给人类审核
        3. 人类可以：批准、要求修改、提供具体修改意见
        4. 根据反馈迭代，直到人类满意
        """
        if not self.novel_id:
            raise ValueError("No novel project created")
        
        step = CreationStep(
            stage=CreationStage.OUTLINE,
            title="情节大纲设计",
            description="基于您的主题和类型，AI将设计小说大纲",
            agent_input={
                "theme": self.novel_data.get("theme", ""),
                "genre": self.novel_data.get("genre", ""),
                "style": self.novel_data.get("style", ""),
                "human_notes": self.novel_data.get("human_input", {}).get("outline_notes", "")
            }
        )
        
        max_iterations = 3
        for iteration in range(max_iterations):
            print(f"\n{'='*60}")
            print(f"大纲设计 - 迭代 {iteration + 1}/{max_iterations}")
            print(f"{'='*60}")
            
            # Agent生成大纲
            step.status = "generating"
            print("\n🤖 AI正在生成大纲...")
            
            plot_data = await self.plot_agent.execute(step.agent_input)
            step.agent_output = plot_data
            
            # 展示给人类
            step.status = "reviewing"
            print("\n" + "-"*60)
            print("📖 AI生成的大纲：")
            print("-"*60)
            print(plot_data.get("plot_outline", ""))
            print("-"*60)
            
            # 获取人类反馈
            feedback = self.feedback_callback(step)
            step.human_feedback = feedback
            
            if feedback.approved:
                print("\n✅ 大纲已批准！")
                step.status = "approved"

                # 立即保存大纲
                self.creation_history.append(step)
                self.novel_data["outline"] = step.agent_output
                self.novel_data["status"] = "outlined"
                self.current_stage = CreationStage.OUTLINE
                await self._save_progress()

                # 同时保存大纲为独立文件
                await self._save_outline_to_file(step.agent_output)

                break
            else:
                print(f"\n📝 人类反馈：{feedback.feedback}")
                if feedback.modifications:
                    step.agent_input.update(feedback.modifications)
                    step.agent_input["revision_notes"] = feedback.feedback
                step.status = "rejected"

        return step.agent_output
    
    async def generate_characters_interactive(self) -> Dict:
        """
        交互式生成角色设定
        
        流程：
        1. Agent根据大纲生成角色
        2. 展示给人类审核
        3. 人类可以：批准、修改角色属性、添加新角色、删除角色
        4. 根据反馈迭代
        """
        if not self.novel_data.get("outline"):
            raise ValueError("Outline not generated yet")
        
        step = CreationStep(
            stage=CreationStage.CHARACTERS,
            title="角色设计",
            description="基于大纲，AI将设计主要角色",
            agent_input={
                "plot_outline": self.novel_data["outline"]["plot_outline"],
                "num_characters": self.config.get("num_characters", 5),
                "human_notes": self.novel_data.get("human_input", {}).get("character_notes", "")
            }
        )
        
        max_iterations = 3
        for iteration in range(max_iterations):
            print(f"\n{'='*60}")
            print(f"角色设计 - 迭代 {iteration + 1}/{max_iterations}")
            print(f"{'='*60}")
            
            # Agent生成角色
            step.status = "generating"
            print("\n🤖 AI正在设计角色...")
            
            character_data = await self.character_agent.execute(step.agent_input)
            step.agent_output = character_data
            
            # 展示给人类
            step.status = "reviewing"
            print("\n" + "-"*60)
            print("👥 AI设计的角色：")
            print("-"*60)
            
            characters = character_data.get("characters", [])
            for i, char in enumerate(characters, 1):
                print(f"\n【角色 {i}】")
                print(f"  姓名：{char.get('name', '未命名')}")
                print(f"  描述：{char.get('description', '')[:100]}...")
            
            if character_data.get("protagonist"):
                print(f"\n🌟 主角：{character_data['protagonist'].get('name', '未知')}")
            
            print("-"*60)
            
            # 获取人类反馈
            feedback = self.feedback_callback(step)
            step.human_feedback = feedback
            
            if feedback.approved:
                print("\n✅ 角色设定已批准！")
                step.status = "approved"

                # 立即保存角色设定
                self.creation_history.append(step)
                self.novel_data["characters"] = step.agent_output
                self.current_stage = CreationStage.CHARACTERS
                await self._save_progress()

                # 同时保存角色设定为独立文件
                await self._save_characters_to_file(step.agent_output)

                break
            else:
                print(f"\n📝 人类反馈：{feedback.feedback}")
                if feedback.modifications:
                    step.agent_input.update(feedback.modifications)
                    step.agent_input["revision_notes"] = feedback.feedback
                step.status = "rejected"

        return step.agent_output
    
    async def generate_world_interactive(self) -> Dict:
        """
        交互式生成世界观设定
        
        流程：
        1. Agent根据类型和时代生成世界观
        2. 展示给人类审核
        3. 人类可以：批准、修改设定、添加细节
        4. 根据反馈迭代
        """
        step = CreationStep(
            stage=CreationStage.WORLD,
            title="世界观构建",
            description="AI将构建小说的世界观设定",
            agent_input={
                "genre": self.novel_data.get("genre", ""),
                "era": self.config.get("era", "现代"),
                "human_notes": self.novel_data.get("human_input", {}).get("world_notes", "")
            }
        )
        
        max_iterations = 3
        for iteration in range(max_iterations):
            print(f"\n{'='*60}")
            print(f"世界观构建 - 迭代 {iteration + 1}/{max_iterations}")
            print(f"{'='*60}")
            
            # Agent生成世界观
            step.status = "generating"
            print("\n🤖 AI正在构建世界观...")
            
            world_data = await self.world_agent.execute(step.agent_input)
            step.agent_output = world_data
            
            # 展示给人类
            step.status = "reviewing"
            print("\n" + "-"*60)
            print("🌍 AI构建的世界观：")
            print("-"*60)
            print(world_data.get("world_description", "")[:800])
            print("..." if len(world_data.get("world_description", "")) > 800 else "")
            print("-"*60)
            
            # 获取人类反馈
            feedback = self.feedback_callback(step)
            step.human_feedback = feedback
            
            if feedback.approved:
                print("\n✅ 世界观设定已批准！")
                step.status = "approved"

                # 立即保存世界观设定
                self.creation_history.append(step)
                self.novel_data["world"] = step.agent_output
                self.current_stage = CreationStage.WORLD
                await self._save_progress()

                # 同时保存世界观设定为独立文件
                await self._save_world_to_file(step.agent_output)

                break
            else:
                print(f"\n📝 人类反馈：{feedback.feedback}")
                if feedback.modifications:
                    step.agent_input.update(feedback.modifications)
                    step.agent_input["revision_notes"] = feedback.feedback
                step.status = "rejected"

        return step.agent_output
    
    async def write_chapter_interactive(self, chapter_num: int, skip_review: bool = False) -> Dict:
        """
        交互式写作单章

        流程：
        1. Agent根据大纲、角色、世界观写作
        2. 展示给人类审核（如果skip_review为False）
        3. 人类可以：批准、要求修改、提供具体修改意见
        4. 根据反馈迭代，包括编辑润色

        Args:
            chapter_num: 章节编号
            skip_review: 是否跳过人类审核，True表示AI自动完成
        """
        # 获取前一章内容作为前情提要
        previous_chapter = ""
        if chapter_num > 1 and self.novel_data["chapters"]:
            prev_ch = self.novel_data["chapters"][-1]
            previous_chapter = prev_ch.get("edited_content", prev_ch.get("content", ""))

        step = CreationStep(
            stage=CreationStage.WRITING,
            title=f"第{chapter_num}章创作",
            description=f"AI将创作第{chapter_num}章内容",
            agent_input={
                "chapter_num": chapter_num,
                "outline": self.novel_data["outline"],
                "characters": self.novel_data["characters"],
                "world": self.novel_data["world"],
                "human_notes": self.novel_data.get("human_input", {}).get(f"chapter_{chapter_num}_notes", ""),
                "previous_chapter": previous_chapter  # 添加前一章内容
            }
        )

        if skip_review:
            # AI自动创作模式
            print(f"\n{'='*60}")
            print(f"🤖 AI自动创作第{chapter_num}章（跳过审核）")
            print(f"{'='*60}")

            step.status = "generating"
            chapter_data = await self.writing_agent.execute(step.agent_input)

            # 编辑润色
            print("📝 AI正在润色内容...")
            edited = await self.editing_agent.execute({
                "content": chapter_data["content"],
                "edit_type": "polish"
            })
            chapter_data["edited_content"] = edited["edited"]

            step.agent_output = chapter_data
            step.status = "approved"
            step.human_feedback = HumanFeedback(approved=True, feedback="AI自动创作，跳过审核")

            # 显示简要信息
            content = chapter_data.get("edited_content", chapter_data["content"])
            print(f"✅ 第{chapter_num}章创作完成")
            print(f"   字数：{chapter_data.get('word_count', 0)}")
            print(f"   预览：{content[:100]}...")

        else:
            # 人类审核模式
            max_iterations = 3
            for iteration in range(max_iterations):
                print(f"\n{'='*60}")
                print(f"第{chapter_num}章创作 - 迭代 {iteration + 1}/{max_iterations}")
                print(f"{'='*60}")

                # Agent写作
                step.status = "generating"
                print(f"\n🤖 AI正在写作第{chapter_num}章...")

                chapter_data = await self.writing_agent.execute(step.agent_input)

                # 编辑润色
                print("📝 AI正在润色内容...")
                edited = await self.editing_agent.execute({
                    "content": chapter_data["content"],
                    "edit_type": "polish"
                })
                chapter_data["edited_content"] = edited["edited"]

                step.agent_output = chapter_data

                # 展示给人类
                step.status = "reviewing"
                print("\n" + "-"*60)
                print(f"📖 AI创作的第{chapter_num}章：")
                print("-"*60)
                content = chapter_data.get("edited_content", chapter_data["content"])
                print(content[:1500])
                print("..." if len(content) > 1500 else "")
                print(f"\n字数：{chapter_data.get('word_count', 0)}")
                print("-"*60)

                # 获取人类反馈
                feedback = self.feedback_callback(step)
                step.human_feedback = feedback

                if feedback.approved:
                    print("\n✅ 章节内容已批准！")
                    step.status = "approved"

                    # 立即保存章节
                    self.creation_history.append(step)
                    self.novel_data["chapters"].append(step.agent_output)
                    await self._save_chapter(chapter_num, step.agent_output)
                    await self._save_progress()

                    print(f"   📄 第{chapter_num}章已保存")

                    break
                else:
                    print(f"\n📝 人类反馈：{feedback.feedback}")
                    if feedback.modifications:
                        step.agent_input.update(feedback.modifications)
                        step.agent_input["revision_notes"] = feedback.feedback
                    step.status = "rejected"

        # 对于AI自动创作模式，也在此处保存
        if skip_review:
            self.creation_history.append(step)
            self.novel_data["chapters"].append(step.agent_output)
            await self._save_chapter(chapter_num, step.agent_output)
            await self._save_progress()

            print(f"   📄 第{chapter_num}章已保存")

        return step.agent_output
    
    async def review_novel_interactive(self) -> Dict:
        """
        交互式审阅整部小说
        
        流程：
        1. Agent审阅整部小说
        2. 展示审阅报告给人类
        3. 人类可以：批准、根据建议修改、要求重新审阅
        """
        # 合并所有章节
        full_text = "\n\n".join([
            ch.get("edited_content", ch["content"]) 
            for ch in self.novel_data["chapters"]
        ])
        
        step = CreationStep(
            stage=CreationStage.REVIEW,
            title="小说审阅",
            description="AI将审阅整部小说并提供改进建议",
            agent_input={
                "content": full_text,
                "review_type": "comprehensive"
            }
        )
        
        print(f"\n{'='*60}")
        print(f"小说审阅")
        print(f"{'='*60}")
        
        # Agent审阅
        step.status = "generating"
        print("\n🤖 AI正在审阅小说...")
        
        review = await self.reviewer_agent.execute(step.agent_input)
        step.agent_output = review
        
        # 展示给人类
        step.status = "reviewing"
        print("\n" + "-"*60)
        print("📋 AI审阅报告：")
        print("-"*60)
        print(f"评分：{review.get('score', 'N/A')}/10")
        print(f"\n审阅内容：")
        print(review.get("review_text", "")[:1000])
        print("..." if len(review.get("review_text", "")) > 1000 else "")
        
        if review.get("suggestions"):
            print(f"\n💡 改进建议：")
            for i, suggestion in enumerate(review.get("suggestions", [])[:5], 1):
                print(f"  {i}. {suggestion}")
        print("-"*60)
        
        # 获取人类反馈
        feedback = self.feedback_callback(step)
        step.human_feedback = feedback
        
        if feedback.approved:
            print("\n✅ 审阅完成，小说已批准！")
            step.status = "approved"
        else:
            print(f"\n📝 人类反馈：{feedback.feedback}")
            step.status = "rejected"
        
        self.creation_history.append(step)
        self.novel_data["review"] = step.agent_output
        self.current_stage = CreationStage.REVIEW
        
        await self._save_progress()
        return step.agent_output
    
    async def run_full_pipeline_interactive(self) -> str:
        """运行完整的交互式创作流程"""
        print("\n" + "="*60)
        print("🚀 开始人机协同小说创作")
        print("="*60)

        # 1. 大纲设计
        await self.generate_outline_interactive()

        # 2. 角色设计
        await self.generate_characters_interactive()

        # 3. 世界观构建
        await self.generate_world_interactive()

        # 4. 询问章节创作模式（在世界观完成后、第一章开始前）
        skip_chapter_review = await self._ask_chapter_review_mode()

        # 5. 逐章写作
        for i in range(1, self.novel_data["num_chapters"] + 1):
            await self.write_chapter_interactive(i, skip_review=skip_chapter_review)

        # 5. 审阅
        await self.review_novel_interactive()

        # 6. 导出
        export_path = await self.export_novel()

        print("\n" + "="*60)
        print("🎉 小说创作完成！")
        print(f"📁 导出路径：{export_path}")
        print("="*60)

        return export_path

    async def _ask_chapter_review_mode(self) -> bool:
        """询问章节创作模式

        在世界观完成后、第一章开始前调用
        返回True表示跳过审核（AI自动创作），False表示逐章审核
        """
        print("\n" + "="*60)
        print("📚 章节创作模式选择")
        print("="*60)
        print(f"\n基础设定已完成！即将开始创作 {self.novel_data['num_chapters']} 个章节的内容。")
        print("\n请选择章节创作模式：")
        print("  1. ✅ 逐章审核 - 每完成一章都让您审核（推荐）")
        print("  2. ⚡ AI自动创作 - 所有章节由AI独立完成，不再询问")

        # 使用反馈回调获取用户选择
        # 创建一个特殊的步骤来获取用户选择
        choice_step = CreationStep(
            stage=CreationStage.WRITING,
            title="章节创作模式选择",
            description="选择是否逐章审核章节内容",
            agent_input={},
            agent_output={
                "message": "请选择章节创作模式",
                "options": [
                    "1. 逐章审核 - 每章都让您审核",
                    "2. AI自动创作 - AI独立完成所有章节"
                ]
            },
            status="awaiting_feedback"
        )

        # 获取人类反馈
        feedback = self.feedback_callback(choice_step)

        # 解析用户选择
        if feedback.modifications and "chapter_mode" in feedback.modifications:
            mode = feedback.modifications["chapter_mode"]
        elif feedback.feedback.strip() == "2" or "自动" in feedback.feedback or "AI" in feedback.feedback:
            mode = "2"
        else:
            mode = "1"  # 默认逐章审核

        if mode == "2":
            print("\n⚡ 已选择：AI自动创作模式")
            print(f"   AI将自动创作所有 {self.novel_data['num_chapters']} 个章节，不再询问审核")
            return True
        else:
            print("\n✅ 已选择：逐章审核模式")
            print("   每完成一章都会展示给您审核")
            return False

    async def _save_outline_to_file(self, outline_data: Dict):
        """保存大纲为独立文件"""
        novel_dir = self._get_novel_dir()

        content = f"""# {self.novel_data['title']} - 情节大纲

## 基本信息
- 主题：{self.novel_data.get('theme', '')}
- 类型：{self.novel_data.get('genre', '')}
- 风格：{self.novel_data.get('style', '')}
- 章节数：{self.novel_data.get('num_chapters', 0)}

## 故事梗概
{outline_data.get('plot_outline', '')}

## 章节大纲
"""

        # 添加章节大纲
        chapter_outlines = outline_data.get('chapter_outlines', [])
        for i, ch in enumerate(chapter_outlines, 1):
            if isinstance(ch, dict):
                title = ch.get('title', '')
                summary = ch.get('summary', '')
                content += f"\n### 第{i}章{f' {title}' if title else ''}\n"
                content += f"{summary}\n"

        self.storage.save_text(
            "outline.md",
            content,
            str(novel_dir)
        )
        print(f"   📄 大纲已保存到: {novel_dir / 'outline.md'}")

    async def _save_characters_to_file(self, character_data: Dict):
        """保存角色设定为独立文件"""
        novel_dir = self._get_novel_dir()

        content = f"""# {self.novel_data['title']} - 角色设定

"""

        # 添加角色信息
        characters = character_data.get('characters', [])
        for i, char in enumerate(characters, 1):
            if isinstance(char, dict):
                content += f"\n## 角色{i}：{char.get('name', '未命名')}\n\n"
                content += f"- **年龄**：{char.get('age', '未知')}\n"
                content += f"- **外貌**：{char.get('appearance', '')}\n"
                content += f"- **性格**：{char.get('personality', '')}\n"
                content += f"- **背景**：{char.get('background', '')}\n"
                content += f"- **动机**：{char.get('motivation', '')}\n"
                content += f"- **弧线**：{char.get('arc', '')}\n"
                content += f"- **关系**：{char.get('relationship', '')}\n"

        # 添加主角和反派信息
        protagonist = character_data.get('protagonist', {})
        antagonist = character_data.get('antagonist', {})

        content += f"\n## 主角\n"
        content += f"- **姓名**：{protagonist.get('name', '未设定')}\n"
        content += f"- **角色定位**：{protagonist.get('role', 'protagonist')}\n"

        content += f"\n## 反派\n"
        content += f"- **姓名**：{antagonist.get('name', '未设定')}\n"
        content += f"- **角色定位**：{antagonist.get('role', 'antagonist')}\n"

        self.storage.save_text(
            "characters.md",
            content,
            str(novel_dir)
        )
        print(f"   📄 角色设定已保存到: {novel_dir / 'characters.md'}")

    async def _save_world_to_file(self, world_data: Dict):
        """保存世界观设定为独立文件"""
        novel_dir = self._get_novel_dir()

        content = f"""# {self.novel_data['title']} - 世界观设定

{world_data.get('world_description', '')}
"""

        self.storage.save_text(
            "world.md",
            content,
            str(novel_dir)
        )
        print(f"   📄 世界观设定已保存到: {novel_dir / 'world.md'}")

    async def _save_progress(self):
        """保存创作进度"""
        novel_dir = self._get_novel_dir()
        self.storage.save_json(
            "metadata.json",
            self.novel_data,
            str(novel_dir.relative_to(self.storage.base_dir))
        )

    async def _save_chapter(self, chapter_num: int, chapter_data: Dict):
        """保存章节文件"""
        novel_dir = self._get_novel_dir()

        # 获取章节标题（如果有）
        chapter_title = ""
        if "outline" in self.novel_data and self.novel_data["outline"]:
            outline = self.novel_data["outline"]
            if isinstance(outline, dict) and "chapter_outlines" in outline:
                chapter_outlines = outline["chapter_outlines"]
                if isinstance(chapter_outlines, list) and len(chapter_outlines) >= chapter_num:
                    ch_outline = chapter_outlines[chapter_num - 1]
                    if isinstance(ch_outline, dict):
                        chapter_title = ch_outline.get("title", "")

        # 构建文件名：包含章节号和标题
        if chapter_title:
            safe_title = sanitize_filename(chapter_title)
            filename = f"chapter_{chapter_num:02d}_{safe_title}.md"
        else:
            filename = f"chapter_{chapter_num:02d}.md"

        content = f"""# 第{chapter_num}章{f" {chapter_title}" if chapter_title else ""}

{chapter_data.get('edited_content', chapter_data['content'])}
"""
        self.storage.save_text(
            filename,
            content,
            str(novel_dir / "chapters")
        )

    async def export_novel(self, format: str = "markdown") -> str:
        """导出完整小说"""
        novel_dir = self._get_novel_dir()

        # 合并所有章节
        full_content = f"# {self.novel_data['title']}\n\n"

        for chapter in self.novel_data["chapters"]:
            chapter_num = chapter['chapter_num']

            # 获取章节标题
            chapter_title = ""
            if "outline" in self.novel_data and self.novel_data["outline"]:
                outline = self.novel_data["outline"]
                if isinstance(outline, dict) and "chapter_outlines" in outline:
                    chapter_outlines = outline["chapter_outlines"]
                    if isinstance(chapter_outlines, list) and len(chapter_outlines) >= chapter_num:
                        ch_outline = chapter_outlines[chapter_num - 1]
                        if isinstance(ch_outline, dict):
                            chapter_title = ch_outline.get("title", "")

            # 添加章节标题
            if chapter_title:
                full_content += f"## 第{chapter_num}章 {chapter_title}\n\n"
            else:
                full_content += f"## 第{chapter_num}章\n\n"

            full_content += chapter.get("edited_content", chapter["content"])
            full_content += "\n\n"

        # 保存完整版本
        self.storage.save_text(
            "full_novel.md",
            full_content,
            str(novel_dir / "final")
        )

        return str(novel_dir / "final" / "full_novel.md")
