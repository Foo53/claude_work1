"""Reddit 投稿取得 collector

Reddit API から subreddit の新着投稿を取得する。
戻り値は normalizer にそのまま渡せる raw dict の list。

利用例::

    collector = RedditCollector()
    posts = collector.fetch_new_posts("MachineLearning", limit=5)
    for post in posts:
        print(post["title"])
"""

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

_REDDIT_BASE = "https://oauth.reddit.com"
_USER_AGENT = settings.reddit_user_agent


def _is_retryable(exc: BaseException) -> bool:
    """429 / 5xx のみリトライする"""
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code == 429 or exc.response.status_code >= 500
    if isinstance(exc, httpx.TimeoutException):
        return True
    return False


class RedditCollector:
    """Reddit API 経由で投稿を取得する"""

    def __init__(self) -> None:
        self._client_id = settings.reddit_client_id
        self._client_secret = settings.reddit_client_secret
        self._token: str | None = None

    def check_config(self) -> str | None:
        """認証に必要な設定が揃っているか確認。不足ならメッセージを返す"""
        missing = []
        if not self._client_id:
            missing.append("REDDIT_CLIENT_ID")
        if not self._client_secret:
            missing.append("REDDIT_CLIENT_SECRET")
        if missing:
            return f"Reddit 認証未設定: {', '.join(missing)} を .env に設定してください"
        return None

    def _ensure_token(self, client: httpx.Client) -> str:
        """アプリケーション_only_ 認証でアクセストークンを取得"""
        if self._token:
            return self._token

        resp = client.post(
            "https://www.reddit.com/api/v1/access_token",
            data={"grant_type": "client_credentials"},
            auth=(self._client_id, self._client_secret),
            headers={"User-Agent": _USER_AGENT},
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
        return self._token

    @retry(
        retry=retry_if_exception(_is_retryable),
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=10),
        reraise=True,
    )
    def fetch_new_posts(self, subreddit: str, limit: int = 20) -> list[dict[str, Any]]:
        """subreddit の新着投稿を取得する

        戻り値の各要素は以下キーを持つ dict:
          id, title, selftext, permalink, url, author,
          created_utc, score, num_comments
        """
        with httpx.Client(timeout=15.0) as client:
            token = self._ensure_token(client)
            resp = client.get(
                f"{_REDDIT_BASE}/r/{subreddit}/new",
                params={"limit": limit},
                headers={
                    "Authorization": f"Bearer {token}",
                    "User-Agent": _USER_AGENT,
                },
            )
            resp.raise_for_status()

        data = resp.json()
        children = data.get("data", {}).get("children", [])

        posts: list[dict[str, Any]] = []
        for child in children:
            d = child.get("data", {})
            posts.append({
                "id": d.get("id", ""),
                "title": d.get("title", ""),
                "selftext": d.get("selftext", ""),
                "permalink": d.get("permalink", ""),
                "url": d.get("url", ""),
                "author": d.get("author", ""),
                "created_utc": d.get("created_utc", 0.0),
                "score": d.get("score", 0),
                "num_comments": d.get("num_comments", 0),
            })

        logger.info("subreddit=%s 取得完了 count=%d", subreddit, len(posts))
        return posts
