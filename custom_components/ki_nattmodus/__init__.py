"""KI Nattmodus – én bryter som setter huset i nattmodus."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN, SERVICE_AKTIVER, SERVICE_DEAKTIVER, SERVICE_VEKSLE
from .nattmodus import Nattmodus

PLATFORMS: list[Platform] = [Platform.SWITCH, Platform.SENSOR, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    nm = Nattmodus(hass, entry)
    await nm.async_start()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = nm

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    async def _aktiver(_call: ServiceCall) -> None:
        await nm.async_aktiver(kilde="tjeneste")

    async def _deaktiver(_call: ServiceCall) -> None:
        await nm.async_deaktiver(kilde="tjeneste")

    async def _veksle(_call: ServiceCall) -> None:
        if nm.aktiv:
            await nm.async_deaktiver(kilde="tjeneste")
        else:
            await nm.async_aktiver(kilde="tjeneste")

    hass.services.async_register(DOMAIN, SERVICE_AKTIVER, _aktiver, schema=vol.Schema({}))
    hass.services.async_register(DOMAIN, SERVICE_DEAKTIVER, _deaktiver, schema=vol.Schema({}))
    hass.services.async_register(DOMAIN, SERVICE_VEKSLE, _veksle, schema=vol.Schema({}))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        nm: Nattmodus = hass.data[DOMAIN].pop(entry.entry_id)
        nm.async_stop()
        for svc in (SERVICE_AKTIVER, SERVICE_DEAKTIVER, SERVICE_VEKSLE):
            hass.services.async_remove(DOMAIN, svc)
    return ok
