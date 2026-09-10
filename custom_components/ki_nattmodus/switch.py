"""Nattmodus-bryteren."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, NAVN, SIGNAL_OPPDATERT
from .nattmodus import Nattmodus


def device_info(entry: ConfigEntry) -> DeviceInfo:
    return DeviceInfo(identifiers={(DOMAIN, entry.entry_id)}, name="Nattmodus", manufacturer=NAVN, model="Husmodus")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    nm: Nattmodus = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NattmodusSwitch(nm)])


class NattmodusSwitch(SwitchEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = None  # bruker enhetsnavnet -> switch.nattmodus
    _attr_icon = "mdi:weather-night"
    _attr_should_poll = False

    def __init__(self, nm: Nattmodus) -> None:
        self._nm = nm
        self._attr_unique_id = f"{nm.entry.entry_id}_switch"
        self._attr_device_info = device_info(nm.entry)

    @property
    def is_on(self) -> bool:
        return self._nm.aktiv

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        o = self._nm.options
        return {
            "sist_aktivert": self._nm.sist_aktivert,
            "sist_deaktivert": self._nm.sist_deaktivert,
            "lys_av": o.get("lys_av"),
            "lys_pa": o.get("lys_pa"),
            "media_av": o.get("media_av"),
            "tid_pa": o.get("tid_pa"),
            "tid_av": o.get("tid_av"),
        }

    async def async_added_to_hass(self) -> None:
        last = await self.async_get_last_state()
        if last is not None and last.state == "on":
            self._nm.aktiv = True  # husk tilstand etter omstart uten å kjøre handlingene på nytt
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_OPPDATERT, self._oppdater))

    @callback
    def _oppdater(self) -> None:
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._nm.async_aktiver(kilde="bryter")

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._nm.async_deaktiver(kilde="bryter")
