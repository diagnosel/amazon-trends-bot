from __future__ import annotations

from amazon_trends_bot.api.keepa_client import KeepaProductSource
from amazon_trends_bot.api.seed_client import SeedProductSource
from amazon_trends_bot.config import Settings


def build_product_source(settings: Settings):
    if settings.product_source == "keepa":
        return KeepaProductSource(settings)
    return SeedProductSource(settings)

