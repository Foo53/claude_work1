"""Qiita 記事取得 collector

Qiita API v2 から新着記事を取得する。
戻り値は normalizer にそのまま渡せる raw dict の list。

利用例::

    collector = QiitaCollector()
    items = collector.fetch_recent_items(per_page=10)
    for item in items:
        print(item["title"])
"""

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

_QIITA_BASE = "https://qiita.com/api/v2"


def _is_retryable(exc: BaseException) -> bool:
    """429 / 5xx のみリトライする"""
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code == 429 or exc.response.status_code >= 500
    if isinstance(exc, httpx.TimeoutException):
        return True
    return False


class QiitaCollector:
    """Qiita API v2 経由で記事を取得する"""

    def __init__(self, token: str | None = None) -> None:
        self._token = token or settings.qiita_access_token

    def _build_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    @retry(
        retry=retry_if_exception(_is_retryable),
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=10),
        reraise=True,
    )
    def fetch_recent_items(self, page: int = 1, per_page: int = 20) -> list[dict[str, Any]]:
        """新着記事を取得する

        戻り値の各要素は以下キーを持つ dict:
          id, title, body, rendered_body, url,
          user_id, user_name,
          created_at, likes_count, stocks_count
        """
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(
                f"{_QIITA_BASE}/items",
                params={"page": page, "per_page": per_page},
                headers=self._build_headers(),
            )
            resp.raise_for_status()

        raw_list: list[dict[str, Any]] = resp.json()
        items: list[dict[str, Any]] = []
        for raw in raw_list:
            user = raw.get("user", {})
            items.append({
                "id": raw.get("id", ""),
                "title": raw.get("title", ""),
                "body": raw.get("body", ""),
                "rendered_body": raw.get("rendered_body", ""),
                "url": raw.get("url", ""),
                "user_id": user.get("id", "") if isinstance(user, dict) else "",
                "user_name": user.get("name", "") if isinstance(user, dict) else "",
                "created_at": raw.get("created_at", ""),
                "likes_count": raw.get("likes_count", 0),
                "stocks_count": raw.get("stocks_count", 0),
            })

        logger.info("Qiita 記事取得完了 page=%d count=%d", page, len(items))
        return items
