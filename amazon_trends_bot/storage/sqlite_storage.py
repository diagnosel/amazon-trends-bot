from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import aiosqlite

from amazon_trends_bot.domain.models import DailyReport


class SQLiteStorage:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    async def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.database_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    generated_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS cache_entries (
                    cache_key TEXT PRIMARY KEY,
                    expires_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            await db.commit()

    async def save_report(self, report: DailyReport) -> None:
        async with aiosqlite.connect(self.database_path) as db:
            await db.execute(
                "INSERT INTO reports (generated_at, payload) VALUES (?, ?)",
                (report.generated_at.isoformat(), json.dumps(report.to_dict())),
            )
            await db.commit()

    async def load_latest_report(self) -> DailyReport | None:
        async with aiosqlite.connect(self.database_path) as db:
            cursor = await db.execute(
                "SELECT payload FROM reports ORDER BY generated_at DESC LIMIT 1"
            )
            row = await cursor.fetchone()
        if not row:
            return None
        return DailyReport.from_dict(json.loads(row[0]))

    async def cache_set(self, cache_key: str, payload: object, ttl_seconds: int) -> None:
        expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
        async with aiosqlite.connect(self.database_path) as db:
            await db.execute(
                """
                INSERT INTO cache_entries (cache_key, expires_at, payload)
                VALUES (?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    expires_at=excluded.expires_at,
                    payload=excluded.payload
                """,
                (cache_key, expires_at.isoformat(), json.dumps(payload)),
            )
            await db.commit()

    async def cache_get(self, cache_key: str) -> object | None:
        async with aiosqlite.connect(self.database_path) as db:
            cursor = await db.execute(
                "SELECT expires_at, payload FROM cache_entries WHERE cache_key = ?",
                (cache_key,),
            )
            row = await cursor.fetchone()
        if not row:
            return None
        expires_at = datetime.fromisoformat(row[0])
        if expires_at < datetime.now(UTC):
            await self.cache_delete(cache_key)
            return None
        return json.loads(row[1])

    async def cache_delete(self, cache_key: str) -> None:
        async with aiosqlite.connect(self.database_path) as db:
            await db.execute("DELETE FROM cache_entries WHERE cache_key = ?", (cache_key,))
            await db.commit()

