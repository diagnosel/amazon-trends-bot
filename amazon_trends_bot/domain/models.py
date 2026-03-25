from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class ProductCandidate:
    asin: str
    title: str
    brand: str
    category: str
    estimated_sales: int
    price: float | None
    url: str

    def to_dict(self) -> dict[str, object]:
        return {
            "asin": self.asin,
            "title": self.title,
            "brand": self.brand,
            "category": self.category,
            "estimated_sales": self.estimated_sales,
            "price": self.price,
            "url": self.url,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "ProductCandidate":
        return cls(
            asin=str(payload["asin"]),
            title=str(payload["title"]),
            brand=str(payload.get("brand", "")),
            category=str(payload.get("category", "")),
            estimated_sales=int(payload.get("estimated_sales", 0)),
            price=float(payload["price"]) if payload.get("price") is not None else None,
            url=str(payload.get("url", "")),
        )


@dataclass(slots=True)
class KeywordCandidate:
    term: str
    trend_score: int
    estimated_volume: int
    difficulty: int | None
    is_branded: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "term": self.term,
            "trend_score": self.trend_score,
            "estimated_volume": self.estimated_volume,
            "difficulty": self.difficulty,
            "is_branded": self.is_branded,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "KeywordCandidate":
        difficulty = payload.get("difficulty")
        return cls(
            term=str(payload["term"]),
            trend_score=int(payload.get("trend_score", 0)),
            estimated_volume=int(payload.get("estimated_volume", 0)),
            difficulty=int(difficulty) if difficulty is not None else None,
            is_branded=bool(payload.get("is_branded", False)),
        )


@dataclass(slots=True)
class ProductKeywordMatch:
    product: ProductCandidate
    keyword: KeywordCandidate
    relevance_score: float
    final_score: float
    seo_suggestions: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "product": self.product.to_dict(),
            "keyword": self.keyword.to_dict(),
            "relevance_score": self.relevance_score,
            "final_score": self.final_score,
            "seo_suggestions": list(self.seo_suggestions),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "ProductKeywordMatch":
        return cls(
            product=ProductCandidate.from_dict(dict(payload["product"])),
            keyword=KeywordCandidate.from_dict(dict(payload["keyword"])),
            relevance_score=float(payload.get("relevance_score", 0.0)),
            final_score=float(payload.get("final_score", 0.0)),
            seo_suggestions=tuple(str(item) for item in payload.get("seo_suggestions", [])),
        )


@dataclass(slots=True)
class DailyReport:
    generated_at: datetime
    matches: tuple[ProductKeywordMatch, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "generated_at": self.generated_at.isoformat(),
            "matches": [match.to_dict() for match in self.matches],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "DailyReport":
        generated_at = datetime.fromisoformat(str(payload["generated_at"]))
        return cls(
            generated_at=generated_at,
            matches=tuple(
                ProductKeywordMatch.from_dict(dict(item)) for item in payload.get("matches", [])
            ),
        )


@dataclass(slots=True)
class KeywordCommandResult:
    keyword: KeywordCandidate
    matches: tuple[ProductKeywordMatch, ...]
    generated_at: datetime = field(default_factory=utc_now)
    note: str | None = None

