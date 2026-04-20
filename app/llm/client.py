"""LLM クライアントの provider 切替ラッパー

httpx ベースで zhipu / anthropic / openai に対応。
APIキー未設定時は stub を返す。

利用例::

    from app.llm.client import generate_text
    text = generate_text("要約して", system="あなたは作家です")
"""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.config import settings
from app.llm.budget import estimate_tokens, truncate_to_budget

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """LLM 呼び出し失敗"""


# ── provider ごとの送信ロジック ────────────────────────────

def _call_zhipu(prompt: str, system: str) -> str:
    """Zhipu AI (OpenAI互換 chat/completions)"""
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = httpx.post(
        f"{settings.llm_base_url}/chat/completions",
        headers={"Authorization": f"Bearer {settings.llm_api_key}"},
        json={
            "model": settings.llm_model,
            "messages": messages,
            "max_tokens": settings.llm_max_tokens,
            "temperature": settings.llm_temperature,
        },
        timeout=60.0,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_anthropic(prompt: str, system: str) -> str:
    """Anthropic Messages API"""
    # anthropic SDK があればそちらを使う、なければ httpx で直接叩く
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.llm_api_key)
        kwargs: dict[str, Any] = {
            "model": settings.llm_model,
            "max_tokens": settings.llm_max_tokens,
            "temperature": settings.llm_temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        response = client.messages.create(**kwargs)
        return response.content[0].text
    except ImportError:
        # httpx フォールバック
        messages = [{"role": "user", "content": prompt}]
        body: dict[str, Any] = {
            "model": settings.llm_model,
            "max_tokens": settings.llm_max_tokens,
            "messages": messages,
        }
        headers = {
            "x-api-key": settings.llm_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        if system:
            body["system"] = system
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=body,
            timeout=60.0,
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]


def _call_openai(prompt: str, system: str) -> str:
    """OpenAI chat/completions"""
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = httpx.post(
        f"{settings.llm_base_url}/chat/completions",
        headers={"Authorization": f"Bearer {settings.llm_api_key}"},
        json={
            "model": settings.llm_model,
            "messages": messages,
            "max_tokens": settings.llm_max_tokens,
            "temperature": settings.llm_temperature,
        },
        timeout=60.0,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


_PROVIDERS: dict[str, callable] = {
    "zhipu": _call_zhipu,
    "anthropic": _call_anthropic,
    "openai": _call_openai,
}


# ── 公開 API ──────────────────────────────────────────────

def generate_text(prompt: str, system: str = "") -> str:
    """プロンプトを送信してテキスト応答を得る"""
    if not settings.llm_api_key:
        return generate_text_stub(prompt, system=system)

    caller = _PROVIDERS.get(settings.llm_provider)
    if caller is None:
        raise LLMError(f"不明な provider: {settings.llm_provider}")

    try:
        return caller(prompt, system)
    except httpx.HTTPStatusError as e:
        raise LLMError(
            f"LLM API エラー ({e.response.status_code}): {e.response.text[:200]}"
        ) from e
    except Exception as e:
        raise LLMError(f"LLM 呼び出し失敗: {e}") from e


def generate_json(prompt: str, system: str = "") -> dict[str, Any]:
    """プロンプトを送信して JSON 応答を得る"""
    raw = generate_text(prompt, system=system)
    try:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            if text.endswith("```"):
                text = text[:-3].strip()
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise LLMError(f"JSON パース失敗: {e}\nraw: {raw[:200]}") from e


def generate_text_stub(prompt: str, system: str = "") -> str:
    """APIキー未設定時のスタブ"""
    logger.info("stub: prompt len=%d", len(prompt))
    return '{"summary": "stub", "tags": [], "novelty_score": 0.0, "buzz_reason": ""}'


class LLMClient:
    """LLM 呼び出しのクラスAPI（関数APIの薄いラッパー）"""

    def generate_text(self, prompt: str, system: str = "") -> str:
        return generate_text(prompt, system=system)

    def generate_json(self, prompt: str, system: str = "") -> dict[str, Any]:
        return generate_json(prompt, system=system)
