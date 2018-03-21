# -*- mode: python -*-

block_cipher = None


a = Analysis(['run_app.py'],
             pathex=['C:\\Users\\lukas\\projekty\\feel the streets', r'c:\python3\lib\site-packages\pygeodesy'],
             binaries=[],
             datas=[("app/sounds", "sounds"), ("app/ui.xrc", "."), ("locale", "locale")],
             hiddenimports=["faker.providers"],
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
          name='run_app',
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
