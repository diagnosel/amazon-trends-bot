from __future__ import annotations

from amazon_trends_bot.domain.models import ProductCandidate
from amazon_trends_bot.storage.sqlite_storage import SQLiteStorage


class ProductService:
    def __init__(self, source, storage: SQLiteStorage, cache_ttl_seconds: int) -> None:
        self.source = source
        self.storage = storage
        self.cache_ttl_seconds = cache_ttl_seconds

    async def get_trending_products(
        self,
        limit: int,
        *,
        force_refresh: bool = False,
    ) -> list[ProductCandidate]:
        cache_key = f"products:{limit}"
        if not force_refresh:
            cached = await self.storage.cache_get(cache_key)
            if isinstance(cached, list):
                return [ProductCandidate.from_dict(item) for item in cached]

        products = await self.source.fetch_trending_products(limit)
        await self.storage.cache_set(
            cache_key,
            [product.to_dict() for product in products],
            self.cache_ttl_seconds,
        )
        return products

