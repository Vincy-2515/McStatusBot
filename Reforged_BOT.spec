# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\main.py', 'src\\GetSettings.py', 'src\\resources\\ConsoleMessagesHandling.py', 'src\\resources\\LatestLogParser.py'],
    pathex=[],
    binaries=[],
    datas=[('Reforged_BOT.toml', 'Reforged_BOT')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=True,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('v', None, 'OPTION')],
    name='Reforged_BOT',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['src\\resources\\images\\Reforged.ico'],
)
