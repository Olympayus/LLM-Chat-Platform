"""Elasticsearch 客户端封装

提供 ES 异步客户端连接管理和基本的索引操作。
同时兼容全局 ES 客户端实例和 get_es() 函数方式。
"""

from typing import Optional

from elasticsearch import AsyncElasticsearch
from app.config import settings


class ESClient:
    """Elasticsearch 客户端封装"""

    def __init__(self):
        self._client: Optional[AsyncElasticsearch] = None

    async def init(self) -> None:
        """初始化 ES 客户端连接"""
        hosts = settings.ES_HOSTS if hasattr(settings, "ES_HOSTS") else "http://localhost:9200"
        self._client = AsyncElasticsearch(hosts=hosts)
        # 验证连通性
        try:
            info = await self._client.info()
            import logging
            logging.info(f"Elasticsearch 连接成功 (version: {info['version']['number']})")
        except Exception as e:
            import logging
            logging.error(f"Elasticsearch 连接失败: {e}")
            raise

    @property
    def client(self) -> AsyncElasticsearch:
        if self._client is None:
            raise RuntimeError("ES client not initialized. Call init() first.")
        return self._client

    async def close(self) -> None:
        """关闭 ES 客户端"""
        if self._client:
            await self._client.close()
            self._client = None

    async def ping(self) -> bool:
        """检测 ES 是否可用"""
        try:
            return await self.client.ping()
        except Exception:
            return False

    async def create_index_if_not_exists(self, index_name: str, mapping: dict) -> bool:
        """创建索引（如果不存在）"""
        exists = await self.client.indices.exists(index=index_name)
        if not exists:
            response = await self.client.indices.create(
                index=index_name,
                body=mapping,
            )
            return response.get("acknowledged", False)
        return True


# 全局单例（成员D 的 ES 服务依赖此实例）
es_client = ESClient()

async def init_elasticsearch() -> None:
    """Init ES connection (lifecycle wrapper)"""
    await es_client.init()

async def close_elasticsearch() -> None:
    """Close ES connection (lifecycle wrapper)"""
    await es_client.close()
