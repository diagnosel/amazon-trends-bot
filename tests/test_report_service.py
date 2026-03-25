from amazon_trends_bot.config import Settings
from amazon_trends_bot.domain.models import KeywordCandidate, ProductCandidate
from amazon_trends_bot.filters import BrandFilter, DifficultyFilter
from amazon_trends_bot.services.keyword_service import KeywordService
from amazon_trends_bot.services.matching_service import MatchingService
from amazon_trends_bot.services.product_service import ProductService
from amazon_trends_bot.services.ranking_service import RankingService
from amazon_trends_bot.services.report_service import ReportService
from amazon_trends_bot.storage.sqlite_storage import SQLiteStorage


class FakeProductSource:
    async def fetch_trending_products(self, limit: int):
        return [
            ProductCandidate(
                asin=f"A{index}",
                title=title,
                brand="",
                category="Home & Kitchen",
                estimated_sales=2000 + index * 100,
                price=20.0,
                url=f"https://amazon.com/dp/A{index}",
            )
            for index, title in enumerate(
                [
                    "Portable Blender for Smoothies",
                    "Desk Organizer with Drawer",
                    "LED Strip Lights for Bedroom",
                    "Mini Desk Fan Rechargeable",
                    "Posture Corrector Support",
                    "Walking Pad Treadmill",
                ],
                start=1,
            )
        ][:limit]


class FakeTrendsClient:
    async def fetch_trending_keywords(self, limit: int):
        seeds = [
            ("portable blender", 88),
            ("desk organizer", 82),
            ("led strip lights", 79),
            ("mini desk fan", 74),
            ("posture corrector", 72),
        ]
        return [
            KeywordCandidate(term, score, score * 100, None, False)
            for term, score in seeds[:limit]
        ]

    async def analyze_keyword(self, term: str):
        return KeywordCandidate(term, 70, 7000, None, False)


class FakeSeoProvider:
    async def get_keyword_difficulty(self, term: str) -> int:
        return 18


async def test_report_generation_and_fallback(tmp_path) -> None:
    storage = SQLiteStorage(tmp_path / "bot.sqlite3")
    await storage.initialize()
    settings = Settings(max_results=5)
    product_service = ProductService(FakeProductSource(), storage, 10)
    keyword_service = KeywordService(
        FakeTrendsClient(),
        FakeSeoProvider(),
        BrandFilter(("apple", "samsung")),
        DifficultyFilter(25),
        storage,
        10,
    )
    report_service = ReportService(
        product_service,
        keyword_service,
        MatchingService(settings),
        RankingService(),
        storage,
        max_results=5,
    )

    report = await report_service.generate_daily_report(force_refresh=True)
    assert len(report.matches) == 5

    cached = await report_service.get_daily_report()
    assert len(cached.matches) == 5


async def test_keyword_analysis_rejects_branded_terms(tmp_path) -> None:
    storage = SQLiteStorage(tmp_path / "bot.sqlite3")
    await storage.initialize()
    keyword_service = KeywordService(
        FakeTrendsClient(),
        FakeSeoProvider(),
        BrandFilter(("apple", "samsung")),
        DifficultyFilter(25),
        storage,
        10,
    )
    try:
        await keyword_service.analyze_keyword("apple watch charger")
    except Exception as exc:
        assert "Брендовые" in str(exc)
    else:
        raise AssertionError("Expected branded keyword error")

