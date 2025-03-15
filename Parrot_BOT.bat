@echo off
::All'avvio di questo .bat:
::  - nessun parametro: console visibile, nessun log salvato
::  - noconsole: console invisibile, log salvato allo spegnimento del bot

IF "%1"=="noconsole" (
    powershell Start-Process -FilePath "Parrot_BOT.exe" -RedirectStandardOutput "Parrot_BOT.log" -WindowStyle Hidden
) ELSE IF "%1"=="" (
    powershell Start-Process -FilePath "Parrot_BOT.exe" -WindowStyle Normal
) ELSE (
    echo Parametro "%1" non valido!
    pause
)

exit
