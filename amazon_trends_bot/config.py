from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_BRANDS = (
    "apple",
    "samsung",
    "xiaomi",
    "nike",
    "adidas",
    "sony",
    "lg",
    "canon",
    "dyson",
    "nintendo",
    "playstation",
    "xbox",
)

DEFAULT_CATEGORY_TERMS = (
    "Home & Kitchen",
    "Electronics",
    "Beauty & Personal Care",
    "Sports & Outdoors",
    "Office Products",
)


def _split_csv(raw_value: str | None, fallback: tuple[str, ...]) -> tuple[str, ...]:
    if not raw_value:
        return fallback
    values = tuple(item.strip() for item in raw_value.split(",") if item.strip())
    return values or fallback


@dataclass(slots=True)
class Settings:
    bot_token: str = ""
    daily_chat_id: str = ""
    product_source: str = "seed"
    keepa_api_key: str = ""
    seo_api_key: str = ""
    timezone: str = "Europe/Kiev"
    daily_hour: int = 9
    daily_minute: int = 0
    amazon_domain: str = "US"
    trends_geo: str = "US"
    max_results: int = 5
    keyword_difficulty_threshold: int = 25
    brands: tuple[str, ...] = field(default_factory=lambda: DEFAULT_BRANDS)
    keepa_category_terms: tuple[str, ...] = field(default_factory=lambda: DEFAULT_CATEGORY_TERMS)
    keepa_products_per_category: int = 8
    cache_ttl_seconds: int = 60 * 60 * 6
    data_dir: Path = Path("data")
    sqlite_path: Path = Path("data/bot.sqlite3")

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        data_dir = Path(os.getenv("DATA_DIR", "data")).expanduser()
        sqlite_path = Path(os.getenv("SQLITE_PATH", str(data_dir / "bot.sqlite3"))).expanduser()
        return cls(
            bot_token=os.getenv("BOT_TOKEN", "").strip(),
            daily_chat_id=os.getenv("DAILY_CHAT_ID", "").strip(),
            product_source=os.getenv("PRODUCT_SOURCE", "seed").strip().lower(),
            keepa_api_key=os.getenv("KEEPA_API_KEY", "").strip(),
            seo_api_key=os.getenv("SEO_API_KEY", "").strip(),
            timezone=os.getenv("TIMEZONE", "Europe/Kiev").strip(),
            daily_hour=int(os.getenv("DAILY_HOUR", "9")),
            daily_minute=int(os.getenv("DAILY_MINUTE", "0")),
            amazon_domain=os.getenv("AMAZON_DOMAIN", "US").strip().upper(),
            trends_geo=os.getenv("TRENDS_GEO", "US").strip().upper(),
            max_results=int(os.getenv("MAX_RESULTS", "5")),
            keyword_difficulty_threshold=int(os.getenv("KEYWORD_DIFFICULTY_THRESHOLD", "25")),
            brands=_split_csv(os.getenv("BRANDS"), DEFAULT_BRANDS),
            keepa_category_terms=_split_csv(os.getenv("KEEPA_CATEGORY_TERMS"), DEFAULT_CATEGORY_TERMS),
            keepa_products_per_category=int(os.getenv("KEEPA_PRODUCTS_PER_CATEGORY", "8")),
            cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", str(60 * 60 * 6))),
            data_dir=data_dir,
            sqlite_path=sqlite_path,
        )

    @property
    def amazon_base_url(self) -> str:
        domain_map = {
            "US": "https://www.amazon.com",
            "UK": "https://www.amazon.co.uk",
            "DE": "https://www.amazon.de",
        }
        return domain_map.get(self.amazon_domain, "https://www.amazon.com")

    def ensure_data_dir(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
