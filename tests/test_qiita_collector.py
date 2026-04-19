"""Qiita collector のテスト"""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.collectors.qiita_collector import QiitaCollector


def _dummy_items_response() -> httpx.Response:
    body = [
        {
            "id": "abc123def",
            "title": "Python 3.12 の新機能",
            "body": "type パラメータ構文が追加されました",
            "rendered_body": "<p>type パラメータ構文が追加されました</p>",
            "url": "https://qiita.com/items/abc123def",
            "user": {"id": "pythonista", "name": "Python 愛好家"},
            "created_at": "2026-01-15T10:30:00+09:00",
            "likes_count": 30,
            "stocks_count": 15,
        },
        {
            "id": "xyz789ghi",
            "title": "Rust 入門",
            "body": "Ownership が重要です",
            "rendered_body": "<p>Ownership が重要です</p>",
            "url": "https://qiita.com/items/xyz789ghi",
            "user": {"id": "rustacean", "name": ""},
            "created_at": "2026-01-14T08:00:00+09:00",
            "likes_count": 5,
            "stocks_count": 2,
        },
    ]
    return httpx.Response(
        200,
        json=body,
        request=httpx.Request("GET", "https://qiita.com/api/v2/items"),
    )


@patch.object(httpx, "Client")
def test_fetch_recent_items_returns_list(mock_client_cls: MagicMock) -> None:
    """正常系: 記事一覧を dict の list で返す"""
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
    mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

    mock_client.get.return_value = _dummy_items_response()

    collector = QiitaCollector(token="test-token")
    items = collector.fetch_recent_items(page=1, per_page=20)

    assert len(items) == 2
    assert items[0]["id"] == "abc123def"
    assert items[0]["title"] == "Python 3.12 の新機能"
    assert items[0]["user_id"] == "pythonista"
    assert items[1]["likes_count"] == 5
    assert items[1]["user_name"] == ""

    # Authorization ヘッダが付いていること
    call_kwargs = mock_client.get.call_args
    assert "Authorization" in call_kwargs.kwargs.get("headers", {})
    assert call_kwargs.kwargs["headers"]["Authorization"] == "Bearer test-token"


@patch.object(httpx, "Client")
def test_fetch_recent_items_no_token(mock_client_cls: MagicMock) -> None:
    """トークンなしでも取得できる（認証ヘッダなし）"""
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
    mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

    mock_client.get.return_value = httpx.Response(
        200,
        json=[],
        request=httpx.Request("GET", "https://qiita.com/api/v2/items"),
    )

    collector = QiitaCollector(token="")
    collector.fetch_recent_items()

    call_kwargs = mock_client.get.call_args
    headers = call_kwargs.kwargs.get("headers", {})
    assert "Authorization" not in headers


@patch.object(httpx, "Client")
def test_fetch_recent_items_raises_on_500(mock_client_cls: MagicMock) -> None:
    """異常系: 5xx で例外を投げる（リトライ後）"""
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
    mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

    mock_client.get.return_value = httpx.Response(
        500,
        text="Internal Server Error",
        request=httpx.Request("GET", "https://qiita.com/api/v2/items"),
    )

    collector = QiitaCollector()
    with pytest.raises(httpx.HTTPStatusError):
        collector.fetch_recent_items()
