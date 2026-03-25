from amazon_trends_bot.config import Settings
from amazon_trends_bot.domain.models import KeywordCandidate, ProductCandidate
from amazon_trends_bot.services.matching_service import MatchingService
from amazon_trends_bot.services.ranking_service import RankingService


def build_product(asin: str, title: str, sales: int) -> ProductCandidate:
    return ProductCandidate(
        asin=asin,
        title=title,
        brand="",
        category="Home & Kitchen",
        estimated_sales=sales,
        price=20.0,
        url=f"https://amazon.com/dp/{asin}",
    )


def test_matching_prefers_overlap() -> None:
    settings = Settings()
    service = MatchingService(settings)
    product = build_product("A1", "Portable Blender for Smoothies", 3000)
    keyword = KeywordCandidate(
        term="portable blender",
        trend_score=80,
        estimated_volume=9000,
        difficulty=18,
        is_branded=False,
    )
    match = service.score_match(product, keyword)
    assert match is not None
    assert match.relevance_score > 0.5


def test_ranking_returns_unique_products() -> None:
    settings = Settings()
    matching = MatchingService(settings)
    ranking = RankingService()
    product = build_product("A1", "Portable Blender for Smoothies", 3000)
    keywords = [
        KeywordCandidate("portable blender", 80, 9000, 18, False),
        KeywordCandidate("travel blender", 75, 7000, 16, False),
    ]
    matches = [matching.score_match(product, keyword) for keyword in keywords]
    top = ranking.select_top_matches([match for match in matches if match is not None], 5)
    assert len(top) == 1
    assert top[0].product.asin == "A1"

