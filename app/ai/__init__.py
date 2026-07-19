"""AI 引擎

包含:
- client.py: LLM 客户端（OpenAI/DashScope 兼容，基于 OpenAI SDK）
- nl2sql_engine.py: NL2SQL 智能问数引擎（成员E）
"""

from app.ai.client import LLMClient, LLMClientFactory

# 全局单例工厂引用（兼容远程已有的引用方式）
llm_client = LLMClientFactory

# NL2SQL 引擎（成员E）
from app.ai.nl2sql import Nl2sqlEngine, nl2sql_engine

__all__ = [
    "LLMClient",
    "LLMClientFactory",
    "llm_client",
    "Nl2sqlEngine",
    "nl2sql_engine",
]