from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    meters: list[dict[str, Any]] = data["meters"]
    coordinators = data["coordinators"]

    entities: list[SensorEntity] = []

    for meter in meters:
        meter_id = meter["meterId"]
        name = meter.get("name") or meter.get("fullSerialNumber", meter_id)
        coord = coordinators[meter_id]

        entities.append(InexogyPowerSensor(coord, meter_id, name))
        entities.append(InexogyEnergyImportSensor(coord, meter_id, name))
        entities.append(InexogyEnergyExportSensor(coord, meter_id, name))

    async_add_entities(entities)


class InexogyBaseSensor(SensorEntity):
    _attr_should_poll = False

    def __init__(self, coordinator, meter_id: str, base_name: str) -> None:
        self.coordinator = coordinator
        self._meter_id = meter_id
        self._base_name = base_name
        self._attr_extra_state_attributes = {"meter_id": meter_id}

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data:
            return None
        return self._extract_value(data)

    def _extract_value(self, data: dict[str, Any]):
        raise NotImplementedError


class InexogyPowerSensor(InexogyBaseSensor):
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    @property
    def name(self) -> str:
        return f"{self._base_name} Power"

    @property
    def unique_id(self) -> str:
        return f"inexogy_{self._meter_id}_power"

    def _extract_value(self, data: dict[str, Any]):
        values = data.get("values", {})
        return values.get("power")


class InexogyEnergyImportSensor(InexogyBaseSensor):
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    @property
    def name(self) -> str:
        return f"{self._base_name} Energy Import"

    @property
    def unique_id(self) -> str:
        return f"inexogy_{self._meter_id}_energy_import"

    def _extract_value(self, data: dict[str, Any]):
        values = data.get("values", {})
        energy = values.get("energy")
        if energy is None:
            return None
        # laut deinem Beispiel: Werte als Wh → kWh
        return float(energy) / 1000.0


class InexogyEnergyExportSensor(InexogyBaseSensor):
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    @property
    def name(self) -> str:
        return f"{self._base_name} Energy Export"

    @property
    def unique_id(self) -> str:
        return f"inexogy_{self._meter_id}_energy_export"

    def _extract_value(self, data: dict[str, Any]):
        values = data.get("values", {})
        energy_out = values.get("energyOut")
        if energy_out is None:
            return None
        return float(energy_out) / 1000.0
