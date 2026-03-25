from __future__ import annotations

import re


class BrandFilter:
    def __init__(self, brands: tuple[str, ...]) -> None:
        self._brands = tuple(self._normalize(brand) for brand in brands if brand.strip())

    def is_branded(self, term: str) -> bool:
        normalized_term = self._normalize(term)
        if not normalized_term:
            return False
        return any(brand and brand in normalized_term for brand in self._brands)

    @staticmethod
    def _normalize(value: str) -> str:
        lowered = value.casefold()
        lowered = re.sub(r"[^a-z0-9\s]+", " ", lowered)
        return " ".join(lowered.split())

