"""文本处理工具"""

import re
from typing import List, Dict


class TextUtils:
    """文本处理工具类"""
    
    @staticmethod
    def count_words(text: str) -> int:
        """统计字数（中文字符+英文单词）"""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        return chinese_chars + english_words
    
    @staticmethod
    def split_into_paragraphs(text: str) -> List[str]:
        """将文本分割成段落"""
        paragraphs = re.split(r'\n\s*\n', text.strip())
        return [p.strip() for p in paragraphs if p.strip()]
    
    @staticmethod
    def extract_dialogue(text: str) -> List[Dict[str, str]]:
        """提取对话内容"""
        # 匹配中文引号内的对话
        pattern = r'[""""]([^""""]+)[""""]'
        dialogues = re.findall(pattern, text)
        return [{"type": "dialogue", "content": d} for d in dialogues]
    
    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本"""
        # 移除多余空格
        text = re.sub(r' +', ' ', text)
        # 移除多余换行
        text = re.sub(r'\n\n\n+', '\n\n', text)
        return text.strip()
