# AI開発トレンド分析ツール

Reddit / Qiita の投稿を収集し、AI開発のトレンドを分析するツール。

## セットアップ

```bash
# リポジトリ克隆後
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# 環境変数設定
cp .env.example .env
# .env に各APIキーを記入
```

## .env 設定例

アプリケーションは `.env` ファイルから環境変数を読み込みます（`python-dotenv` 使用）。

```bash
# LLM Provider（zhipu / anthropic / openai）
LLM_PROVIDER=zhipu
LLM_API_KEY=your-zhipu-api-key
LLM_BASE_URL=https://api.z.ai/api/paas/v4/
LLM_MODEL=glm-4-flash
LLM_MAX_TOKENS=2048
LLM_TEMPERATURE=0.3

# Anthropic に切り替える場合:
# LLM_PROVIDER=anthropic
# LLM_API_KEY=your-anthropic-key
# LLM_MODEL=claude-sonnet-4-20250514

# Reddit API
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=ai-trend-analyzer/0.1

# Qiita API
QIITA_ACCESS_TOKEN=

# DBパス
DB_PATH=data/trends.db
```

## 使い方

```bash
# 動作確認
python -m app.main hello

# Qiita 記事収集（トークンなしでも動く）
python -m app.main collect --source qiita --page 1 --per-page 10

# Reddit 投稿収集（認証情報が必要）
python -m app.main collect --source reddit --subreddit MachineLearning --limit 10

# 要約・分類（LLM_API_KEY が必要）
python -m app.main summarize --limit 10

# 要約ドライラン
python -m app.main summarize --limit 5 --dry-run --debug-ranking

# レポート出力
python -m app.main report

# レポートをファイルに保存
python -m app.main report --hours 48 --output report.md
```

## 処理フロー

1. **collect** — Reddit / Qiita から投稿を取得し SQLite に保存
2. **summarize** — 未処理投稿を LLM で要約・分類し enriched_items に保存
3. **report** — enriched_items を集計して Markdown レポートを出力

## LLM Provider 切替

`LLM_PROVIDER` 環境変数で provider を切り替えます。

| Provider | LLM_BASE_URL（デフォルト） | 備考 |
|----------|---------------------------|------|
| `zhipu` | `https://api.z.ai/api/paas/v4/` | OpenAI互換 API |
| `anthropic` | `https://api.anthropic.com` | Messages API |
| `openai` | `https://api.openai.com/v1` | OpenAI互換 API |

APIキー未設定時は stub モードで動作し、エラーになりません。

## ライセンス

MIT
