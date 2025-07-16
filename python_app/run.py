#!/usr/bin/env python3
"""
Script para executar o Sistema CRM de Compressores
"""

import sys
import subprocess
import os

def install_requirements():
    """Instala as dependências necessárias"""
    try:
        print("Instalando dependências...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar dependências: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 50)
    print("Sistema CRM de Compressores")
    print("=" * 50)
    
    # Verificar se está no diretório correto
    if not os.path.exists("requirements.txt"):
        print("Erro: Execute este script do diretório python_app/")
        sys.exit(1)
    
    # Instalar dependências
    if not install_requirements():
        print("Falha na instalação das dependências. Abortando...")
        sys.exit(1)
    
    # Executar o sistema
    try:
        print("\nIniciando o sistema...")
        from main import main as run_main
        run_main()
    except ImportError as e:
        print(f"Erro ao importar módulos: {e}")
        print("Certifique-se de que todos os arquivos estão no local correto.")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()