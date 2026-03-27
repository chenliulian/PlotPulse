"""存储工具"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


class Storage:
    """文件存储管理"""
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def save_json(self, filename: str, data: Dict, subdir: str = ""):
        """保存JSON文件"""
        filepath = self._get_filepath(filename, subdir)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_json(self, filename: str, subdir: str = "") -> Optional[Dict]:
        """加载JSON文件"""
        filepath = self._get_filepath(filename, subdir)
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_text(self, filename: str, content: str, subdir: str = ""):
        """保存文本文件"""
        filepath = self._get_filepath(filename, subdir)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def load_text(self, filename: str, subdir: str = "") -> Optional[str]:
        """加载文本文件"""
        filepath = self._get_filepath(filename, subdir)
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _get_filepath(self, filename: str, subdir: str) -> Path:
        """获取文件路径"""
        if subdir:
            return self.base_dir / subdir / filename
        return self.base_dir / filename
    
    def list_files(self, subdir: str = "", pattern: str = "*") -> list:
        """列出文件"""
        target_dir = self.base_dir / subdir if subdir else self.base_dir
        if not target_dir.exists():
            return []
        return [f.name for f in target_dir.glob(pattern)]
