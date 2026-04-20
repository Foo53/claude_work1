"""トークン予算管理"""

# 概算: 日本語1文字 ≈ 2-3 tokens、英語1単語 ≈ 1.3 tokens
CHARS_PER_TOKEN = 2.5
DEFAULT_BUDGET = 4000


def estimate_tokens(text: str) -> int:
    """テキストのトークン数を概算する"""
    return int(len(text) / CHARS_PER_TOKEN)


def truncate_to_budget(text: str, budget: int = DEFAULT_BUDGET) -> str:
    """予算内に収まるようにテキストを切り詰める"""
    max_chars = int(budget * CHARS_PER_TOKEN)
    if len(text) <= max_chars:
        return text
    return text[:max_chars]


def build_truncated_text(text: str, budget: int = DEFAULT_BUDGET) -> str:
    """truncate_to_budget のエイリアス"""
    return truncate_to_budget(text, budget=budget)
