@echo off
::All'avvio di questo .bat:
::  - nessun parametro: console visibile, nessun log salvato
::  - noconsole: console invisibile, log salvato allo spegnimento del bot

set BOT_NAME = "Reworked_BOT"

IF "%1"=="noconsole" (
    powershell Start-Process -FilePath "%BOT_NAME%.exe" -RedirectStandardOutput "%BOT_NAME%.log" -WindowStyle Hidden
) ELSE IF "%1"=="" (
    powershell Start-Process -FilePath "%BOT_NAME%.exe" -WindowStyle Normal
) ELSE (
    echo Parametro "%1" non valido!
    pause
)

exit
