"""Reddit 投稿を共通 Item に正規化する

利用例::

    from app.normalizers.reddit_normalizer import RedditNormalizer

    normalizer = RedditNormalizer()
    items = normalizer.normalize_posts(raw_list)
    for item in items:
        print(item.title, item.url)
"""

from datetime import datetime, timezone
from typing import Any

from app.models import Item
from app.normalizers.base import BaseNormalizer

_REDDIT_ORIGIN = "https://www.reddit.com"


class RedditNormalizer(BaseNormalizer):
    """Reddit collector の raw dict → 共通 Item"""

    def normalize(self, raw: dict[str, Any]) -> Item:
        try:
            return self._convert(raw)
        except (KeyError, TypeError) as e:
            raise ValueError(f"Reddit 投稿の正規化に失敗: id={raw.get('id', '?')}") from e

    def normalize_posts(self, raw_items: list[dict[str, Any]]) -> list[Item]:
        return [self.normalize(r) for r in raw_items]

    def _convert(self, raw: dict[str, Any]) -> Item:
        permalink = raw.get("permalink", "")
        url = _ensure_absolute(permalink) or raw.get("url", "")

        return Item(
            source="reddit",
            source_item_id=raw["id"],
            title=raw["title"],
            body=raw.get("selftext", "") or "",
            url=url,
            author=raw.get("author", "") or "",
            published_at=datetime.fromtimestamp(raw["created_utc"], tz=timezone.utc),
            engagement_score=_calc_engagement(raw),
            raw_json=dict(raw),
        )


def _ensure_absolute(path: str) -> str:
    """相対パスなら https://www.reddit.com を付与"""
    if not path:
        return ""
    if path.startswith("http"):
        return path
    return _REDDIT_ORIGIN + path


def _calc_engagement(raw: dict[str, Any]) -> float:
    return float(raw.get("score", 0) + raw.get("num_comments", 0) * 2)


# モジュールレベルの便利関数（完了条件に合わせて公開）
_default_normalizer = RedditNormalizer()


def normalize_reddit_post(raw: dict[str, Any]) -> Item:
    """単一投稿を正規化する"""
    return _default_normalizer.normalize(raw)


def normalize_reddit_posts(raw_items: list[dict[str, Any]]) -> list[Item]:
    """複数投稿を一括正規化する"""
    return _default_normalizer.normalize_posts(raw_items)
