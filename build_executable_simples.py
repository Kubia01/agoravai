#!/usr/bin/env python3
"""
Script SIMPLIFICADO para construir executável do Sistema CRM Compressores
Versão sem arquivo .spec - mais compatível
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
            print("Tente manualmente: pip install pyinstaller")
            return False

def limpar_build():
    """Remove arquivos de build anteriores"""
    print("🧹 Limpando builds anteriores...")
    dirs_para_remover = ['build', 'dist']
    for dir_name in dirs_para_remover:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removido: {dir_name}/")

def construir_executavel():
    """Constrói o executável usando PyInstaller sem arquivo .spec"""
    print("🔨 Construindo executável (método simplificado)...")
    
    try:
        # Comando PyInstaller simplificado
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--name", "CRM_Compressores",
            "--add-data", "assets;assets",
            "--add-data", "interface;interface", 
            "--add-data", "pdf_generators;pdf_generators",
            "--add-data", "utils;utils",
            "--add-data", "database.py;.",
            "--add-data", "crm_compressores.db;.",
            "--add-data", "logo.jpg;.",
            "--hidden-import", "tkinter",
            "--hidden-import", "tkinter.ttk",
            "--hidden-import", "tkinter.messagebox",
            "--hidden-import", "tkinter.filedialog",
            "--hidden-import", "sqlite3",
            "--hidden-import", "fpdf2",
            "--hidden-import", "PIL",
            "--hidden-import", "PIL.Image",
            "--hidden-import", "requests",
            "--console",  # Manter console para debug
            "main.py"
        ]
        
        # No Windows, usar ; como separador, no Linux usar :
        if sys.platform == "win32":
            # Comandos já estão com ; para Windows
            pass
        else:
            # Substituir ; por : no Linux
            for i, arg in enumerate(cmd):
                if "--add-data" in arg:
                    continue
                if ";" in arg and "--add-data" in cmd[i-1]:
                    cmd[i] = arg.replace(";", ":")
        
        print(f"Executando PyInstaller...")
        print(f"Comando: {' '.join(cmd[:5])} ... (+ {len(cmd)-5} argumentos)")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Executável construído com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao construir executável: {e}")
        print("\n📋 STDOUT:")
        print(e.stdout)
        print("\n📋 STDERR:")
        print(e.stderr)
        print("\n💡 DICAS:")
        print("1. Verifique se todos os arquivos existem")
        print("2. Tente fechar antivírus temporariamente")
        print("3. Execute como administrador (Windows)")
        return False

def verificar_resultado():
    """Verifica se o executável foi criado corretamente"""
    exe_name = "CRM_Compressores.exe" if sys.platform == "win32" else "CRM_Compressores"
    exe_path = Path(f'dist/{exe_name}')
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ Executável criado: {exe_path}")
        print(f"   Tamanho: {size_mb:.1f} MB")
        
        # Criar pasta para distribuição
        dist_folder = Path('CRM_Executavel')
        if dist_folder.exists():
            shutil.rmtree(dist_folder)
        
        dist_folder.mkdir()
        
        # Copiar executável
        shutil.copy2(exe_path, dist_folder)
        
        # Copiar documentação importante
        docs_importantes = ['README.md', 'EXECUTAR.md']
        for doc in docs_importantes:
            if Path(doc).exists():
                shutil.copy2(doc, dist_folder)
        
        print(f"✅ Arquivos organizados em: {dist_folder}/")
        print(f"📦 EXECUTÁVEL PRONTO!")
        print(f"   Pasta: {dist_folder}/")
        print(f"   Executável: {exe_name}")
        
        return True
    else:
        print("❌ Executável não foi criado")
        print(f"   Esperado: {exe_path}")
        return False

def main():
    """Função principal"""
    print("🚀 === CONSTRUTOR SIMPLIFICADO - CRM COMPRESSORES ===")
    print("Versão sem arquivo .spec - mais compatível")
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
    
    # Passo 3: Construir executável
    if not construir_executavel():
        return 1
    
    # Passo 4: Verificar resultado
    if not verificar_resultado():
        return 1
    
    print("\n🎉 SUCESSO! Executável criado com sucesso!")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Teste o executável na pasta 'CRM_Executavel/'")
    print("2. Copie a pasta para outros computadores")
    print("3. Execute o arquivo diretamente (não precisa Python)")
    print("\n⚠️  OBSERVAÇÕES:")
    print("- Testado com Python 3.13.x")
    print("- Compatível com Windows e Linux")
    print("- Inclui todas as dependências")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    input("\nPressione Enter para fechar...")  # Manter janela aberta
    sys.exit(exit_code)