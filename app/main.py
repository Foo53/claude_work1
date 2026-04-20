"""AI開発トレンド分析ツール CLI"""

from __future__ import annotations

import typer

from app.config import settings
from app.utils.logging import get_logger, setup_logging

app = typer.Typer(help="AI開発トレンド分析ツール", invoke_without_command=True)
logger = get_logger(__name__)


@app.callback()
def main():
    """AI開発トレンド分析ツール"""
    setup_logging()
    logger.info("起動完了 db_path=%s", settings.db_path)


@app.command()
def hello():
    """動作確認用"""
    setup_logging()
    logger.info("hello コマンド実行")
    typer.echo("ai-trend-analyzer is ready!")


@app.command()
def collect(
    source: str = typer.Option(..., help="収集元: reddit / qiita"),
    subreddit: str = typer.Option("MachineLearning", help="subreddit名（reddit用）"),
    limit: int = typer.Option(20, help="取得件数（reddit用）"),
    page: int = typer.Option(1, help="ページ番号（qiita用）"),
    per_page: int = typer.Option(20, help="ページあたり件数（qiita用）"),
):
    """投稿を収集してSQLiteに保存する"""
    setup_logging()

    # DB初期化
    from app.storage.db import init_db
    init_db()

    if source == "reddit":
        _collect_reddit(subreddit, limit)
    elif source == "qiita":
        _collect_qiita(page, per_page)
    else:
        typer.echo(f"エラー: 不明なsource '{source}'。reddit / qiita を指定してください。")
        raise typer.Exit(code=1)


def _clean_item(item: "Item") -> None:
    """Item の title / body に clean_text を適用する"""
    from app.preprocessing.cleaner import clean_text

    item.title = clean_text(item.title)
    item.body = clean_text(item.body)


def _collect_reddit(subreddit: str, limit: int) -> None:
    from app.collectors.reddit_collector import RedditCollector
    from app.normalizers.reddit_normalizer import normalize_reddit_posts
    from app.storage.repositories import ItemRepository

    typer.echo(f"Reddit: r/{subreddit} から {limit}件取得中...")

    collector = RedditCollector()
    raw_posts = collector.fetch_new_posts(subreddit, limit=limit)
    logger.info("Reddit 取得完了 subreddit=%s count=%d", subreddit, len(raw_posts))

    items = normalize_reddit_posts(raw_posts)
    for item in items:
        _clean_item(item)
    logger.info("正規化+cleaning完了 count=%d", len(items))

    repo = ItemRepository()
    saved = 0
    for item in items:
        repo.upsert(item)
        saved += 1
    repo.close()

    typer.echo(f"完了: 取得{len(raw_posts)}件 / 保存{saved}件")


def _collect_qiita(page: int, per_page: int) -> None:
    from app.collectors.qiita_collector import QiitaCollector
    from app.normalizers.qiita_normalizer import normalize_qiita_items
    from app.storage.repositories import ItemRepository

    typer.echo(f"Qiita: page={page}, per_page={per_page} 取得中...")

    collector = QiitaCollector()
    raw_items = collector.fetch_recent_items(page=page, per_page=per_page)
    logger.info("Qiita 取得完了 page=%d count=%d", page, len(raw_items))

    items = normalize_qiita_items(raw_items)
    for item in items:
        _clean_item(item)
    logger.info("正規化+cleaning完了 count=%d", len(items))

    repo = ItemRepository()
    saved = 0
    for item in items:
        repo.upsert(item)
        saved += 1
    repo.close()

    typer.echo(f"完了: 取得{len(raw_items)}件 / 保存{saved}件")


@app.command()
def summarize(
    limit: int = typer.Option(20, help="処理する最大件数"),
    pending_limit: int = typer.Option(100, help="未処理itemの取得上限"),
    dry_run: bool = typer.Option(False, help="DB保存せず結果だけ表示"),
    debug_ranking: bool = typer.Option(False, help="候補除外理由を表示"),
):
    """未処理の投稿を要約・分類して保存する"""
    setup_logging()

    from app.storage.db import init_db
    init_db()

    from app.llm.classifier import classify_item
    from app.llm.summarizer import summarize_item
    from app.preprocessing.ranking import select_candidates, explain_candidate
    from app.storage.repositories import EnrichedItemRepository, ItemRepository

    typer.echo("未処理アイテムを取得中...")

    enrich_repo = EnrichedItemRepository()
    pending = enrich_repo.list_pending_items(limit=pending_limit)

    if not pending:
        typer.echo("未処理アイテムなし。先に collect を実行してください。")
        enrich_repo.close()
        return

    # ItemRow → Item に変換して ranking
    items = [_row_to_item(r) for r in pending]

    if debug_ranking:
        typer.echo("--- ranking debug ---")
        for item in items:
            info = explain_candidate(item)
            mark = "OK" if info["passed"] else "NG"
            reasons = ", ".join(info["reasons"]) if info["reasons"] else ""
            typer.echo(f"  [{mark}] {item.title[:50]:50s} t={info['title_len']:>3d} b={info['body_len']:>4d} e={info['engagement_score']:>5.1f} {reasons}")
        typer.echo("---")

    candidates = select_candidates(items, limit=limit)

    typer.echo(f"候補選定: {len(pending)}件中 {len(candidates)}件を処理")

    # item_id を引き当てるためのマップ
    id_map = {f"{r.source}:{r.source_item_id}": r.id for r in pending}

    saved = 0
    errors = 0
    for item in candidates:
        key = f"{item.source}:{item.source_item_id}"
        item_id = id_map.get(key)
        if item_id is None:
            logger.warning("item_id 不明: %s", key)
            errors += 1
            continue

        try:
            summary_result = summarize_item(item)
            category = classify_item(item.title, summary_result["summary"], summary_result["tags"])

            if dry_run:
                typer.echo(f"  [{category}] {item.title[:40]} → {summary_result['summary'][:60]}")
            else:
                enrich_repo.save(
                    item_id=item_id,
                    short_summary=summary_result["summary"],
                    category=category,
                    tags=summary_result["tags"],
                    novelty_score=summary_result["novelty_score"],
                    buzz_reason=summary_result["buzz_reason"],
                    llm_model=settings.llm_model,
                    prompt_version="1.0",
                )
            saved += 1
        except Exception:
            logger.warning("処理スキップ: %s", key, exc_info=True)
            errors += 1

    enrich_repo.close()
    status = " (dry-run)" if dry_run else ""
    typer.echo(f"完了{status}: 候補{len(candidates)}件 / 成功{saved}件 / エラー{errors}件")


@app.command()
def report(
    hours: int = typer.Option(24, help="集計対象時間"),
    output: str = typer.Option("", help="出力ファイルパス（空なら標準出力）"),
):
    """日次トレンドレポートを Markdown で出力する"""
    setup_logging()

    from app.storage.db import init_db
    init_db()

    from app.analysis.trend_detector import build_daily_stats
    from app.reporting.markdown_report import render_markdown_report

    stats = build_daily_stats(hours=hours)
    md = render_markdown_report(stats)

    if output:
        from pathlib import Path
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(md, encoding="utf-8")
        typer.echo(f"レポート保存: {output} ({stats['total']}件)")
    else:
        typer.echo(md)


def _row_to_item(row: "ItemRow") -> "Item":
    """ItemRow → Item に変換"""
    from app.models import Item
    from app.storage.models import ItemRow

    return Item(
        source=row.source,
        source_item_id=row.source_item_id,
        title=row.title,
        body=row.body,
        url=row.url,
        author=row.author,
        published_at=row.published_at,
        collected_at=row.collected_at,
        language=row.language,
        engagement_score=row.engagement_score,
        raw_json=row.get_raw_json(),
    )


if __name__ == "__main__":
    app()
