"""items テーブルのリポジトリ"""

from sqlalchemy import select

from app.models import Item
from app.storage.db import get_session
from app.storage.models import ItemRow


class ItemRepository:
    """Item の永続化を担当する"""

    def __init__(self) -> None:
        self._session = get_session()

    def insert(self, item: Item) -> ItemRow:
        """新規保存（重複時は RuntimeError）"""
        row = self._to_row(item)
        self._session.add(row)
        self._session.commit()
        return row

    def upsert(self, item: Item) -> ItemRow:
        """保存または更新（同じ source + source_item_id なら上書き）"""
        existing = self._session.execute(
            select(ItemRow).where(
                ItemRow.source == item.source,
                ItemRow.source_item_id == item.source_item_id,
            )
        ).scalar_one_or_none()

        if existing:
            existing.title = item.title
            existing.body = item.body
            existing.url = item.url
            existing.author = item.author
            existing.published_at = item.published_at
            existing.language = item.language
            existing.engagement_score = item.engagement_score
            if item.raw_json:
                existing.set_raw_json(item.raw_json)
            self._session.commit()
            return existing

        return self.insert(item)

    def list_recent(self, limit: int = 20) -> list[ItemRow]:
        """collected_at 降順で取得"""
        rows = self._session.execute(
            select(ItemRow).order_by(ItemRow.collected_at.desc()).limit(limit)
        ).scalars().all()
        return list(rows)

    def close(self) -> None:
        self._session.close()

    @staticmethod
    def _to_row(item: Item) -> ItemRow:
        row = ItemRow(
            source=item.source,
            source_item_id=item.source_item_id,
            title=item.title,
            body=item.body,
            url=item.url,
            author=item.author,
            published_at=item.published_at,
            collected_at=item.collected_at,
            language=item.language,
            engagement_score=item.engagement_score,
        )
        if item.raw_json:
            row.set_raw_json(item.raw_json)
        return row
