PYINST =pyinstaller

BOT_NAME =McStatusBot

FILE_NAME =--name $(BOT_NAME)
#CONFIGS =--add-data $(BOT_NAME).toml:$(BOT_NAME)
#FILE_ICON =--icon res\images\$(BOT_NAME).ico
PYINST_FLAGS =--onefile --debug all --console --distpath ./ --paths=.venv\Lib\site-packages $(FILE_NAME) $(FILE_VERSION) $(CONFIGS) $(FILE_ICON)

.PHONY = clean_all
FILES = src/main.py src/lib/GetSettings.py src/lib/LatestLogParser.py
SEPARATOR = ------------------------------------------------------------------------------------------

MAIN_FILE =./src/main.py
TOML_CONFIG_FILE =../McStatusBot.toml

test: # C:\msys64\ucrt64\bin\mingw32-make.exe test
	@cls
	@echo Activating Python Virtual-Environment and running "$(MAIN_FILE)"...
	@.venv\Scripts\activate
	@python -Wdefault $(MAIN_FILE) --config-toml $(TOML_CONFIG_FILE)

clean_all: # C:\msys64\ucrt64\bin\mingw32-make.exe clean_all
	-powershell Remove-Item -r "*.exe" -ErrorAction SilentlyContinue
	-powershell Remove-Item -r "*.spec" -ErrorAction SilentlyContinue
	-powershell Remove-Item -r "build/*" -ErrorAction SilentlyContinue
	-powershell Remove-Item -r "src/lib/__pycache__" -ErrorAction SilentlyContinue
	-powershell Remove-Item -r "*.pytest_cache" -ErrorAction SilentlyContinue
	-powershell Remove-Item -r "logs/*" -ErrorAction SilentlyContinue
	@echo $(SEPARATOR)
	@echo Removed all the generated files and logs
	@echo $(SEPARATOR)

build_clean:
	.venv\Scripts\activate
	$(PYINST) $(FILES) $(PYINST_FLAGS) --clean
	-powershell Remove-Item -r "*.spec" -ErrorAction SilentlyContinue
	@echo $(SEPARATOR)
	@echo Successfully generated the binary
	@echo $(SEPARATOR)

build:
	$(PYINST) $(FILES) $(PYINST_FLAGS)
	@echo $(SEPARATOR)
	@echo Successfully generated the binary
	@echo $(SEPARATOR)
	