"""Hvorfor ett lys kan bli stående på, og hva som fanger det."""
import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock

from custom_components.ki_nattmodus.nattmodus import Nattmodus


def _motor(tilstander, options):
    m = object.__new__(Nattmodus)
    m.hass = MagicMock()
    m.hass.states.get.side_effect = lambda e: tilstander.get(e)
    m.hass.states.async_all.side_effect = lambda d=None: [
        SimpleNamespace(entity_id=k, state=v.state)
        for k, v in tilstander.items() if k.startswith(f"{d}.")
    ]
    m.entry = SimpleNamespace(data={}, options=options)
    m.aktiv = True
    m.kall = []
    m._etterkontroll = None

    async def _kall(domain, service, data, blocking=False):
        ider = data["entity_id"]
        ider = [ider] if isinstance(ider, str) else list(ider)
        # et lys som ikke tåler kallet river hele gruppen med seg, slik HA gjør
        if "light.vrang" in ider and len(ider) > 1:
            raise ValueError("ugyldig for light.vrang")
        if "light.vrang" in ider:
            raise ValueError("ugyldig for light.vrang")
        m.kall.append((domain, service, ider))

    m.hass.services.async_call = _kall
    return m


def _st(state):
    return SimpleNamespace(state=state, attributes={}, entity_id=None)


def test_en_vrang_entitet_stopper_ikke_resten():
    """Én entitet som avviser kallet tok før hele gruppen med seg — da ble ingen av
    lysene slått av, og loggen nevnte bare hele lista."""
    t = {"light.stue": _st("on"), "light.vrang": _st("on"), "light.kjokken": _st("on")}
    m = _motor(t, {})
    asyncio.get_event_loop().run_until_complete(
        m._call("light", "turn_off", ["light.stue", "light.vrang", "light.kjokken"]))
    slatt_av = [e for _, _, ider in m.kall for e in ider]
    assert "light.stue" in slatt_av
    assert "light.kjokken" in slatt_av
    assert "light.vrang" not in slatt_av


def test_lys_i_begge_lister_blir_ikke_slatt_av():
    """Står et lys både i «slås av» og «nattlys», vinner nattlys. Det er en
    oppsettfeil som ser ut som en programfeil, så den skal advares om."""
    t = {"light.gang": _st("on")}
    m = _motor(t, {"lys_av": ["light.gang"], "lys_pa": ["light.gang"]})
    assert m._lys_som_skal_av() == []
    assert m._advart_om == {"light.gang"}


def test_etterkontroll_finner_lyset_som_fortsatt_star_pa():
    t = {"light.stue": _st("off"), "light.seig": _st("on")}
    m = _motor(t, {"lys_av": ["light.stue", "light.seig"], "etterkontroll": 5})
    asyncio.get_event_loop().run_until_complete(m._sjekk_at_lysene_er_av())
    forsokt = [e for _, _, ider in m.kall for e in ider]
    assert forsokt == ["light.seig"], forsokt


def test_etterkontroll_rorer_ikke_nattlys():
    t = {"light.nattlys": _st("on")}
    m = _motor(t, {"lys_av": ["light.nattlys"], "lys_pa": ["light.nattlys"],
                   "etterkontroll": 5})
    asyncio.get_event_loop().run_until_complete(m._sjekk_at_lysene_er_av())
    assert m.kall == []


def test_etterkontroll_kan_slas_av():
    t = {"light.seig": _st("on")}
    m = _motor(t, {"lys_av": ["light.seig"], "etterkontroll": 0})
    asyncio.get_event_loop().run_until_complete(m._sjekk_at_lysene_er_av())
    assert m.kall == []
