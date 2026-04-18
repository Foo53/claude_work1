"""AI開発トレンド分析ツール CLI"""

import typer

app = typer.Typer(help="AI開発トレンド分析ツール", invoke_without_command=True)


@app.callback()
def main():
    """AI開発トレンド分析ツール"""


@app.command()
def hello():
    """動作確認用"""
    typer.echo("ai-trend-analyzer is ready!")


if __name__ == "__main__":
    app()
