"""LLM 用プロンプトテンプレート"""


SUMMARY_SYSTEM = """あなたはテクニカルライターです。
与えられた投稿の要約を日本語で簡潔に作成してください。"""


SUMMARY_PROMPT = """以下の投稿を要約し、JSONで返してください。

タイトル: {title}
本文抜粋: {body}
ソース: {source}
エンゲージメントスコア: {engagement_score}

以下のJSON形式で返してください:
{{"summary": "120文字以内の要約", "tags": ["タグ1", "タグ2"], "novelty_score": 0.0〜1.0の数値, "buzz_reason": "注目されている理由を1文で"}}

- summary: 120文字以内、技術的なポイントを押さえる
- tags: 関連技術タグ、最大5個
- novelty_score: 新規性の高さ（0.0=既知の話題, 1.0=革新的）
- buzz_reason: なぜ注目されているか"""


CLASSIFY_SYSTEM = """あなたはAI開発トレンド記事の分類器です。
与えられた投稿を以下のカテゴリから1つ選んでください。"""


CLASSIFY_PROMPT = """以下の投稿を分類してください。

タイトル: {title}
要約: {summary}
タグ: {tags}

カテゴリ候補: {categories}

以下のJSON形式で返してください:
{{"category": "カテゴリ"}}"""


CLASSIFY_CATEGORIES = ", ".join([
    "coding_agent", "mcp_tool_use", "rag", "eval_benchmark",
    "local_llm", "oss_cli", "voice_realtime", "ai_ide_devex",
    "prompt_engineering", "ai_infra_serving", "other",
])
