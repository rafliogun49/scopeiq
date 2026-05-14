import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Postgres
    DATABASE_URL: str = "postgresql+psycopg://scopeiq:changeme@localhost:5432/scopeiq"
    TEST_DATABASE_URL: str = ""

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Auth
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 7

    # OpenAI
    OPENAI_API_KEY: str = ""

    # Tavily
    TAVILY_API_KEY: str = ""

    # Langfuse
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    # MCP
    MCP_SERVER_URL: str = "http://mcp:7000"

    # CORS — frontend origins allowed
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Budget & resilience (A-PR5)
    BUDGET_INPUT_TOKENS: int = 100_000
    BUDGET_OUTPUT_TOKENS: int = 25_000
    MAX_FETCHES: int = 15
    MAX_SEARCHES: int = 8
    MAX_AGENT_TURNS: int = 12
    RETRY_ATTEMPTS: int = 3
    RETRY_BASE_SECONDS: float = 2.0


settings = Settings()

# pydantic-settings populates `Settings` from .env, but third-party SDKs
# (openai, openai-agents, tavily) read their keys directly from `os.environ`.
# Mirror the relevant secrets so they're visible to those libraries without
# requiring callers to use `uv run --env-file`.
for _name in ("OPENAI_API_KEY", "TAVILY_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST"):
    _value = getattr(settings, _name, "")
    if _value and not os.environ.get(_name):
        os.environ[_name] = _value
