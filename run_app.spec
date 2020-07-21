# -*- mode: python -*-
from openal.al_lib import lib

block_cipher = None


a = Analysis(['run_app.py'],
             pathex=['C:\\Users\\lukas\\projekty\\feel the streets', r'c:\python3\lib\site-packages\pygeodesy'],
             binaries=[],
             datas=[("app/sounds", "sounds"), ("locale", "locale"), ("*.yml", "."), (lib._name, ".")],
             hiddenimports=["pkg_resources.py2_warn"],
             hookspath=["hooks"],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='fts',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='fts')
