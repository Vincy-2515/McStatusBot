@echo off
set BOT_NAME=McStatusBot
start "%BOT_NAME%" "%BOT_NAME%.bat" --no-console
::PLACEHOLDER: JAVA SERVER STARTER COMMAND GOES HERE!!!
powershell Get-Process -Name "%BOT_NAME%" -ErrorAction Ignore >nul 2>&1 && ECHO Warning! "%BOT_NAME%" is still running.
