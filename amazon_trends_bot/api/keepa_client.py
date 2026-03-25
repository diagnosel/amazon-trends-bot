from __future__ import annotations

import logging
from typing import Any

from amazon_trends_bot.config import Settings
from amazon_trends_bot.domain.models import ProductCandidate
from amazon_trends_bot.api.seed_client import SeedProductSource

logger = logging.getLogger(__name__)


class KeepaProductSource:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.seed_source = SeedProductSource(settings)

    async def fetch_trending_products(self, limit: int) -> list[ProductCandidate]:
        if not self.settings.keepa_api_key:
            logger.warning("KEEPA_API_KEY is not set. Falling back to mock products.")
            return await self.seed_source.fetch_trending_products(limit)

        try:
            import keepa
        except ImportError:
            logger.warning("keepa package is unavailable. Falling back to mock products.")
            return await self.seed_source.fetch_trending_products(limit)

        try:
            api = await keepa.AsyncKeepa().create(self.settings.keepa_api_key)
            asins: list[str] = []
            category_names: dict[str, str] = {}
            for term in self.settings.keepa_category_terms:
                category_id, category_name = await self._resolve_category(api, term)
                if not category_id:
                    continue
                batch = await api.best_sellers_query(
                    category_id,
                    domain=self.settings.amazon_domain,
                    wait=True,
                )
                for asin in batch[: self.settings.keepa_products_per_category]:
                    if asin not in asins:
                        asins.append(asin)
                        category_names[asin] = category_name
                if len(asins) >= limit * 3:
                    break

            if not asins:
                logger.warning("Keepa returned no ASINs. Falling back to mock products.")
                return await self.seed_source.fetch_trending_products(limit)

            raw_products = await api.query(
                asins[: limit * 3],
                stats=30,
                history=False,
                progress_bar=False,
                domain=self.settings.amazon_domain,
                wait=True,
            )
            products = [
                self._map_product(product, category_names.get(product.get("asin", ""), "Amazon US"))
                for product in raw_products
                if isinstance(product, dict) and product.get("asin")
            ]
            products = [product for product in products if product.title]
            if products[:limit]:
                return products[:limit]
            return await self.seed_source.fetch_trending_products(limit)
        except Exception as exc:
            logger.warning("Keepa fetch failed, using mock products instead: %s", exc)
            return await self.seed_source.fetch_trending_products(limit)

    async def _resolve_category(self, api: Any, term: str) -> tuple[str | None, str]:
        categories = await api.search_for_categories(term, domain=self.settings.amazon_domain)
        if not categories:
            return None, term
        first_key = next(iter(categories))
        first_value = categories[first_key]
        chosen = first_value
        for value in categories.values():
            if value.get("matched"):
                chosen = value
                break
        category_id = str(chosen.get("catId", first_key))
        return category_id, str(chosen.get("name", term))

    def _map_product(self, payload: dict[str, Any], fallback_category: str) -> ProductCandidate:
        asin = str(payload.get("asin", ""))
        title = str(payload.get("title", "")).strip()
        brand = str(payload.get("brand") or payload.get("manufacturer") or "").strip()
        category_tree = payload.get("categoryTree") or []
        category = fallback_category
        if isinstance(category_tree, list) and category_tree:
            first_category = category_tree[0]
            if isinstance(first_category, dict):
                category = str(first_category.get("name", fallback_category))

        monthly_sold = payload.get("monthlySold") or 0
        if not monthly_sold:
            stats = payload.get("stats") or {}
            monthly_sold = int(stats.get("salesRankDrops30") or 0) * 12
        monthly_sold = int(monthly_sold or 0)
        price = self._extract_price(payload)

        return ProductCandidate(
            asin=asin,
            title=title,
            brand=brand,
            category=category,
            estimated_sales=max(monthly_sold, 1),
            price=price,
            url=f"{self.settings.amazon_base_url}/dp/{asin}",
        )

    @staticmethod
    def _extract_price(payload: dict[str, Any]) -> float | None:
        for key in ("buyBoxPrice", "buyBoxShipping", "lastPrice", "newPrice"):
            value = payload.get(key)
            if isinstance(value, (int, float)) and value > 0:
                return round(float(value) / 100, 2)

        stats = payload.get("stats") or {}
        current = stats.get("current")
        if isinstance(current, list):
            for value in current:
                if isinstance(value, (int, float)) and value > 0:
                    return round(float(value) / 100, 2)
        return None

