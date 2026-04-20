"""summarizer のテスト"""

from datetime import datetime, timezone
from unittest.mock import patch

from app.models import Item
from app.llm.summarizer import build_summary_input, summarize_item, summarize_items


def _make(title="Test", body="body text", score=5.0):
    return Item(
        source="reddit", source_item_id="x", title=title, body=body,
        url="", author="", published_at=datetime.now(timezone.utc),
        engagement_score=score,
    )


def test_build_summary_input_truncates_body():
    item = _make(body="あ" * 1000)
    inputs = build_summary_input(item)
    assert len(inputs["body"]) == 500
    assert inputs["title"] == "Test"
    assert inputs["source"] == "reddit"


def test_fallback_on_llm_error():
    """APIキー未設定時は stub が返る"""
    item = _make(title="Fallback test title")
    result = summarize_item(item)
    # キー未設定 → generate_text_stub → JSONをパース
    assert isinstance(result["summary"], str)
    assert isinstance(result["tags"], list)
    assert isinstance(result["novelty_score"], float)


@patch("app.llm.summarizer.generate_json")
def test_summarize_item_success(mock_gen):
    mock_gen.return_value = {
        "summary": "AI技術の最新動向を解説",
        "tags": ["AI", "LLM", "Python"],
        "novelty_score": 0.8,
        "buzz_reason": "新モデルの発表",
    }
    item = _make()
    result = summarize_item(item)
    assert result["summary"] == "AI技術の最新動向を解説"
    assert len(result["tags"]) == 3
    assert result["novelty_score"] == 0.8


@patch("app.llm.summarizer.generate_json")
def test_summarize_item_truncates_long_summary(mock_gen):
    mock_gen.return_value = {
        "summary": "あ" * 200,
        "tags": ["t"] * 10,
        "novelty_score": 1.5,
        "buzz_reason": "reason",
    }
    item = _make()
    result = summarize_item(item)
    assert len(result["summary"]) <= 120
    assert len(result["tags"]) <= 5


def test_summarize_items():
    items = [_make(title="A"), _make(title="B")]
    results = summarize_items(items)
    assert len(results) == 2
