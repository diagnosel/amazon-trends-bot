from __future__ import annotations

from dataclasses import replace

from amazon_trends_bot.domain.models import KeywordCandidate, ProductCandidate
from amazon_trends_bot.filters.brand_filter import BrandFilter
from amazon_trends_bot.filters.difficulty_filter import DifficultyFilter
from amazon_trends_bot.filters.keyword_filter import (
    extract_keyword_candidates,
    is_keyword_meaningful,
    normalize_keyword,
)
from amazon_trends_bot.storage.sqlite_storage import SQLiteStorage


class KeywordValidationError(ValueError):
    pass


class BrandedKeywordError(ValueError):
    pass


class KeywordService:
    def __init__(
        self,
        trends_client,
        seo_provider,
        brand_filter: BrandFilter,
        difficulty_filter: DifficultyFilter,
        storage: SQLiteStorage,
        cache_ttl_seconds: int,
    ) -> None:
        self.trends_client = trends_client
        self.seo_provider = seo_provider
        self.brand_filter = brand_filter
        self.difficulty_filter = difficulty_filter
        self.storage = storage
        self.cache_ttl_seconds = cache_ttl_seconds

    async def get_trending_keywords(
        self,
        limit: int,
        *,
        force_refresh: bool = False,
    ) -> list[KeywordCandidate]:
        cache_key = f"keywords:{limit}"
        if not force_refresh:
            cached = await self.storage.cache_get(cache_key)
            if isinstance(cached, list):
                return [KeywordCandidate.from_dict(item) for item in cached]

        raw_keywords = await self.trends_client.fetch_trending_keywords(limit * 3)
        keywords = []
        seen: set[str] = set()
        for raw_keyword in raw_keywords:
            normalized = normalize_keyword(raw_keyword.term)
            if normalized in seen or not is_keyword_meaningful(normalized):
                continue
            if self.brand_filter.is_branded(normalized):
                continue
            difficulty = await self.seo_provider.get_keyword_difficulty(normalized)
            keyword = replace(
                raw_keyword,
                term=normalized,
                difficulty=difficulty,
                is_branded=False,
            )
            if not self.difficulty_filter.allows(keyword.difficulty):
                continue
            seen.add(normalized)
            keywords.append(keyword)
            if len(keywords) >= limit:
                break

        await self.storage.cache_set(
            cache_key,
            [keyword.to_dict() for keyword in keywords],
            self.cache_ttl_seconds,
        )
        return keywords

    async def analyze_keyword(self, term: str) -> KeywordCandidate:
        normalized = normalize_keyword(term)
        if not is_keyword_meaningful(normalized):
            raise KeywordValidationError("Некорректный keyword.")
        if self.brand_filter.is_branded(normalized):
            raise BrandedKeywordError("Брендовые запросы исключены.")

        keyword = await self.trends_client.analyze_keyword(normalized)
        difficulty = await self.seo_provider.get_keyword_difficulty(normalized)
        return replace(
            keyword,
            difficulty=difficulty,
            is_branded=False,
        )

    async def derive_keyword_for_product(self, product: ProductCandidate) -> KeywordCandidate | None:
        candidates = extract_keyword_candidates(product.title, product.brand, limit=3)
        best_candidate: KeywordCandidate | None = None
        for candidate in candidates:
            try:
                keyword = await self._build_internal_candidate(candidate)
            except (KeywordValidationError, BrandedKeywordError):
                continue
            if not self.difficulty_filter.allows(keyword.difficulty):
                continue
            if best_candidate is None or keyword.trend_score > best_candidate.trend_score:
                best_candidate = keyword
        return best_candidate

    async def _build_internal_candidate(self, term: str) -> KeywordCandidate:
        normalized = normalize_keyword(term)
        if not is_keyword_meaningful(normalized):
            raise KeywordValidationError("Некорректный keyword.")
        if self.brand_filter.is_branded(normalized):
            raise BrandedKeywordError("Брендовые запросы исключены.")
        difficulty = await self.seo_provider.get_keyword_difficulty(normalized)
        trend_score = 48 + min(len(normalized.split()) * 9, 28)
        estimated_volume = max(600, trend_score * 100 * max(1, len(normalized.split())))
        return KeywordCandidate(
            term=normalized,
            trend_score=min(90, trend_score),
            estimated_volume=estimated_volume,
            difficulty=difficulty,
            is_branded=False,
        )
