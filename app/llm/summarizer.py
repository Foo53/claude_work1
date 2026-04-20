"""投稿要約モジュール

LLM で title + body先頭 → JSON要約 を生成する。
LLM 失敗時は title ベースの fallback を返す。

利用例::

    from app.llm.summarizer import summarize_item
    result = summarize_item(item)
    print(result["summary"])
"""

from __future__ import annotations

import logging
from typing import Any

from app.llm.client import generate_json
from app.llm.prompts import SUMMARY_PROMPT, SUMMARY_SYSTEM
from app.models import Item

logger = logging.getLogger(__name__)

_BODY_MAX_CHARS = 500


def build_summary_input(item: Item) -> dict[str, str]:
    """LLM に渡す入力を整形する（body は先頭500文字まで）"""
    return {
        "title": item.title,
        "body": item.body[:_BODY_MAX_CHARS],
        "source": item.source,
        "engagement_score": str(item.engagement_score),
    }


def _fallback(item: Item) -> dict[str, Any]:
    """LLM 失敗時の最低限の結果"""
    return {
        "summary": item.title[:120],
        "tags": [],
        "novelty_score": 0.0,
        "buzz_reason": "",
    }


def summarize_item(item: Item) -> dict[str, Any]:
    """1件の投稿を要約する"""
    inputs = build_summary_input(item)
    prompt = SUMMARY_PROMPT.format(**inputs)

    try:
        result = generate_json(prompt, system=SUMMARY_SYSTEM)
        return {
            "summary": str(result.get("summary", ""))[:120],
            "tags": list(result.get("tags", []))[:5],
            "novelty_score": float(result.get("novelty_score", 0.0)),
            "buzz_reason": str(result.get("buzz_reason", "")),
        }
    except Exception:
        logger.warning("要約失敗、fallback使用 source_item_id=%s", item.source_item_id, exc_info=True)
        return _fallback(item)


def summarize_items(items: list[Item]) -> list[dict[str, Any]]:
    """複数件を一括要約する"""
    return [summarize_item(item) for item in items]
