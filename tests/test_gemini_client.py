"""Gemini provider の最小テスト（httpx をモック）"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.llm.client import LLMError, generate_json, generate_text


def _mock_settings():
    """テスト用の Gemini 設定オブジェクト"""
    s = MagicMock()
    s.llm_provider = "gemini"
    s.llm_api_key = "test-key"
    s.llm_base_url = "https://generativelanguage.googleapis.com/v1beta"
    s.llm_model = "gemini-3-flash-preview"
    s.llm_max_tokens = 1024
    s.llm_temperature = 0.3
    return s


_SETTINGS_PATH = "app.llm.client.settings"


@patch(_SETTINGS_PATH, _mock_settings())
@patch("app.llm.client.httpx.post")
def test_gemini_provider_selected(mock_post):
    """gemini provider が呼ばれる"""
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Hello"}]}}],
    }
    result = generate_text("Hi")
    assert result == "Hello"
    call_url = str(mock_post.call_args.kwargs.get("url", mock_post.call_args[0][0]))
    assert "generateContent" in call_url


@patch(_SETTINGS_PATH, _mock_settings())
@patch("app.llm.client.httpx.post")
def test_generate_json_uses_json_mode(mock_post):
    """generate_json で json_mode が有効化される"""
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": '{"category": "coding_agent"}'}]}}],
    }
    result = generate_json("classify this")
    assert result["category"] == "coding_agent"
    call_json = mock_post.call_args.kwargs["json"]
    assert call_json["generationConfig"]["responseMimeType"] == "application/json"


@patch(_SETTINGS_PATH, _mock_settings())
@patch("app.llm.client.httpx.post")
def test_missing_text_raises_llm_error(mock_post):
    """text が取れないレスポンスで LLMError"""
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "candidates": [{"finishReason": "SAFETY"}],
    }
    with pytest.raises(LLMError, match="Gemini レスポンス形式エラー"):
        generate_text("test")
