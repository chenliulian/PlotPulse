"""模型管理器"""

from typing import Dict, Optional, Type
from .base_model import BaseModel


class ModelManager:
    """管理多个模型实例"""
    
    def __init__(self):
        self._models: Dict[str, BaseModel] = {}
        self._default_model: Optional[str] = None
    
    def register_model(self, name: str, model: BaseModel, default: bool = False):
        """注册模型"""
        self._models[name] = model
        if default or self._default_model is None:
            self._default_model = name
    
    def get_model(self, name: Optional[str] = None) -> BaseModel:
        """获取模型实例"""
        if name is None:
            name = self._default_model
        if name not in self._models:
            raise ValueError(f"Model '{name}' not found")
        return self._models[name]
    
    def list_models(self) -> list:
        """列出所有可用模型"""
        return list(self._models.keys())
