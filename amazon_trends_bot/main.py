from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher

from amazon_trends_bot.api import GoogleTrendsClient, MockSeoDifficultyProvider, build_product_source
from amazon_trends_bot.bot import BotHandlers
from amazon_trends_bot.config import Settings
from amazon_trends_bot.filters import BrandFilter, DifficultyFilter
from amazon_trends_bot.scheduler import BotScheduler
from amazon_trends_bot.services import (
    KeywordService,
    MatchingService,
    ProductService,
    RankingService,
    ReportService,
)
from amazon_trends_bot.storage import SQLiteStorage


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


async def main() -> None:
    configure_logging()
    settings = Settings.from_env()
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is required to start the bot.")

    settings.ensure_data_dir()
    storage = SQLiteStorage(settings.sqlite_path)
    await storage.initialize()

    product_source = build_product_source(settings)
    trends_client = GoogleTrendsClient(settings)
    seo_provider = MockSeoDifficultyProvider()
    brand_filter = BrandFilter(settings.brands)
    difficulty_filter = DifficultyFilter(settings.keyword_difficulty_threshold)

    product_service = ProductService(product_source, storage, settings.cache_ttl_seconds)
    keyword_service = KeywordService(
        trends_client,
        seo_provider,
        brand_filter,
        difficulty_filter,
        storage,
        settings.cache_ttl_seconds,
    )
    matching_service = MatchingService(settings)
    ranking_service = RankingService()
    report_service = ReportService(
        product_service,
        keyword_service,
        matching_service,
        ranking_service,
        storage,
        max_results=settings.max_results,
    )

    bot = Bot(settings.bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(BotHandlers(report_service, settings).build_router())

    scheduler = BotScheduler(bot, report_service, settings)
    scheduler.start()

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dispatcher.start_polling(bot)
    finally:
        await scheduler.stop()
        await bot.session.close()


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
