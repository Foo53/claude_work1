"""items / enriched_items のリポジトリ"""

from datetime import datetime, timezone

from sqlalchemy import select, not_, exists, func

from app.models import Item
from app.storage.db import get_session
from app.storage.models import EnrichedItemRow, ItemRow


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

    def get_by_id(self, item_id: int) -> ItemRow | None:
        return self._session.get(ItemRow, item_id)

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


class EnrichedItemRepository:
    """EnrichedItem の永続化を担当する"""

    def __init__(self) -> None:
        self._session = get_session()

    def save(self, item_id: int, short_summary: str, category: str,
             tags: list[str], novelty_score: float, buzz_reason: str,
             llm_model: str = "", prompt_version: str = "") -> EnrichedItemRow:
        """upsert で保存（同じ item_id なら上書き）"""
        existing = self._session.execute(
            select(EnrichedItemRow).where(EnrichedItemRow.item_id == item_id)
        ).scalar_one_or_none()

        if existing:
            existing.short_summary = short_summary
            existing.category = category
            existing.set_tags(tags)
            existing.novelty_score = novelty_score
            existing.buzz_reason = buzz_reason
            existing.llm_model = llm_model
            existing.prompt_version = prompt_version
            self._session.commit()
            return existing

        row = EnrichedItemRow(
            item_id=item_id,
            short_summary=short_summary,
            category=category,
            novelty_score=novelty_score,
            buzz_reason=buzz_reason,
            llm_model=llm_model,
            prompt_version=prompt_version,
        )
        row.set_tags(tags)
        self._session.add(row)
        self._session.commit()
        return row

    def is_enriched(self, item_id: int) -> bool:
        """指定 item_id が既に enrich 済みか"""
        return self._session.query(
            exists().where(EnrichedItemRow.item_id == item_id)
        ).scalar()

    def list_pending_items(self, limit: int = 50) -> list[ItemRow]:
        """まだ enrich されていない Item を取得"""
        enriched_ids = select(EnrichedItemRow.item_id)
        rows = self._session.execute(
            select(ItemRow)
            .where(not_(ItemRow.id.in_(enriched_ids)))
            .order_by(ItemRow.collected_at.desc())
            .limit(limit)
        ).scalars().all()
        return list(rows)

    def list_enriched_since(self, since: datetime) -> list[EnrichedItemRow]:
        """指定日時以降に作成された enriched_items を取得"""
        return list(self._session.execute(
            select(EnrichedItemRow)
            .where(EnrichedItemRow.created_at >= since)
            .order_by(EnrichedItemRow.created_at.desc())
        ).scalars().all())

    def list_fallback_items(self, limit: int = 100) -> list[tuple[EnrichedItemRow, ItemRow]]:
        """fallback 判定の enriched_items と対応する ItemRow を取得"""
        from app.analysis.trend_detector import is_fallback
        enriched_list = self._session.execute(
            select(EnrichedItemRow)
            .order_by(EnrichedItemRow.created_at.desc())
            .limit(limit)
        ).scalars().all()
        fallback = [e for e in enriched_list if is_fallback(e)]
        if not fallback:
            return []
        item_map = self.get_items_by_ids([e.item_id for e in fallback])
        return [(e, item_map[e.item_id]) for e in fallback if e.item_id in item_map]

    def get_items_by_ids(self, item_ids: list[int]) -> dict[int, ItemRow]:
        """item_id → ItemRow のマップ"""
        rows = self._session.execute(
            select(ItemRow).where(ItemRow.id.in_(item_ids))
        ).scalars().all()
        return {r.id: r for r in rows}

    def close(self) -> None:
        self._session.close()
