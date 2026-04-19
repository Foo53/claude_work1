"""設定管理モジュール"""

from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
import os


@dataclass
class Settings:
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "ai-trend-analyzer/0.1"
    qiita_access_token: str = ""
    db_path: str = "data/trends.db"


def _load_settings() -> Settings:
    load_dotenv()
    return Settings(
        reddit_client_id=os.getenv("REDDIT_CLIENT_ID", ""),
        reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
        reddit_user_agent=os.getenv("REDDIT_USER_AGENT", "ai-trend-analyzer/0.1"),
        qiita_access_token=os.getenv("QIITA_ACCESS_TOKEN", ""),
        db_path=os.getenv("DB_PATH", "data/trends.db"),
    )


settings = _load_settings()
