## Day1-1
'''
目的:
AI開発トレンド分析ツールのMVPを2日で作りたいです。今日は Day 1 として、プロジェクト雛形、SQLite保存、Reddit/Qiita収集、共通スキーマ、collect CLI まで進めたいです。

進め方:
- 一度に全部実装しない
- まずはプロジェクト雛形だけを作る
- その後に collector や DB を分割して進める

制約:
- Python 3.11
- Typer
- SQLite + SQLAlchemy
- 個人開発向けの最小構成
- 過剰な抽象化を避ける

今回の依頼:
まずは Day 1 の最初のステップとして、ディレクトリ構成、pyproject.toml、app/main.py、README.md、.env.example を含む初期雛形を作ってください。

出力ルール:
- まずディレクトリ構成
- 次に各ファイルの完全コード
- 必要最小限の説明
'''
### 結果確認コマンド
'''console
# 1) 生成されたファイル一覧
find . -maxdepth 3 -type f | sort

# 2) 主要ファイルの中身
printf '\n===== pyproject.toml =====\n'; cat pyproject.toml
printf '\n===== app/main.py =====\n'; cat app/main.py
printf '\n===== README.md =====\n'; cat README.md
printf '\n===== .env.example =====\n'; cat .env.example

# 3) もし git 管理しているなら差分確認
git status --short
git diff -- pyproject.toml app/main.py README.md .env.example

# 4) 実行できるか確認
python -m app.main --help
'''

## Day1-2
'''
目的:
設定管理とロギングの最小実装を追加したいです。

変更対象:
- app/config.py
- app/utils/logging.py
- .env.example
- 必要なら app/main.py

制約:
- Python 3.12
- 環境変数は python-dotenv で読む
- シンプルな dataclass ベースでよい
- 設定項目:
  - REDDIT_CLIENT_ID
  - REDDIT_CLIENT_SECRET
  - REDDIT_USER_AGENT
  - QIITA_ACCESS_TOKEN
  - DB_PATH
- Settings オブジェクトとして import できるようにする
- logging は標準 logging を使う
- コンソールで見やすいフォーマットにする
- main.py 起動時に logger 初期化できるようにする

完了条件:
- from app.config import settings ができる
- logger = get_logger(__name__) が使える
- main.py 実行時にログが出る
- 過剰設計しない

出力ルール:
- 変更ファイルの完全コード
- 実行確認コマンドも最後に書く
'''

### 結果確認コマンド
'''console
printf '\n===== app/config.py =====\n'; cat app/config.py
printf '\n===== app/utils/logging.py =====\n'; cat app/utils/logging.py
printf '\n===== app/main.py =====\n'; cat app/main.py
printf '\n===== .env.example =====\n'; cat .env.example
python -m app.main hello
'''

## Day1-3
'''
目的:
Reddit と Qiita の投稿を共通形式で扱うためのデータモデルを作りたいです。

変更対象:
- app/models.py または app/storage/models.py
- app/normalizers/base.py
- 必要なら app/__init__.py

制約:
- Python 3.12
- 最初は共通 Item モデルだけでよい
- 必須項目:
  - source
  - source_item_id
  - title
  - body
  - url
  - author
  - published_at
  - collected_at
  - language
  - engagement_score
  - raw_json
- dataclass ベースで実装する
- 後で SQLite 保存しやすい shape にする
- normalizer 用のインターフェースも定義する
- 過剰設計しない
- まだ ORM モデルは作らない

完了条件:
- 共通 Item モデルが定義されている
- normalizer が返すべき型が明確
- 利用例がコメントか docstring でわかる
- 型ヒントがついている

出力ルール:
- 変更ファイルの完全コード
- どのファイルに置いたか理由を短く添える
'''

### 結果確認コマンド
'''console
printf '\n===== app/models.py =====\n'; cat app/models.py 2>/dev/null || true
printf '\n===== app/storage/models.py =====\n'; cat app/storage/models.py 2>/dev/null || true
printf '\n===== app/normalizers/base.py =====\n'; cat app/normalizers/base.py
'''

## Day1-4
'''
目的:
取得した投稿を SQLite に保存するための最小 DB レイヤーを実装したいです。

変更対象:
- app/storage/db.py
- app/storage/models.py
- app/storage/repositories.py
- 必要なら app/models.py

制約:
- Python 3.12
- SQLAlchemy を使う
- DB は SQLite
- items テーブルだけでよい
- source + source_item_id にユニーク制約をつける
- raw_json は SQLite に保存しやすいように text で保存する
- 必要なら app/models.py の Item 側も最小限修正してよい
- まずは insert / upsert / list_recent があれば十分
- Alembic はまだ不要
- MVP向けに過剰設計しない
- ドメインモデルと ORM モデルは分けてもよいが、複雑にしすぎない

完了条件:
- DB 初期化関数がある
- items テーブルが作成される
- Item を保存できる repository がある
- 重複時の扱いが明確
- list_recent(limit: int) で直近データを取得できる

出力ルール:
- 変更ファイルの完全コード
- 実行確認コマンドも最後に書く
'''

### 結果確認コマンド
'''console
printf '\n===== app/models.py =====\n'; cat app/models.py
printf '\n===== app/storage/db.py =====\n'; cat app/storage/db.py
printf '\n===== app/storage/models.py =====\n'; cat app/storage/models.py
printf '\n===== app/storage/repositories.py =====\n'; cat app/storage/repositories.py

python - <<'PY'
from app.storage.db import init_db
init_db()
print("db init ok")
PY
'''

## Day1-5
'''
目的:
Reddit の投稿を取得する collector を実装したいです。

変更対象:
- app/collectors/reddit_collector.py
- tests/test_reddit_collector.py
- 必要なら app/config.py

制約:
- Python 3.12
- httpx を使用
- リトライは tenacity
- subreddit 名を受け取り、新着投稿を取得する
- 戻り値は raw dict の list でよい
- 取得項目は最低限:
  - id
  - title
  - selftext
  - permalink または url
  - author
  - created_utc
  - score
  - num_comments
- 429 と 5xx を考慮
- API 認証情報は環境変数経由にする
- 実装は後で normalizer に渡しやすい shape にする
- まずはコメント取得までは不要
- MVP向けに過剰設計しない

完了条件:
- fetch_new_posts(subreddit: str, limit: int = 20) が使える
- 失敗時の例外がわかりやすい
- テストが2件以上ある
- ダミーレスポンスで通る
- 実行例がある

出力ルール:
- 変更ファイルの完全コード
- 必要なら config の変更も含める
- テストコードも含める
'''

### 結果確認コマンド
'''console
printf '\n===== app/collectors/reddit_collector.py =====\n'; cat app/collectors/reddit_collector.py
printf '\n===== tests/test_reddit_collector.py =====\n'; cat tests/test_reddit_collector.py

pytest -q tests/test_reddit_collector.py
'''

## Day1-6
'''
目的:
Reddit の raw データを共通 Item モデルに正規化したいです。

変更対象:
- app/normalizers/reddit_normalizer.py
- 必要なら app/models.py

制約:
- Python 3.12
- 入力は Reddit collector の生 dict
- 出力は共通 Item
- engagement_score は暫定で score + num_comments * 2
- body が空でも動く
- permalink は絶対URLに正規化する
- raw_json は保持する
- 例外時はどの投稿で失敗したかわかるようにする
- MVP向けに過剰設計しない

完了条件:
- normalize_reddit_post(raw: dict) -> Item
- normalize_reddit_posts(raw_items: list[dict]) -> list[Item]
- published_at を created_utc から datetime に変換する
- permalink が相対URLなら https://www.reddit.com を付けて絶対URL化する

出力ルール:
- 変更ファイルの完全コード
- 必要なら app/models.py の最小修正も含める
- 利用例を短く添える
'''

### 結果確認コマンド
'''console
printf '\n===== app/normalizers/reddit_normalizer.py =====\n'; cat app/normalizers/reddit_normalizer.py
printf '\n===== app/models.py =====\n'; cat app/models.py

python - <<'PY'
from app.normalizers.reddit_normalizer import normalize_reddit_post

raw = {
    "id": "abc123",
    "title": "Test title",
    "selftext": "",
    "permalink": "/r/test/comments/abc123/test/",
    "url": "https://example.com",
    "author": "user1",
    "created_utc": 1700000000.0,
    "score": 10,
    "num_comments": 5,
}
item = normalize_reddit_post(raw)
print(item.source, item.source_item_id, item.url, item.engagement_score)
PY
'''

## Day1-6.1
'''
目的:
Reddit normalizer の公開APIを、依頼した完了条件に合わせて整えたいです。

変更対象:
- app/normalizers/reddit_normalizer.py

修正内容:
- 既存の RedditNormalizer クラスは残す
- 追加で以下の関数を公開してください
  - normalize_reddit_post(raw: dict) -> Item
  - normalize_reddit_posts(raw_items: list[dict]) -> list[Item]
- 実装は RedditNormalizer の wrapper でよい
- 過剰な変更はしない
- 既存の挙動は壊さない

完了条件:
- from app.normalizers.reddit_normalizer import normalize_reddit_post ができる
- from app.normalizers.reddit_normalizer import normalize_reddit_posts ができる
- 既存クラスAPIも残る

出力ルール:
- app/normalizers/reddit_normalizer.py の完全コードだけ出す
- 変更理由は1〜2文だけ
'''

### 確認コマンド
'''console
python - <<'PY'
from app.normalizers.reddit_normalizer import normalize_reddit_post

raw = {
    "id": "abc123",
    "title": "Test title",
    "selftext": "",
    "permalink": "/r/test/comments/abc123/test/",
    "url": "https://example.com",
    "author": "user1",
    "created_utc": 1700000000.0,
    "score": 10,
    "num_comments": 5,
}
item = normalize_reddit_post(raw)
print(item.source, item.source_item_id, item.url, item.engagement_score)
PY
'''

## Day1-7
'''
目的:
Qiita の記事を取得する collector を実装したいです。

変更対象:
- app/collectors/qiita_collector.py
- tests/test_qiita_collector.py
- 必要なら app/config.py
- 必要なら .env.example

制約:
- Python 3.12
- httpx を使用
- Qiita API v2 を利用
- 認証トークンあり / なし両対応
- 最初は新着記事取得だけでよい
- 戻り値は raw dict の list
- 扱う項目は最低限:
  - id
  - title
  - body または rendered_body
  - url
  - user
  - created_at
  - likes_count
  - stocks_count
- 失敗時の例外がわかりやすい
- 実装は後で normalizer に渡しやすい shape にする
- MVP向けに過剰設計しない

完了条件:
- fetch_recent_items(page: int = 1, per_page: int = 20) がある
- 認証トークンがあれば Authorization ヘッダを付ける
- テストが2件以上ある
- ダミーレスポンスで通る
- 実行例がある

出力ルール:
- 変更ファイルの完全コード
- 必要なら config や .env.example の変更も含める
- テストコードも含める
'''

### 確認コマンド
'''console
printf '\n===== app/collectors/qiita_collector.py =====\n'; cat app/collectors/qiita_collector.py
printf '\n===== tests/test_qiita_collector.py =====\n'; cat tests/test_qiita_collector.py
pytest -q tests/test_qiita_collector.py
'''

## Day1-8
'''
目的:
Qiita の raw 記事データを共通 Item に正規化したいです。

変更対象:
- app/normalizers/qiita_normalizer.py
- 必要なら app/models.py

制約:
- Python 3.12
- 入力は Qiita collector の raw dict
- 出力は共通 Item
- engagement_score は likes_count + stocks_count * 2
- body があれば body を優先、なければ rendered_body を使う
- language は暫定で "ja"
- raw_json は保持する
- created_at は datetime に変換する
- author は user_name があればそれを優先し、なければ user_id
- URL はそのまま使う
- 例外時はどの記事 id で失敗したかわかるようにする
- Reddit normalizer と同じ公開API形式にする
  - normalize_qiita_item(raw: dict) -> Item
  - normalize_qiita_items(raw_items: list[dict]) -> list[Item]
- クラスAPIがあってもよい

完了条件:
- 単体記事を Item に変換できる
- 複数件を list[Item] に変換できる
- created_at が datetime になる
- engagement_score が正しい

出力ルール:
- 完全コード
- 必要なら app/models.py の最小修正も含める
- 利用例を短く添える
'''

### 確認コマンド
'''console
printf '\n===== app/normalizers/qiita_normalizer.py =====\n'; cat app/normalizers/qiita_normalizer.py
python - <<'PY'
from app.normalizers.qiita_normalizer import normalize_qiita_item

raw = {
    "id": "abc123",
    "title": "Qiita Test",
    "body": "hello",
    "rendered_body": "",
    "url": "https://qiita.com/items/abc123",
    "user_id": "user1",
    "user_name": "User One",
    "created_at": "2026-01-15T10:30:00+09:00",
    "likes_count": 10,
    "stocks_count": 5,
}
item = normalize_qiita_item(raw)
print(item.source, item.author, item.language, item.engagement_score)
PY
'''

## Day1-9
'''
目的:
CLI から Reddit と Qiita の収集を実行し、正規化して SQLite に保存できるようにしたいです。

変更対象:
- app/main.py
- 必要なら app/storage/repositories.py
- 必要なら app/storage/db.py
- 必要なら app/collectors/__init__.py
- 必要なら app/normalizers/__init__.py

制約:
- Python 3.12
- Typer を使う
- collect コマンドを追加する
- source は reddit / qiita を受け付ける
- reddit の場合は subreddit と limit を指定できる
- qiita の場合は page と per_page を指定できる
- 処理フローは以下にする
  1. DB 初期化
  2. source に応じて collector 実行
  3. normalizer 実行
  4. repository で upsert 保存
- 保存件数と取得件数を表示する
- エラー時は原因がわかるメッセージを出す
- MVP向けに過剰設計しない
- 既存の hello コマンドは残してよい

完了条件:
- python -m app.main collect --source reddit --subreddit MachineLearning --limit 5
- python -m app.main collect --source qiita --page 1 --per-page 5
のように実行できる
- source ごとの分岐が分かりやすい
- DB に upsert 保存される
- 実行結果として件数が表示される

出力ルール:
- 変更ファイルの完全コード
- 実行確認コマンドも最後に書く
'''

### 確認コマンド
'''console
printf '\n===== app/main.py =====\n'; cat app/main.py
printf '\n===== app/storage/repositories.py =====\n'; cat app/storage/repositories.py
python -m app.main --help

python -m app.main collect --source qiita --page 1 --per-page 3
'''

## Day1-10
'''
目的:
保存前に最低限の前処理を入れたいです。cleaning と dedup 補助を追加してください。

変更対象:
- app/preprocessing/cleaner.py
- app/preprocessing/dedup.py
- 必要なら app/main.py
- 必要なら app/models.py

制約:
- Python 3.12
- 過剰な自然言語処理はまだ不要
- cleaner:
  - 連続空白の正規化
  - 先頭末尾空白除去
  - 改行の整理
  - 不要なURLの簡易除去を関数として用意してもよい
- dedup:
  - title を比較しやすい形に正規化する関数
  - title hash を作る関数
  - 近い将来の重複判定に使える補助関数を用意
- まずは純粋関数中心で実装
- collect 時に title/body に clean_text を適用してから保存する
- 既存の repository や collector の責務はなるべく壊さない
- MVP向けに過剰設計しない

完了条件:
- clean_text(text: str) -> str がある
- normalize_title(title: str) -> str がある
- title_hash(title: str) -> str がある
- collect 時に cleaning が適用される
- 将来 dedup に使える最小基盤になっている

出力ルール:
- 完全コード
- 実行確認方法も最後に書く
'''

### 確認コマンド
'''console
printf '\n===== app/preprocessing/cleaner.py =====\n'; cat app/preprocessing/cleaner.py
printf '\n===== app/preprocessing/dedup.py =====\n'; cat app/preprocessing/dedup.py
printf '\n===== app/main.py =====\n'; cat app/main.py

python - <<'PY'
from app.preprocessing.cleaner import clean_text
from app.preprocessing.dedup import normalize_title, title_hash

print(clean_text("  hello   world \n\n test  "))
print(normalize_title("  Claude Code 入門!!! "))
print(title_hash("Claude Code 入門!!!"))
PY
'''

Day2-1
'''
目的:
LLM に送る前に候補を絞り込む ranking ロジックを実装したいです。

変更対象:
- app/preprocessing/ranking.py
- 必要なら app/storage/repositories.py
- 必要なら app/models.py

制約:
- Python 3.12
- Reddit と Qiita 共通で使えるようにする
- まずはルールベースでよい
- 基本ルール:
  - title が短すぎるものは除外
  - body が極端に短いものは除外
  - engagement_score が低すぎるものは除外
- score_candidates(items) のような関数を用意してよい
- select_candidates(items, limit=20) を用意する
- 純粋関数中心で実装する
- 閾値は定数化する
- MVP向けに過剰設計しない

完了条件:
- select_candidates(items, limit=20) がある
- 候補選別ルールがコード上で読みやすい
- score 付きで並び替えられる
- テストしやすい構成になっている

出力ルール:
- 完全コード
- スコア式の説明を短く添える
- 必要なら簡単な利用例も付ける
'''

### 確認コマンド
'''console
printf '\n===== app/preprocessing/ranking.py =====\n'; cat app/preprocessing/ranking.py

python - <<'PY'
from datetime import datetime, timezone
from app.models import Item
from app.preprocessing.ranking import select_candidates

items = [
    Item(
        source="qiita",
        source_item_id="1",
        title="Claude CodeでMCPを使う",
        body="これは十分に長い本文です。" * 10,
        url="https://example.com/1",
        author="a",
        published_at=datetime.now(timezone.utc),
        engagement_score=20,
    ),
    Item(
        source="qiita",
        source_item_id="2",
        title="短い",
        body="x",
        url="https://example.com/2",
        author="b",
        published_at=datetime.now(timezone.utc),
        engagement_score=1,
    ),
]
selected = select_candidates(items, limit=10)
print(len(selected))
for item in selected:
    print(item.source_item_id, item.title, item.engagement_score)
PY
'''

## Day2-2
'''
目的:
要約と分類に使う LLM クライアント層の骨組みを作りたいです。

変更対象:
- app/llm/client.py
- app/llm/prompts.py
- app/llm/budget.py
- 必要なら app/config.py
- 必要なら .env.example

制約:
- Python 3.12
- Claude 系モデルを想定したインターフェースにする
- ただし SDK 依存を薄くし、後で差し替えやすくする
- generate_json(prompt: str) のような薄いAPIを用意する
- token budget を管理する簡単な関数を用意する
- モデル名、max_tokens、temperature を config 化する
- まだ複雑な最適化は不要
- SDK が未導入でも、fallback / stub で壊れない構成にする
- MVP向けに過剰設計しない

完了条件:
- summarizer/classifier から呼べる最小 client がある
- prompt テンプレートを別ファイル化している
- 失敗時の例外方針が明確
- TODO コメントで未実装箇所がわかる
- 必要な環境変数が整理されている

出力ルール:
- 完全コード
- 実装方針を短く添える
- 実行確認方法も最後に書く
'''

### 確認コマンド
'''console
printf '\n===== app/llm/client.py =====\n'; cat app/llm/client.py
printf '\n===== app/llm/prompts.py =====\n'; cat app/llm/prompts.py
printf '\n===== app/llm/budget.py =====\n'; cat app/llm/budget.py
printf '\n===== app/config.py =====\n'; cat app/config.py
printf '\n===== .env.example =====\n'; cat .env.example

python - <<'PY'
from app.llm.client import LLMClient
from app.llm.budget import build_truncated_text

print("import ok")
print(build_truncated_text("hello world", 20))
client = LLMClient()
print(client.__class__.__name__)
PY
'''
### Day2-2.1
'''
目的:
LLM モジュールの公開APIを、依頼した完了条件に合わせて整えたいです。

変更対象:
- app/llm/client.py
- app/llm/budget.py

修正内容:
1. app.llm.client に LLMClient クラスを追加する
   - generate_text()
   - generate_json()
   の薄いメソッドを持つ wrapper でよい
   - 既存の関数APIは残す

2. app.llm.budget に build_truncated_text(text: str, budget: int = DEFAULT_BUDGET) を追加する
   - 既存 truncate_to_budget の alias wrapper でよい

3. 過剰な変更はしない
4. 既存挙動は壊さない

完了条件:
- from app.llm.client import LLMClient ができる
- from app.llm.budget import build_truncated_text ができる
- 既存 generate_json / generate_text も使える

出力ルール:
- 変更ファイルの完全コードだけ出す
- 変更理由は短く
'''

## Day2-3
'''
目的:
投稿ごとの短い要約を生成する summarizer を実装したいです。

変更対象:
- app/llm/summarizer.py
- 必要なら app/llm/prompts.py
- 必要なら tests/

制約:
- Python 3.12
- 投稿全文をそのまま送らない
- 入力は title + body先頭500文字 + engagement_score + source
- build_summary_input(item) のような入力整形関数を用意する
- 出力は JSON:
  {
    "summary": "...",
    "tags": ["..."],
    "novelty_score": 0.0,
    "buzz_reason": "..."
  }
- summary は120文字以内を目安
- tags は最大5個程度
- novelty_score は 0.0〜1.0
- LLM失敗時は fallback を返す
- fallback では title ベースの短い summary を生成
- JSON 以外を返したときの保険も入れる
- MVP向けに過剰設計しない

完了条件:
- summarize_item(item) がある
- summarize_items(items) がある
- build_summary_input(item) がある
- fallback 実装あり
- LLMエラー時にも最低限の結果を返せる

出力ルール:
- 完全コード
- fallback の挙動を短く説明
- 必要なら prompts の変更も含める
'''

### 確認コマンド
'''console
printf '\n===== app/llm/summarizer.py =====\n'; cat app/llm/summarizer.py
printf '\n===== app/llm/prompts.py =====\n'; cat app/llm/prompts.py

python - <<'PY'
from datetime import datetime, timezone
from app.models import Item
from app.llm.summarizer import build_summary_input, summarize_item

item = Item(
    source="qiita",
    source_item_id="1",
    title="Claude CodeでMCPを使った開発フロー",
    body="Claude Code と MCP を組み合わせて開発効率を上げる方法を紹介します。" * 20,
    url="https://example.com",
    author="user1",
    published_at=datetime.now(timezone.utc),
    engagement_score=25,
)

print(build_summary_input(item))
result = summarize_item(item)
print(result)
PY
'''

## Day2-4
'''
目的:
AI開発トレンド向けのカテゴリ分類器を実装したいです。

変更対象:
- app/llm/classifier.py
- 必要なら app/constants.py
- 必要なら app/llm/prompts.py

制約:
- Python 3.12
- まずルールベース分類
- 当てはまらない場合のみ LLM 分類
- カテゴリ候補は以下:
  - coding_agent
  - mcp_tool_use
  - rag
  - eval_benchmark
  - local_llm
  - oss_cli
  - voice_realtime
  - ai_ide_devex
  - prompt_engineering
  - ai_infra_serving
  - other
- title と summary と tags を使って判定してよい
- 出力は category のみでよい
- LLM 側にも固定候補から選ばせる
- LLM失敗時は other を返す
- MVP向けに過剰設計しない

完了条件:
- classify_item(title: str, summary: str, tags: list[str]) -> str がある
- ルール辞書が定義されている
- 不明時は LLM 分類を試す
- LLM失敗時は other を返す
- カテゴリ候補がコード上で見やすい

出力ルール:
- 完全コード
- ルールベース部分を後で調整しやすく実装する
- 簡単な利用例も付ける
'''

### 確認コマンド
'''console
printf '\n===== app/llm/classifier.py =====\n'; cat app/llm/classifier.py
printf '\n===== app/llm/prompts.py =====\n'; cat app/llm/prompts.py

python - <<'PY'
from app.llm.classifier import classify_item

print(classify_item(
    title="Claude CodeでMCPを使った開発フロー",
    summary="Claude Code と MCP を組み合わせた開発支援ワークフローの紹介",
    tags=["Claude Code", "MCP", "agent"]
))

print(classify_item(
    title="vLLMで推論基盤を構築する",
    summary="vLLM と GPU サービング構成の解説",
    tags=["vLLM", "serving", "GPU"]
))
PY
'''

## Day2-5
'''
目的:
要約・分類済みデータを保存できるように enriched_items のモデルと保存処理を作りたいです。

変更対象:
- app/storage/models.py
- app/storage/repositories.py
- app/storage/db.py
- 必要なら app/models.py

制約:
- Python 3.12
- items テーブルはそのまま使う
- enriched_items テーブルを追加する
- 項目:
  - item_id
  - short_summary
  - category
  - tags_json
  - novelty_score
  - buzz_reason
  - llm_model
  - prompt_version
  - created_at
- item_id は items と関連付ける
- すでに enrich 済みならスキップできるようにしたい
- pending items を取得できるようにしたい
- MVP向けに過剰設計しない
- tags は SQLite 保存しやすいように text/json文字列でよい

完了条件:
- enriched_items テーブルが追加される
- 保存関数がある
- enrich 済み判定ができる
- pending items を取得できる
- DB 初期化で作成される

出力ルール:
- 完全コード
- 実行確認方法も最後に書く
'''

### 確認コマンド
'''console
printf '\n===== app/storage/models.py =====\n'; cat app/storage/models.py
printf '\n===== app/storage/repositories.py =====\n'; cat app/storage/repositories.py
printf '\n===== app/storage/db.py =====\n'; cat app/storage/db.py

python - <<'PY'
from app.storage.db import init_db
init_db()
print("db init ok")
PY
'''

## Day2-6
'''
目的:
未処理の投稿を要約・分類して enriched_items に保存する CLI コマンドを作りたいです。

変更対象:
- app/main.py
- 必要なら app/storage/repositories.py
- 必要なら app/llm/summarizer.py
- 必要なら app/llm/classifier.py
- 必要なら app/preprocessing/ranking.py

制約:
- Python 3.12
- summarize コマンドを追加する
- 処理フロー:
  1. DB 初期化
  2. 未処理 items を取得
  3. ranking で候補を絞る
  4. summarize
  5. classify
  6. enriched_items に保存
- limit を指定できる
- pending_limit も指定できるとよい
- dry-run を追加してもよい
- エラー時はその item をスキップして続行する
- 何件処理したか出力する
- llm_model, prompt_version も保存する
- MVP向けに過剰設計しない

完了条件:
- python -m app.main summarize --limit 20
が動く
- 未処理 item がない場合のメッセージがある
- fallback でも保存まで進める
- 何件候補に選ばれたか、何件保存したかが出る

出力ルール:
- 完全コード
- 実行確認コマンドも最後に書く
'''

### 確認コマンド
'''console
printf '\n===== app/main.py =====\n'; cat app/main.py
printf '\n===== app/storage/repositories.py =====\n'; cat app/storage/repositories.py
python -m app.main --help

python -m app.main summarize --limit 5
'''

### Day2-6.1
'''
目的:
summarize で候補0件になる理由を確認しやすくしたいです。ranking のデバッグ補助を追加してください。

変更対象:
- app/preprocessing/ranking.py
- 必要なら app/main.py

制約:
- Python 3.12
- 既存の select_candidates() の挙動はできるだけ壊さない
- 追加で、各 item がなぜ除外されたか分かる補助関数を作る
- 例:
  - explain_candidate(item) -> dict
  - 戻り値に
    - title_len
    - body_len
    - engagement_score
    - passed
    - reasons
  を含める
- summarize コマンドに --debug-ranking オプションを追加してもよい
- debug 時は、候補から落ちた item の理由を簡潔に表示する
- MVP向けに過剰設計しない

完了条件:
- 各 item の除外理由を確認できる
- 候補0件の原因が CLI 上で分かる
- 既存の summarize コマンドは壊さない

出力ルール:
- 完全コード
- 実行確認コマンドも最後に書く
'''

### 確認コマンド
'''console
python -m app.main summarize --limit 5 --debug-ranking
'''

### Day2-6.2
'''
目的:
MVP段階では候補がゼロになりやすいので、ranking 条件を少し緩めたいです。

変更対象:
- app/preprocessing/ranking.py

制約:
- Python 3.12
- 既存の関数構成はなるべく変えない
- MVPではまず summarize の流れを通すことを優先する
- engagement_score の足切りを緩める
- まずは ENGAGEMENT_FLOOR を 0.0 にする
- title/body の最低長はそのままでよい
- explain_candidate 系の debug 表示はそのまま使えるようにする
- 過剰設計しない

完了条件:
- engagement_score が 0.0 の item でも、title/body 条件を満たせば候補に入る
- select_candidates の既存挙動は大きく壊さない
- debug-ranking でも理由表示が自然

出力ルール:
- app/preprocessing/ranking.py の完全コードだけ出す
- 変更理由は短く
'''

### 確認コマンド
'''console
python -m app.main summarize --limit 5 --debug-ranking

python -m app.main summarize --limit 5
'''

## Day2-7
'''
目的:
日次レポート用に enriched_items を集計する分析ロジックを作りたいです。

変更対象:
- app/analysis/trend_detector.py
- app/analysis/buzz_score.py
- 必要なら app/storage/repositories.py

制約:
- Python 3.12
- 直近24時間のデータを対象にする
- 以下を集計する
  - category ごとの件数
  - source ごとの件数
  - buzz score 上位 items
- buzz score はまず単純でよい
  例:
  engagement_score + novelty_score * 10
- 後で拡張しやすい形にする
- MVP向けに過剰設計しない

完了条件:
- build_daily_stats() 的な関数がある
- レポート生成に渡せる dict を返せる
- highlighted items 用の上位データが取れる

出力ルール:
- 完全コード
- データ構造例も少し示す
'''

### 確認コマンド
'''console
printf '\n===== app/analysis/trend_detector.py =====\n'; cat app/analysis/trend_detector.py
printf '\n===== app/analysis/buzz_score.py =====\n'; cat app/analysis/buzz_score.py
printf '\n===== app/storage/repositories.py =====\n'; cat app/storage/repositories.py
'''

## Day2-8
'''
目的:
日次トレンド結果を Markdown で出力する report generator を作りたいです。

変更対象:
- app/reporting/markdown_report.py
- 必要なら app/analysis/trend_detector.py

制約:
- Python 3.12
- build_daily_stats() の結果を受け取って Markdown 文字列を返す
- 以下の構成にする
  - タイトル
  - サマリー（総件数）
  - category 集計
  - source 集計
  - top tags
  - highlighted items
- highlighted items には以下を表示
  - summary
  - category
  - buzz_score
  - tags
  - buzz_reason
- 読みやすい Markdown にする
- MVP向けに過剰装飾しない

完了条件:
- render_markdown_report(stats: dict) -> str がある
- stats が空でも壊れない
- そのまま .md 保存できる文字列になる

出力ルール:
- 完全コード
- サンプル出力を少し示す
'''

### 確認コマンド
'''
printf '\n===== app/reporting/markdown_report.py =====\n'; cat app/reporting/markdown_report.py

python - <<'PY'
from app.analysis.trend_detector import build_daily_stats
from app.reporting.markdown_report import render_markdown_report

stats = build_daily_stats()
md = render_markdown_report(stats)
print(md[:2000])
PY
'''

### Day2-8.1
'''
目的:
Markdown レポートを CLI から出力できる report コマンドを追加したいです。

変更対象:
- app/main.py
- 必要なら app/reporting/markdown_report.py
- 必要なら app/analysis/trend_detector.py

制約:
- Python 3.12
- Typer を使う
- report コマンドを追加する
- build_daily_stats() を呼んで render_markdown_report() に渡す
- 標準出力に表示できるようにする
- --output オプションがあればファイル保存できるようにする
- --hours オプションで対象期間を変えられるようにする
- データが少なくても壊れない
- 既存の collect / summarize は壊さない
- MVP向けに過剰設計しない

完了条件:
- python -m app.main report
  で Markdown が標準出力に出る
- python -m app.main report --output report.md
  で保存できる
- python -m app.main report --hours 48
  のように対象期間を変えられる

出力ルール:
- 変更ファイルの完全コード
- 実行確認コマンドも最後に書く
'''

### 確認コマンド
'''console
printf '\n===== app/main.py =====\n'; cat app/main.py
python -m app.main --help
python -m app.main report

python -m app.main report --output report.md
printf '\n===== report.md =====\n'; cat report.md
'''

## Day2-8.2
'''
目的:
Zhipu AI (智譜AI) の GLM を実際に使えるように、LLM client 層を provider 切替式に改善したいです。

変更対象:
- app/llm/client.py
- app/config.py
- .env.example
- README.md
- 必要なら app/llm/prompts.py
- 必要なら pyproject.toml

制約:
- Python 3.12
- 現在使いたい provider は Zhipu AI (GLM)
- 将来的に Anthropic / OpenAI にも切り替え可能な構成にする
- provider 切替式にする
- 環境変数例:
  - LLM_PROVIDER=zhipu
    Z.ai (Zhipu AI) の GLM API に対応するよう client.py を修正してください
  - LLM_API_KEY=
  - LLM_BASE_URL=
  - LLM_MODEL=
- 既存の generate_text(), generate_json(), LLMClient は互換維持
- SDK依存を増やしすぎない
- 可能なら httpx ベースで実装する
- Zhipu の OpenAI互換 API を前提にしてよい
- APIキー未設定時は fallback 動作を維持する
- 既存の summarizer / classifier は壊さない
- MVP向けに過剰設計しない

実装方針:
- provider ごとの送信処理を分離する
- zhipu は OpenAI互換の chat/completions 形式に対応する
- base_url を設定可能にする
- レスポンスから text を安全に取り出す
- エラー時は既存の fallback へ流せるようにする

完了条件:
- provider=zhipu で summarize が実API利用できる
- provider 未設定や APIキー未設定でも fallback 動作する
- 将来 provider追加しやすい構成
- README に .env 設定例と実行手順がある

出力ルール:
- 完全コード
- セットアップ手順も書く
- 変更理由は短く
'''