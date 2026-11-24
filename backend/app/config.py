from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./pulse.db"
    redis_url: str = ""
    opensearch_url: str = ""
    youtube_api_key: str = ""
    vapid_public_key: str = ""
    vapid_private_key: str = ""
    vapid_subject: str = "mailto:acdh.creatives@gmail.com"
    sentry_dsn: str = ""
    cron_secret: str = ""
    ingest_budget_s: float = 45.0
    cors_origins: str = "http://localhost:5173"
    trend_emerging_max_age_h: float = 3
    trend_rising_velocity: float = 1.5
    trend_declining_velocity: float = 0.3
    trend_archive_after_h: float = 72
    user_agent: str = "PULSE/0.1 (+public discovery; respects robots and publisher terms)"


settings = Settings()
