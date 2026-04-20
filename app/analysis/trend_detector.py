"""日次レポート用の集計ロジック

直近24時間の enriched_items を分析し、レポート生成に渡せる dict を返す。

利用例::

    from app.analysis.trend_detector import build_daily_stats
    stats = build_daily_stats()
    print(stats["category_counts"])
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from app.analysis.buzz_score import rank_by_buzz
from app.storage.repositories import EnrichedItemRepository

_HOURS = 24


def build_daily_stats(hours: int = _HOURS) -> dict[str, Any]:
    """直近 N 時間の enriched_items を集計する"""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    repo = EnrichedItemRepository()
    enriched_list = repo.list_enriched_since(since)

    if not enriched_list:
        repo.close()
        return _empty_stats(hours)

    # item_id → ItemRow を一括取得
    item_ids = [e.item_id for e in enriched_list]
    item_map = repo.get_items_by_ids(item_ids)

    # engagement_score を引き当て
    pairs = [(e, item_map[e.item_id].engagement_score) for e in enriched_list if e.item_id in item_map]

    # category / source 集計
    category_counts = Counter(e.category for e in enriched_list)
    source_counts = Counter(item_map[e.item_id].source for e in enriched_list if e.item_id in item_map)

    # tag 集計
    tag_counts: Counter[str] = Counter()
    for e in enriched_list:
        tag_counts.update(e.get_tags())

    repo.close()

    return {
        "hours": hours,
        "total": len(enriched_list),
        "category_counts": dict(category_counts.most_common()),
        "source_counts": dict(source_counts.most_common()),
        "tag_top10": dict(tag_counts.most_common(10)),
        "highlighted": rank_by_buzz(pairs, limit=10),
    }


def _empty_stats(hours: int) -> dict[str, Any]:
    return {
        "hours": hours,
        "total": 0,
        "category_counts": {},
        "source_counts": {},
        "tag_top10": {},
        "highlighted": [],
    }
