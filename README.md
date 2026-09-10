# KI Nattmodus

Custom integration for Home Assistant: **én bryter som setter huset i nattmodus**.

`switch.nattmodus` på →
1. slår av TV / valgte mediaspillere
2. slår av valgte lys og brytere (eller *alle* lys)
3. tenner nattlysene med valgt lysstyrke
4. låser valgte låser og lukker valgte gardiner/markiser
5. kjører valgfrie scener/skript/automasjoner

`switch.nattmodus` av →
1. slår av nattlysene
2. gjenoppretter lysene slik de var før aktivering (lysstyrke/farge), hvis valgt
3. kjører valgfrie scener/skript for deaktivering

Alt velges i UI (Innstillinger → Integrasjoner → KI Nattmodus → Konfigurer). Ingen YAML.

## Entiteter

| Entitet | |
|---|---|
| `switch.nattmodus` | bryteren – husker tilstand over omstart uten å kjøre handlingene på nytt |
| `sensor.nattmodus_sist_aktivert` | tidsstempel |
| `button.nattmodus_kjor_pa_nytt` | kjører aktiveringen på nytt (f.eks. om noen slo på et lys) |

## Tjenester

`ki_nattmodus.aktiver`, `ki_nattmodus.deaktiver`, `ki_nattmodus.veksle` – til automasjoner, Homey-flows, knapper.

## Tidsplan

Valgfritt klokkeslett for automatisk aktivering og deaktivering, med «bare når noen er hjemme» (person.* = home).

## Dashboard

```yaml
type: custom:ki-toggle-card
size: tile
entity: switch.nattmodus
name: Nattmodus
label: TV av, nattlys på, dører låst
icon: mdi:weather-night
```

Eller i ki-rom-card «Scener»-raden: `scener_ekstra: [switch.nattmodus]` er ikke støttet – bruk et skript som kaller `ki_nattmodus.veksle`.

## Installasjon

HACS → Custom repositories → `SebastianKristo/ki-nattmodus` (Integration), restart, legg til «KI Nattmodus».
