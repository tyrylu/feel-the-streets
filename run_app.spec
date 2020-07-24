# -*- mode: python -*-
import os
from openal.al_lib import lib
import platform
from ctypes.util import find_library
import PyInstaller.depend.bindepend as bd



block_cipher = None

# Assumes that the libraries under Linux are a system-wide installed ones residing in the system-wide library directory
if platform.system() == "Linux" and platform.architecture()[0] == "64bit":
    additional_libs = (f"/usr/lib64/{lib._name}", "/usr/lib64/mod_spatialite.so")
elif platform.system() == "Windows":
    additional_libs = (lib._name, find_library("mod_spatialite"), find_library("libvorbisfile"))

toc = [(os.path.basename(name), name, "BINARY") for name in additional_libs]
toc_with_deps = bd.Dependencies(toc)
print(f"Toc with deps: {toc_with_deps}")
binaries = [(path, ".") for local_name, path, typ in toc_with_deps]

a = Analysis(['run_app.py'],
             pathex=['C:\\Users\\lukas\\projekty\\feel the streets', r'c:\python3\lib\site-packages\pygeodesy'],
             binaries=binaries,
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
