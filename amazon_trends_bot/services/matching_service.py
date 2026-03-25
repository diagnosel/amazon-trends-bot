from __future__ import annotations

from amazon_trends_bot.config import Settings
from amazon_trends_bot.domain.models import KeywordCandidate, ProductCandidate, ProductKeywordMatch
from amazon_trends_bot.filters.keyword_filter import extract_meaningful_tokens


class MatchingService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def match_products(
        self,
        products: list[ProductCandidate],
        keywords: list[KeywordCandidate],
        *,
        min_relevance: float = 0.15,
    ) -> list[ProductKeywordMatch]:
        matches: list[ProductKeywordMatch] = []
        for product in products:
            for keyword in keywords:
                match = self.score_match(product, keyword)
                if match and match.relevance_score >= min_relevance:
                    matches.append(match)
        return matches

    def score_match(
        self,
        product: ProductCandidate,
        keyword: KeywordCandidate,
    ) -> ProductKeywordMatch | None:
        keyword_tokens = set(extract_meaningful_tokens(keyword.term))
        product_tokens = set(extract_meaningful_tokens(f"{product.title} {product.category}"))
        if not keyword_tokens or not product_tokens:
            return None

        overlap = keyword_tokens & product_tokens
        overlap_score = len(overlap) / max(1, len(keyword_tokens))
        partial_score = 0.0
        if overlap_score == 0 and keyword.term in product.title.casefold():
            partial_score = 0.35
        category_bonus = 0.15 if any(token in extract_meaningful_tokens(product.category) for token in keyword_tokens) else 0.0
        relevance_score = min(1.0, overlap_score + partial_score + category_bonus)
        if relevance_score <= 0:
            return None

        sales_score = min(product.estimated_sales / 5000, 1.0)
        trend_score = min(keyword.trend_score / 100, 1.0)
        difficulty = keyword.difficulty if keyword.difficulty is not None else 100
        difficulty_bonus = max(0.0, 1 - (difficulty / max(1, self.settings.keyword_difficulty_threshold * 2)))
        final_score = (
            relevance_score * 0.5
            + sales_score * 0.25
            + trend_score * 0.15
            + difficulty_bonus * 0.10
        )
        return ProductKeywordMatch(
            product=product,
            keyword=keyword,
            relevance_score=round(relevance_score, 4),
            final_score=round(final_score, 4),
            seo_suggestions=self._build_suggestions(product, keyword),
        )

    @staticmethod
    def _build_suggestions(
        product: ProductCandidate,
        keyword: KeywordCandidate,
    ) -> tuple[str, ...]:
        return (
            f"Сделать отдельную статью под запрос '{keyword.term}'.",
            f"Использовать '{keyword.term}' в title, H2 и FAQ блока для товара '{product.title}'.",
            f"Добавить сравнение и long-tail варианты вокруг темы '{keyword.term}'.",
        )

