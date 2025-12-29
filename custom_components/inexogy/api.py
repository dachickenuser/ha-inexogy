from __future__ import annotations

from typing import Any

import requests
from requests_oauthlib import OAuth1

from .const import BASE_URL, ENDPOINT_METERS, ENDPOINT_LAST_READING


class InexogyAPI:
    """Simple Inexogy API client."""

    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        access_token: str,
        access_secret: str,
    ) -> None:
        self._auth = OAuth1(
            client_key=consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_secret,
            signature_method="HMAC-SHA1",
        )

    def get_meters(self) -> list[dict[str, Any]]:
        url = BASE_URL + ENDPOINT_METERS
        resp = requests.get(url, auth=self._auth, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_last_reading(self, meter_id: str) -> dict[str, Any]:
        url = BASE_URL + ENDPOINT_LAST_READING
        params = {"meterId": meter_id}
        resp = requests.get(url, params=params, auth=self._auth, timeout=10)
        resp.raise_for_status()
        return resp.json()
