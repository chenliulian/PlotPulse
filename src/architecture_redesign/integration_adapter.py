"""
StoryBrain 集成适配器

将新架构的StoryBrain集成到现有的InteractiveNovelPipeline中。
提供向后兼容的接口，同时增加新架构的功能。
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from typing import Dict, Any, Optional, List
from pathlib import Path
import json

from src.architecture_redesign import (
    StoryBrain,
    CharacterState,
    PlotPoint,
    ChapterPlan,
    ChapterExecution
)


class StoryBrainAdapter:
    """
    StoryBrain适配器
    
    将现有的novel_data格式转换为StoryBrain格式，
    并提供增强功能。
    """
    
    def __init__(self, novel_id: str, output_dir: str = "data/novels"):
        self.novel_id = novel_id
        self.output_dir = Path(output_dir)
        self.story_brain: Optional[StoryBrain] = None
        self._legacy_data: Dict[str, Any] = {}
        
    def initialize_from_legacy(self, novel_data: Dict[str, Any]) -> StoryBrain:
        """
        从现有的novel_data初始化StoryBrain
        
        Args:
            novel_data: 现有的pipeline中的novel_data
            
        Returns:
            初始化好的StoryBrain实例
        """
        self._legacy_data = novel_data
        
        # 创建StoryBrain
        title = novel_data.get("title", "未命名小说")
        self.story_brain = StoryBrain(
            novel_id=self.novel_id,
            title=title
        )
        
        # 转换角色数据
        characters = self._convert_characters(novel_data.get("characters", []))
        
        # 初始化故事
        self.story_brain.initialize_story(
            theme=novel_data.get("theme", ""),
            genre=novel_data.get("genre", ""),
            style=novel_data.get("style", ""),
            target_chapters=novel_data.get("num_chapters", 10),
            characters=characters
        )
        
        # 转换大纲为情节点
        self._convert_outline_to_plot_points(novel_data.get("outline", ""))
        
        print(f"✅ StoryBrain适配器初始化完成")
        print(f"   小说: {title}")
        print(f"   角色: {len(characters)}")
        print(f"   情节点: {len(self.story_brain.plot_points)}")
        
        return self.story_brain
    
    def _convert_characters(self, legacy_characters: List[Dict]) -> List[Dict]:
        """转换角色数据格式"""
        converted = []
        
        if not legacy_characters:
            return converted
        
        for char in legacy_characters:
            converted_char = {
                "name": char.get("name", "未命名"),
                "age": char.get("age", "未知"),
                "appearance": char.get("appearance", ""),
                "personality": char.get("personality", ""),
                "background": char.get("background", ""),
                "motivation": char.get("motivation", ""),
                "initial_emotion": "neutral",
                "initial_goals": [char.get("motivation", "完成故事")]
            }
            converted.append(converted_char)
            
        return converted
    
    def _convert_outline_to_plot_points(self, outline: str):
        """将大纲文本转换为情节点"""
        if not outline:
            return
            
        # 简单解析：按章节分割
        import re
        
        # 尝试提取章节信息
        chapter_matches = re.findall(r'第[一二三四五六七八九十\d]+章[：:](.+?)(?=第[一二三四五六七八九十\d]+章|$)', 
                                     outline, re.DOTALL)
        
        if not chapter_matches:
            # 如果没有匹配到，将整个大纲作为一个情节点
            self.story_brain.register_plot_point(PlotPoint(
                id="main_plot",
                description="主线情节",
                chapter_introduced=1,
                related_characters=list(self.story_brain.characters.keys())
            ))
            return
        
        # 为每个章节创建一个情节点
        for i, chapter_content in enumerate(chapter_matches[:self.story_brain.target_chapters], 1):
            # 提取章节标题和关键事件
            lines = chapter_content.strip().split('\n')
            title = lines[0].strip() if lines else f"第{i}章"
            
            # 创建情节点
            self.story_brain.register_plot_point(PlotPoint(
                id=f"chapter_{i}_plot",
                description=f"{title}: {chapter_content[:100]}...",
                chapter_introduced=i,
                related_characters=list(self.story_brain.characters.keys())
            ))
    
    def create_enhanced_chapter_plan(self, chapter_num: int, 
                                     legacy_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        创建增强的章节规划
        
        结合StoryBrain的状态管理和现有的上下文
        
        Args:
            chapter_num: 章节号
            legacy_context: 现有的上下文信息
            
        Returns:
            增强的上下文字典
        """
        if not self.story_brain:
            raise ValueError("StoryBrain未初始化")
        
        # 获取StoryBrain的上下文
        story_context = self.story_brain.get_context_for_chapter_writing(chapter_num)
        
        # 如果没有章节规划，创建一个默认的
        if chapter_num not in self.story_brain.chapter_plans:
            plan = ChapterPlan(
                chapter_num=chapter_num,
                title=f"第{chapter_num}章",
                objectives=[f"推进第{chapter_num}章情节"],
                plot_points_to_advance=[pp_id for pp_id in self.story_brain.active_plot_points][:2],
                character_arcs_to_develop=list(self.story_brain.characters.keys())[:1],
                foreshadowing_to_plant=[],
                conflicts_to_introduce_or_resolve=[],
                expected_word_count=3000,
                key_scenes=[],
                emotional_tone="neutral"
            )
            self.story_brain.create_chapter_plan(plan)
            story_context = self.story_brain.get_context_for_chapter_writing(chapter_num)
        
        # 合并现有的上下文
        enhanced_context = {
            # StoryBrain提供的增强信息
            "story_brain_context": story_context,
            "character_states": story_context.get("character_states_at_start", {}),
            "active_plot_points": story_context.get("active_plot_points", []),
            "foreshadowing_to_resolve": story_context.get("foreshadowing_to_resolve", []),
            "consistency_constraints": story_context.get("consistency_constraints", []),
            
            # 向后兼容的字段
            "chapter_num": chapter_num,
            "outline": self._legacy_data.get("outline", ""),
            "characters": self._legacy_data.get("characters", []),
            "world": self._legacy_data.get("world", {}),
            
            # 增强的前情提要（替代原来的500字限制）
            "previous_chapter_recap": story_context.get("previous_chapter_recap", ""),
            "full_story_summary": self._generate_full_summary()
        }
        
        # 合并legacy_context
        if legacy_context:
            enhanced_context.update(legacy_context)
        
        return enhanced_context
    
    def _generate_full_summary(self) -> str:
        """生成完整的故事摘要"""
        summary_parts = []
        
        # 基础信息
        summary_parts.append(f"《{self.story_brain.title}》")
        summary_parts.append(f"主题: {self.story_brain.theme}")
        summary_parts.append(f"类型: {self.story_brain.genre}")
        summary_parts.append("")
        
        # 角色信息
        summary_parts.append("【角色】")
        for name, char in self.story_brain.characters.items():
            if isinstance(char, dict):
                summary_parts.append(f"- {name}: {char.get('motivation', '')}")
            elif isinstance(char, list) and len(char) > 0:
                # 处理角色是列表的情况
                summary_parts.append(f"- {name}: {char[0] if isinstance(char[0], str) else ''}")
            else:
                summary_parts.append(f"- {name}")
        summary_parts.append("")
        
        # 已完成章节摘要
        if self.story_brain.chapter_executions:
            summary_parts.append("【已完成章节】")
            for ch_num in sorted(self.story_brain.chapter_executions.keys()):
                exec_data = self.story_brain.chapter_executions[ch_num]
                summary_parts.append(f"第{ch_num}章: {len(exec_data.content)}字")
        
        return "\n".join(summary_parts)
    
    def record_chapter_completion(self, chapter_num: int, content: str,
                                   quality_score: float = 0.0):
        """
        记录章节完成
        
        更新StoryBrain的状态
        """
        if not self.story_brain:
            return
        
        # 更新角色状态（简化版本，实际应该由Agent分析内容后更新）
        for char_name in self.story_brain.characters.keys():
            current_state = self.story_brain.get_character_state(chapter_num, char_name)
            if current_state:
                # 简单地推进到下一章
                next_state = CharacterState(
                    chapter=chapter_num + 1,
                    emotional_state=current_state.emotional_state,
                    goals=current_state.goals,
                    relationships=current_state.relationships,
                    knowledge=current_state.knowledge,
                    development_stage=current_state.development_stage,
                    key_decisions=current_state.key_decisions
                )
                self.story_brain.update_character_state(chapter_num + 1, char_name, next_state)
        
        # 记录章节执行
        execution = ChapterExecution(
            chapter_num=chapter_num,
            content=content,
            word_count=len(content),
            plot_points_advanced=[],
            character_states_after={},
            foreshadowing_planted=[],
            foreshadowing_resolved=[],
            consistency_issues=[],
            quality_score=quality_score
        )
        self.story_brain.record_chapter_execution(execution)
        
        print(f"✅ 第{chapter_num}章已记录到StoryBrain")
    
    def check_chapter_consistency(self, chapter_num: int, content: str) -> List[Dict]:
        """
        检查章节一致性
        
        Args:
            chapter_num: 章节号
            content: 章节内容
            
        Returns:
            一致性问题列表
        """
        if not self.story_brain:
            return []
        
        issues = self.story_brain.check_consistency(chapter_num, content)
        
        if issues:
            print(f"\n⚠️  发现 {len(issues)} 个一致性问题:")
            for issue in issues[:5]:  # 只显示前5个
                print(f"   - [{issue['type']}] {issue.get('check', '')}")
        else:
            print(f"✅ 第{chapter_num}章一致性检查通过")
        
        return issues
    
    def save_state(self):
        """保存StoryBrain状态"""
        if not self.story_brain:
            return
        
        save_path = self.output_dir / f"{self.novel_id}_story_brain.json"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.story_brain.save_to_file(str(save_path))
        print(f"✅ StoryBrain状态已保存: {save_path}")
    
    def load_state(self) -> Optional[StoryBrain]:
        """加载StoryBrain状态"""
        save_path = self.output_dir / f"{self.novel_id}_story_brain.json"
        
        if not save_path.exists():
            print(f"⚠️  未找到保存的状态: {save_path}")
            return None
        
        self.story_brain = StoryBrain.load_from_file(str(save_path))
        print(f"✅ StoryBrain状态已加载: {self.story_brain.title}")
        return self.story_brain
    
    def get_novel_report(self) -> Dict[str, Any]:
        """获取小说创作报告"""
        if not self.story_brain:
            return {}
        
        return {
            "novel_id": self.novel_id,
            "title": self.story_brain.title,
            "progress": {
                "total_chapters": self.story_brain.target_chapters,
                "completed_chapters": len(self.story_brain.chapter_executions),
                "completion_rate": len(self.story_brain.chapter_executions) / self.story_brain.target_chapters * 100
            },
            "plot_points": {
                "total": len(self.story_brain.plot_points),
                "active": len(self.story_brain.active_plot_points),
                "resolved": len(self.story_brain.resolved_plot_points)
            },
            "foreshadowing": {
                "planted": len(self.story_brain.foreshadowing_planted),
                "resolved": len(self.story_brain.foreshadowing_resolved)
            },
            "characters": {
                name: {
                    "arc_length": len(self.story_brain.get_character_arc(name))
                }
                for name in self.story_brain.characters.keys()
            }
        }


class EnhancedWritingContext:
    """
    增强的写作上下文生成器
    
    为WritingAgent提供更丰富的上下文信息
    """
    
    def __init__(self, story_brain: StoryBrain):
        self.story_brain = story_brain
    
    def generate_context(self, chapter_num: int, 
                         previous_content: str = "") -> Dict[str, Any]:
        """
        生成增强的写作上下文
        
        Args:
            chapter_num: 章节号
            previous_content: 前一章的内容（用于兼容性）
            
        Returns:
            增强的上下文字典
        """
        # 获取基础上下文
        base_context = self.story_brain.get_context_for_chapter_writing(chapter_num)
        
        # 生成增强信息
        enhanced = {
            # 基础信息
            "novel_title": self.story_brain.title,
            "theme": self.story_brain.theme,
            "genre": self.story_brain.genre,
            "style": self.story_brain.style,
            
            # 章节信息
            "chapter_num": chapter_num,
            "chapter_plan": base_context.get("chapter_plan", {}),
            
            # 角色信息（增强版）
            "characters": self._generate_character_info(chapter_num),
            
            # 前情提要（完整版，替代500字限制）
            "story_so_far": base_context.get("previous_chapter_recap", ""),
            
            # 情节点信息
            "active_plot_points": self._format_plot_points(
                base_context.get("active_plot_points", [])
            ),
            
            # 伏笔信息
            "foreshadowing": {
                "to_resolve": base_context.get("foreshadowing_to_resolve", []),
                "planted": list(self.story_brain.foreshadowing_planted.keys())
            },
            
            # 一致性约束
            "consistency_rules": base_context.get("consistency_constraints", []),
            
            # 写作指导
            "writing_guidance": self._generate_writing_guidance(chapter_num),
            
            # 向后兼容
            "outline": self._generate_outline_summary(),
            "world": self._generate_world_summary()
        }
        
        return enhanced
    
    def _generate_character_info(self, chapter_num: int) -> Dict[str, Any]:
        """生成角色信息"""
        character_info = {}
        
        for char_name in self.story_brain.characters.keys():
            static = self.story_brain.characters[char_name]
            state = self.story_brain.get_character_state_for_chapter(chapter_num, char_name)
            arc = self.story_brain.get_character_arc(char_name)
            
            character_info[char_name] = {
                "static": static,
                "current_state": state.to_dict() if state else {},
                "arc_progress": f"{len(arc)}章",
                "development_stage": state.development_stage if state else "unknown"
            }
        
        return character_info
    
    def _format_plot_points(self, plot_point_ids: List[str]) -> List[Dict]:
        """格式化情节点信息"""
        formatted = []
        
        for pp_id in plot_point_ids:
            if pp_id in self.story_brain.plot_points:
                pp = self.story_brain.plot_points[pp_id]
                formatted.append({
                    "id": pp_id,
                    "description": pp.description,
                    "status": pp.status,
                    "introduced_in": pp.chapter_introduced
                })
        
        return formatted
    
    def _generate_writing_guidance(self, chapter_num: int) -> Dict[str, Any]:
        """生成写作指导"""
        guidance = {
            "chapter_position": self._get_chapter_position(chapter_num),
            "focus_areas": [],
            "tone_suggestions": []
        }
        
        # 根据章节位置给出建议
        total = self.story_brain.target_chapters
        ratio = chapter_num / total
        
        if ratio < 0.2:
            guidance["chapter_position"] = "开头"
            guidance["focus_areas"] = ["引入角色", "建立世界观", "埋下伏笔"]
            guidance["tone_suggestions"] = ["引人入胜", "建立悬念"]
        elif ratio < 0.6:
            guidance["chapter_position"] = "发展"
            guidance["focus_areas"] = ["推进情节", "发展角色", "增加冲突"]
            guidance["tone_suggestions"] = ["紧张", "深入"]
        elif ratio < 0.9:
            guidance["chapter_position"] = "高潮"
            guidance["focus_areas"] = ["解决主要冲突", "回收伏笔", "角色抉择"]
            guidance["tone_suggestions"] = ["激烈", "情感丰富"]
        else:
            guidance["chapter_position"] = "结局"
            guidance["focus_areas"] = ["收尾", "主题升华", "留下余韵"]
            guidance["tone_suggestions"] = ["圆满", "深刻"]
        
        return guidance
    
    def _get_chapter_position(self, chapter_num: int) -> str:
        """获取章节位置描述"""
        total = self.story_brain.target_chapters
        ratio = chapter_num / total
        
        if ratio < 0.2:
            return "第一幕（开端）"
        elif ratio < 0.6:
            return "第二幕（发展）"
        elif ratio < 0.9:
            return "第三幕（高潮）"
        else:
            return "结局"
    
    def _generate_outline_summary(self) -> str:
        """生成大纲摘要"""
        parts = []
        
        for ch_num in sorted(self.story_brain.chapter_plans.keys()):
            plan = self.story_brain.chapter_plans[ch_num]
            parts.append(f"第{ch_num}章: {plan.title}")
        
        return "\n".join(parts)
    
    def _generate_world_summary(self) -> str:
        """生成世界观摘要"""
        return self._legacy_data.get("world", {}).get("description", "")


# 便捷的集成函数
def integrate_with_pipeline(pipeline_instance, novel_data: Dict[str, Any]) -> StoryBrainAdapter:
    """
    便捷函数：将StoryBrain集成到现有的pipeline
    
    使用示例:
        adapter = integrate_with_pipeline(pipeline, pipeline.novel_data)
        enhanced_context = adapter.create_enhanced_chapter_plan(1)
    """
    adapter = StoryBrainAdapter(
        novel_id=pipeline_instance.novel_id or "unknown",
        output_dir=str(pipeline_instance.output_dir)
    )
    
    adapter.initialize_from_legacy(novel_data)
    
    return adapter


if __name__ == "__main__":
    # 测试适配器
    print("StoryBrain适配器测试")
    print("=" * 60)
    
    # 模拟现有的novel_data
    mock_novel_data = {
        "title": "测试小说",
        "theme": "测试主题",
        "genre": "科幻",
        "style": "硬科幻",
        "num_chapters": 10,
        "characters": [
            {
                "name": "主角A",
                "age": "30岁",
                "appearance": "高大",
                "personality": "勇敢",
                "background": "背景故事",
                "motivation": "拯救世界"
            }
        ],
        "outline": "第一章：开端\n故事开始...\n第二章：发展\n情节推进..."
    }
    
    # 创建适配器
    adapter = StoryBrainAdapter("test_novel_001")
    story_brain = adapter.initialize_from_legacy(mock_novel_data)
    
    # 创建增强的章节规划
    context = adapter.create_enhanced_chapter_plan(1)
    
    print(f"\n增强上下文包含的字段:")
    for key in context.keys():
        print(f"  - {key}")
    
    # 保存状态
    adapter.save_state()
    
    # 生成报告
    report = adapter.get_novel_report()
    print(f"\n小说报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))
