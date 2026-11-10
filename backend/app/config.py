from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        extra="ignore",
    )

    app_name: str = "Sentinela"
    app_env: str = "demo"
    simulate: bool = True
    confirm_execute: bool = False
    database_url: str = "sqlite:///./sentinela.db"
    log_scan_path: str = str(ROOT_DIR / "data" / "logs")
    export_path: str = str(ROOT_DIR / "data" / "exports")

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    slack_webhook_url: str = ""

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    report_email_to: str = "sustentacao@empresa.local"

    ticket_source: str = "glpi"
    jira_url: str = ""
    jira_user: str = ""
    jira_token: str = ""
    glpi_url: str = ""
    glpi_app_token: str = ""
    glpi_user_token: str = ""
    servicenow_url: str = ""
    servicenow_user: str = ""
    servicenow_password: str = ""
    zendesk_subdomain: str = ""
    zendesk_email: str = ""
    zendesk_token: str = ""

    disk_threshold: int = 90
    memory_threshold: int = 92


@lru_cache
def get_settings() -> Settings:
    return Settings()
