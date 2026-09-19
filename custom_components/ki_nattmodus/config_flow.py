"""Oppsett for KI Nattmodus."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_ALLE_LYS_AV,
    CONF_GARDINER,
    CONF_GJENOPPRETT,
    CONF_ETTERKONTROLL,
    CONF_HJEMME_ENTITETER,
    CONF_KREVER_HJEMME,
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
    DOMAIN,
    NAVN,
)

SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_MEDIA_AV): selector.EntitySelector(selector.EntitySelectorConfig(domain="media_player", multiple=True)),
        vol.Optional(CONF_LYS_AV): selector.EntitySelector(selector.EntitySelectorConfig(domain=["light", "switch", "fan"], multiple=True)),
        vol.Optional(CONF_ALLE_LYS_AV, default=False): selector.BooleanSelector(),
        vol.Optional(CONF_LYS_PA): selector.EntitySelector(selector.EntitySelectorConfig(domain=["light", "switch"], multiple=True)),
        # SCHEMA bygges når modulen importeres, så standardverdien må være en konstant.
        # Lagrede verdier fylles inn av add_suggested_values_to_schema i options-flyten
        # under; et oppslag her var både ugyldig og unødvendig.
        vol.Optional(CONF_ETTERKONTROLL, default=5):
            selector.NumberSelector(selector.NumberSelectorConfig(
                min=0, max=120, step=1, unit_of_measurement="sek",
                mode=selector.NumberSelectorMode.BOX)),
        vol.Optional(CONF_LYSSTYRKE, default=20): selector.NumberSelector(selector.NumberSelectorConfig(min=1, max=100, step=1, unit_of_measurement="%", mode="slider")),
        vol.Optional(CONF_LASER): selector.EntitySelector(selector.EntitySelectorConfig(domain="lock", multiple=True)),
        vol.Optional(CONF_GARDINER): selector.EntitySelector(selector.EntitySelectorConfig(domain="cover", multiple=True)),
        vol.Optional(CONF_SCENER): selector.EntitySelector(selector.EntitySelectorConfig(domain=["scene", "script", "automation"], multiple=True)),
        vol.Optional(CONF_SCENER_AV): selector.EntitySelector(selector.EntitySelectorConfig(domain=["scene", "script", "automation"], multiple=True)),
        vol.Optional(CONF_GJENOPPRETT, default=True): selector.BooleanSelector(),
        vol.Optional(CONF_NATTLYS_AV_VED_DEAKT, default=True): selector.BooleanSelector(),
        vol.Optional(CONF_TID_PA): selector.TimeSelector(),
        vol.Optional(CONF_TID_AV): selector.TimeSelector(),
        vol.Optional(CONF_KUN_HJEMME, default=False): selector.BooleanSelector(),
        # Hvem som teller som hjemme. Tom = alle person-entiteter, som før.
        # Brytere er med fordi en hytte ofte ikke kan skilles fra hjemme med sonene
        # alene — da styrer man det selv med en bryter.
        vol.Optional(CONF_HJEMME_ENTITETER): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=["person", "device_tracker", "switch", "input_boolean",
                        "binary_sensor"],
                multiple=True)),
        # Ting som bare skal gjøres når noen er hjemme. Resten kjører uansett.
        vol.Optional(CONF_KREVER_HJEMME): selector.EntitySelector(
            selector.EntitySelectorConfig(multiple=True)),
    }
)


class KiNattmodusConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            return self.async_create_entry(title=NAVN, data={}, options=user_input)
        return self.async_show_form(step_id="user", data_schema=SCHEMA)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return KiNattmodusOptionsFlow()


class KiNattmodusOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(SCHEMA, self.config_entry.options),
        )
