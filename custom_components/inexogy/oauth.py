from __future__ import annotations

from urllib.parse import parse_qsl

from requests_oauthlib import OAuth1Session

from .const import (
    BASE_URL,
    OAUTH_REQUEST_TOKEN,
    OAUTH_AUTHORIZE,
    OAUTH_ACCESS_TOKEN,
)


class InexogyOAuthClient:
    """Handles OAuth1 flow for Inexogy API."""

    def __init__(self, consumer_key: str, consumer_secret: str) -> None:
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    def get_request_token(self) -> dict:
        oauth = OAuth1Session(self.consumer_key, client_secret=self.consumer_secret)
        url = BASE_URL + OAUTH_REQUEST_TOKEN
        resp = oauth.post(url)
        resp.raise_for_status()
        return dict(parse_qsl(resp.text))

    def get_authorize_url(self, oauth_token: str) -> str:
        return f"{BASE_URL}{OAUTH_AUTHORIZE}?oauth_token={oauth_token}"

    def get_access_token(
        self, request_token: str, request_secret: str, verifier: str
    ) -> dict:
        oauth = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=request_token,
            resource_owner_secret=request_secret,
            verifier=verifier,
        )
        url = BASE_URL + OAUTH_ACCESS_TOKEN
        resp = oauth.post(url)
        resp.raise_for_status()
        return dict(parse_qsl(resp.text))
