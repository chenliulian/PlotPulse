"""阿里云 DashScope 模型封装（支持 kimi-k2.5 等模型）"""

import os
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI

from .base_model import BaseModel


class DashScopeModel(BaseModel):
    """阿里云 DashScope 模型封装
    
    支持通过 .env 文件配置：
    - LLM_BASE_URL: https://coding.dashscope.aliyuncs.com/v1
    - LLM_API_KEY: 你的 API Key
    - LLM_MODEL: kimi-k2.5
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[Dict] = None
    ):
        # 从环境变量或参数获取配置
        self.model_name = model_name or os.getenv("LLM_MODEL", "kimi-k2.5")
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url or os.getenv(
            "LLM_BASE_URL",
            "https://coding.dashscope.aliyuncs.com/v1"
        )
        
        if not self.api_key:
            raise ValueError(
                "DashScope API key is required. "
                "Please set LLM_API_KEY in .env file"
            )
        
        super().__init__(self.model_name, config)
        
        # 创建 OpenAI 兼容客户端
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """生成文本"""
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
    
    async def generate_with_system(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """带系统提示词的生成"""
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content
