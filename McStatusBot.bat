@echo off
:: All'avvio di questo .bat:
::  - nessun parametro: console visibile, nessun log salvato
::  - "--no-console": console invisibile, log salvato allo spegnimento del bot

:: %~n0: is the name of this current file
set BOT_NAME=%~n0
set BOT_TOML=../McStatusBot.toml

IF "%1"=="--no-console" (
    powershell Start-Process -FilePath "%BOT_NAME%.exe" -ArgumentList '--config-toml="%BOT_TOML%"' -WindowStyle Hidden
) ELSE IF "%1"=="" (
    powershell Start-Process -FilePath "%BOT_NAME%.exe" -ArgumentList '--config-toml="%BOT_TOML%"' -WindowStyle Normal
) ELSE (
    echo Parametro "%1" non valido!
    pause
)

exit
