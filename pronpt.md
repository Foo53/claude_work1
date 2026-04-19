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