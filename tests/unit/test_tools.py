"""工具单元测试"""

import pytest
import json

from src.tools import TextUtils, OutputParser, Storage


class TestTextUtils:
    """测试文本工具"""
    
    def test_count_words_chinese(self):
        text = "这是一段中文文本"
        count = TextUtils.count_words(text)
        assert count == 8  # 8个中文字符
    
    def test_count_words_english(self):
        text = "This is English text"
        count = TextUtils.count_words(text)
        assert count == 4  # 4个英文单词
    
    def test_count_words_mixed(self):
        text = "这是mixed文本with英文"
        count = TextUtils.count_words(text)
        assert count == 8  # 4中文 + 2英文单词
    
    def test_split_into_paragraphs(self):
        text = "段落1\n\n段落2\n\n段落3"
        paragraphs = TextUtils.split_into_paragraphs(text)
        assert len(paragraphs) == 3
        assert paragraphs[0] == "段落1"
    
    def test_extract_dialogue(self):
        text = '他说："你好"，然后回答："再见"'
        dialogues = TextUtils.extract_dialogue(text)
        assert len(dialogues) == 2
    
    def test_clean_text(self):
        text = "  多余  空格   和\n\n\n\n换行  "
        cleaned = TextUtils.clean_text(text)
        assert "  " not in cleaned
        assert "\n\n\n" not in cleaned


class TestOutputParser:
    """测试输出解析器"""
    
    def test_parse_json_valid(self):
        text = '{"key": "value", "number": 123}'
        result = OutputParser.parse_json(text)
        assert result == {"key": "value", "number": 123}
    
    def test_parse_json_in_code_block(self):
        text = '```json\n{"key": "value"}\n```'
        result = OutputParser.parse_json(text)
        assert result == {"key": "value"}
    
    def test_parse_json_invalid(self):
        text = "不是JSON格式"
        result = OutputParser.parse_json(text)
        assert result is None
    
    def test_parse_sections(self):
        text = """## 标题1
内容1

## 标题2
内容2"""
        sections = OutputParser.parse_sections(text)
        assert "标题1" in sections
        assert "标题2" in sections
    
    def test_extract_list(self):
        text = """1. 第一项
2. 第二项
- 第三项
* 第四项"""
        items = OutputParser.extract_list(text)
        assert len(items) == 4


class TestStorage:
    """测试存储工具"""
    
    @pytest.fixture
    def storage(self, tmp_path):
        return Storage(str(tmp_path))
    
    def test_save_and_load_json(self, storage):
        data = {"key": "value", "list": [1, 2, 3]}
        storage.save_json("test.json", data)
        loaded = storage.load_json("test.json")
        assert loaded == data
    
    def test_save_and_load_text(self, storage):
        content = "测试文本内容"
        storage.save_text("test.txt", content)
        loaded = storage.load_text("test.txt")
        assert loaded == content
    
    def test_load_nonexistent_file(self, storage):
        result = storage.load_json("nonexistent.json")
        assert result is None
    
    def test_save_with_subdir(self, storage):
        data = {"test": "data"}
        storage.save_json("test.json", data, "subdir")
        loaded = storage.load_json("test.json", "subdir")
        assert loaded == data
