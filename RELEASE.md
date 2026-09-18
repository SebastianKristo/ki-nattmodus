# KI Nattmodus 1.1.1

## Integrasjonen startet ikke

```
File "/config/custom_components/ki_nattmodus/config_flow.py", line 38, in <module>
    vol.Optional(CONF_ETTERKONTROLL, default=d.get(CONF_ETTERKONTROLL, 5)):
NameError: name 'd' is not defined
```

`SCHEMA` er en konstant som bygges når modulen importeres. Der finnes ingen `d` — den
hører til en funksjon som leser lagrede verdier. Importen kastet derfor, og Home
Assistant fikk aldri lastet config_flow:

```
Error importing platform config_flow from integration ki_nattmodus
to set up ki_nattmodus configuration entry
```

Standardverdien er nå konstanten `5`, som alle de andre feltene i skjemaet bruker.

**Oppslaget var også unødvendig.** Options-flyten kaller
`add_suggested_values_to_schema(SCHEMA, self.config_entry.options)`, som alt fyller inn
lagrede verdier i hvert felt. Etterkontrollen fikk derfor riktig verdi uansett — linja
gjorde ingenting annet enn å knekke importen.

### Kontrollert

Alle seks modulene importeres nå slik Home Assistant gjør det, og `SCHEMA` bygges med
`etterkontroll: 5` blant standardverdiene. De fem eksisterende testene passerer.
