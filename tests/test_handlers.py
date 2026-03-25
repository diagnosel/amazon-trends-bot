from types import SimpleNamespace

from amazon_trends_bot.bot.handlers import BotHandlers
from amazon_trends_bot.config import Settings
from amazon_trends_bot.domain.models import DailyReport, KeywordCandidate, KeywordCommandResult, ProductCandidate, ProductKeywordMatch, utc_now


class DummyMessage:
    def __init__(self) -> None:
        self.answers: list[str] = []

    async def answer(self, text: str, reply_markup=None) -> None:
        self.answers.append(text)


class FakeReportService:
    async def get_daily_report(self):
        return DailyReport(
            generated_at=utc_now(),
            matches=(self._match(),),
        )

    async def analyze_keyword(self, term: str):
        return KeywordCommandResult(
            keyword=KeywordCandidate(term=term, trend_score=70, estimated_volume=7000, difficulty=18, is_branded=False),
            matches=(self._match(),),
        )

    @staticmethod
    def _match():
        return ProductKeywordMatch(
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
            seo_suggestions=("Сделать статью.", "Добавить FAQ."),
        )


async def test_start_handler_returns_russian_text() -> None:
    handlers = BotHandlers(FakeReportService(), Settings())
    message = DummyMessage()
    await handlers.handle_start(message)
    assert "Привет" in message.answers[0]


async def test_daily_handler_returns_report() -> None:
    handlers = BotHandlers(FakeReportService(), Settings())
    message = DummyMessage()
    await handlers.handle_daily(message)
    assert "Ежедневный top 5" in message.answers[0]


async def test_keyword_handler_returns_report() -> None:
    handlers = BotHandlers(FakeReportService(), Settings())
    message = DummyMessage()
    await handlers.handle_keyword(message, SimpleNamespace(args="portable blender"))
    assert "Keyword: portable blender" in message.answers[0]

