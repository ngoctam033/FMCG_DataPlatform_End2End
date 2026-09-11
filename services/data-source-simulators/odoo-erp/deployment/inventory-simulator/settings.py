"""Environment-backed application settings."""

import os
from dataclasses import dataclass


def _positive_int(name: str, default: int) -> int:
    value = int(os.getenv(name, str(default)))
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return value


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    return default if value is None else value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    base_url: str
    database: str
    api_key: str
    cron: str
    batch_size: int
    run_on_start: bool
    timezone: str
    request_timeout: int
    lookup_page_size: int
    log_level: str

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = os.getenv("ODOO_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("ODOO_API_KEY is required")
        return cls(
            base_url=os.getenv("ODOO_BASE_URL", "http://odoo:8069").rstrip("/"),
            database=os.getenv("ODOO_DATABASE", "fmcg_erp"),
            api_key=api_key,
            cron=os.getenv("SIMULATOR_CRON", "*/5 * * * *"),
            batch_size=_positive_int("SIMULATOR_BATCH_SIZE", 50),
            run_on_start=_env_bool("SIMULATOR_RUN_ON_START", True),
            timezone=os.getenv("SIMULATOR_TIMEZONE", "Asia/Ho_Chi_Minh"),
            request_timeout=_positive_int("ODOO_REQUEST_TIMEOUT", 120),
            lookup_page_size=_positive_int("SIMULATOR_LOOKUP_PAGE_SIZE", 500),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )
