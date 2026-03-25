from amazon_trends_bot.domain.models import DailyReport, KeywordCandidate, ProductCandidate, ProductKeywordMatch, utc_now
from amazon_trends_bot.storage.sqlite_storage import SQLiteStorage


async def test_storage_persists_latest_report(tmp_path) -> None:
    database_path = tmp_path / "bot.sqlite3"
    storage = SQLiteStorage(database_path)
    await storage.initialize()

    report = DailyReport(
        generated_at=utc_now(),
        matches=(
            ProductKeywordMatch(
                product=ProductCandidate(
                    asin="A1",
                    title="Portable Blender",
                    brand="",
                    category="Home & Kitchen",
                    estimated_sales=3200,
                    price=29.0,
                    url="https://amazon.com/dp/A1",
                ),
                keyword=KeywordCandidate(
                    term="portable blender",
                    trend_score=80,
                    estimated_volume=9000,
                    difficulty=18,
                    is_branded=False,
                ),
                relevance_score=0.9,
                final_score=0.86,
                seo_suggestions=("Сделать статью.",),
            ),
        ),
    )
    await storage.save_report(report)

    reopened = SQLiteStorage(database_path)
    await reopened.initialize()
    latest = await reopened.load_latest_report()
    assert latest is not None
    assert latest.matches[0].product.asin == "A1"

