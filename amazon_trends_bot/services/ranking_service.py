from __future__ import annotations

from amazon_trends_bot.domain.models import ProductKeywordMatch


class RankingService:
    def select_top_matches(
        self,
        matches: list[ProductKeywordMatch],
        limit: int,
    ) -> list[ProductKeywordMatch]:
        ranked = sorted(
            matches,
            key=lambda item: (
                item.final_score,
                item.keyword.estimated_volume,
                item.product.estimated_sales,
            ),
            reverse=True,
        )
        unique_matches: list[ProductKeywordMatch] = []
        seen_asins: set[str] = set()
        for match in ranked:
            if match.product.asin in seen_asins:
                continue
            seen_asins.add(match.product.asin)
            unique_matches.append(match)
            if len(unique_matches) >= limit:
                break
        return unique_matches

