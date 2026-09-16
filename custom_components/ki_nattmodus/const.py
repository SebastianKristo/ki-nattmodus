"""Konstanter for KI Nattmodus."""

DOMAIN = "ki_nattmodus"
NAVN = "KI Nattmodus"

CONF_LYS_AV = "lys_av"              # lys/brytere som slås av
CONF_ALLE_LYS_AV = "alle_lys_av"    # slå av ALLE lys (unntatt lys_pa)
CONF_LYS_PA = "lys_pa"              # lys som slås på (nattlys)
CONF_LYSSTYRKE = "lysstyrke"        # % for nattlys
CONF_MEDIA_AV = "media_av"          # media_player som slås av
CONF_LASER = "laser"                # låser som låses
CONF_GARDINER = "gardiner"          # covers som lukkes
CONF_SCENER = "scener"              # scener/skript som kjøres ved aktivering
CONF_SCENER_AV = "scener_av"        # scener/skript som kjøres ved deaktivering
CONF_GJENOPPRETT = "gjenopprett"    # gjenopprett lys slik de var, ved deaktivering
CONF_NATTLYS_AV_VED_DEAKT = "nattlys_av_ved_deaktivering"
CONF_TID_PA = "tid_pa"              # automatisk aktivering (HH:MM)
CONF_TID_AV = "tid_av"              # automatisk deaktivering (HH:MM)
CONF_KUN_HJEMME = "kun_hjemme"      # bare automatisk hvis noen er hjemme (person.*)
# Sekunder etter aktivering før vi sjekker at lysene faktisk ble slukket, og prøver
# en gang til på dem som fortsatt står på. 0 slår kontrollen av.
CONF_ETTERKONTROLL = "etterkontroll"

SERVICE_AKTIVER = "aktiver"
SERVICE_DEAKTIVER = "deaktiver"
SERVICE_VEKSLE = "veksle"

SIGNAL_OPPDATERT = f"{DOMAIN}_oppdatert"
