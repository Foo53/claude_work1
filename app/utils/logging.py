"""ロギングユーティリティ"""

import logging
import sys

_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """モジュール名を指定してロガーを取得する"""
    return logging.getLogger(name)


def setup_logging(level: int = logging.INFO) -> None:
    """ルートロガーの初期化（main.pyの起動時に1回だけ呼ぶ）"""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_FORMAT, datefmt=_DATE_FORMAT))
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)
