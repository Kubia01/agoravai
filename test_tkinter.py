#!/usr/bin/env python3

import tkinter as tk
import sys

print("=== Teste do Tkinter ===")
print(f"Python version: {sys.version}")

try:
    print("Tentando importar tkinter...")
    import tkinter as tk
    print("✅ Tkinter importado com sucesso!")
    
    print("Criando janela de teste...")
    root = tk.Tk()
    root.title("Teste Tkinter - CRM")
    root.geometry("400x200")
    
    # Centralizar na tela
    root.eval('tk::PlaceWindow . center')
    
    label = tk.Label(root, text="Tkinter está funcionando!", font=('Arial', 14))
    label.pack(pady=50)
    
    button = tk.Button(root, text="Fechar", command=root.quit)
    button.pack(pady=10)
    
    print("✅ Janela criada! Mostrando...")
    root.mainloop()
    print("Janela fechada.")
    
except Exception as e:
    print(f"❌ Erro ao usar tkinter: {e}")
    import traceback
    traceback.print_exc()