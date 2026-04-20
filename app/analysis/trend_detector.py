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

    # tag 集計（簡易正規化）
    tag_counts: Counter[str] = Counter()
    for e in enriched_list:
        tag_counts.update(_normalize_tag(t) for t in e.get_tags())

    # fallback / LLM 判定
    fallback_count = sum(1 for e in enriched_list if is_fallback(e))
    llm_count = len(enriched_list) - fallback_count

    repo.close()

    return {
        "hours": hours,
        "total": len(enriched_list),
        "category_counts": dict(category_counts.most_common()),
        "source_counts": dict(source_counts.most_common()),
        "tag_top10": dict(tag_counts.most_common(10)),
        "highlighted": rank_by_buzz(pairs, limit=10),
        "fallback_count": fallback_count,
        "llm_count": llm_count,
    }


def _empty_stats(hours: int) -> dict[str, Any]:
    return {
        "hours": hours,
        "total": 0,
        "category_counts": {},
        "source_counts": {},
        "tag_top10": {},
        "highlighted": [],
        "fallback_count": 0,
        "llm_count": 0,
    }


_TAG_ALIASES: dict[str, str] = {
    "large-language-model": "llm",
    "language-model": "llm",
    "language-models": "llm",
    "large language model": "llm",
    "ai-agent": "ai-agent",
    "ai-agents": "ai-agent",
    "ai agent": "ai-agent",
    "agents": "ai-agent",
    "vs-code": "vscode",
    "visual-studio-code": "vscode",
    "openai-api": "openai",
    "gpt-4": "gpt",
    "gpt-4o": "gpt",
    "chatgpt": "gpt",
}


def _normalize_tag(tag: str) -> str:
    """表記ゆれの軽い正規化"""
    t = tag.strip().lower().replace(" ", "-")
    return _TAG_ALIASES.get(t, t)


def is_fallback(enriched: "EnrichedItemRow") -> bool:
    """LLM未使用の fallback データかどうかを判定"""
    if enriched.buzz_reason == "(LLM未使用)":
        return True
    # 補助条件: モデル名空 + タグ空 + novelty 0.0 → 旧データの fallback の可能性
    if not enriched.llm_model and not enriched.get_tags() and enriched.novelty_score == 0.0:
        return True
    return False
