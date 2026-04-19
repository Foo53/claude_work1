"""items テーブルの ORM モデル"""

import json
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Index, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ItemRow(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    source_item_id: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    author: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    collected_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    engagement_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    raw_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

    __table_args__ = (
        Index("ix_source_item", "source", "source_item_id", unique=True),
    )

    def set_raw_json(self, data: dict) -> None:
        self.raw_json = json.dumps(data, ensure_ascii=False, default=str)

    def get_raw_json(self) -> dict:
        return json.loads(self.raw_json) if self.raw_json else {}
