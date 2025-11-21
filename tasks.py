import os, shutil
from invoke.tasks import task  # type: ignore
from invoke.context import Context

SEPARATOR = "------------------------------------------------------------------------------------------"

PYINST = "pyinstaller"
PYINST_FLAGS = "\
 --name=McStatusBot\
 --onefile\
 --console\
 --specpath=.\\dist\
 --log-level=INFO\
 --hidden-import=discord"

FILES = ".\\src\\main.py"
MAIN_FILE = ".\\src\\main.py"
BATCH_FILE = ".\\testing_resources\\minecraft_run.bat"
TOML_CONFIG_FILE = ".\\testing_resources\\McStatusBot.toml"


@task(help={"clean": "Same as 'cleanAll' task, performed before the build"})  # type: ignore
def build(c: Context, clean: bool = False):
    """Builds the project."""

    os.system("cls")

    command = f"{PYINST} {FILES} {PYINST_FLAGS}"

    if clean:
        __cleanAll(c)
        command += " --clean"

    result = c.run(command, echo=True)

    if result is None:
        return

    if result.ok:
        __printMessageWithSeparator("Successfully builded the binary")
    else:
        __printMessageWithSeparator(f"Build failed (return-code: {result.return_code}):")
        print(result.stderr)


@task(help={"binary": f"Executes the binary instead of the code. Binary executed trough the '{BATCH_FILE}'"})  # type: ignore
def run(c: Context, binary: bool = False):
    """Simply runs the code."""

    os.system("cls")

    if binary:
        c.run(BATCH_FILE, echo=True)
    else:
        c.run(".venv\\Scripts\\activate", echo=True)
        c.run(f"python -Wdefault {MAIN_FILE} --config-toml={TOML_CONFIG_FILE}", echo=True)


@task
def clean(c: Context):
    """Deletes '*.pytest_cache' and every '__pycache__' folder inside this workspace."""

    os.system("cls")

    __clean(c)


@task
def cleanAll(c: Context):
    """Deletes '*.pytest_cache', 'build\\*', 'dist\\*', 'logs\\*' and every '__pycache__' folder inside this workspace."""

    os.system("cls")

    __cleanAll(c)


## other functions ####################################################################################################


def __clean(c: Context):
    c.run("powershell Remove-Item -r '*.pytest_cache'", echo=True)
    __removePycacheFolders(".\\")

    __printMessageWithSeparator("Cleaned cache")


def __cleanAll(c: Context):
    c.run("powershell Remove-Item -r '*.pytest_cache'", echo=True)
    c.run("powershell Remove-Item -r 'logs\\*'", echo=True)
    c.run("powershell Remove-Item -r 'build\\*'", echo=True)
    c.run("powershell Remove-Item -r 'dist\\*'", echo=True)
    __removePycacheFolders(".\\")

    __printMessageWithSeparator("Cleaned all the generated files and the cache")


def __removePycacheFolders(directory: str):
    for root, dirs, _ in os.walk(directory):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            shutil.rmtree(pycache_path)
            print(f"Removed: {pycache_path}")


def __printMessageWithSeparator(msg: str):
    print(SEPARATOR)
    print(msg)
    print(SEPARATOR)
