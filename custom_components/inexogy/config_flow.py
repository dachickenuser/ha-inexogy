from __future__ import annotations

from typing import Any

import voluptuous as vol
import logging

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback

from .const import (
    DOMAIN,
    CONF_CONSUMER_KEY,
    CONF_CONSUMER_SECRET,
    CONF_ACCESS_TOKEN,
    CONF_ACCESS_SECRET,
    CONF_METERS,
)
from .oauth import InexogyOAuthClient
from .api import InexogyAPI

_LOGGER = logging.getLogger(__name__)


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CONSUMER_KEY): str,
        vol.Required(CONF_CONSUMER_SECRET): str,
    }
)

STEP_VERIFIER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("verifier"): str,
    }
)


class InexogyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Inexogy."""

    VERSION = 1

    def __init__(self) -> None:
        self._consumer_key: str | None = None
        self._consumer_secret: str | None = None
        self._request_token: str | None = None
        self._request_secret: str | None = None
        self._authorize_url: str | None = None

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            self._consumer_key = user_input[CONF_CONSUMER_KEY]
            self._consumer_secret = user_input[CONF_CONSUMER_SECRET]

            oauth_client = InexogyOAuthClient(
                self._consumer_key, self._consumer_secret
            )

            try:
                # Request Token holen
                data = await self.hass.async_add_executor_job(
                    oauth_client.get_request_token
                )
                self._request_token = data["oauth_token"]
                self._request_secret = data["oauth_token_secret"]
                self._authorize_url = oauth_client.get_authorize_url(
                    self._request_token
                )

                # Weiter zu Verifier-Step
                return await self.async_step_verifier()
            except Exception as err:
                _LOGGER.exception("Error requesting request token: %s", err)
                errors["base"] = "auth_error"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_verifier(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            verifier = user_input["verifier"]

            oauth_client = InexogyOAuthClient(
                self._consumer_key, self._consumer_secret
            )
            try:
                # Access Token holen
                token_data = await self.hass.async_add_executor_job(
                    oauth_client.get_access_token,
                    self._request_token,
                    self._request_secret,
                    verifier,
                )

                access_token = token_data["oauth_token"]
                access_secret = token_data["oauth_token_secret"]

                # Test: Meter abrufen
                api = InexogyAPI(
                    self._consumer_key,
                    self._consumer_secret,
                    access_token,
                    access_secret,
                )
                meters = await self.hass.async_add_executor_job(api.get_meters)

                # Meter-Objekte vereinheitlichen (mindestens meterId + name)
                norm_meters: list[dict[str, Any]] = []
                for m in meters:
                    meter_id = m.get("meterId") or m.get("id")
                    name = m.get("fullSerialNumber") or m.get("serialNumber") or meter_id
                    norm_meters.append(
                        {
                            "meterId": meter_id,
                            "name": name,
                        }
                    )

                data = {
                    CONF_CONSUMER_KEY: self._consumer_key,
                    CONF_CONSUMER_SECRET: self._consumer_secret,
                    CONF_ACCESS_TOKEN: access_token,
                    CONF_ACCESS_SECRET: access_secret,
                    CONF_METERS: norm_meters,
                }

                return self.async_create_entry(
                    title="Inexogy", data=data
                )
            except Exception as err:
                _LOGGER.exception("Error obtaining access token or fetching meters: %s", err)
                errors["base"] = "auth_error"

        # Hinweis: dem Nutzer die Authorize-URL anzeigen
        description_placeholders = {
            "authorize_url": self._authorize_url or "",
        }

        return self.async_show_form(
            step_id="verifier",
            data_schema=STEP_VERIFIER_DATA_SCHEMA,
            errors=errors,
            description_placeholders=description_placeholders,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return InexogyOptionsFlow(config_entry)


class InexogyOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ):
        current = self.config_entry.options.get("update_interval", 60)

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({vol.Optional("update_interval", default=current): int})

        return self.async_show_form(step_id="init", data_schema=schema)
