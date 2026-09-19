# KI Nattmodus 1.2.0

## Velg selv hvem som teller som hjemme

Nytt felt **«Hjemme-entiteter»**. Tidligere leste integrasjonen alle `person`-entiteter,
og det var det eneste alternativet.

Nå kan du velge `person`, `device_tracker`, `switch`, `input_boolean` eller
`binary_sensor`. Brytere er med fordi en hytte ofte ikke kan skilles fra hjemme med
sonene alene — da styrer du det selv med en bryter.

Lar du feltet stå tomt, teller alle `person`-entiteter som før. Eksisterende oppsett er
uendret.

«Hjemme» er `home` eller `on`. De to dekker alle typene uten at integrasjonen må vite
hvilken den ser på.

## Kjør alt unntatt én ting når ingen er hjemme

Nytt felt **«Krever at noen er hjemme»**. Entitetene du legger der hoppes over når ingen
er hjemme — resten kjører som normalt.

Det er forskjellen fra «Bare når noen er hjemme», som fantes fra før: den hopper over
**hele** aktiveringen. Dette hopper over de enkeltdelene du peker ut.

Bruken det er laget for: slå på privacy mode hjemme, men ikke når dere er på hytta og
huset står tomt om dagen. Lys, låser og gardiner gjør fortsatt sitt.

Legg `input_boolean.innendors_privace_mode` i feltet, og velg en bryter eller en person
som «hjemme-entitet».

### Hvor filteret ligger

I `_call` og `_kjor_scener`, ikke i hver enkelt handling. Det betyr at det virker uansett
hvilken liste entiteten står i — lys som slås av, lys som slås på, låser, gardiner,
media eller scener. Én entitet på lista blir hoppet over overalt, og du slipper å finne
ut hvilken liste den tilfeldigvis står i.

## Tester

19 nye i `tests/test_hjemme.py`: alle fem entitetstypene, egne entiteter som overstyrer
person, én hjemme som holder, entitet som ikke finnes, filtrering hjemme og borte, flere
ting som krever hjemme, tom liste, og én entitet gitt som streng i stedet for liste.
24 tester i alt.

---

# KI Nattmodus 1.1.1

Integrasjonen startet ikke: `SCHEMA` brukte `d.get(...)` på modulnivå, der `d` ikke
finnes. Standardverdien er nå konstanten `5`.
