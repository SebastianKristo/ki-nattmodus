# KI Nattmodus 1.1.0

## Ett lys ble ikke slått av

Tre ting er gjort, og til sammen dekker de både årsakene og feilsøkingen.

**Én vrang entitet tok hele gruppen med seg.** Avslåingen sendte alle lysene i ett
tjenestekall. Avviser Home Assistant kallet — fordi én entitet er utilgjengelig, eller
ikke tåler et parameter — feiler hele kallet, og *ingen* av lysene blir slått av. Loggen
nevnte bare hele lista, så det var umulig å se hvilket lys som var problemet.

Nå prøves gruppen først, og feiler den, tas lysene én og én. Resten blir slått av, og
loggen peker på entiteten som faktisk avviste kallet.

**Etterkontroll.** Fem sekunder etter aktivering sjekkes det at lysene faktisk er av. De
som fortsatt står på, får ett nytt forsøk, og loggen navngir dem:

> Nattmodus: disse lysene sto fortsatt på etter avslåingen, prøver igjen: light.stue.
> Skjer det hver gang, slår noe dem på igjen — en bevegelsesautomasjon, en bryter på
> veggen, eller en scene som kjører etterpå.

Nattlys røres ikke. `etterkontroll: 0` slår kontrollen av, og feltet ligger i oppsettet.

**Lys i begge lister.** Står et lys både i «lys som slås av» og i «nattlys», vinner
nattlys — og lyset blir aldri slått av. Det er en oppsettfeil som ser ut som en
programfeil. Nå advares det i loggen med entitets-id-en.

## Hva du bør sjekke

Kjør nattmodus én gang og se i loggen. Får du advarselen om etterkontroll hver gang for
samme lys, er det noe som slår det på igjen — og da hjelper ingen endring her; det er
automasjonen eller scenen som må finnes. Får du den bare av og til, var det et treg
enhet, og det nye forsøket ordner det.
