::Avviare questo file bat con: start Parrot_BOT.bat

::OPZIONE 1: console visibile, nessun log salvato
::start "Parrot_BOT.exe" Parrot_BOT.exe

::OPZIONE 2: console invisibile, log aggiornato allo spegnimento del bot
echo Set WshShell = CreateObject("WScript.Shell") > "%temp%\run_invisible.vbs" && echo WshShell.Run "cmd /c Parrot_BOT.exe > Parrot_BOT.log 2>&1", 0, False >> "%temp%\run_invisible.vbs" && cscript //nologo "%temp%\run_invisible.vbs" && del "%temp%\run_invisible.vbs"

exit
