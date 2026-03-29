"""Storage 工具测试用例"""

import os
import tempfile
from pathlib import Path

import pytest

from src.tools.storage import Storage


class TestStorage:
    """Storage 测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.storage = Storage(base_dir=self.temp_dir)
    
    def teardown_method(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_save_json(self):
        """测试保存JSON文件"""
        # 准备数据
        data = {
            "name": "测试",
            "value": 123
        }
        
        # 执行
        self.storage.save_json("test.json", data)
        
        # 验证
        file_path = Path(self.temp_dir) / "test.json"
        assert file_path.exists()
        
        # 读取验证
        with open(file_path, 'r', encoding='utf-8') as f:
            import json
            loaded_data = json.load(f)
        assert loaded_data == data
    
    def test_save_json_with_subdir(self):
        """测试在子目录中保存JSON文件"""
        # 准备数据
        data = {
            "name": "测试",
            "value": 123
        }
        
        # 执行
        self.storage.save_json("test.json", data, "subdir")
        
        # 验证
        file_path = Path(self.temp_dir) / "subdir" / "test.json"
        assert file_path.exists()
    
    def test_load_json(self):
        """测试加载JSON文件"""
        # 准备数据
        data = {
            "name": "测试",
            "value": 123
        }
        
        # 先保存
        self.storage.save_json("test.json", data)
        
        # 执行
        loaded_data = self.storage.load_json("test.json")
        
        # 验证
        assert loaded_data == data
    
    def test_load_json_with_subdir(self):
        """测试加载子目录中的JSON文件"""
        # 准备数据
        data = {
            "name": "测试",
            "value": 123
        }
        
        # 先保存
        self.storage.save_json("test.json", data, "subdir")
        
        # 执行
        loaded_data = self.storage.load_json("test.json", "subdir")
        
        # 验证
        assert loaded_data == data
    
    def test_load_json_nonexistent(self):
        """测试加载不存在的JSON文件"""
        # 执行
        loaded_data = self.storage.load_json("nonexistent.json")
        
        # 验证
        assert loaded_data is None
    
    def test_save_text(self):
        """测试保存文本文件"""
        # 准备数据
        content = "测试文本内容"
        
        # 执行
        self.storage.save_text("test.txt", content)
        
        # 验证
        file_path = Path(self.temp_dir) / "test.txt"
        assert file_path.exists()
        
        # 读取验证
        with open(file_path, 'r', encoding='utf-8') as f:
            loaded_content = f.read()
        assert loaded_content == content
    
    def test_save_text_with_subdir(self):
        """测试在子目录中保存文本文件"""
        # 准备数据
        content = "测试文本内容"
        
        # 执行
        self.storage.save_text("test.txt", content, "subdir")
        
        # 验证
        file_path = Path(self.temp_dir) / "subdir" / "test.txt"
        assert file_path.exists()
    
    def test_load_text(self):
        """测试加载文本文件"""
        # 准备数据
        content = "测试文本内容"
        
        # 先保存
        self.storage.save_text("test.txt", content)
        
        # 执行
        loaded_content = self.storage.load_text("test.txt")
        
        # 验证
        assert loaded_content == content
    
    def test_load_text_with_subdir(self):
        """测试加载子目录中的文本文件"""
        # 准备数据
        content = "测试文本内容"
        
        # 先保存
        self.storage.save_text("test.txt", content, "subdir")
        
        # 执行
        loaded_content = self.storage.load_text("test.txt", "subdir")
        
        # 验证
        assert loaded_content == content
    
    def test_load_text_nonexistent(self):
        """测试加载不存在的文本文件"""
        # 执行
        loaded_content = self.storage.load_text("nonexistent.txt")
        
        # 验证
        assert loaded_content is None
    
    def test_list_files(self):
        """测试列出文件"""
        # 准备数据
        self.storage.save_text("test1.txt", "内容1")
        self.storage.save_text("test2.txt", "内容2")
        self.storage.save_json("test3.json", {"key": "value"})
        
        # 执行
        files = self.storage.list_files()
        
        # 验证
        assert "test1.txt" in files
        assert "test2.txt" in files
        assert "test3.json" in files
    
    def test_list_files_with_subdir(self):
        """测试列出子目录中的文件"""
        # 准备数据
        self.storage.save_text("test1.txt", "内容1", "subdir")
        self.storage.save_text("test2.txt", "内容2", "subdir")
        
        # 执行
        files = self.storage.list_files("subdir")
        
        # 验证
        assert "test1.txt" in files
        assert "test2.txt" in files
    
    def test_list_files_with_pattern(self):
        """测试使用模式列出文件"""
        # 准备数据
        self.storage.save_text("test1.txt", "内容1")
        self.storage.save_text("test2.txt", "内容2")
        self.storage.save_json("test3.json", {"key": "value"})
        
        # 执行
        txt_files = self.storage.list_files(pattern="*.txt")
        json_files = self.storage.list_files(pattern="*.json")
        
        # 验证
        assert "test1.txt" in txt_files
        assert "test2.txt" in txt_files
        assert "test3.json" not in txt_files
        assert "test3.json" in json_files
        assert "test1.txt" not in json_files
    
    def test_list_files_nonexistent_dir(self):
        """测试列出不存在目录中的文件"""
        # 执行
        files = self.storage.list_files("nonexistent")
        
        # 验证
        assert files == []


if __name__ == "__main__":
    pytest.main([__file__])
