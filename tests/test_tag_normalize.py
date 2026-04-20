"""tag 正規化のテスト"""

from app.analysis.trend_detector import _normalize_tag


def test_basic_normalize():
    assert _normalize_tag("  LLM  ") == "llm"
    assert _normalize_tag("VS Code") == "vscode"


def test_alias_mapping():
    assert _normalize_tag("large-language-model") == "llm"
    assert _normalize_tag("language-model") == "llm"
    assert _normalize_tag("ai-agents") == "ai-agent"
    assert _normalize_tag("chatgpt") == "gpt"
    assert _normalize_tag("vs-code") == "vscode"
    assert _normalize_tag("visual-studio-code") == "vscode"


def test_unknown_passthrough():
    assert _normalize_tag("python") == "python"
    assert _normalize_tag("React") == "react"
