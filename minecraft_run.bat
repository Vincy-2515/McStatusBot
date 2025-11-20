@echo off

::Add "-WindowStyle Hidden" to the end of the next line to hide the console window 
powershell Start-Process -FilePath "McStatusBot.exe"

::PLACEHOLDER: Java Minecraft Server Launch Command goes here

powershell Get-Process -Name "McStatusBot" -ErrorAction Ignore >nul 2>&1 && ECHO Warning! "McStatusBot" is still running.
