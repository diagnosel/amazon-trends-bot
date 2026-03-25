from __future__ import annotations

from typing import Protocol

from amazon_trends_bot.filters.keyword_filter import extract_meaningful_tokens


class SeoDifficultyProvider(Protocol):
    async def get_keyword_difficulty(self, term: str) -> int:
        ...


class MockSeoDifficultyProvider:
    async def get_keyword_difficulty(self, term: str) -> int:
        tokens = extract_meaningful_tokens(term)
        base = 34
        long_tail_bonus = max(0, len(tokens) - 2) * 5
        token_length_bonus = min(len(" ".join(tokens)), 30) // 5
        commercial_penalty = sum(1 for token in tokens if token in {"best", "top", "cheap", "review"})
        difficulty = base - long_tail_bonus - token_length_bonus + commercial_penalty * 4
        return max(8, min(55, difficulty))

