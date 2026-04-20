"""カテゴリ分類器

ルールベースで判定 → 当てはまらなければ LLM にフォールバック。
LLM 失敗時は "other" を返す。

利用例::

    from app.llm.classifier import classify_item
    cat = classify_item("New Claude Code features", "summary", ["AI", "CLI"])
    print(cat)  # "oss_cli"
"""

from __future__ import annotations

import logging

from app.llm.client import generate_json
from app.llm.prompts import CLASSIFY_PROMPT, CLASSIFY_SYSTEM, CLASSIFY_CATEGORIES
from app.constants import CATEGORIES

logger = logging.getLogger(__name__)

# カテゴリ → キーワードのルール辞書（後で調整しやすい）
_RULES: dict[str, list[str]] = {
    "coding_agent": ["coding agent", "コーディングエージェント", "devin", "swe-agent", "autonomous agent"],
    "mcp_tool_use": ["mcp", "tool use", "function calling", "ツール使用"],
    "rag": ["rag", "retrieval", "検索拡張", "vector search", "embedding"],
    "eval_benchmark": ["benchmark", "eval", "評価", "leaderboard", "mt-bench"],
    "local_llm": ["local llm", "llama", "ollama", "on-device", "gguf", "量化"],
    "oss_cli": ["cli", "ターミナル", "コマンドライン", "oss", "オープンソースツール"],
    "voice_realtime": ["voice", "音声", "realtime", "speech", "tts", "whisper"],
    "ai_ide_devex": ["ide", "開発体験", "devex", "copilot", "補完", "lsp", "エディタ"],
    "prompt_engineering": ["prompt", "プロンプト", "chain-of-thought", "few-shot", "cot"],
    "ai_infra_serving": ["serving", "推論", "inference", "deploy", "vllm", "triton", "サービング"],
}


def _rule_based(title: str, summary: str, tags: list[str]) -> str | None:
    """キーワードマッチで分類（最初にヒットしたカテゴリを返す）"""
    text = f"{title} {summary} {' '.join(tags)}".lower()
    for category, keywords in _RULES.items():
        for kw in keywords:
            if kw in text:
                return category
    return None


def _llm_classify(title: str, summary: str, tags: list[str]) -> str:
    """LLM で分類（失敗時は other）"""
    prompt = CLASSIFY_PROMPT.format(
        title=title,
        summary=summary,
        tags=", ".join(tags),
        categories=CLASSIFY_CATEGORIES,
    )
    try:
        result = generate_json(prompt, system=CLASSIFY_SYSTEM)
        category = str(result.get("category", "other"))
        if category in CATEGORIES:
            return category
        logger.warning("LLM が未知カテゴリを返した: %s", category)
        return "other"
    except Exception:
        logger.warning("LLM分類失敗、other を返す", exc_info=True)
        return "other"


def classify_item(title: str, summary: str, tags: list[str]) -> str:
    """投稿をカテゴリに分類する"""
    rule_result = _rule_based(title, summary, tags)
    if rule_result:
        return rule_result
    return _llm_classify(title, summary, tags)
