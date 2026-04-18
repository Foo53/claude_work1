# AI開発トレンド分析ツール

Reddit / Qiita の投稿を収集し、AI開発のトレンドを分析するツール。

## セットアップ

```bash
cp .env.example .env
# .env にAPIキーを記入

pip install -e ".[dev]"
```

## 使い方

```bash
# 動作確認
trend hello

# データ収集（Day 1 後半で実装）
trend collect --source reddit --query "claude code"
trend collect --source qiita  --query "AIエージェント"
```

## ライセンス

MIT
