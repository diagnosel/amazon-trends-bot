from amazon_trends_bot.filters import BrandFilter, DifficultyFilter, is_keyword_meaningful, normalize_keyword


def test_brand_filter_blocks_known_brands() -> None:
    filter_ = BrandFilter(("apple", "samsung"))
    assert filter_.is_branded("best apple charger")
    assert filter_.is_branded("Samsung galaxy accessories")
    assert not filter_.is_branded("portable blender")


def test_keyword_normalization_and_validation() -> None:
    assert normalize_keyword(" Portable   Blender!! ") == "portable blender"
    assert is_keyword_meaningful("portable blender")
    assert not is_keyword_meaningful("12")


def test_difficulty_filter_allows_low_values() -> None:
    filter_ = DifficultyFilter(25)
    assert filter_.allows(18)
    assert not filter_.allows(31)
    assert not filter_.allows(None)

