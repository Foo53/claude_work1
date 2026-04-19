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


if __name__ == "__main__":
    app()
