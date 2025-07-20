import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
import os
import shutil
import hashlib

DB_PATH = "inventario.db"

# ========== BASE DE DATOS ==========
def conectar_db():
    return sqlite3.connect(DB_PATH)

def crear_tablas():
    conn = conectar_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            categoria TEXT,
            iva REAL DEFAULT 21.0,
            fecha_agregado TEXT NOT NULL,
            fecha_vencimiento TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nombre_completo TEXT NOT NULL,
            correo TEXT
        )
    ''')
    conn.commit()
    conn.close()

def crear_usuarios_por_defecto():
    conn = conectar_db()
    c = conn.cursor()
    usuarios_defecto = [
        ("Esteban", "pepe12A", "Esteban García", "esteban@mail.com"),
        ("Belen", "admin123", "Belén Rodríguez", "belen@mail.com"),
        ("Marcela", "pass456", "Marcela López", "marcela@mail.com"),
        ("Pola", "secret789", "Pola Martínez", "pola@mail.com")
    ]
    for username, password, nombre, correo in usuarios_defecto:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            c.execute("INSERT INTO usuarios (username, password, nombre_completo, correo) VALUES (?, ?, ?, ?)",
                      (username, password_hash, nombre, correo))
        except sqlite3.IntegrityError:
            continue
    conn.commit()
    conn.close()

def crear_productos_por_defecto():
    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM productos")
    if c.fetchone()[0] > 0:
        conn.close()
        return
    productos_defecto = [
        ("Laptop HP", "Laptop HP Pavilion 15.6 pulgadas", 5, 850000.00, "Electrónicos", 21.0, "2024-01-15", "2026-01-15"),
        ("Mouse Logitech", "Mouse inalámbrico Logitech MX Master", 25, 45000.00, "Accesorios", 21.0, "2024-02-01", "2026-02-01"),
        ("Teclado Mecánico", "Teclado mecánico RGB Corsair K70", 15, 120000.00, "Accesorios", 21.0, "2024-01-20", "2026-01-20"),
        ("Monitor Samsung", "Monitor Samsung 24 pulgadas Full HD", 8, 320000.00, "Electrónicos", 21.0, "2024-01-10", "2026-01-10"),
        ("Impresora Canon", "Impresora multifunción Canon Pixma", 12, 180000.00, "Oficina", 21.0, "2024-02-05", "2026-02-05"),
        ("Disco Duro SSD", "SSD Samsung 1TB", 30, 95000.00, "Almacenamiento", 21.0, "2024-01-25", "2026-01-25"),
        ("Webcam Logitech", "Webcam HD Logitech C920", 20, 75000.00, "Accesorios", 21.0, "2024-02-10", "2026-02-10"),
        ("Auriculares Sony", "Auriculares inalámbricos Sony WH-1000XM4", 10, 380000.00, "Audio", 21.0, "2024-01-30", "2026-01-30"),
        ("Tablet Samsung", "Tablet Samsung Galaxy Tab A8", 7, 280000.00, "Electrónicos", 21.0, "2024-02-15", "2026-02-15"),
        ("Cargador Universal", "Cargador USB-C 65W", 50, 25000.00, "Accesorios", 21.0, "2024-02-20", "2026-02-20")
    ]
    for producto in productos_defecto:
        c.execute("INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria, iva, fecha_agregado, fecha_vencimiento) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  producto)
    conn.commit()
    conn.close()

# Inicializar base de datos
crear_tablas()
crear_usuarios_por_defecto()
crear_productos_por_defecto()

# ========== USUARIOS ==========
def verificar_usuario(username, password):
    conn = conectar_db()
    c = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT nombre_completo FROM usuarios WHERE username=? AND password=?", (username, password_hash))
    resultado = c.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def registrar_usuario_nuevo():
    def guardar():
        username = entry_username.get().strip()
        password = entry_password.get().strip()
        nombre = entry_nombre.get().strip()
        correo = entry_correo.get().strip()
        
        if not username or not password or not nombre:
            messagebox.showwarning("Atención", "Completa todos los campos obligatorios")
            return
            
        if len(password) < 6:
            messagebox.showwarning("Atención", "La contraseña debe tener al menos 6 caracteres")
            return
            
        conn = conectar_db()
        c = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            c.execute("INSERT INTO usuarios (username, password, nombre_completo, correo) VALUES (?, ?, ?, ?)",
                      (username, password_hash, nombre, correo))
            conn.commit()
            messagebox.showinfo("Registro", "Usuario registrado correctamente")
            ventana.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ese usuario ya existe")
        finally:
            conn.close()
    
    ventana = tk.Toplevel()
    ventana.title("Registrar Usuario")
    ventana.geometry("400x350")
    ventana.configure(bg="#2C3E50")
    ventana.resizable(False, False)
    
    tk.Label(ventana, text="📝 Registrar Nuevo Usuario", font=("Helvetica", 14, "bold"),
             bg="#2C3E50", fg="#ECF0F1").pack(pady=20)
    
    frame = tk.Frame(ventana, bg="#34495E", relief="raised", bd=2)
    frame.pack(padx=30, pady=20, fill="both", expand=True)
    
    tk.Label(frame, text="Usuario*", bg="#34495E", fg="#ECF0F1").pack(pady=(20,5))
    entry_username = tk.Entry(frame, width=25)
    entry_username.pack(pady=(0,10))
    
    tk.Label(frame, text="Contraseña*", bg="#34495E", fg="#ECF0F1").pack(pady=(0,5))
    entry_password = tk.Entry(frame, show="*", width=25)
    entry_password.pack(pady=(0,10))
    
    tk.Label(frame, text="Nombre Completo*", bg="#34495E", fg="#ECF0F1").pack(pady=(0,5))
    entry_nombre = tk.Entry(frame, width=25)
    entry_nombre.pack(pady=(0,10))
    
    tk.Label(frame, text="Correo", bg="#34495E", fg="#ECF0F1").pack(pady=(0,5))
    entry_correo = tk.Entry(frame, width=25)
    entry_correo.pack(pady=(0,20))
    
    btn_frame = tk.Frame(frame, bg="#34495E")
    btn_frame.pack(pady=10)
    
    tk.Button(btn_frame, text="Guardar", command=guardar, bg="#27AE60", fg="white",
              font=("Helvetica", 10, "bold"), padx=20).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Cancelar", command=ventana.destroy, bg="#E74C3C", fg="white",
              font=("Helvetica", 10, "bold"), padx=20).pack(side="left", padx=5)

def recuperar_contraseña():
    correo = simpledialog.askstring("Recuperar", "Ingrese su correo registrado:")
    if not correo:
        return
        
    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT username FROM usuarios WHERE correo=?", (correo,))
    res = c.fetchone()
    conn.close()
    
    if res:
        messagebox.showinfo("Recuperación", 
                          f"Usuario encontrado: {res[0]}\n\nPor seguridad, contacte al administrador para restablecer su contraseña.")
    else:
        messagebox.showerror("Error", "Correo no encontrado")

def ver_usuarios():
    conn = conectar_db()
    c = conn.cursor()
    usuarios = c.execute("SELECT id, username, nombre_completo, correo FROM usuarios").fetchall()
    conn.close()
    
    ventana = tk.Toplevel()
    ventana.title("Usuarios Registrados")
    ventana.geometry("600x400")
    ventana.configure(bg="#2C3E50")
    
    tk.Label(ventana, text="👥 Usuarios Registrados", font=("Helvetica", 14, "bold"),
             bg="#2C3E50", fg="#ECF0F1").pack(pady=20)
    
    frame = tk.Frame(ventana, bg="#2C3E50")
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Crear Treeview para mostrar usuarios
    columns = ("ID", "Usuario", "Nombre Completo", "Correo")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    
    for usuario in usuarios:
        tree.insert("", "end", values=usuario)
    
    tree.pack(fill="both", expand=True)
    
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

# ========== PRODUCTOS ==========
def registrar_producto(nombre, descripcion, cantidad, precio, categoria, iva=21.0, fecha_vencimiento=None):
    conn = conectar_db()
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    c.execute("INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria, iva, fecha_agregado, fecha_vencimiento) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (nombre, descripcion, cantidad, precio, categoria, iva, fecha_actual, fecha_vencimiento))
    conn.commit()
    conn.close()

def obtener_productos():
    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT * FROM productos ORDER BY fecha_agregado DESC")
    datos = c.fetchall()
    conn.close()
    return datos

def eliminar_producto(id_producto):
    conn = conectar_db()
    c = conn.cursor()
    c.execute("DELETE FROM productos WHERE id=?", (id_producto,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def actualizar_producto(id_producto, nombre, descripcion, cantidad, precio, categoria, iva=21.0, fecha_vencimiento=None):
    conn = conectar_db()
    c = conn.cursor()
    c.execute("""
        UPDATE productos
        SET nombre=?, descripcion=?, cantidad=?, precio=?, categoria=?, iva=?, fecha_vencimiento=?
        WHERE id=?
    """, (nombre, descripcion, cantidad, precio, categoria, iva, fecha_vencimiento, id_producto))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def buscar_productos(termino):
    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT * FROM productos WHERE nombre LIKE ? OR categoria LIKE ? OR descripcion LIKE ?",
              (f"%{termino}%", f"%{termino}%", f"%{termino}%"))
    datos = c.fetchall()
    conn.close()
    return datos

def obtener_producto_por_id(id_producto):
    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT * FROM productos WHERE id=?", (id_producto,))
    producto = c.fetchone()
    conn.close()
    return producto

def obtener_estadisticas_mensuales():
    conn = conectar_db()
    c = conn.cursor()
    c.execute("""
        SELECT strftime('%Y-%m', fecha_agregado) as mes,
               COUNT(*) as total_productos,
               SUM(cantidad) as total_cantidad,
               SUM(precio * cantidad) as valor_total
        FROM productos
        GROUP BY strftime('%Y-%m', fecha_agregado)
        ORDER BY mes DESC
    """)
    datos = c.fetchall()
    conn.close()
    return datos

def obtener_estadisticas_anuales():
    conn = conectar_db()
    c = conn.cursor()
    c.execute("""
        SELECT strftime('%Y', fecha_agregado) as año,
               COUNT(*) as total_productos,
               SUM(cantidad) as total_cantidad,
               SUM(precio * cantidad) as valor_total
        FROM productos
        GROUP BY strftime('%Y', fecha_agregado)
        ORDER BY año DESC
    """)
    datos = c.fetchall()
    conn.close()
    return datos

def exportar_txt():
    productos = obtener_productos()
    try:
        with open("productos.txt", "w", encoding="utf-8") as file:
            file.write("=== REPORTE DE PRODUCTOS ===\n")
            file.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for row in productos:
                file.write(f"ID: {row[0]}\n")
                file.write(f"Nombre: {row[1]}\n")
                file.write(f"Descripción: {row[2]}\n")
                file.write(f"Cantidad: {row[3]}\n")
                file.write(f"Precio: ${row[4]:,.2f}\n")
                file.write(f"Categoría: {row[5]}\n")
                file.write(f"IVA: {row[6]}%\n")
                file.write(f"Fecha Agregado: {row[7]}\n")
                file.write(f"Fecha Vencimiento: {row[8] if row[8] else 'N/A'}\n")
                file.write("-" * 40 + "\n")
                
        messagebox.showinfo("Exportar", "Productos exportados a productos.txt")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")

def crear_backup():
    if os.path.exists(DB_PATH):
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{DB_PATH}"
        shutil.copy(DB_PATH, backup_name)
        messagebox.showinfo("Backup", f"Backup creado: {backup_name}")
    else:
        messagebox.showerror("Error", "Base de datos no encontrada")

# ========== INTERFAZ PRINCIPAL ==========
class GestorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🛍️ Gestor de Inventario - Adriana Serrano")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2C3E50")
        self.root.resizable(True, True)
        self.usuario_actual = None
        self.configurar_estilos()
        self.mostrar_login()

    def configurar_estilos(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Estilos personalizados
        self.style.configure("Title.TLabel", 
                           font=("Helvetica", 24, "bold"), 
                           background="#2C3E50", 
                           foreground="#ECF0F1")
        self.style.configure("Subtitle.TLabel", 
                           font=("Helvetica", 12), 
                           background="#2C3E50", 
                           foreground="#BDC3C7")
        self.style.configure("Custom.TButton", 
                           font=("Helvetica", 11, "bold"), 
                           padding=10, 
                           background="#3498DB", 
                           foreground="white")
        self.style.map("Custom.TButton", 
                      background=[('active', '#2980B9')])
        self.style.configure("Login.TButton", 
                           font=("Helvetica", 12, "bold"), 
                           padding=8, 
                           background="#27AE60", 
                           foreground="white")
        self.style.configure("Exit.TButton", 
                           font=("Helvetica", 11, "bold"), 
                           padding=8, 
                           background="#E74C3C", 
                           foreground="white")

    def mostrar_login(self):
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal del login
        login_frame = tk.Frame(self.root, bg="#2C3E50")
        login_frame.pack(expand=True, fill="both")
        
        # Título
        title_label = ttk.Label(login_frame, text="🛍️ GESTOR DE INVENTARIO", style="Title.TLabel")
        title_label.pack(pady=(50, 10))
        
        subtitle_label = ttk.Label(login_frame, text="Sistema de Gestión de Productos", style="Subtitle.TLabel")
        subtitle_label.pack(pady=(0, 40))
        
        # Caja de login
        login_box = tk.Frame(login_frame, bg="#34495E", relief="raised", bd=2)
        login_box.pack(padx=50, pady=20)
        
        tk.Label(login_box, text="Iniciar Sesión", 
                font=("Helvetica", 16, "bold"), 
                bg="#34495E", fg="#ECF0F1").pack(pady=(20, 30))
        
        # Campo usuario
        tk.Label(login_box, text="Usuario:", 
                font=("Helvetica", 12), 
                bg="#34495E", fg="#ECF0F1").pack(pady=(0, 5))
        self.username_entry = tk.Entry(login_box, font=("Helvetica", 12), width=20)
        self.username_entry.pack(pady=(0, 15))
        
        # Campo contraseña
        tk.Label(login_box, text="Contraseña:", 
                font=("Helvetica", 12), 
                bg="#34495E", fg="#ECF0F1").pack(pady=(0, 5))
        self.password_entry = tk.Entry(login_box, show="*", font=("Helvetica", 12), width=20)
        self.password_entry.pack(pady=(0, 20))
        
        # Botones
        login_btn = ttk.Button(login_box, text="Ingresar", command=self.login, style="Login.TButton")
        login_btn.pack(pady=(0, 20))
        
        btn_registrar = ttk.Button(login_box, text="Registrar Usuario", 
                                 command=registrar_usuario_nuevo, style="Custom.TButton")
        btn_registrar.pack(pady=(0, 10))
        
        btn_olvido = ttk.Button(login_box, text="Olvidé mi contraseña", 
                               command=recuperar_contraseña, style="Custom.TButton")
        btn_olvido.pack(pady=(0, 10))
        
        # Información de usuarios disponibles
        info_frame = tk.Frame(login_frame, bg="#2C3E50")
        info_frame.pack(pady=20)
        
        tk.Label(info_frame, text="Usuarios disponibles:", 
                font=("Helvetica", 10, "bold"), 
                bg="#2C3E50", fg="#BDC3C7").pack()
        tk.Label(info_frame, text="Esteban (pepe12A) | Belen (admin123) | Marcela (pass456) | Pola (secret789)",
                font=("Helvetica", 9), 
                bg="#2C3E50", fg="#95A5A6").pack()
        
        # Eventos
        self.root.bind('<Return>', lambda event: self.login())
        self.username_entry.focus()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor, ingrese usuario y contraseña")
            return
        
        nombre_completo = verificar_usuario(username, password)
        if nombre_completo:
            self.usuario_actual = nombre_completo
            self.mostrar_menu_principal()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            self.password_entry.delete(0, tk.END)

    def mostrar_menu_principal(self):
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#2C3E50")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg="#2C3E50")
        header_frame.pack(fill="x", pady=(0, 30))
        
        title_label = ttk.Label(header_frame, text="🛍️ GESTOR DE INVENTARIO", style="Title.TLabel")
        title_label.pack()
        
        welcome_label = ttk.Label(header_frame, text=f"Bienvenido/a, {self.usuario_actual}", style="Subtitle.TLabel")
        welcome_label.pack(pady=(5, 0))
        
        # Grid de botones
        buttons_frame = tk.Frame(main_frame, bg="#2C3E50")
        buttons_frame.pack(expand=True, fill="both")
        
        # Configurar columnas
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)
        
        # Botones del menú
        botones = [
            ("📝 Registrar Producto", self.ventana_registro, 0, 0),
            ("📋 Visualizar Productos", self.ventana_visualizar, 0, 1),
            ("✏️ Actualizar Producto", self.ventana_actualizar, 0, 2),
            ("🗑️ Eliminar Producto", self.ventana_eliminar, 1, 0),
            ("🔍 Buscar Producto", self.ventana_buscar, 1, 1),
            ("📊 Estadísticas", self.mostrar_estadisticas, 1, 2),
            ("📊 Estadísticas Mensuales/Anuales", self.mostrar_estadisticas_detalladas, 2, 0),
            ("💾 Exportar Productos TXT", exportar_txt, 2, 1),
            ("🗄️ Backup BD", crear_backup, 2, 2),
            ("👥 Ver Usuarios", ver_usuarios, 3, 0),
            ("ℹ️ Acerca de", self.acerca_de, 3, 1),
            ("🔄 Cambiar Usuario", self.mostrar_login, 3, 2),
            ("❌ Salir", self.salir_aplicacion, 4, 1)
        ]
        
        for (texto, comando, fila, columna) in botones:
            style = "Exit.TButton" if texto == "❌ Salir" else "Custom.TButton"
            btn = ttk.Button(buttons_frame, text=texto, command=comando, style=style)
            btn.grid(row=fila, column=columna, padx=10, pady=10, sticky="ew", ipadx=20, ipady=10)

    def ventana_registro(self):
        def limpiar_campos():
            for var in variables:
                var.set("")
                
        def guardar():
            try:
                nombre = nombre_var.get().strip()
                descripcion = desc_var.get().strip()
                cantidad = int(cant_var.get())
                precio = float(precio_var.get())
                categoria = cat_var.get().strip()
                iva = float(iva_var.get()) if iva_var.get() else 21.0
                fecha_venc = fecha_venc_var.get().strip() if fecha_venc_var.get().strip() else None
                
                if not nombre or not categoria or cantidad <= 0 or precio <= 0:
                    messagebox.showerror("Error", "Completa todos los campos obligatorios correctamente")
                    return
                
                # Validar formato de fecha si se proporciona
                if fecha_venc:
                    try:
                        datetime.strptime(fecha_venc, "%Y-%m-%d")
                    except ValueError:
                        messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                        return
                
                registrar_producto(nombre, descripcion, cantidad, precio, categoria, iva, fecha_venc)
                messagebox.showinfo("Éxito", "Producto registrado correctamente")
                limpiar_campos()
                
            except ValueError:
                messagebox.showerror("Error", "Ingrese valores numéricos válidos")
        
        top = tk.Toplevel(self.root)
        top.title("Registrar Nuevo Producto")
        top.geometry("500x600")
        top.configure(bg="#2C3E50")
        top.resizable(False, False)
        
        tk.Label(top, text="📝 Registrar Nuevo Producto", 
                font=("Helvetica", 16, "bold"),
                bg="#2C3E50", fg="#ECF0F1").pack(pady=20)
        
        frame = tk.Frame(top, bg="#34495E", relief="raised", bd=2)
        frame.pack(padx=30, pady=20, fill="both", expand=True)
        
        # Variables para los campos
        nombre_var = tk.StringVar()
        desc_var = tk.StringVar()
        cant_var = tk.StringVar()
        precio_var = tk.StringVar()
        cat_var = tk.StringVar()
        iva_var = tk.StringVar(value="21.0")
        fecha_venc_var = tk.StringVar()
        
        variables = [nombre_var, desc_var, cant_var, precio_var, cat_var, iva_var, fecha_venc_var]
        
        # Campos del formulario
        campos = [
            ("Nombre *:", nombre_var),
            ("Descripción:", desc_var),
            ("Cantidad *:", cant_var),
            ("Precio *:", precio_var),
            ("Categoría *:", cat_var),
            ("IVA (%):", iva_var),
            ("Fecha Vencimiento (YYYY-MM-DD):", fecha_venc_var)
        ]
        
        for i, (label, var) in enumerate(campos):
            tk.Label(frame, text=label, font=("Helvetica", 11),
                    bg="#34495E", fg="#ECF0F1").pack(pady=(15, 5), anchor="w", padx=20)
            entry = tk.Entry(frame, textvariable=var, font=("Helvetica", 11), width=40)
            entry.pack(pady=(0, 5), padx=20)
        
        # Botones
        btn_frame = tk.Frame(frame, bg="#34495E")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Guardar", command=guardar, 
                  font=("Helvetica", 11, "bold"),
                  bg="#27AE60", fg="white", padx=20).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Limpiar", command=limpiar_campos, 
                  font=("Helvetica", 11, "bold"),
                  bg="#F39C12", fg="white", padx=20).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancelar", command=top.destroy, 
                  font=("Helvetica", 11, "bold"),
                  bg="#E74C3C", fg="white", padx=20).pack(side="left", padx=10)

    def ventana_visualizar(self):
        productos = obtener_productos()
        
        top = tk.Toplevel(self.root)
        top.title("Visualizar Productos")
        top.geometry("1200x600")
        top.configure(bg="#2C3E50")
        
        tk.Label(top, text="📋 Lista de Productos", 
                font=("Helvetica", 16, "bold"),
                bg="#2C3E50", fg="#ECF0F1").pack(pady=20)
        
        if not productos:
            tk.Label(top, text="⚠️ No hay productos en el inventario",
                    font=("Helvetica", 14), 
                    bg="#2C3E50", fg="#E74C3C").pack(pady=50)
            return
        
        # Frame principal
        frame = tk.Frame(top, bg="#2C3E50")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configurar Treeview
        columns = ("ID", "Nombre", "Descripción", "Cantidad", "Precio", "Categoría", "IVA", "F.Agregado", "F.Vencimiento")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)
        
        # Configurar columnas
        anchos = [50, 150, 200, 80, 100, 100, 60, 100, 100]
        for col, ancho in zip(columns, anchos):
            tree.heading(col, text=col)
            tree.column(col, width=ancho, anchor="center")
        
        # Insertar datos
        for producto in productos:
            # Formatear precio
            precio_formateado = f"${producto[4]:,.2f}"
            valores = list(producto)
            valores[4] = precio_formateado
            tree.insert("", "end", values=valores)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        h_scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Posicionar elementos
        tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Frame de botones
        btn_frame = tk.Frame(top, bg="#2C3E50")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🔄 Actualizar", 
                  command=lambda: self.actualizar_tabla(tree), 
                  bg="#3498DB", fg="white", font=("Helvetica", 10, "bold")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="❌ Cerrar", 
                  command=top.destroy, 
                  bg="#E74C3C", fg="white", font=("Helvetica", 10, "bold")).pack(side="left", padx=5)

    def actualizar_tabla(self, tree):
        """Actualizar la tabla de productos"""
        for item in tree.get_children():
            tree.delete(item)
            
        productos = obtener_productos()
        for producto in productos:
            precio_formateado = f"${producto[4]:,.2f}"
            valores = list(producto)
            valores[4] = precio_formateado
            tree.insert("", "end", values=valores)

    def ventana_actualizar(self):
        def buscar_producto():
            try:
                id_producto = int(id_var.get())
                producto = obtener_producto_por_id(id_producto)
                
                if producto:
                    # Llenar campos con datos del producto
                    nombre_var.set(producto[1])
                    desc_var.set(producto[2] or "")
                    cant_var.set(str(producto[3]))
                    precio_var.set(str(producto[4]))
                    cat_var.set(producto[5] or "")
                    iva_var.set(str(producto[6]))
                    fecha_venc_var.set(producto[8] or "")
                    
                    # Habilitar campos
                    for entry in entries:
                        entry.config(state="normal")
                    btn_guardar.config(state="normal")
                    
                else:
                    messagebox.showerror("Error", "Producto no encontrado")
                    
            except ValueError:
                messagebox.showerror("Error", "Ingrese un ID válido")
        
        def guardar_cambios():
            try:
                id_producto = int(id_var.get())
                nombre = nombre_var.get().strip()
                descripcion = desc_var.get().strip()
                cantidad = int(cant_var.get())
                precio = float(precio_var.get())
                categoria = cat_var.get().strip()
                iva = float(iva_var.get()) if iva_var.get() else 21.0
                fecha_venc = fecha_venc_var.get().strip() if fecha_venc_var.get().strip() else None
                
                if not nombre or not categoria or cantidad <= 0 or precio <= 0:
                    messagebox.showerror("Error", "Complete todos los campos obligatorios")
                    return
                
                # Validar formato de fecha
                if fecha_venc:
                    try:
                        datetime.strptime(fecha_venc, "%Y-%m-%d")
                    except ValueError:
                        messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                        return
                
                if actualizar_producto(id_producto, nombre, descripcion, cantidad, precio, categoria, iva, fecha_venc):
                    messagebox.showinfo("Éxito", "Producto actualizado correctamente")
                    top.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el producto")
                    
            except ValueError:
                messagebox.showerror("Error", "Ingrese valores numéricos válidos")
        
        top = tk.Toplevel(self.root)
        top.title("Actualizar Producto")
        top.geometry("500x650")
        top.configure(bg="#2C3E50")
        top.resizable(False, False)
        
        tk.Label(top, text="✏️ Actualizar Producto", 
                font=("Helvetica", 16, "bold"),
                bg="#2C3E50", fg="#ECF0F1").pack(pady=20)
        
        # Frame de búsqueda
        search_frame = tk.Frame(top, bg="#34495E", relief="raised", bd=2)
        search_frame.pack(padx=30, pady=(0, 20), fill="x")
        
        tk.Label(search_frame, text="ID del Producto:", 
                font=("Helvetica", 12, "bold"),
                bg="#34495E", fg="#ECF0F1").pack(pady=10)
        
        id_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=id_var, 
                font=("Helvetica", 12), width=15).pack(pady=5)
        
        tk.Button(search_frame, text="🔍 Buscar", command=buscar_producto,
                  bg="#3498DB", fg="white", font=("Helvetica", 10, "bold")).pack(pady=10)
        
        # Frame de campos
        frame = tk.Frame(top, bg="#34495E", relief="raised", bd=2)
        frame.pack(padx=30, pady=20, fill="both", expand=True)
        
        # Variables
        nombre_var = tk.StringVar()
        desc_var = tk.StringVar()
        cant_var = tk.StringVar()
        precio_var = tk.StringVar()
        cat_var = tk.StringVar()
        iva_var = tk.StringVar()
        fecha_venc_var = tk.StringVar()
        
        # Campos del formulario
        campos = [
            ("Nombre *:", nombre_var),
            ("Descripción:", desc_var),
            ("Cantidad *:", cant_var),
            ("Precio *:", precio_var),
            ("Categoría *:", cat_var),
            ("IVA (%):", iva_var),
            ("Fecha Vencimiento (YYYY-MM-DD):", fecha_venc_var)
        ]
        
        entries = []
        for label, var in campos:
            tk.Label(frame, text=label, font=("Helvetica", 11),
                    bg="#34495E", fg="#ECF0F1").pack(pady=(10, 5), anchor="w", padx=20)
            entry = tk.Entry(frame, textvariable=var, font=("Helvetica", 11), 
                           width=40, state="disabled")
            entry.pack(pady=(0, 5), padx=20)
            entries.append(entry)
        
        # Botones
        btn_frame = tk.Frame(frame, bg="#34495E")
        btn_frame.pack(pady=20)
        
        btn_guardar = tk.Button(btn_frame, text="Guardar Cambios", command=guardar_cambios,
                               font=("Helvetica", 11, "bold"),
                               bg="#27AE60", fg="white", padx=20, state="disabled")
        btn_guardar.pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="Cancelar", command=top.destroy,
                  font=("Helvetica", 11, "bold"),
                  bg="#E74C3C", fg="white", padx=20).pack(side="left", padx=10)

    def ventana_eliminar(self):
        def eliminar():
            try:
                id_producto = int(id_var.get())
                producto = obtener_producto_por_id(id_producto)
                
                if not producto:
                    messagebox.showerror("Error", "Producto no encontrado")
                    return
                
                # Mostrar información del producto
                info = f"¿Está seguro de eliminar este producto?\n\n"
                info += f"ID: {producto[0]}\n"
                info += f"Nombre: {producto[1]}\n"
                info += f"Cantidad: {producto[3]}\n"
                info += f"Precio: ${producto[4]:,.2f}\n"
                info += f"Categoría: {producto[5]}"
                
                if messagebox.askyesno("Confirmar eliminación", info):
                    if eliminar_producto(id_producto):
                        messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                        id_var.set("")
                        info_label.config(text="")
                    else:
                        messagebox.showerror("Error", "No se pudo eliminar el producto")
                        
            except ValueError:
                messagebox.showerror("Error", "Ingrese un ID válido")
        
        def buscar_info():
            try:
                id_producto = int(id_var.get())
                producto = obtener_producto_por_id(id_producto)
                
                if producto:
                    info = f"Información del producto:\n\n"
                    info += f"ID: {producto[0]}\n"
                    info += f"Nombre: {producto[1]}\n"
                    info += f"Descripción: {producto[2] or 'N/A'}\n"
                    info += f"Cantidad: {producto[3]}\n"
                    info += f"Precio: ${producto[4]:,.2f}\n"
                    info += f"Categoría: {producto[5]}\n"
                    info += f"IVA: {producto[6]}%\n"
                    info += f"Fecha Agregado: {producto[7]}\n"
                    info += f"Fecha Vencimiento: {producto[8] or 'N/A'}"
                    
                    info_label.config(text=info, fg="#ECF0F1")
                    btn_eliminar.config(state="normal")
                else:
                    info_label.config(text="❌ Producto no encontrado", fg="#E74C3C")
                    btn_eliminar.config(state="disabled")
                    
            except ValueError:
                info_label.config(text="⚠️ Ingrese un ID válido", fg="#F39C12")
                btn_eliminar.config(state="disabled")
        
        top = tk.Toplevel(self.root)
        top.title("Eliminar Producto")
        top.geometry("500x500")
        top.configure(bg="#2C3E50")
        top.resizable(False, False)
        
        tk.Label(top, text="🗑️ Eliminar Producto", 
                font=("Helvetica", 16, "bold"),
                bg="#2C3E50", fg="#ECF0F1").pack(pady=20)
        
        # Frame principal
        frame = tk.Frame(top, bg="#34495E", relief="raised", bd=2)
        frame.pack(padx=30, pady=20, fill="both", expand=True)
        
        tk.Label(frame, text="ID del Producto:", 
                font=("Helvetica", 12, "bold"),
                bg="#34495E", fg="#ECF0F1").pack(pady=(20, 5))
        
        id_var = tk.StringVar()
        id_entry = tk.Entry(frame, textvariable=id_var, font=("Helvetica", 12), width=15)
        id_entry.pack(pady=5)
        
        # Vincular evento para buscar automáticamente
        id_var.trace('w', lambda *args: buscar_info())
        
        tk.Button(frame, text="🔍 Buscar", command=buscar_info,
                  bg="#3498DB", fg="white", font=("Helvetica", 10, "bold")).pack(pady=10)
        
        # Label para mostrar información
        info_label = tk.Label(frame, text="", font=("Helvetica", 10),
                             bg="#34495E", fg="#BDC3C7", justify="left")
        info_label.pack(pady=20, padx=20)
        
        # Botones
        btn_frame = tk.Frame(frame, bg="#34495E")
        btn_frame.pack(pady=20)
        
        btn_eliminar = tk.Button(btn_frame, text="🗑️ Eliminar", command=eliminar,
                                font=("Helvetica", 11, "bold"),
                                bg="#E74C3C", fg="white", padx=20, state="disabled")
        btn_eliminar.pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="Cancelar", command=top.destroy,
                  font=("Helvetica", 11, "bold"),
                  bg="#95A5A6", fg="white", padx=20).pack(side="left", padx=10)

    def ventana_buscar(self):
        def realizar_busqueda():
            termino = busqueda_var.get().strip()
            if not termino:
                messagebox.showwarning("Atención", "Ingrese un término de búsqueda")
                return
            
            resultados = buscar_productos(termino)
            
            # Limpiar tabla
            for item in tree.get_children():
                tree.delete(item)
            
            # Mostrar resultados
            if resultados:
                for producto in resultados:
                    precio_formateado = f"${producto[4]:,.2f}"
                    valores = list(producto)
                    valores[4] = precio_formateado
                    tree.insert("", "end", values=valores)
                resultado_label.config(text=f"✅ {len(resultados)} productos encontrados", fg="#27AE60")
            else:
                resultado_label.config(text="❌ No se encontraron productos", fg="#E74C3C")
        
        top = tk.Toplevel(self.root)
        top.title("Buscar Productos")
        top.geometry("1000x600")
        top.configure(bg="#2C3E50")
        
        tk.Label(top, text="🔍 Buscar Productos", 
                font=("Helvetica", 16, "bold"),
                bg="#2C3E50", fg="#ECF0F1").pack(pady=20)
        
        # Frame de búsqueda
        search_frame = tk.Frame(top, bg="#34495E", relief="raised", bd=2)
        search_frame.pack(padx=30, pady=(0, 20), fill="x")
        
        tk.Label(search_frame, text="Término de búsqueda:", 
                font=("Helvetica", 12),
                bg="#34495E", fg="#ECF0F1").pack(pady=10)
        
        busqueda_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=busqueda_var, 
                               font=("Helvetica", 12), width=30)
        search_entry.pack(pady=5)
        
        tk.Button(search_frame, text="🔍 Buscar", command=realizar_busqueda,
                  bg="#3498DB", fg="white", font=("Helvetica", 10, "bold")).pack(pady=10)
        
        # Label de resultado
        resultado_label = tk.Label(search_frame, text="", font=("Helvetica", 10),
                                  bg="#34495E")
        resultado_label.pack(pady=5)
        
        # Frame de resultados
        frame = tk.Frame(top, bg="#2C3E50")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Treeview para resultados
        columns = ("ID", "Nombre", "Descripción", "Cantidad", "Precio", "Categoría")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        anchos = [50, 180, 200, 80, 100, 120]
        for col, ancho in zip(columns, anchos):
            tree.heading(col, text=col)
            tree.column(col, width=ancho, anchor="center")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=v_scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        
        # Vincular Enter para buscar
        search_entry.bind('<Return>', lambda event: realizar_busqueda())
        search_entry.focus()

    def mostrar_estadisticas(self):
        productos = obtener_productos()
        
        if not productos:
            messagebox.showinfo("Información", "No hay productos para mostrar estadísticas")
            return
        
        # Calcular estadísticas
        total_productos = len(productos)
        total_cantidad = sum(p[3] for p in productos)
        valor_total = sum(p[3] * p[4] for p in productos)
        
        # Productos por categoría
        categorias = {}
        for producto in productos:
            cat = producto[5] or "Sin categoría"
            categorias[cat] = categorias.get(cat, 0) + 1
        
        # Producto más caro y más barato
        producto_mas_caro = max(productos, key=lambda x: x[4])
        producto_mas_barato = min(productos, key=lambda x: x[4])
        
        top = tk.Toplevel(self.root)
        top.title("Estadísticas del Inventario")
        top.geometry("600x500")
        top.configure(bg="#2C3E50")
        
        tk.Label(top, text="📊 Estadísticas del Inventario", 
                font=("Helvetica", 16, "bold"),
                bg="#2C3E50", fg="#ECF0F1").pack(pady=20)
        
        # Frame principal
        frame = tk.Frame(top, bg="#34495E", relief="raised", bd=2)
        frame.pack(padx=30, pady=20, fill="both", expand=True)
        
        # Estadísticas generales
        stats_text = f"""
        📈 ESTADÍSTICAS GENERALES
        
        Total de productos: {total_productos}
        Cantidad total en inventario: {total_cantidad:,}
        Valor total del inventario: ${valor_total:,.2f}
        
        💰 PRODUCTOS DESTACADOS
        
        Más caro: {producto_mas_caro[1]} - ${producto_mas_caro[4]:,.2f}
        Más barato: {producto_mas_barato[1]} - ${producto_mas_barato[4]:,.2f}
        
        📦 PRODUCTOS POR CATEGORÍA
        """
        
        for cat, count in sorted(categorias.items()):
            stats_text += f"\n        {cat}: {count} productos"
        
        stats_label = tk.Label(frame, text=stats_text, 
                              font=("Helvetica", 11),
                              bg="#34495E", fg="#ECF0F1", 
                              justify="left")
        stats_label.pack(pady=20, padx=20)

    def mostrar_estadisticas_detalladas(self):
        def mostrar_mensuales():
            datos = obtener_estadisticas_mensuales()
            mostrar_datos(datos, "Estadísticas Mensuales", 
                         ["Mes", "Productos", "Cantidad", "Valor Total"])
        
        def mostrar_anuales():
            datos = obtener_estadisticas_anuales()
            mostrar_datos(datos, "Estadísticas Anuales", 
                         ["Año", "Productos", "Cantidad", "Valor Total"])
        
        def mostrar_datos(datos, titulo, columnas):
            ventana = tk.Toplevel(self.root)
            ventana.title(titulo)
            ventana.geometry("700x400")
            ventana.configure(bg="#2C3E50")
            
            tk.Label(ventana, text=f"📊 {titulo}", 
                    font=("Helvetica", 16, "bold"),
                    bg="#2C3E50", fg="#ECF0F1").pack(pady=20)
            
            if not datos:
                tk.Label(ventana, text="⚠️ No hay datos disponibles",
                        font=("Helvetica", 12),
                        bg="#2C3E50", fg="#E74C3C").pack(pady=50)
                return
            
            frame = tk.Frame(ventana, bg="#2C3E50")
            frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            tree = ttk.Treeview(frame, columns=columnas, show="headings", height=15)
            
            for col in columnas:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor="center")
            
            for row in datos:
                valores = list(row)
                # Formatear valor total
                if len(valores) > 3:
                    valores[3] = f"${valores[3]:,.2f}"
                tree.insert("", "end", values=valores)
            
            tree.pack(fill="both", expand=True)
            
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
        
        top = tk.Toplevel(self.root)
        top.title("Estadísticas Detalladas")
        top.geometry("400x300")
        top.configure(bg="#2C3E50")
        
        tk.Label(top, text="📊 Estadísticas Detalladas", 
                font=("Helvetica", 16, "bold"),
                bg="#2C3E50", fg="#ECF0F1").pack(pady=30)
        
        frame = tk.Frame(top, bg="#2C3E50")
        frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        tk.Button(frame, text="📅 Estadísticas Mensuales", 
                  command=mostrar_mensuales,
                  font=("Helvetica", 12, "bold"),
                  bg="#3498DB", fg="white", pady=15).pack(fill="x", pady=10)
        
        tk.Button(frame, text="📈 Estadísticas Anuales", 
                  command=mostrar_anuales,
                  font=("Helvetica", 12, "bold"),
                  bg="#27AE60", fg="white", pady=15).pack(fill="x", pady=10)
        
        tk.Button(frame, text="❌ Cerrar", 
                  command=top.destroy,
                  font=("Helvetica", 12, "bold"),
                  bg="#E74C3C", fg="white", pady=10).pack(fill="x", pady=10)

    def acerca_de(self):
        top = tk.Toplevel(self.root)
        top.title("Acerca de")
        top.geometry("500x400")
        top.configure(bg="#2C3E50")
        top.resizable(False, False)
        
        tk.Label(top, text="ℹ️ Acerca del Sistema", 
                font=("Helvetica", 16, "bold"),
                bg="#2C3E50", fg="#ECF0F1").pack(pady=20)
        
        frame = tk.Frame(top, bg="#34495E", relief="raised", bd=2)
        frame.pack(padx=30, pady=20, fill="both", expand=True)
        
        info_text = """
        🛍️ GESTOR DE INVENTARIO
        
        Desarrollado por: Adriana Serrano
        Versión: 2.0
        Fecha: 2024
        
        📋 CARACTERÍSTICAS:
        
        ✓ Gestión completa de productos
        ✓ Sistema de usuarios seguro
        ✓ Búsqueda avanzada
        ✓ Estadísticas detalladas
        ✓ Exportación de datos
        ✓ Sistema de backup
        ✓ Interfaz moderna y intuitiva
        
        🛠️ TECNOLOGÍAS UTILIZADAS:
        
        • Python 3.x
        • Tkinter (Interfaz gráfica)
        • SQLite (Base de datos)
        • Hashlib (Seguridad)
        
        © 2024 - Todos los derechos reservados
        """
        
        tk.Label(frame, text=info_text, 
                font=("Helvetica", 10),
                bg="#34495E", fg="#ECF0F1", 
                justify="left").pack(pady=20, padx=20)
        
        tk.Button(frame, text="❌ Cerrar", command=top.destroy,
                  font=("Helvetica", 10, "bold"),
                  bg="#E74C3C", fg="white", padx=20).pack(pady=10)

    def salir_aplicacion(self):
        if messagebox.askyesno("Confirmar salida", "¿Está seguro de que desea salir?"):
            self.root.quit()

# ========== FUNCIÓN PRINCIPAL ==========
def main():
    root = tk.Tk()
    app = GestorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
