"""角色设计Agent"""

import re
from typing import Any, Dict, List
from .base_agent import NovelAgent


class CharacterAgent(NovelAgent):
    """负责角色设计和开发"""
    
    def __init__(self, model, config=None):
        super().__init__("CharacterAgent", model, config)
    
    async def execute(self, input_data: Dict) -> Dict:
        """
        设计小说角色
        input_data: 包含情节大纲、角色数量要求等
        """
        plot_outline = input_data.get("plot_outline", "")
        num_characters = input_data.get("num_characters", 3)
        revision_notes = input_data.get("revision_notes", "")
        
        prompt = self._build_prompt(plot_outline, num_characters, revision_notes)
        characters_text = await self.generate(prompt)
        
        return {
            "characters": self._parse_characters(characters_text),
            "protagonist": self._identify_protagonist(characters_text),
            "antagonist": self._identify_antagonist(characters_text),
            "raw_content": characters_text
        }
    
    def _build_prompt(self, plot_outline: str, num_characters: int, revision_notes: str = "") -> str:
        revision_section = f"\n修改要求：{revision_notes}\n" if revision_notes else ""
        
        # 生成角色模板
        character_templates = []
        for i in range(1, num_characters + 1):
            character_templates.append(f"""角色{i}：
- 姓名：[角色姓名]
- 年龄：[年龄]
- 外貌：[外貌特征描述]
- 性格：[性格特点]
- 背景：[背景故事]
- 动机：[动机和目标]
- 弧线：[角色发展弧线]
- 关系：[与其他角色的关系]
""")
        
        all_templates = "\n".join(character_templates)
        
        return f"""基于以下情节大纲，设计**{num_characters}个**主要角色。

【重要】必须严格按照要求设计**{num_characters}个角色**，不能多也不能少。

情节大纲：
{plot_outline}
{revision_section}
请为每个角色提供以下信息（使用清晰的格式）：

{all_templates}

【要求】
1. 必须设计**{num_characters}个角色**，每个角色都要有完整的设定
2. 角色要有鲜明的个性差异
3. 主角需要有清晰的成长弧线
4. 反派动机要充分，不要脸谱化
5. 角色之间的关系要有张力
6. 使用"角色X："的格式清晰标注每个角色
"""
    
    def _parse_characters(self, text: str) -> List[Dict]:
        """解析角色信息"""
        characters = []
        
        # 尝试匹配角色块 - 支持多种格式
        # 格式1: "角色1：" 或 "角色1:"
        # 格式2: "## 角色1" 或 "### 角色1"
        # 格式3: "**角色1**"
        character_blocks = re.split(r'(?:\n|\r\n)(?:#{1,3}\s*)?角色\d+[:：]|(?:\n|\r\n)(?:#{1,3}\s*)?\*\*角色\d+\*\*', text)
        
        # 如果上面的分割没有结果，尝试其他模式
        if len(character_blocks) <= 1:
            # 尝试匹配 "角色1" 作为标题的情况
            character_blocks = re.split(r'(?:\n|\r\n)角色\d+\s*[:：]?\s*(?:\n|\r\n)', text)
        
        for block in character_blocks[1:]:  # 跳过第一个空块
            block = block.strip()
            if not block:
                continue
                
            character = {}
            
            # 提取姓名 - 支持多种格式
            # 格式1: "- 姓名：xxx" 或 "- 姓名: xxx"
            # 格式2: "**姓名**：xxx"
            # 格式3: "姓名：xxx" (行首)
            name_match = re.search(r'(?:^|\n)\s*[-*]*\s*\*?姓名\*?[:：]\s*(.+?)(?:\n|$)', block, re.MULTILINE)
            if not name_match:
                # 尝试匹配 "姓名：xxx" 在行中的情况
                name_match = re.search(r'姓名[:：]\s*([^\n]+)', block)
            character['name'] = name_match.group(1).strip() if name_match else "未命名"
            
            # 提取年龄
            age_match = re.search(r'(?:^|\n)\s*[-*]*\s*\*?年龄\*?[:：]\s*(.+?)(?:\n|$)', block, re.MULTILINE)
            if not age_match:
                age_match = re.search(r'年龄[:：]\s*([^\n]+)', block)
            character['age'] = age_match.group(1).strip() if age_match else "未知"
            
            # 提取外貌
            appearance_match = re.search(r'(?:^|\n)\s*[-*]*\s*\*?外貌\*?[:：]\s*(.+?)(?=\n\s*[-*]*\s*\*?[^\n]*\*?[:：]|$)', block, re.MULTILINE | re.DOTALL)
            if not appearance_match:
                appearance_match = re.search(r'外貌[:：]\s*(.+?)(?=\n[^\n]*[:：]|$)', block, re.DOTALL)
            character['appearance'] = appearance_match.group(1).strip() if appearance_match else ""
            
            # 提取性格
            personality_match = re.search(r'(?:^|\n)\s*[-*]*\s*\*?性格\*?[:：]\s*(.+?)(?=\n\s*[-*]*\s*\*?[^\n]*\*?[:：]|$)', block, re.MULTILINE | re.DOTALL)
            if not personality_match:
                personality_match = re.search(r'性格[:：]\s*(.+?)(?=\n[^\n]*[:：]|$)', block, re.DOTALL)
            character['personality'] = personality_match.group(1).strip() if personality_match else ""
            
            # 提取背景
            background_match = re.search(r'(?:^|\n)\s*[-*]*\s*\*?背景\*?[:：]\s*(.+?)(?=\n\s*[-*]*\s*\*?[^\n]*\*?[:：]|$)', block, re.MULTILINE | re.DOTALL)
            if not background_match:
                background_match = re.search(r'背景[:：]\s*(.+?)(?=\n[^\n]*[:：]|$)', block, re.DOTALL)
            character['background'] = background_match.group(1).strip() if background_match else ""
            
            # 提取动机
            motivation_match = re.search(r'(?:^|\n)\s*[-*]*\s*\*?动机\*?[:：]\s*(.+?)(?=\n\s*[-*]*\s*\*?[^\n]*\*?[:：]|$)', block, re.MULTILINE | re.DOTALL)
            if not motivation_match:
                motivation_match = re.search(r'动机[:：]\s*(.+?)(?=\n[^\n]*[:：]|$)', block, re.DOTALL)
            character['motivation'] = motivation_match.group(1).strip() if motivation_match else ""
            
            # 提取弧线
            arc_match = re.search(r'(?:^|\n)\s*[-*]*\s*\*?弧线\*?[:：]\s*(.+?)(?=\n\s*[-*]*\s*\*?[^\n]*\*?[:：]|$)', block, re.MULTILINE | re.DOTALL)
            if not arc_match:
                arc_match = re.search(r'弧线[:：]\s*(.+?)(?=\n[^\n]*[:：]|$)', block, re.DOTALL)
            character['arc'] = arc_match.group(1).strip() if arc_match else ""
            
            # 提取关系
            relationship_match = re.search(r'(?:^|\n)\s*[-*]*\s*\*?关系\*?[:：]\s*(.+?)(?=\n\s*[-*]*\s*\*?[^\n]*\*?[:：]|$)', block, re.MULTILINE | re.DOTALL)
            if not relationship_match:
                relationship_match = re.search(r'关系[:：]\s*(.+?)(?=\n[^\n]*[:：]|$)', block, re.DOTALL)
            character['relationship'] = relationship_match.group(1).strip() if relationship_match else ""
            
            # 生成描述摘要
            description_parts = []
            if character.get('age') and character['age'] != "未知":
                description_parts.append(f"年龄：{character['age']}")
            if character.get('personality'):
                description_parts.append(f"性格：{character['personality'][:50]}...")
            if character.get('background'):
                description_parts.append(f"背景：{character['background'][:50]}...")
            
            character['description'] = ' | '.join(description_parts) if description_parts else "暂无描述"
            
            characters.append(character)
        
        return characters if characters else [{"name": "未命名角色", "description": "暂无描述"}]
    
    def _identify_protagonist(self, text: str) -> Dict:
        """识别主角"""
        # 尝试找到标记为主角的角色
        protagonist_match = re.search(r'主角|主人公|主角[:：]', text, re.IGNORECASE)
        if protagonist_match:
            # 尝试提取主角姓名
            name_match = re.search(r'(?:主角|主人公)[:：]?\s*\n?姓名[:：]\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
            if name_match:
                return {"name": name_match.group(1).strip(), "role": "protagonist"}
        
        # 默认返回第一个角色为主角
        return {"name": "主角", "role": "protagonist"}
    
    def _identify_antagonist(self, text: str) -> Dict:
        """识别反派"""
        # 尝试找到标记为反派的角色
        antagonist_match = re.search(r'反派|对手|敌人| antagonist', text, re.IGNORECASE)
        if antagonist_match:
            # 尝试提取反派姓名
            name_match = re.search(r'(?:反派|对手|敌人)[:：]?\s*\n?姓名[:：]\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
            if name_match:
                return {"name": name_match.group(1).strip(), "role": "antagonist"}
        
        return {"name": "反派", "role": "antagonist"}
