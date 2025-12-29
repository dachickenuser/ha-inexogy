from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_CONSUMER_KEY,
    CONF_CONSUMER_SECRET,
    CONF_ACCESS_TOKEN,
    CONF_ACCESS_SECRET,
    CONF_METERS,
)
from .api import InexogyAPI
from .coordinator import InexogyCoordinator


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up from YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Inexogy from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    data = entry.data
    consumer_key = data[CONF_CONSUMER_KEY]
    consumer_secret = data[CONF_CONSUMER_SECRET]
    access_token = data[CONF_ACCESS_TOKEN]
    access_secret = data[CONF_ACCESS_SECRET]
    meters: list[dict[str, Any]] = data[CONF_METERS]

    api = InexogyAPI(consumer_key, consumer_secret, access_token, access_secret)

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "meters": meters,
        "coordinators": {},
    }

    for meter in meters:
        meter_id = meter["meterId"]
        name = meter.get("name") or meter.get("fullSerialNumber", meter_id)

        coordinator = InexogyCoordinator(hass, api, meter_id, name)
        await coordinator.async_config_entry_first_refresh()

        hass.data[DOMAIN][entry.entry_id]["coordinators"][meter_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
