"""ノーマライザーの基底インターフェース

各ソースの生データ（Reddit submission, Qiita article 等）を
共通 Item へ変換する規約を定義する。

利用例::

    from app.normalizers.base import BaseNormalizer

    class RedditNormalizer(BaseNormalizer):
        def normalize(self, raw: dict) -> Item:
            return Item(
                source="reddit",
                source_item_id=raw["id"],
                title=raw["title"],
                ...
            )
"""

from abc import ABC, abstractmethod
from typing import Any

from app.models import Item


class BaseNormalizer(ABC):
    """生データを共通 Item に変換するインターフェース"""

    @abstractmethod
    def normalize(self, raw: dict[str, Any]) -> Item:
        """ソース固有の dict を Item に変換する"""
        ...
