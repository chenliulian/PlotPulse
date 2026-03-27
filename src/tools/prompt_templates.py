"""提示词模板管理"""

import os
from typing import Dict, Optional
from pathlib import Path


class PromptTemplates:
    """提示词模板管理器"""
    
    def __init__(self, templates_dir: str = "prompts"):
        self.templates_dir = Path(templates_dir)
        self._templates: Dict[str, str] = {}
        self._load_templates()
    
    def _load_templates(self):
        """加载所有模板文件"""
        if not self.templates_dir.exists():
            return
        
        for template_file in self.templates_dir.rglob("*.txt"):
            template_name = template_file.stem
            with open(template_file, 'r', encoding='utf-8') as f:
                self._templates[template_name] = f.read()
    
    def get(self, name: str, **kwargs) -> str:
        """获取模板并填充变量"""
        if name not in self._templates:
            raise ValueError(f"Template '{name}' not found")
        
        template = self._templates[name]
        # 简单变量替换
        for key, value in kwargs.items():
            template = template.replace(f"{{{key}}}", str(value))
        
        return template
    
    def list_templates(self) -> list:
        """列出所有可用模板"""
        return list(self._templates.keys())
    
    def add_template(self, name: str, content: str):
        """添加新模板"""
        self._templates[name] = content
