PYINST = pyinstaller

FILE_NAME =--name Parrot_BOT
FILE_SETTINGS =--add-data Parrot_BOT_settings.txt:Parrot_BOT
FILE_ICON =--icon src/resources/images/parrot-trapping-wasabi.ico
FLAGS =--onefile --debug all --console --distpath ./ $(FILE_NAME) $(FILE_VERSION) $(FILE_SETTINGS) $(FILE_ICON)

FILES = src/main.py src/GetValues.py src/resources/ConsoleMessagesHandling.py src/resources/IpAddressGrabber.py src/resources/LatestLogParser.py
SEPARATOR = ------------------------------------------------------------------------------------------
.PHONY = clean_all build_clean

clean_all: # C:\msys64\ucrt64\bin\mingw32-make.exe clean_all
	-powershell Remove-Item -r "*.exe" -ErrorAction SilentlyContinue
	-powershell Remove-Item -r "*.spec" -ErrorAction SilentlyContinue
	-powershell Remove-Item -r "build/*" -ErrorAction SilentlyContinue
	-powershell Remove-Item -r "__pycache__" -ErrorAction SilentlyContinue
	-powershell Remove-Item -r ".pytest_cache" -ErrorAction SilentlyContinue
	@echo $(SEPARATOR)
	@echo Removed all the generated files
	@echo $(SEPARATOR)

build_clean:
	$(PYINST) $(FILES) $(FLAGS) --clean
	powershell Remove-Item -r "*.spec"
	@echo $(SEPARATOR)
	@echo Cleaned the cache
	@echo $(SEPARATOR)

build:
	$(PYINST) $(FILES) $(FLAGS)
	@echo $(SEPARATOR)
	@echo Successfully created the executable file
	@echo $(SEPARATOR)
	