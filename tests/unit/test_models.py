"""模型单元测试"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from src.models import ModelManager
from src.models.base_model import BaseModel


class TestModelManager:
    """测试模型管理器"""
    
    @pytest.fixture
    def manager(self):
        return ModelManager()
    
    @pytest.fixture
    def mock_model(self):
        model = Mock(spec=BaseModel)
        model.get_name.return_value = "test_model"
        return model
    
    def test_register_model(self, manager, mock_model):
        manager.register_model("test", mock_model)
        assert "test" in manager.list_models()
    
    def test_get_model(self, manager, mock_model):
        manager.register_model("test", mock_model)
        retrieved = manager.get_model("test")
        assert retrieved == mock_model
    
    def test_get_default_model(self, manager, mock_model):
        manager.register_model("test", mock_model, default=True)
        retrieved = manager.get_model()
        assert retrieved == mock_model
    
    def test_get_nonexistent_model(self, manager):
        with pytest.raises(ValueError):
            manager.get_model("nonexistent")


class TestBaseModel:
    """测试模型基类"""
    
    def test_model_initialization(self):
        # 抽象类不能直接实例化
        with pytest.raises(TypeError):
            BaseModel("test")
