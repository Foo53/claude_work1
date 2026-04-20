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


def _extract_fallback_tags(item: Item) -> list[str]:
    """title/body から簡易的に技術キーワードを抽出する"""
    _KNOWN = [
        "python", "javascript", "typescript", "rust", "go", "java",
        "react", "vue", "next.js", "aws", "gcp", "azure", "docker", "kubernetes",
        "llm", "gpt", "claude", "gemini", "ai", "ml", "deep learning",
        "api", "rest", "graphql", "sql", "database", "redis",
        "terraform", "ci/cd", "github", "git",
    ]
    text = f"{item.title} {item.body[:300]}".lower()
    return [t for t in _KNOWN if t in text][:5]


def _fallback(item: Item) -> dict[str, Any]:
    """LLM 失敗時の最低限の結果"""
    body_head = item.body[:80].replace("\n", " ").strip()
    summary = f"{item.title[:80]}。{body_head}" if body_head else item.title[:120]
    logger.info("fallback で保存: source_item_id=%s", item.source_item_id)
    return {
        "summary": summary[:120],
        "tags": _extract_fallback_tags(item),
        "novelty_score": 0.0,
        "buzz_reason": "(LLM未使用)",
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
