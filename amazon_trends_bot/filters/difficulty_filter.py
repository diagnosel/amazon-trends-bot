from __future__ import annotations


class DifficultyFilter:
    def __init__(self, max_difficulty: int) -> None:
        self.max_difficulty = max_difficulty

    def allows(self, difficulty: int | None) -> bool:
        if difficulty is None:
            return False
        return difficulty <= self.max_difficulty

