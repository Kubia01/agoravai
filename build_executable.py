#!/usr/bin/env python3
"""
Script para construir executável do Sistema CRM Compressores
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def verificar_pyinstaller():
    """Verifica se PyInstaller está instalado"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} encontrado")
        return True
    except ImportError:
        print("❌ PyInstaller não encontrado")
        print("Instalando PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✅ PyInstaller instalado com sucesso")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar PyInstaller")
            return False

def limpar_build():
    """Remove arquivos de build anteriores"""
    print("🧹 Limpando builds anteriores...")
    dirs_para_remover = ['build', 'dist', '__pycache__']
    for dir_name in dirs_para_remover:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removido: {dir_name}/")
    
    # Remover arquivos .spec anteriores
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"   Removido: {spec_file}")

def criar_spec_file():
    """Cria arquivo .spec personalizado para o PyInstaller"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Definir dados a serem incluídos
added_files = [
    ('assets', 'assets'),
    ('interface', 'interface'),
    ('pdf_generators', 'pdf_generators'),
    ('utils', 'utils'),
    ('database.py', '.'),
    ('crm_compressores.db', '.'),
    ('logo.jpg', '.'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'sqlite3',
        'fpdf2',
        'PIL',
        'PIL.Image',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CRM_Compressores',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Manter console para debug
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Adicione caminho do ícone se tiver
)
'''
    
    with open('crm_compressores.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Arquivo crm_compressores.spec criado")

def construir_executavel():
    """Constrói o executável usando PyInstaller"""
    print("🔨 Construindo executável...")
    
    try:
        # Comando PyInstaller - sem --onefile pois já está no .spec
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "crm_compressores.spec"
        ]
        
        print(f"Executando: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Executável construído com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao construir executável: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def verificar_resultado():
    """Verifica se o executável foi criado corretamente"""
    exe_path = Path('dist/CRM_Compressores')
    if sys.platform == "win32":
        exe_path = Path('dist/CRM_Compressores.exe')
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ Executável criado: {exe_path}")
        print(f"   Tamanho: {size_mb:.1f} MB")
        
        # Criar pasta para distribuição
        dist_folder = Path('distribuicao')
        if dist_folder.exists():
            shutil.rmtree(dist_folder)
        
        dist_folder.mkdir()
        
        # Copiar executável
        shutil.copy2(exe_path, dist_folder)
        
        # Copiar arquivos importantes (opcionalmente)
        important_files = ['README.md', 'EXECUTAR.md']
        for file in important_files:
            if Path(file).exists():
                shutil.copy2(file, dist_folder)
        
        print(f"✅ Arquivos copiados para: {dist_folder}/")
        print("\n📦 EXECUTÁVEL PRONTO!")
        print(f"   Localização: {dist_folder}/")
        print(f"   Para executar: ./{dist_folder}/CRM_Compressores")
        
        return True
    else:
        print("❌ Executável não foi criado")
        return False

def main():
    """Função principal"""
    print("🚀 === CONSTRUTOR DE EXECUTÁVEL - CRM COMPRESSORES ===")
    print()
    
    # Verificar se estamos no diretório correto
    if not Path('main.py').exists():
        print("❌ Erro: main.py não encontrado")
        print("Execute este script no diretório raiz do projeto")
        return 1
    
    # Passo 1: Verificar PyInstaller
    if not verificar_pyinstaller():
        return 1
    
    # Passo 2: Limpar builds anteriores
    limpar_build()
    
    # Passo 3: Criar arquivo .spec
    criar_spec_file()
    
    # Passo 4: Construir executável
    if not construir_executavel():
        return 1
    
    # Passo 5: Verificar resultado
    if not verificar_resultado():
        return 1
    
    print("\n🎉 SUCESSO! Executável criado com sucesso!")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Teste o executável na pasta 'distribuicao/'")
    print("2. Copie a pasta 'distribuicao/' para outros computadores")
    print("3. No computador destino, apenas execute o arquivo")
    print("\n⚠️  OBSERVAÇÕES:")
    print("- O executável contém todas as dependências necessárias")
    print("- Não precisa instalar Python no computador destino")
    print("- O banco de dados será criado automaticamente")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)