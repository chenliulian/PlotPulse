"""OpenAI模型封装"""

import os
from typing import Any, Dict, List, Optional
import openai

from .base_model import BaseModel


class OpenAIModel(BaseModel):
    """OpenAI GPT模型封装"""
    
    def __init__(
        self, 
        model_name: str = "gpt-4",
        api_key: Optional[str] = None,
        config: Optional[Dict] = None
    ):
        super().__init__(model_name, config)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
    
    async def generate(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """使用OpenAI API生成文本"""
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """对话模式"""
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            **kwargs
        )
        return response.choices[0].message.content
