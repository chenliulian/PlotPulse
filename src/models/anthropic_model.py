"""Anthropic Claude模型封装"""

import os
from typing import Any, Dict, List, Optional
import anthropic

from .base_model import BaseModel


class AnthropicModel(BaseModel):
    """Anthropic Claude模型封装"""
    
    def __init__(
        self, 
        model_name: str = "claude-3-opus-20240229",
        api_key: Optional[str] = None,
        config: Optional[Dict] = None
    ):
        super().__init__(model_name, config)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
    
    async def generate(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """使用Claude API生成文本"""
        message = await self.client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return message.content[0].text
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """对话模式"""
        message = await self.client.messages.create(
            model=self.model_name,
            max_tokens=kwargs.get("max_tokens", 2000),
            temperature=temperature,
            messages=messages,
            **kwargs
        )
        return message.content[0].text
