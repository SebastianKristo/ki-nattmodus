"""Knapp som kjører nattmodus-handlingene på nytt (uten å endre bryteren)."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .nattmodus import Nattmodus
from .switch import device_info


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    nm: Nattmodus = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([KjorPaNyttButton(nm)])


class KjorPaNyttButton(ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Kjør på nytt"
    _attr_icon = "mdi:replay"

    def __init__(self, nm: Nattmodus) -> None:
        self._nm = nm
        self._attr_unique_id = f"{nm.entry.entry_id}_rerun"
        self._attr_device_info = device_info(nm.entry)

    async def async_press(self) -> None:
        await self._nm.async_aktiver(kilde="knapp")
