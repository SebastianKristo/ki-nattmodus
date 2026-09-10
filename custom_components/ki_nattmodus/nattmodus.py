"""Logikken bak nattmodus."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util

from .const import (
    CONF_ALLE_LYS_AV,
    CONF_GARDINER,
    CONF_GJENOPPRETT,
    CONF_KUN_HJEMME,
    CONF_LASER,
    CONF_LYS_AV,
    CONF_LYS_PA,
    CONF_LYSSTYRKE,
    CONF_MEDIA_AV,
    CONF_NATTLYS_AV_VED_DEAKT,
    CONF_SCENER,
    CONF_SCENER_AV,
    CONF_TID_AV,
    CONF_TID_PA,
    SIGNAL_OPPDATERT,
)

_LOGGER = logging.getLogger(__name__)

LIGHT_ATTRS = ("brightness", "color_temp_kelvin", "rgb_color", "xy_color", "hs_color", "effect")


class Nattmodus:
    """Holder tilstand og utfører aktivering/deaktivering."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.aktiv = False
        self.sist_aktivert: datetime | None = None
        self.sist_deaktivert: datetime | None = None
        self._snapshot: dict[str, dict[str, Any]] = {}
        self._unsub: list = []

    # ------------------------------------------------------------ oppsett
    @property
    def options(self) -> dict[str, Any]:
        return {**self.entry.data, **self.entry.options}

    def _liste(self, key: str) -> list[str]:
        v = self.options.get(key) or []
        return [v] if isinstance(v, str) else list(v)

    async def async_start(self) -> None:
        for key, aktiver in ((CONF_TID_PA, True), (CONF_TID_AV, False)):
            tid = self.options.get(key)
            if not tid:
                continue
            try:
                hh, mm = str(tid).split(":")[:2]
            except ValueError:
                _LOGGER.warning("Ugyldig tid for %s: %s", key, tid)
                continue
            self._unsub.append(
                async_track_time_change(
                    self.hass,
                    self._lag_planlagt(aktiver),
                    hour=int(hh),
                    minute=int(mm),
                    second=0,
                )
            )

    @callback
    def async_stop(self) -> None:
        for u in self._unsub:
            u()
        self._unsub = []

    def _lag_planlagt(self, aktiver: bool):
        async def _kjor(_now):
            if self.options.get(CONF_KUN_HJEMME) and not self._noen_hjemme():
                _LOGGER.debug("Nattmodus: ingen hjemme, hopper over planlagt %s", "aktivering" if aktiver else "deaktivering")
                return
            if aktiver:
                await self.async_aktiver(kilde="tidsplan")
            else:
                await self.async_deaktiver(kilde="tidsplan")

        return _kjor

    def _noen_hjemme(self) -> bool:
        return any(
            st.state == "home"
            for st in self.hass.states.async_all("person")
        )

    # ------------------------------------------------------------ handlinger
    async def _call(self, domain: str, service: str, entity_ids: list[str], **data: Any) -> None:
        if not entity_ids:
            return
        try:
            await self.hass.services.async_call(
                domain, service, {"entity_id": entity_ids, **data}, blocking=True
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Nattmodus: %s.%s feilet for %s: %s", domain, service, entity_ids, err)

    def _lys_som_skal_av(self) -> list[str]:
        lys_pa = set(self._liste(CONF_LYS_PA))
        if self.options.get(CONF_ALLE_LYS_AV):
            alle = [
                st.entity_id
                for st in self.hass.states.async_all("light")
                if st.state == "on" and st.entity_id not in lys_pa
            ]
            return alle + [e for e in self._liste(CONF_LYS_AV) if not e.startswith("light.")]
        return [e for e in self._liste(CONF_LYS_AV) if e not in lys_pa]

    def _ta_snapshot(self, entity_ids: list[str]) -> None:
        self._snapshot = {}
        for eid in entity_ids:
            st = self.hass.states.get(eid)
            if st is None:
                continue
            self._snapshot[eid] = {
                "state": st.state,
                "attrs": {k: st.attributes[k] for k in LIGHT_ATTRS if k in st.attributes},
            }

    async def async_aktiver(self, kilde: str = "manuell") -> None:
        _LOGGER.info("Nattmodus aktiveres (%s)", kilde)
        lys_av = self._lys_som_skal_av()
        lys_pa = self._liste(CONF_LYS_PA)

        if self.options.get(CONF_GJENOPPRETT, True):
            self._ta_snapshot(lys_av + lys_pa)

        # media av
        await self._call("media_player", "turn_off", self._liste(CONF_MEDIA_AV))
        # lys/brytere av
        av_lys = [e for e in lys_av if e.startswith("light.")]
        av_switch = [e for e in lys_av if e.startswith("switch.")]
        av_annet = [e for e in lys_av if not e.startswith(("light.", "switch."))]
        await self._call("light", "turn_off", av_lys)
        await self._call("switch", "turn_off", av_switch)
        await self._call("homeassistant", "turn_off", av_annet)
        # nattlys på
        pct = int(self.options.get(CONF_LYSSTYRKE, 20))
        await self._call("light", "turn_on", [e for e in lys_pa if e.startswith("light.")], brightness_pct=pct)
        await self._call("homeassistant", "turn_on", [e for e in lys_pa if not e.startswith("light.")])
        # låser og gardiner
        await self._call("lock", "lock", self._liste(CONF_LASER))
        await self._call("cover", "close_cover", self._liste(CONF_GARDINER))
        # scener/skript
        await self._kjor_scener(self._liste(CONF_SCENER))

        self.aktiv = True
        self.sist_aktivert = dt_util.now()
        async_dispatcher_send(self.hass, SIGNAL_OPPDATERT)

    async def async_deaktiver(self, kilde: str = "manuell") -> None:
        _LOGGER.info("Nattmodus deaktiveres (%s)", kilde)
        lys_pa = self._liste(CONF_LYS_PA)

        if self.options.get(CONF_NATTLYS_AV_VED_DEAKT, True):
            await self._call("light", "turn_off", [e for e in lys_pa if e.startswith("light.")])
            await self._call("homeassistant", "turn_off", [e for e in lys_pa if not e.startswith("light.")])

        if self.options.get(CONF_GJENOPPRETT, True) and self._snapshot:
            for eid, snap in self._snapshot.items():
                if eid in lys_pa and self.options.get(CONF_NATTLYS_AV_VED_DEAKT, True):
                    continue
                if snap["state"] == "on":
                    if eid.startswith("light."):
                        await self._call("light", "turn_on", [eid], **snap["attrs"])
                    else:
                        await self._call("homeassistant", "turn_on", [eid])
                elif snap["state"] == "off":
                    await self._call("homeassistant", "turn_off", [eid])
            self._snapshot = {}

        await self._kjor_scener(self._liste(CONF_SCENER_AV))

        self.aktiv = False
        self.sist_deaktivert = dt_util.now()
        async_dispatcher_send(self.hass, SIGNAL_OPPDATERT)

    async def _kjor_scener(self, ids: list[str]) -> None:
        for eid in ids:
            dom = eid.split(".")[0]
            if dom == "scene":
                await self._call("scene", "turn_on", [eid])
            elif dom == "script":
                await self._call("script", "turn_on", [eid])
            elif dom == "automation":
                await self._call("automation", "trigger", [eid], skip_condition=True)
            else:
                await self._call("homeassistant", "turn_on", [eid])
