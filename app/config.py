"""設定管理モジュール"""

from dataclasses import dataclass

from dotenv import load_dotenv
import os


@dataclass
class Settings:
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "ai-trend-analyzer/0.1"
    qiita_access_token: str = ""
    db_path: str = "data/trends.db"
    llm_provider: str = "zhipu"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = "glm-4-flash"
    llm_max_tokens: int = 2048
    llm_temperature: float = 0.3


def _load_settings() -> Settings:
    load_dotenv()
    provider = os.getenv("LLM_PROVIDER", "zhipu")
    defaults = _provider_defaults(provider)
    return Settings(
        reddit_client_id=os.getenv("REDDIT_CLIENT_ID", ""),
        reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
        reddit_user_agent=os.getenv("REDDIT_USER_AGENT", "ai-trend-analyzer/0.1"),
        qiita_access_token=os.getenv("QIITA_ACCESS_TOKEN", ""),
        db_path=os.getenv("DB_PATH", "data/trends.db"),
        llm_provider=provider,
        llm_api_key=os.getenv("LLM_API_KEY", ""),
        llm_base_url=os.getenv("LLM_BASE_URL", defaults["base_url"]),
        llm_model=os.getenv("LLM_MODEL", defaults["model"]),
        llm_max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2048")),
        llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
    )


def _provider_defaults(provider: str) -> dict[str, str]:
    """provider ごとのデフォルト値"""
    _defaults = {
        "zhipu": {
            "base_url": "https://api.z.ai/api/paas/v4/",
            "model": "glm-4-flash",
        },
        "anthropic": {
            "base_url": "https://api.anthropic.com",
            "model": "claude-sonnet-4-20250514",
        },
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o",
        },
    }
    return _defaults.get(provider, _defaults["zhipu"])


settings = _load_settings()
