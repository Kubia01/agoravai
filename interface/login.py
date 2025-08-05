import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import os

# Database configuration
DB_NAME = "crm_database.db"

class LoginWindow:
    def __init__(self, root=None):
        # Create root window if not provided
        if root is None:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide main window initially
        else:
            self.root = root
            
        # Create login window
        self.login_window = tk.Toplevel(self.root) if root else tk.Tk()
        self.setup_window()
        self.create_login_ui()
        self.center_window()
        self.setup_focus()
        
        # Initialize database if needed
        self.init_database()
        
    def setup_window(self):
        """Configure the login window"""
        self.login_window.title("🔐 Login - Sistema CRM Compressores")
        self.login_window.geometry("400x450")
        self.login_window.resizable(False, False)
        self.login_window.configure(bg='#f8fafc')
        
        # Window management
        if hasattr(self, 'root') and self.root != self.login_window:
            self.login_window.transient(self.root)
        
        # Forçar janela para aparecer na frente
        self.login_window.lift()
        self.login_window.attributes('-topmost', True)
        self.login_window.after_idle(lambda: self.login_window.attributes('-topmost', False))
        
        # Focar na janela
        self.login_window.focus_force()
            
        # Handle window closing
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def center_window(self):
        """Center the window on screen"""
        self.login_window.update_idletasks()
        
        width = 400
        height = 400
        screen_width = self.login_window.winfo_screenwidth()
        screen_height = self.login_window.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.login_window.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_focus(self):
        """Setup window focus and grab"""
        self.login_window.lift()
        self.login_window.attributes('-topmost', True)
        self.login_window.after(100, lambda: self.login_window.attributes('-topmost', False))
        self.login_window.focus_force()
        self.login_window.grab_set()
        
        # Focus on username field after a short delay
        self.login_window.after(200, lambda: self.username_entry.focus())
        
    def create_login_ui(self):
        """Create the login interface"""
        # Main container
        main_frame = tk.Frame(self.login_window, bg='#f8fafc')
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Sistema CRM\nCompressores", 
            font=('Arial', 18, 'bold'),
            bg='#f8fafc',
            fg='#1e293b',
            justify='center'
        )
        title_label.pack(pady=(0, 30))
        
        # Fields frame
        fields_frame = tk.Frame(main_frame, bg='#f8fafc')
        fields_frame.pack(fill="x", pady=(0, 20))
        
        # Username field
        tk.Label(
            fields_frame, 
            text="Usuário:", 
            font=('Arial', 10, 'bold'),
            bg='#f8fafc',
            fg='#374151'
        ).pack(anchor="w", pady=(0, 5))
        
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(
            fields_frame, 
            textvariable=self.username_var,
            font=('Arial', 11),
            relief='solid',
            bd=1
        )
        self.username_entry.pack(fill="x", ipady=8, pady=(0, 15))
        
        # Password field
        tk.Label(
            fields_frame, 
            text="Senha:", 
            font=('Arial', 10, 'bold'),
            bg='#f8fafc',
            fg='#374151'
        ).pack(anchor="w", pady=(0, 5))
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            fields_frame, 
            textvariable=self.password_var,
            font=('Arial', 11),
            relief='solid',
            bd=1,
            show="*"
        )
        self.password_entry.pack(fill="x", ipady=8)
        
        # Login button
        login_btn = tk.Button(
            main_frame, 
            text="Entrar",
            font=('Arial', 11, 'bold'),
            bg='#3b82f6',
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self.login
        )
        login_btn.pack(fill="x", ipady=10, pady=(20, 0))
        
        # Bind Enter key
        self.login_window.bind('<Return>', lambda e: self.login())
        
        # Test login section
        test_frame = tk.Frame(main_frame, bg='#f8fafc')
        test_frame.pack(fill="x", pady=(20, 0))
        
        tk.Label(
            test_frame, 
            text="Login padrão: admin / admin123",
            font=('Arial', 9),
            bg='#f8fafc',
            fg='#6b7280'
        ).pack()
        
        test_btn = tk.Button(
            test_frame, 
            text="Preencher Login Teste",
            font=('Arial', 9),
            bg='#e5e7eb',
            fg='#374151',
            command=self.fill_test_login
        )
        test_btn.pack(pady=(10, 0))
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="",
            font=('Arial', 9),
            bg='#f8fafc',
            fg='#ef4444'
        )
        self.status_label.pack(pady=(10, 0))
        
    def fill_test_login(self):
        """Fill fields with test credentials"""
        self.username_var.set("admin")
        self.password_var.set("admin123")
        
    def init_database(self):
        """Initialize database with default user if needed"""
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            
            # Create users table if it doesn't exist
            c.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    nome_completo TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Check if admin user exists
            c.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
            if c.fetchone()[0] == 0:
                # Create default admin user
                admin_password = hashlib.sha256("admin123".encode()).hexdigest()
                c.execute('''
                    INSERT INTO usuarios (username, password, role, nome_completo)
                    VALUES (?, ?, ?, ?)
                ''', ("admin", admin_password, "admin", "Administrador"))
                
                print("Default admin user created: admin/admin123")
            
            conn.commit()
            self.status_label.config(text="Database initialized successfully", fg='#10b981')
            
        except sqlite3.Error as e:
            self.status_label.config(text=f"Database error: {e}", fg='#ef4444')
            print(f"Database error: {e}")
        finally:
            conn.close()
            
    def login(self):
        """Handle login attempt"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
            
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            c.execute(
                "SELECT id, role, nome_completo FROM usuarios WHERE username=? AND password=?", 
                (username, password_hash)
            )
            user = c.fetchone()
            
            if user:
                user_id, role, nome_completo = user
                messagebox.showinfo("Sucesso", f"Login realizado com sucesso!\nBem-vindo, {nome_completo}")
                
                # Try to open main window first
                try:
                    self.open_main_window(user_id, role, nome_completo)
                    # Only close login window if main window opened successfully
                    self.login_window.destroy()
                except Exception as e:
                    # If main window fails, update status instead of closing
                    if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                        self.status_label.config(text="❌ Erro no sistema principal", fg='#ef4444')
                    print(f"Failed to open main window: {e}")
                    # Don't destroy the login window, let user try again
                
            else:
                messagebox.showerror("Erro", "Usuário ou senha incorretos!")
                self.password_var.set("")
                if hasattr(self, 'password_entry') and self.password_entry.winfo_exists():
                    self.password_entry.focus()
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro no banco de dados: {e}")
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.config(text="❌ Erro no banco de dados", fg='#ef4444')
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.config(text="❌ Erro inesperado", fg='#ef4444')
        finally:
            if 'conn' in locals():
                conn.close()
            
    def open_main_window(self, user_id, role, nome_completo):
        """Open the main application window"""
        try:
            # Try to import and open main window
            from interface.main_window import MainWindow
            MainWindow(self.root, user_id, role, nome_completo)
        except ImportError as e:
            # If main window doesn't exist, show a placeholder
            print(f"ImportError: {e}")
            messagebox.showinfo("Info", f"Login successful!\nUser: {nome_completo}\nRole: {role}")
            print(f"Main window would open here for user {nome_completo} with role {role}")
        except IndentationError as e:
            # Handle indentation errors in imported modules
            print(f"IndentationError: {e}")
            messagebox.showerror("Erro de Código", 
                f"Erro de indentação no código:\n{str(e)}\n\n"
                "Verifique o arquivo indicado no erro.")
        except SyntaxError as e:
            # Handle syntax errors in imported modules
            print(f"SyntaxError: {e}")
            messagebox.showerror("Erro de Sintaxe", 
                f"Erro de sintaxe no código:\n{str(e)}\n\n"
                "Verifique o arquivo indicado no erro.")
        except Exception as e:
            # Handle any other errors
            print(f"Exception: {e}")
            messagebox.showerror("Erro", 
                f"Erro ao abrir sistema principal:\n{str(e)}\n\n"
                "Verifique os logs para mais detalhes.")
            
    def on_closing(self):
        """Handle window closing"""
        if hasattr(self, 'root') and self.root != self.login_window:
            self.root.quit()
        else:
            self.login_window.quit()
            
    def run(self):
        """Start the login window"""
        self.login_window.mainloop()

# Test the login window
if __name__ == "__main__":
    print("Starting CRM Login System...")
    login = LoginWindow()
    login.run()