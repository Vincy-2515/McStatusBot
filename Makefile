PYINST = pyinstaller

FILE_NAME =--name Parrot_BOT
FILE_SETTINGS =--add-data Parrot_BOT_settings.txt:Parrot_BOT
FILE_ICON =--icon src/resources/images/parrot-trapping-wasabi.ico
FLAGS =--onefile --debug all --console --distpath ./ $(FILE_NAME) $(FILE_VERSION) $(FILE_SETTINGS) $(FILE_ICON)

FILES = main.py GetValues.py src/ConsoleMessagesHandling.py src/IpAddressGrabber.py src/LatestLogParser.py
SEPARATOR = ------------------------------------------------------------------------------------------
.PHONY = clean_all build_clean

clean_all: # C:\msys64\ucrt64\bin\mingw32-make.exe clean_all
	powershell Remove-Item -r "*.exe" -Erroraction silentlycontinue
	powershell Remove-Item -r "*.spec" -Erroraction silentlycontinue
	powershell Remove-Item -r "dist/*" -Erroraction silentlycontinue
	powershell Remove-Item -r "build/*" -Erroraction silentlycontinue
	powershell Remove-Item -r "__pycache__" -Erroraction silentlycontinue
	powershell Remove-Item -r ".pytest_cache" -Erroraction silentlycontinue
	@echo Removed all the generated files
	$(SEPARATOR)

build_clean:
	$(PYINST) $(FILES) $(FLAGS) --clean
	powershell Remove-Item -r "*.spec"
	@echo Cleaned the cache
	$(SEPARATOR)

build:
	$(PYINST) $(FILES) $(FLAGS)
	@echo Successfully created the executable file
	$(SEPARATOR)
	