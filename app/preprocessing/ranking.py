"""候補絞り込み・スコアリング

収集済み Item から LLM 分析対象を選別・順位付けする。

スコア式::

    final_score = engagement_score * ENGAGEMENT_WEIGHT
                 + title_bonus（TITLE_MIN_LEN 以上なら +TITLE_BONUS）
                 + body_bonus （BODY_MIN_LEN  以上なら +BODY_BONUS）

利用例::

    from app.preprocessing.ranking import select_candidates
    top = select_candidates(all_items, limit=10)
"""

from app.models import Item

# 閾値
TITLE_MIN_LEN = 10
BODY_MIN_LEN = 20
ENGAGEMENT_FLOOR = 0.0

# スコア重み
ENGAGEMENT_WEIGHT = 1.0
TITLE_BONUS = 50.0
BODY_BONUS = 30.0


def _is_valid(item: Item) -> bool:
    """除外判定: タイトル短すぎ / 本文短すぎ / エンゲージメント低すぎ"""
    if len(item.title) < TITLE_MIN_LEN:
        return False
    if len(item.body) < BODY_MIN_LEN:
        return False
    if item.engagement_score < ENGAGEMENT_FLOOR:
        return False
    return True


def score_candidates(items: list[Item]) -> list[tuple[Item, float]]:
    """各 Item にスコアを付与し (item, score) のリストを返す"""
    scored: list[tuple[Item, float]] = []
    for item in items:
        if not _is_valid(item):
            continue
        s = item.engagement_score * ENGAGEMENT_WEIGHT
        if len(item.title) >= TITLE_MIN_LEN:
            s += TITLE_BONUS
        if len(item.body) >= BODY_MIN_LEN:
            s += BODY_BONUS
        scored.append((item, s))
    return scored


def select_candidates(items: list[Item], limit: int = 20) -> list[Item]:
    """スコア順で上位 limit 件を返す"""
    scored = score_candidates(items)
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [item for item, _ in scored[:limit]]


def explain_candidate(item: Item) -> dict:
    """item が候補として通るかどうかと、その理由を返す"""
    reasons: list[str] = []
    title_len = len(item.title)
    body_len = len(item.body)

    if title_len < TITLE_MIN_LEN:
        reasons.append(f"title短すぎ ({title_len} < {TITLE_MIN_LEN})")
    if body_len < BODY_MIN_LEN:
        reasons.append(f"body短すぎ ({body_len} < {BODY_MIN_LEN})")
    if item.engagement_score < ENGAGEMENT_FLOOR:
        reasons.append(f"engagement低い ({item.engagement_score} < {ENGAGEMENT_FLOOR})")

    return {
        "title_len": title_len,
        "body_len": body_len,
        "engagement_score": item.engagement_score,
        "passed": len(reasons) == 0,
        "reasons": reasons,
    }
