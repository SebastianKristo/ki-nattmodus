"""Tester for hvem som teller som hjemme, og hva som hoppes over når ingen er det."""
from __future__ import annotations

import types

import pytest

from custom_components.ki_nattmodus.const import (
    CONF_HJEMME_ENTITETER,
    CONF_KREVER_HJEMME,
)
from custom_components.ki_nattmodus.nattmodus import Nattmodus


class FalskSt:
    def __init__(self, state):
        self.state = str(state)
        self.attributes = {}


class FalskeStates:
    def __init__(self, d):
        self._d = d

    def get(self, eid):
        return self._d.get(eid)

    def async_all(self, domain):
        return [v for k, v in self._d.items() if k.startswith(f"{domain}.")]


def lag(states, options):
    """Bygger en Nattmodus uten konstruktøren, som krever hele HA.

    `options` er en property som leser fra config entry, så vi setter entry i stedet
    for å overstyre propertyen.
    """
    n = object.__new__(Nattmodus)
    n.hass = types.SimpleNamespace(states=FalskeStates(states))
    n.entry = types.SimpleNamespace(data=options, options={})
    return n


PRIVACY = "input_boolean.innendors_privace_mode"


# ------------------------------------------------------- hvem teller som hjemme
def test_uten_egne_entiteter_brukes_person():
    """Eksisterende oppsett skal være uendret."""
    n = lag({"person.sebastian": FalskSt("home"),
             "person.cybele": FalskSt("not_home")}, {})
    assert n._noen_hjemme() is True

    n = lag({"person.sebastian": FalskSt("not_home")}, {})
    assert n._noen_hjemme() is False


def test_egne_entiteter_overstyrer_person():
    """Er noe valgt, er det bare det som teller — også når personene sier noe annet."""
    states = {"person.sebastian": FalskSt("home"),
              "switch.hjemme": FalskSt("off")}
    n = lag(states, {CONF_HJEMME_ENTITETER: ["switch.hjemme"]})
    assert n._noen_hjemme() is False


@pytest.mark.parametrize("eid,verdi,ventet", [
    ("person.sebastian", "home", True),
    ("person.sebastian", "not_home", False),
    ("device_tracker.bil", "home", True),
    ("switch.hjemme", "on", True),
    ("switch.hjemme", "off", False),
    ("input_boolean.vi_er_hjemme", "on", True),
    ("binary_sensor.noen_inne", "on", True),
    ("binary_sensor.noen_inne", "off", False),
])
def test_alle_typer_teller(eid, verdi, ventet):
    """«home» eller «on» dekker person, tracker, bryter og sensor uten typesjekk."""
    n = lag({eid: FalskSt(verdi)}, {CONF_HJEMME_ENTITETER: [eid]})
    assert n._noen_hjemme() is ventet


def test_en_hjemme_holder():
    states = {"person.a": FalskSt("not_home"), "person.b": FalskSt("home")}
    n = lag(states, {CONF_HJEMME_ENTITETER: ["person.a", "person.b"]})
    assert n._noen_hjemme() is True


def test_entitet_som_ikke_finnes_teller_ikke():
    n = lag({}, {CONF_HJEMME_ENTITETER: ["switch.finnes_ikke"]})
    assert n._noen_hjemme() is False


# --------------------------------------------------- hva som hoppes over
def test_uten_liste_filtreres_ingenting():
    n = lag({"person.a": FalskSt("not_home")}, {})
    assert n._filtrer(["light.stue", PRIVACY]) == ["light.stue", PRIVACY]


def test_hjemme_kjorer_alt():
    n = lag({"switch.hjemme": FalskSt("on")},
            {CONF_HJEMME_ENTITETER: ["switch.hjemme"],
             CONF_KREVER_HJEMME: [PRIVACY]})
    assert n._filtrer(["light.stue", PRIVACY]) == ["light.stue", PRIVACY]


def test_borte_hopper_bare_over_den_ene():
    """Alt annet skal kjøre som normalt — det er hele poenget."""
    n = lag({"switch.hjemme": FalskSt("off")},
            {CONF_HJEMME_ENTITETER: ["switch.hjemme"],
             CONF_KREVER_HJEMME: [PRIVACY]})
    assert n._filtrer(["light.stue", PRIVACY, "lock.inngang"]) == [
        "light.stue", "lock.inngang"]


def test_flere_ting_kan_kreve_hjemme():
    n = lag({"switch.hjemme": FalskSt("off")},
            {CONF_HJEMME_ENTITETER: ["switch.hjemme"],
             CONF_KREVER_HJEMME: [PRIVACY, "media_player.stue"]})
    assert n._filtrer([PRIVACY, "light.stue", "media_player.stue"]) == ["light.stue"]


def test_krever_hjemme_uten_treff_endrer_ingenting():
    n = lag({"switch.hjemme": FalskSt("off")},
            {CONF_HJEMME_ENTITETER: ["switch.hjemme"],
             CONF_KREVER_HJEMME: [PRIVACY]})
    assert n._filtrer(["light.stue", "lock.inngang"]) == ["light.stue", "lock.inngang"]


def test_alt_filtrert_gir_tom_liste():
    n = lag({"switch.hjemme": FalskSt("off")},
            {CONF_HJEMME_ENTITETER: ["switch.hjemme"],
             CONF_KREVER_HJEMME: [PRIVACY]})
    assert n._filtrer([PRIVACY]) == []


def test_krever_hjemme_som_enkeltstreng():
    """Skjemaet kan gi én entitet som streng i stedet for liste."""
    n = lag({"switch.hjemme": FalskSt("off")},
            {CONF_HJEMME_ENTITETER: "switch.hjemme",
             CONF_KREVER_HJEMME: PRIVACY})
    assert n._filtrer(["light.stue", PRIVACY]) == ["light.stue"]
