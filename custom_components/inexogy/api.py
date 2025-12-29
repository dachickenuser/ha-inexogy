from __future__ import annotations

from typing import Any
import time
import logging
from typing import Optional

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
        self._session = requests.Session()
        self._logger = logging.getLogger(__name__)

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        retries: int = 3,
        backoff: float = 1.0,
    ) -> Any:
        url = BASE_URL + endpoint
        headers = {"Accept": "application/json, text/plain"}
        attempt = 0
        while True:
            try:
                resp = self._session.request(
                    method,
                    url,
                    params=params,
                    data=data,
                    auth=self._auth,
                    headers=headers,
                    timeout=10,
                )
                if not resp.ok:
                    text = resp.text
                    self._logger.error(
                        "HTTP %s %s failed: %s %s", method, url, resp.status_code, text
                    )
                    resp.raise_for_status()
                # prefer JSON, but include text/plain message if returned
                try:
                    return resp.json()
                except ValueError:
                    # not JSON
                    return resp.text
            except requests.RequestException as err:
                attempt += 1
                if attempt > retries:
                    self._logger.exception("Request failed after %s attempts: %s", attempt, err)
                    raise
                sleep_for = backoff * (2 ** (attempt - 1))
                self._logger.debug("Request error, retrying in %s seconds: %s", sleep_for, err)
                time.sleep(sleep_for)

    def get_meters(self) -> list[dict[str, Any]]:
        resp = self._request("GET", ENDPOINT_METERS)
        if isinstance(resp, str):
            # server returned plain text error or message
            raise Exception(f"Unexpected text response for meters: {resp}")
        return resp

    def get_last_reading(self, meter_id: str) -> dict[str, Any]:
        params = {"meterId": meter_id}
        resp = self._request("GET", ENDPOINT_LAST_READING, params=params)
        if isinstance(resp, str):
            raise Exception(f"Unexpected text response for last_reading {meter_id}: {resp}")
        return resp
