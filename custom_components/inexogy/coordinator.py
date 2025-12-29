from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import InexogyAPI


class InexogyCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to poll last_reading for one meter."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: InexogyAPI,
        meter_id: str,
        name: str,
    ) -> None:
        super().__init__(
            hass,
            hass.helpers.logger.async_get_logger(__name__),
            name=f"Inexogy {name}",
            update_interval=timedelta(seconds=30),
        )
        self._api = api
        self._meter_id = meter_id

    async def _async_update_data(self) -> dict[str, Any]:
        return await self.hass.async_add_executor_job(
            self._api.get_last_reading, self._meter_id
        )
