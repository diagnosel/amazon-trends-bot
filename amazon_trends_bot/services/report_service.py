from __future__ import annotations

import logging

from amazon_trends_bot.domain.models import DailyReport, KeywordCommandResult, ProductKeywordMatch, utc_now
from amazon_trends_bot.services.keyword_service import BrandedKeywordError, KeywordValidationError

logger = logging.getLogger(__name__)


class ReportService:
    def __init__(
        self,
        product_service,
        keyword_service,
        matching_service,
        ranking_service,
        storage,
        *,
        max_results: int,
    ) -> None:
        self.product_service = product_service
        self.keyword_service = keyword_service
        self.matching_service = matching_service
        self.ranking_service = ranking_service
        self.storage = storage
        self.max_results = max_results

    async def get_daily_report(self) -> DailyReport:
        latest = await self.storage.load_latest_report()
        if latest is not None:
            return latest
        return await self.generate_daily_report(force_refresh=False)

    async def generate_daily_report(self, *, force_refresh: bool) -> DailyReport:
        latest = await self.storage.load_latest_report()
        try:
            products = await self.product_service.get_trending_products(
                limit=self.max_results * 4,
                force_refresh=force_refresh,
            )
            keywords = await self.keyword_service.get_trending_keywords(
                limit=self.max_results * 6,
                force_refresh=force_refresh,
            )
            matches = self.matching_service.match_products(products, keywords)
            if len(self.ranking_service.select_top_matches(matches, self.max_results)) < self.max_results:
                matches.extend(await self._build_supplemental_matches(products, matches))

            top_matches = self.ranking_service.select_top_matches(matches, self.max_results)
            if len(top_matches) < self.max_results:
                raise RuntimeError("Not enough matches to build daily report")

            report = DailyReport(
                generated_at=utc_now(),
                matches=tuple(top_matches[: self.max_results]),
            )
            await self.storage.save_report(report)
            return report
        except Exception as exc:
            logger.exception("Daily report generation failed: %s", exc)
            if latest is not None:
                return latest
            raise

    async def analyze_keyword(self, term: str) -> KeywordCommandResult:
        keyword = await self.keyword_service.analyze_keyword(term)
        products = await self.product_service.get_trending_products(limit=15, force_refresh=False)
        matches = self.matching_service.match_products(products, [keyword], min_relevance=0.0)
        ranked = self.ranking_service.select_top_matches(matches, 3)
        note = None
        if not ranked:
            note = "Сильных товарных совпадений не найдено. Попробуйте более конкретный long-tail запрос."
        return KeywordCommandResult(
            keyword=keyword,
            matches=tuple(ranked),
            generated_at=utc_now(),
            note=note,
        )

    async def _build_supplemental_matches(
        self,
        products,
        current_matches: list[ProductKeywordMatch],
    ) -> list[ProductKeywordMatch]:
        current_asins = {match.product.asin for match in current_matches}
        supplemental: list[ProductKeywordMatch] = []
        for product in products:
            if product.asin in current_asins:
                continue
            keyword = await self.keyword_service.derive_keyword_for_product(product)
            if keyword is None:
                continue
            match = self.matching_service.score_match(product, keyword)
            if match:
                supplemental.append(match)
            if len(supplemental) >= self.max_results:
                break
        return supplemental


__all__ = [
    "BrandedKeywordError",
    "KeywordValidationError",
    "ReportService",
]
