from __future__ import annotations

import re


STOPWORDS = {
    "for",
    "with",
    "and",
    "the",
    "from",
    "that",
    "your",
    "this",
    "into",
    "usb",
    "amazon",
}


def normalize_keyword(term: str) -> str:
    cleaned = term.casefold()
    cleaned = re.sub(r"https?://\S+", " ", cleaned)
    cleaned = re.sub(r"[^a-z0-9\s]+", " ", cleaned)
    return " ".join(cleaned.split())


def is_keyword_meaningful(term: str) -> bool:
    normalized = normalize_keyword(term)
    if len(normalized) < 3:
        return False
    if not any(char.isalpha() for char in normalized):
        return False
    return len(normalized.split()) >= 1


def extract_meaningful_tokens(text: str) -> tuple[str, ...]:
    normalized = normalize_keyword(text)
    tokens = []
    for token in normalized.split():
        if len(token) < 3:
            continue
        if token in STOPWORDS:
            continue
        tokens.append(token)
    return tuple(tokens)


def extract_keyword_candidates(title: str, brand: str = "", limit: int = 3) -> tuple[str, ...]:
    tokens = [token for token in extract_meaningful_tokens(title) if token not in extract_meaningful_tokens(brand)]
    if not tokens:
        return ()
    candidates: list[str] = []
    for size in (3, 2):
        for index in range(0, max(0, len(tokens) - size + 1)):
            chunk = tokens[index : index + size]
            candidate = " ".join(chunk)
            if candidate not in candidates:
                candidates.append(candidate)
            if len(candidates) >= limit:
                return tuple(candidates)
    if not candidates:
        candidates.append(" ".join(tokens[:limit]))
    return tuple(candidates[:limit])
