"""テキスト前処理ユーティリティ"""

import re


def clean_text(text: str) -> str:
    """連続空白・改行・前後空白を正規化する"""
    if not text:
        return ""
    # 連続する空白（半角・全角）を1つに
    text = re.sub(r"[ \t\u3000]+", " ", text)
    # 3行以上の連続改行を2行に
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 前後空白除去
    return text.strip()


def strip_urls(text: str) -> str:
    """http/https のURLを除去する"""
    return re.sub(r"https?://\S+", "", text)
