"""重複判定補助ユーティリティ"""

import hashlib
import re
import unicodedata


def normalize_title(title: str) -> str:
    """title を比較しやすい形に正規化する"""
    t = unicodedata.normalize("NFKC", title)
    t = t.lower()
    t = re.sub(r"\s+", "", t)
    return t


def title_hash(title: str) -> str:
    """正規化済みtitleのSHA256ハッシュ（先頭16文字）を返す"""
    normalized = normalize_title(title)
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]
