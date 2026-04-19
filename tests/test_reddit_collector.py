"""Reddit collector のテスト"""

import json
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.collectors.reddit_collector import RedditCollector


def _dummy_token_response() -> httpx.Response:
    return httpx.Response(
        200,
        json={"access_token": "fake-token", "token_type": "bearer"},
        request=httpx.Request("POST", "https://www.reddit.com/api/v1/access_token"),
    )


def _dummy_posts_response() -> httpx.Response:
    body = {
        "data": {
            "children": [
                {
                    "kind": "t3",
                    "data": {
                        "id": "abc123",
                        "title": "New LLM released",
                        "selftext": "Amazing model!",
                        "permalink": "/r/MachineLearning/comments/abc123/",
                        "url": "https://example.com/paper",
                        "author": "researcher1",
                        "created_utc": 1700000000.0,
                        "score": 42,
                        "num_comments": 7,
                    },
                },
                {
                    "kind": "t3",
                    "data": {
                        "id": "def456",
                        "title": "Another post",
                        "selftext": "",
                        "permalink": "/r/MachineLearning/comments/def456/",
                        "url": "https://example.com/link",
                        "author": "[deleted]",
                        "created_utc": 1699999999.0,
                        "score": 10,
                        "num_comments": 3,
                    },
                },
            ]
        }
    }
    return httpx.Response(
        200,
        json=body,
        request=httpx.Request("GET", "https://oauth.reddit.com/r/MachineLearning/new"),
    )


@patch.object(httpx, "Client")
def test_fetch_new_posts_returns_list(mock_client_cls: MagicMock) -> None:
    """正常系: 投稿一覧を dict の list で返す"""
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
    mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

    # 認証 → 投稿取得の順で呼ばれる
    mock_client.post.return_value = _dummy_token_response()
    mock_client.get.return_value = _dummy_posts_response()

    collector = RedditCollector()
    posts = collector.fetch_new_posts("MachineLearning", limit=2)

    assert len(posts) == 2
    assert posts[0]["id"] == "abc123"
    assert posts[0]["title"] == "New LLM released"
    assert posts[0]["score"] == 42
    assert posts[1]["author"] == "[deleted]"


@patch.object(httpx, "Client")
def test_fetch_new_posts_raises_on_500(mock_client_cls: MagicMock) -> None:
    """異常系: 5xx で例外を投げる（リトライ後）"""
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
    mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

    mock_client.post.return_value = _dummy_token_response()
    mock_client.get.return_value = httpx.Response(
        500,
        text="Internal Server Error",
        request=httpx.Request("GET", "https://oauth.reddit.com/r/test/new"),
    )

    collector = RedditCollector()
    # tenacity のリトライ3回 → 最終的に例外
    with pytest.raises(httpx.HTTPStatusError):
        collector.fetch_new_posts("test")
