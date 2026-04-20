"""CLI / 集計まわりの最小テスト"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.llm.client import LLMError
from app.analysis.trend_detector import is_fallback, _normalize_tag


# ── is_fallback 境界ケース ─────────────────────────────────


def _enriched(buzz_reason="", llm_model="", tags=None, novelty_score=0.0):
    """テスト用の EnrichedItemRow モック"""
    e = MagicMock()
    e.buzz_reason = buzz_reason
    e.llm_model = llm_model
    e.novelty_score = novelty_score
    e.get_tags.return_value = tags or []
    return e


def test_is_fallback_explicit_marker():
    assert is_fallback(_enriched(buzz_reason="(LLM未使用)")) is True


def test_is_fallback_llm_data():
    assert is_fallback(_enriched(llm_model="gemini-3-flash-preview", tags=["ai"])) is False


def test_is_fallback_empty_model_no_tags_zero_novelty():
    """旧データの fallback 疑い"""
    assert is_fallback(_enriched(llm_model="", tags=[], novelty_score=0.0)) is True


def test_is_fallback_has_tags_not_fallback():
    """タグがあれば fallback 扱いしない"""
    assert is_fallback(_enriched(llm_model="", tags=["python"])) is False


# ── report 集計: LLM/fallback 件数 ────────────────────────


@patch("app.analysis.trend_detector.EnrichedItemRepository")
def test_build_daily_stats_counts_fallback(mock_repo_cls):
    from app.analysis.trend_detector import build_daily_stats

    e1 = _enriched(buzz_reason="(LLM未使用)", llm_model="")
    e2 = _enriched(buzz_reason="", llm_model="gemini", tags=["ai"], novelty_score=0.5)
    e1.item_id = 1
    e2.item_id = 2

    mock_repo = MagicMock()
    mock_repo.list_enriched_since.return_value = [e1, e2]
    item_row = MagicMock()
    item_row.engagement_score = 5.0
    item_row.source = "qiita"
    mock_repo.get_items_by_ids.return_value = {1: item_row, 2: item_row}
    mock_repo.close.return_value = None
    mock_repo_cls.return_value = mock_repo

    stats = build_daily_stats(hours=48)
    assert stats["total"] == 2
    assert stats["fallback_count"] == 1
    assert stats["llm_count"] == 1


# ── CLI: collect --source all ──────────────────────────────


@patch("app.main._collect_qiita")
@patch("app.main._collect_reddit")
@patch("app.storage.db.init_db")
def test_collect_all_calls_both_sources(mock_db, mock_reddit, mock_qiita):
    from typer.testing import CliRunner
    from app.main import app

    runner = CliRunner()
    result = runner.invoke(app, ["collect", "--source", "all"])
    assert result.exit_code == 0
    mock_qiita.assert_called_once()
    mock_reddit.assert_called_once()


# ── CLI: resummarize --dry-run ─────────────────────────────


@patch("app.storage.repositories.EnrichedItemRepository")
@patch("app.storage.db.init_db")
def test_resummarize_dry_run_shows_count(mock_db, mock_repo_cls):
    from typer.testing import CliRunner
    from app.main import app

    mock_repo = MagicMock()
    mock_repo.list_fallback_items.return_value = []
    mock_repo.close.return_value = None
    mock_repo_cls.return_value = mock_repo

    runner = CliRunner()
    result = runner.invoke(app, ["resummarize", "--dry-run"])
    assert result.exit_code == 0
    assert "再処理候補: 0件" in result.output
