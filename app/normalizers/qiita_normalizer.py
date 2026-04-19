"""Qiita 記事を共通 Item に正規化する

利用例::

    from app.normalizers.qiita_normalizer import normalize_qiita_item

    item = normalize_qiita_item(raw)
    print(item.title, item.engagement_score)
"""

from datetime import datetime, timezone
from typing import Any

from app.models import Item
from app.normalizers.base import BaseNormalizer


class QiitaNormalizer(BaseNormalizer):
    """Qiita collector の raw dict → 共通 Item"""

    def normalize(self, raw: dict[str, Any]) -> Item:
        try:
            return self._convert(raw)
        except (KeyError, TypeError) as e:
            raise ValueError(f"Qiita 記事の正規化に失敗: id={raw.get('id', '?')}") from e

    def normalize_items(self, raw_items: list[dict[str, Any]]) -> list[Item]:
        return [self.normalize(r) for r in raw_items]

    def _convert(self, raw: dict[str, Any]) -> Item:
        body = raw.get("body", "") or raw.get("rendered_body", "")
        author = raw.get("user_name", "") or raw.get("user_id", "")

        return Item(
            source="qiita",
            source_item_id=raw["id"],
            title=raw["title"],
            body=body,
            url=raw.get("url", ""),
            author=author,
            published_at=_parse_created_at(raw["created_at"]),
            language="ja",
            engagement_score=_calc_engagement(raw),
            raw_json=dict(raw),
        )


def _parse_created_at(value: str) -> datetime:
    """ISO 8601 文字列 → datetime（タイムゾーン付き）"""
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _calc_engagement(raw: dict[str, Any]) -> float:
    return float(raw.get("likes_count", 0) + raw.get("stocks_count", 0) * 2)


_default_normalizer = QiitaNormalizer()


def normalize_qiita_item(raw: dict[str, Any]) -> Item:
    """単一記事を正規化する"""
    return _default_normalizer.normalize(raw)


def normalize_qiita_items(raw_items: list[dict[str, Any]]) -> list[Item]:
    """複数記事を一括正規化する"""
    return _default_normalizer.normalize_items(raw_items)
