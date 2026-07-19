"""统一 LLM 客户端 — 兼容 OpenAI 协议

兼容 OpenAI / DashScope (阿里百炼) 接口，支持流式与非流式调用。
基于 OpenAI SDK 的异步客户端，支持 Function Calling。
成员B 实现。
"""

from typing import Any, Optional

from loguru import logger
from openai import AsyncOpenAI


class LLMClient:
    """统一 LLM 客户端，兼容 OpenAI / 阿里百炼 DashScope 协议

    支持多模型实例化（每个 ModelConfig 创建一个实例）。
    """

    def __init__(self, base_url: str, api_key: str, model_id: str):
        """
        Args:
            base_url: API Base URL（如 https://dashscope.aliyuncs.com/compatible-mode/v1）
            api_key: API Key
            model_id: 模型 ID（如 qwen-max）
        """
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self.model_id = model_id

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: Optional[list[dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
    ) -> Any:
        """
        调用 LLM 对话接口

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            tools: OpenAI Function Calling 工具定义列表
            temperature: 模型温度 (0.0 ~ 2.0)
            max_tokens: 最大输出 Token 数
            stream: 是否流式输出

        Returns:
            OpenAI 响应对象
        """
        kwargs = {
            "model": self.model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        if tools:
            kwargs["tools"] = tools

        try:
            response = await self.client.chat.completions.create(**kwargs)
            return response
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise

    async def test_connection(self) -> bool:
        """测试模型连通性 — 发送简单消息验证"""
        try:
            response = await self.chat(
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
            )
            if response and response.choices:
                logger.info(f"模型 {self.model_id} 连通性测试成功")
                return True
            return False
        except Exception as e:
            logger.warning(f"模型 {self.model_id} 连通性测试失败: {e}")
            return False


class LLMClientFactory:
    """LLM 客户端工厂 — 从 ModelConfig 创建客户端"""

    @staticmethod
    def create(base_url: str, api_key: str, model_id: str) -> LLMClient:
        """创建 LLM 客户端实例"""
        return LLMClient(base_url=base_url, api_key=api_key, model_id=model_id)