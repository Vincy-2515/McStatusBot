echo Set WshShell = CreateObject("WScript.Shell") > "%temp%\run_invisible.vbs" & rem Scrive il comando per creare l'oggetto WshShell nel file VBS
echo WshShell.Run "cmd /c Parrot_BOT.exe > Parrot_BOT.log 2>&1", 0, False >> "%temp%\run_invisible.vbs" & rem Scrive il comando per eseguire il programma e reindirizzare l'output al file di log
cscript //nologo "%temp%\run_invisible.vbs" & rem Esegue il file VBS senza mostrare la finestra della console
del "%temp%\run_invisible.vbs" & rem Rimuove il file VBS temporaneo dopo l'esecuzione
