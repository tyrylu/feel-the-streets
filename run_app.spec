# -*- mode: python -*-
from openal.al_lib import lib
import platform
from ctypes.util import find_library


block_cipher = None
spatialite_lib = find_library("mod_spatialite")
# Assume that the library under Linux is a system-wide installed one residing in the system-wide library directory
if platform.system() == "Linux" and platform.architecture()[0] == "64bit":
    openal_library_path = f"/usr/lib64/{lib._name}"
    spatialite_library_path = f"/usr/lib64/{spatialite_lib}"
elif platform.system() == "Windows":
    openal_library_path = lib._name
    spatialite_library_path = spatialite_lib

a = Analysis(['run_app.py'],
             pathex=['C:\\Users\\lukas\\projekty\\feel the streets', r'c:\python3\lib\site-packages\pygeodesy'],
             binaries=[(openal_library_path, "."), (spatialite_library_path, ".")],
             datas=[("app/sounds", "sounds"), ("locale", "locale"), ("*.yml", ".")],
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
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='fts')
