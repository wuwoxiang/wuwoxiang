# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['2400166f0a8fb0a449290d4f3e15e1e49cb57ccaf41f8a7072b014cfe993dc429cb57ccaf41f8a7', 'run.py'],
             pathex=['D:\\Goods'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='2400166f0a8fb0a449290d4f3e15e1e49cb57ccaf41f8a7072b014cfe993dc429cb57ccaf41f8a7',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
