# AI開発トレンド分析ツール

Reddit / Qiita の投稿を収集し、AI開発のトレンドを分析するツール。

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
# .env に各APIキーを記入
```

## .env 設定

アプリケーションは `.env` ファイルから環境変数を読み込みます（`python-dotenv` 使用）。

```bash
# LLM Provider（gemini / zhipu / anthropic / openai）
LLM_PROVIDER=gemini
LLM_API_KEY=your-gemini-api-key
LLM_MODEL=gemini-3-flash-preview
LLM_MAX_TOKENS=1024
LLM_TEMPERATURE=0.3

# Reddit API（未設定なら Qiita のみ収集）
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=ai-trend-analyzer/0.1

# Qiita API（未設定でも動作）
QIITA_ACCESS_TOKEN=

# DBパス
DB_PATH=data/trends.db
```

他の provider に切り替える場合:
```bash
# LLM_PROVIDER=zhipu
# LLM_API_KEY=your-zhipu-api-key
# LLM_BASE_URL=https://api.z.ai/api/paas/v4/
# LLM_MODEL=glm-4-flash

# LLM_PROVIDER=anthropic
# LLM_API_KEY=your-anthropic-key
# LLM_MODEL=claude-sonnet-4-20250514
```

## 最短実行手順

```bash
# 1. 動作確認
python -m app.main hello

# 2. 収集（デフォルト: qiita + reddit）
python -m app.main collect

# 3. 要約・分類
python -m app.main summarize --limit 10

# 4. レポート出力
python -m app.main report
```

Qiita だけ試す場合:
```bash
python -m app.main collect --source qiita --per-page 5
python -m app.main summarize --limit 3
python -m app.main report
```

## コマンド一覧

| コマンド | 説明 |
|---|---|
| `hello` | 動作確認 |
| `collect` | 投稿を収集して SQLite に保存 |
| `summarize` | 未処理投稿を LLM で要約・分類 |
| `resummarize` | fallback データを LLM で再要約 |
| `report` | 集計結果を Markdown で出力 |

### collect

```bash
python -m app.main collect                                    # 全ソース
python -m app.main collect --source qiita --per-page 10       # Qiita のみ
python -m app.main collect --source reddit --limit 10         # Reddit のみ
```

Reddit は `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` が必要。未設定時は Qiita のみ収集が継続します。

### summarize

```bash
python -m app.main summarize --limit 10                       # 要約・分類
python -m app.main summarize --limit 5 --dry-run              # 確認のみ
```

### resummarize

API quota 切れ等で fallback 保存されたアイテムを再処理:

```bash
python -m app.main resummarize --limit 10                     # 再要約
python -m app.main resummarize --dry-run                      # 確認のみ
```

全リセットして再実行する場合:
```bash
sqlite3 data/trends.db "DELETE FROM enriched_items;"
python -m app.main summarize --limit 10
```

### report

```bash
python -m app.main report                                     # 標準出力
python -m app.main report --hours 48 --output report.md       # ファイル保存
```

## 注意点

- **Gemini quota 切れ**: summarize / classify は fallback 動作で継続。`resummarize` で後から再処理可能
- **Reddit 認証未設定**: Qiita のみ収集され、エラーで停止しない
- **APIキー未設定**: stub モードで動作し、エラーにならない

## テスト

```bash
python -m pytest tests/ -q                                    # 全テスト
python -m pytest tests/test_gemini_client.py -v               # Gemini のみ
```

## LLM Provider

| Provider | デフォルト base_url | 備考 |
|----------|---------------------|------|
| `gemini` | `https://generativelanguage.googleapis.com/v1beta` | generateContent REST API |
| `zhipu` | `https://api.z.ai/api/paas/v4/` | OpenAI互換 API |
| `anthropic` | `https://api.anthropic.com` | Messages API |
| `openai` | `https://api.openai.com/v1` | OpenAI互換 API |

## ライセンス

MIT
