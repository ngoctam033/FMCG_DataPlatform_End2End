"""Odoo JSON-2 HTTP client."""

import logging
import time
from typing import Any

import requests

from settings import Settings

logger = logging.getLogger(__name__)


class OdooJson2Client:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Authorization": f"Bearer {settings.api_key}",
            "Content-Type": "application/json",
            "X-Odoo-Database": settings.database,
            "User-Agent": "fmcg-inventory-simulator-api",
        })

    def call(self, model: str, method: str, *, retry_safe: bool = False, **payload: Any) -> Any:
        url = f"{self.settings.base_url}/json/2/{model}/{method}"
        attempts = 3 if retry_safe else 1
        for attempt in range(1, attempts + 1):
            try:
                response = self.session.post(url, json=payload, timeout=self.settings.request_timeout)
                response.raise_for_status()
                return response.json()
            except (requests.ConnectionError, requests.Timeout):
                if attempt == attempts:
                    raise
                logger.warning("Odoo read failed; retrying (%s/%s)", attempt, attempts)
                time.sleep(attempt)
            except requests.HTTPError:
                logger.error("Odoo API error %s: %s", response.status_code, response.text)
                if response.status_code < 500 or attempt == attempts:
                    raise
                time.sleep(attempt)
        raise AssertionError("unreachable")

    def search_read_all(self, model: str, domain: list, fields: list[str]) -> list[dict]:
        records = []
        offset = 0
        while True:
            page = self.call(
                model, "search_read", retry_safe=True, domain=domain, fields=fields,
                offset=offset, limit=self.settings.lookup_page_size,
            )
            records.extend(page)
            if len(page) < self.settings.lookup_page_size:
                return records
            offset += self.settings.lookup_page_size

    def create_picking(self, values: dict) -> list[int]:
        return self.call("stock.picking", "create", vals_list=[values])
