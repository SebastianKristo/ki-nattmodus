"""Sensor: når nattmodus sist ble aktivert."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_OPPDATERT
from .nattmodus import Nattmodus
from .switch import device_info


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    nm: Nattmodus = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SistAktivertSensor(nm)])


class SistAktivertSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Sist aktivert"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-outline"
    _attr_should_poll = False

    def __init__(self, nm: Nattmodus) -> None:
        self._nm = nm
        self._attr_unique_id = f"{nm.entry.entry_id}_sist_aktivert"
        self._attr_device_info = device_info(nm.entry)

    @property
    def native_value(self) -> datetime | None:
        return self._nm.sist_aktivert

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_OPPDATERT, self._oppdater))

    @callback
    def _oppdater(self) -> None:
        self.async_write_ha_state()
