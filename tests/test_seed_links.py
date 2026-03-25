from amazon_trends_bot.api.seed_client import SeedProductSource
from amazon_trends_bot.bot.messages import format_match
from amazon_trends_bot.config import Settings
from amazon_trends_bot.domain.models import KeywordCandidate, ProductKeywordMatch


async def test_seed_source_builds_search_urls() -> None:
    source = SeedProductSource(Settings())
    products = await source.fetch_trending_products(1)
    assert products[0].url.startswith("https://www.amazon.com/s?k=")


def test_seed_items_are_labeled_clearly_in_messages() -> None:
    source = SeedProductSource(Settings())
    product = __import__("asyncio").run(source.fetch_trending_products(1))[0]
    match = ProductKeywordMatch(
        product=product,
        keyword=KeywordCandidate(
            term="portable blender",
            trend_score=80,
            estimated_volume=9000,
            difficulty=18,
            is_branded=False,
        ),
        relevance_score=0.9,
        final_score=0.85,
        seo_suggestions=("Сделать статью.",),
    )
    rendered = format_match(match, 1)
    assert "Seed ID" in rendered
    assert "Search URL" in rendered
