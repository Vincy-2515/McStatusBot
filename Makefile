PYINST = pyinstaller

FILE_NAME =--name Reforged_BOT
CONFIGS =--add-data Reforged_BOT.toml:Reforged_BOT
FILE_ICON =--icon src\resources\images\Reforged.ico
FLAGS =--onefile --debug all --console --distpath ./ --paths=.venv\Lib\site-packages $(FILE_NAME) $(FILE_VERSION) $(CONFIGS) $(FILE_ICON)

FILES = src/main.py src/GetSettings.py src/resources/ConsoleMessagesHandling.py src/resources/LatestLogParser.py
SEPARATOR = ------------------------------------------------------------------------------------------
.PHONY = clean_all

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
	.venv\Scripts\activate
	$(PYINST) $(FILES) $(FLAGS) --clean
	powershell Remove-Item -r "*.spec"
	@echo $(SEPARATOR)
	@echo Successfully created the executable
	@echo $(SEPARATOR)

build:
	$(PYINST) $(FILES) $(FLAGS)
	@echo $(SEPARATOR)
	@echo Successfully created the executable file
	@echo $(SEPARATOR)
	