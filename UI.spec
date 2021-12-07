# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['UI.py'],
             pathex=[],
             binaries=[],
             hiddenimports=['plotly', 'PyQt5.QtWebEngine', 'PyQt5.QtWebEngineWidgets', 'PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.QtGui', 'plotly.graph_objects', 'tkinter', 'pandas', 'sklearn.manifold', 'xlwings', 'math', 'numbers', 'datetime', 'numpy'],
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
          name='UI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='app-icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='UI')
