"""本地模型封装"""

from typing import Any, Dict, List, Optional

from .base_model import BaseModel


class LocalModel(BaseModel):
    """本地部署模型封装（如使用transformers）"""
    
    def __init__(
        self, 
        model_path: str,
        config: Optional[Dict] = None
    ):
        super().__init__("local_model", config)
        self.model_path = model_path
        self._model = None
        self._tokenizer = None
    
    def _load_model(self):
        """懒加载模型"""
        if self._model is None:
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                self._model = AutoModelForCausalLM.from_pretrained(self.model_path)
            except ImportError:
                raise ImportError("transformers library is required for local models")
    
    async def generate(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """使用本地模型生成文本"""
        self._load_model()
        # 实际实现需要使用transformers的generate方法
        return "本地模型生成的文本"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """对话模式"""
        # 将消息列表转换为单个prompt
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        return await self.generate(prompt, temperature, **kwargs)
