@echo off
:: All'avvio di questo .bat:
::  - nessun parametro: console visibile, nessun log salvato
::  - "--no-console": console invisibile, log salvato allo spegnimento del bot

:: %~n0: is the name of this current file
set BOT_NAME=%~n0

IF "%1"=="--no-console" (
    powershell Start-Process -FilePath "%BOT_NAME%.exe" -ArgumentList '--config-toml="../McStatusBot.toml"' -RedirectStandardOutput "%BOT_NAME%.log" -WindowStyle Hidden
) ELSE IF "%1"=="" (
    powershell Start-Process -FilePath "%BOT_NAME%.exe" -ArgumentList '--config-toml="../McStatusBot.toml"' -WindowStyle Normal
    powershell -Command "Get-Content '%BOT_NAME%.log' -Wait | Out-Host"
) ELSE (
    echo Parametro "%1" non valido!
    pause
)

exit
