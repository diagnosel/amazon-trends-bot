from __future__ import annotations

import asyncio
import logging

from amazon_trends_bot.config import Settings
from amazon_trends_bot.domain.models import KeywordCandidate
from amazon_trends_bot.filters.keyword_filter import normalize_keyword

logger = logging.getLogger(__name__)


class GoogleTrendsClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.timeout_seconds = 8

    async def fetch_trending_keywords(self, limit: int) -> list[KeywordCandidate]:
        try:
            terms = await asyncio.wait_for(
                asyncio.to_thread(self._fetch_trending_terms_sync),
                timeout=self.timeout_seconds,
            )
            if not terms:
                raise ValueError("Google Trends returned no terms")
            keywords = []
            for index, term in enumerate(terms[:limit]):
                normalized = normalize_keyword(term)
                if not normalized:
                    continue
                trend_score = max(20, 100 - index * 4)
                keywords.append(
                    KeywordCandidate(
                        term=normalized,
                        trend_score=trend_score,
                        estimated_volume=self._estimate_volume(trend_score, normalized),
                        difficulty=None,
                        is_branded=False,
                    )
                )
            return keywords or self._mock_keywords(limit)
        except Exception as exc:
            logger.warning("Google Trends fetch failed, using mock keywords instead: %s", exc)
            return self._mock_keywords(limit)

    async def analyze_keyword(self, term: str) -> KeywordCandidate:
        normalized = normalize_keyword(term)
        if not normalized:
            raise ValueError("Keyword is empty after normalization")
        try:
            trend_score = await asyncio.wait_for(
                asyncio.to_thread(self._analyze_keyword_sync, normalized),
                timeout=self.timeout_seconds,
            )
        except Exception as exc:
            logger.warning("Keyword analysis via Google Trends failed, using heuristic score: %s", exc)
            trend_score = self._heuristic_trend_score(normalized)

        return KeywordCandidate(
            term=normalized,
            trend_score=trend_score,
            estimated_volume=self._estimate_volume(trend_score, normalized),
            difficulty=None,
            is_branded=False,
        )

    def _fetch_trending_terms_sync(self) -> list[str]:
        from pytrends.request import TrendReq

        client = TrendReq(hl="en-US", tz=360)
        data = client.trending_searches(pn=self._pn_value())
        if data.empty:
            return []
        return [str(item).strip() for item in data.iloc[:, 0].tolist() if str(item).strip()]

    def _analyze_keyword_sync(self, term: str) -> int:
        from pytrends.request import TrendReq

        client = TrendReq(hl="en-US", tz=360)
        client.build_payload([term], timeframe="today 3-m", geo=self.settings.trends_geo)
        interest = client.interest_over_time()
        if interest.empty or term not in interest.columns:
            return self._heuristic_trend_score(term)
        values = [int(value) for value in interest[term].tolist() if value is not None]
        if not values:
            return self._heuristic_trend_score(term)
        recent_window = values[-10:] if len(values) >= 10 else values
        return max(10, min(100, int(sum(recent_window) / len(recent_window))))

    def _estimate_volume(self, trend_score: int, term: str) -> int:
        token_bonus = max(1, len(term.split()))
        return max(500, int(trend_score * 110 * token_bonus))

    @staticmethod
    def _heuristic_trend_score(term: str) -> int:
        score = 45 + min(len(term.split()) * 8, 25)
        if any(token in term for token in ("portable", "desk", "led", "skin", "walking", "meal")):
            score += 10
        return max(15, min(90, score))

    def _mock_keywords(self, limit: int) -> list[KeywordCandidate]:
        seeds = [
            ("portable blender", 88),
            ("desk organizer", 83),
            ("led strip lights bedroom", 79),
            ("mini desk fan", 77),
            ("posture corrector", 76),
            ("coffee mug warmer", 73),
            ("walking pad", 80),
            ("ice roller face", 72),
            ("meal prep containers", 71),
            ("sunscreen stick", 69),
        ]
        return [
            KeywordCandidate(
                term=term,
                trend_score=score,
                estimated_volume=self._estimate_volume(score, term),
                difficulty=None,
                is_branded=False,
            )
            for term, score in seeds[:limit]
        ]

    def _pn_value(self) -> str:
        mapping = {
            "US": "united_states",
            "UK": "united_kingdom",
        }
        return mapping.get(self.settings.trends_geo, "united_states")
