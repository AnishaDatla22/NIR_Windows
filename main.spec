# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['C:/Users/Elico/Desktop/NIRO-windows_ver/app/main.py'],
             pathex=[],
             binaries=[('C:/Users/Elico/Desktop/NIRO-windows_ver/app/Sensor/src/libdlpspec.dll', '.')],
             datas=[('C:/Users/Elico/Desktop/NIRO-windows_ver/app/Data', 'Data/'), ('C:/Users/Elico/Desktop/NIRO-windows_ver/app/main.py', '.')],
             hiddenimports=['sklearn.utils._typedefs', 'uvicorn.lifespan.off', 'uvicorn.lifespan.on', 'uvicorn.lifespan', 'uvicorn.protocols.websockets.auto', 'uvicorn.protocols.websockets.wsproto_impl', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.http.h11_impl', 'uvicorn.protocols.http.httptools_impl', 'uvicorn.protocols.websockets', 'uvicorn.protocols.http', 'uvicorn.protocols', 'uvicorn.loops.auto', 'uvicorn.loops.asyncio', 'uvicorn.loops.uvloop', 'uvicorn.loops', 'uvicorn.logging'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , embed_manifest=False)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
