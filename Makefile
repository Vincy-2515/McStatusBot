PYINST =pyinstaller

BOT_NAME =McStatusBot

FILE_NAME =--name $(BOT_NAME)
#CONFIGS =--add-data $(BOT_NAME).toml:$(BOT_NAME)
#FILE_ICON =--icon res\images\$(BOT_NAME).ico
FLAGS =--onefile --debug all --console --distpath ./ --paths=.venv\Lib\site-packages $(FILE_NAME) $(FILE_VERSION) $(CONFIGS) $(FILE_ICON)

FILES = src/main.py src/lib/GetSettings.py src/lib/ConsoleMessagesHandling.py src/lib/LatestLogParser.py
SEPARATOR = ------------------------------------------------------------------------------------------
.PHONY = clean_all

test: # C:\msys64\ucrt64\bin\mingw32-make.exe test
	.venv\Scripts\activate
	python -Wdefault ./src/main.py --config-toml ../McStatusBot.toml

clean_all: # C:\msys64\ucrt64\bin\mingw32-make.exe clean_all
	-powershell Remove-Item -r "*.exe" -ErrorAction SilentlyContinue
	-powershell Remove-Item -r "*.spec" -ErrorAction SilentlyContinue
	-powershell Remove-Item -r "build/*" -ErrorAction SilentlyContinue
	-powershell Remove-Item -r "src/lib/__pycache__" -ErrorAction SilentlyContinue
	-powershell Remove-Item -r "*.pytest_cache" -ErrorAction SilentlyContinue
	@echo $(SEPARATOR)
	@echo Removed all the generated files
	@echo $(SEPARATOR)

build_clean:
	.venv\Scripts\activate
	$(PYINST) $(FILES) $(FLAGS) --clean
	-powershell Remove-Item -r "*.spec" -ErrorAction SilentlyContinue
	@echo $(SEPARATOR)
	@echo Successfully created the executable
	@echo $(SEPARATOR)

build:
	$(PYINST) $(FILES) $(FLAGS)
	@echo $(SEPARATOR)
	@echo Successfully created the executable file
	@echo $(SEPARATOR)
	