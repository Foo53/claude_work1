"""buzz score 計算

enriched item に対して単純なスコアを付与する。
後で重みや要因を追加しやすい構造。

スコア式::

    buzz_score = engagement_score + novelty_score * NOVELTY_WEIGHT
"""

from typing import Any

from app.storage.models import EnrichedItemRow

NOVELTY_WEIGHT = 10.0


def calc_buzz_score(enriched: EnrichedItemRow, engagement_score: float = 0.0) -> float:
    """単一 item の buzz score を計算"""
    return engagement_score + enriched.novelty_score * NOVELTY_WEIGHT


def rank_by_buzz(
    pairs: list[tuple[EnrichedItemRow, float]],
    limit: int = 10,
) -> list[dict[str, Any]]:
    """(EnrichedItemRow, engagement_score) のリストを buzz score 順に返す"""
    scored = [(e, eng, calc_buzz_score(e, eng)) for e, eng in pairs]
    scored.sort(key=lambda t: t[2], reverse=True)

    results: list[dict[str, Any]] = []
    for enriched, engagement, buzz in scored[:limit]:
        results.append({
            "item_id": enriched.item_id,
            "short_summary": enriched.short_summary,
            "category": enriched.category,
            "tags": enriched.get_tags(),
            "buzz_score": round(buzz, 2),
            "novelty_score": enriched.novelty_score,
            "engagement_score": engagement,
            "buzz_reason": enriched.buzz_reason,
        })
    return results
