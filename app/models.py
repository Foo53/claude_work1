"""収集アイテムの共通データモデル

各ソース（Reddit, Qiita 等）の投稿を統一形式で扱う。
SQLite 保存を前提としたフラットな dataclass。

利用例::

    from app.models import Item
    item = Item(
        source="reddit",
        source_item_id="abc123",
        title="New LLM released",
        body="...",
        url="https://reddit.com/r/...",
        author="user1",
        published_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        collected_at=datetime.now(timezone.utc),
    )
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Item:
    source: str  # "reddit" | "qiita"
    source_item_id: str
    title: str
    body: str
    url: str
    author: str
    published_at: datetime
    collected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    language: str = "unknown"
    engagement_score: float = 0.0
    raw_json: dict[str, Any] = field(default_factory=dict)
