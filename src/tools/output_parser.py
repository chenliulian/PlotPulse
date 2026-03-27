"""输出解析器"""

import json
import re
from typing import Dict, Any, List, Optional


class OutputParser:
    """解析AI模型输出"""
    
    @staticmethod
    def parse_json(text: str) -> Optional[Dict]:
        """从文本中提取JSON"""
        try:
            # 尝试直接解析
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # 尝试从代码块中提取
        pattern = r'```(?:json)?\s*([\s\S]*?)```'
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue
        
        return None
    
    @staticmethod
    def parse_sections(text: str) -> Dict[str, str]:
        """按章节解析文本"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in text.split('\n'):
            # 匹配标题行（如：## 标题、1. 标题、标题：）
            if re.match(r'^(#{1,6}\s+|\d+\.\s+|.+[：:])', line.strip()):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = re.sub(r'^(#{1,6}\s+|\d+\.\s+|\s*[：:]\s*)', '', line.strip())
                current_content = []
            else:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    @staticmethod
    def extract_list(text: str) -> List[str]:
        """提取列表项"""
        # 匹配数字列表或符号列表
        pattern = r'^(?:\d+[.．]\s*|[•\-\*]\s*)(.+)$'
        items = []
        for line in text.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                items.append(match.group(1).strip())
        return items
