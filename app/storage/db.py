"""DB接続とテーブル初期化"""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_engine(db_path: str | None = None) -> Engine:
    """SQLite エンジンを取得する（遅延初期化）"""
    global _engine
    if _engine is None:
        path = db_path or settings.db_path
        _engine = create_engine(f"sqlite:///{path}", echo=False)
    return _engine


def get_session() -> Session:
    """新しいセッションを返す"""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(get_engine())
    return _session_factory()


def init_db(db_path: str | None = None) -> None:
    """テーブルを作成する（Alembic なしの MVP 用）"""
    from app.storage.models import Base

    Base.metadata.create_all(get_engine(db_path))
