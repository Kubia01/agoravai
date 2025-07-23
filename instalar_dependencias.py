#!/usr/bin/env python3
"""
Script para instalar dependências necessárias para o Sistema CRM
"""

import subprocess
import sys
import os

def instalar_pacote(pacote):
    """Instalar um pacote usando pip"""
    try:
        print(f"📦 Instalando {pacote}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])
        print(f"✅ {pacote} instalado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar {pacote}: {e}")
        return False

def verificar_pacote(pacote):
    """Verificar se um pacote está instalado"""
    try:
        __import__(pacote)
        return True
    except ImportError:
        return False

def main():
    print("=== Instalador de Dependências - Sistema CRM ===\n")
    
    # Lista de dependências essenciais
    dependencias = [
        ("reportlab", "reportlab"),
        ("Pillow", "PIL"),
    ]
    
    # Dependências opcionais mas recomendadas
    opcionais = [
        ("requests", "requests"),
    ]
    
    print("🔍 Verificando dependências essenciais...")
    
    for nome_pip, nome_import in dependencias:
        if verificar_pacote(nome_import):
            print(f"✅ {nome_pip} já está instalado")
        else:
            print(f"❌ {nome_pip} não encontrado")
            if instalar_pacote(nome_pip):
                print(f"✅ {nome_pip} instalado com sucesso!")
            else:
                print(f"❌ Falha ao instalar {nome_pip}")
    
    print("\n🔍 Verificando dependências opcionais...")
    
    for nome_pip, nome_import in opcionais:
        if verificar_pacote(nome_import):
            print(f"✅ {nome_pip} já está instalado")
        else:
            print(f"⚠️ {nome_pip} não encontrado (opcional)")
            resposta = input(f"Deseja instalar {nome_pip}? (s/n): ").lower()
            if resposta in ['s', 'sim', 'y', 'yes']:
                instalar_pacote(nome_pip)
    
    print("\n=== Verificação Final ===")
    
    # Testar imports principais
    try:
        from reportlab.lib.pagesizes import A4
        print("✅ ReportLab: OK - Geração de PDF disponível")
    except ImportError:
        print("❌ ReportLab: FALHOU - Geração de PDF limitada")
    
    try:
        from PIL import Image
        print("✅ Pillow: OK - Processamento de imagens disponível")
    except ImportError:
        print("❌ Pillow: FALHOU - Preview de imagens limitado")
    
    print("\n" + "="*50)
    print("🚀 Instalação concluída!")
    print("Agora você pode executar: python main.py")
    print("="*50)

if __name__ == "__main__":
    main()