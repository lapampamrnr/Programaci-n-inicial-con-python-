import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date
import os
import hashlib
from collections import defaultdict

# ========================= BASE DE DATOS =========================
DB_PATH = "inventario.db"

def conectar_db():
    return sqlite3.connect(DB_PATH)

def crear_tablas():
    conn = conectar_db()
    c = conn.cursor()
    
    # Tabla de productos
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
    
    # Tabla de usuarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nombre_completo TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def crear_usuarios_por_defecto():
    conn = conectar_db()
    c = conn.cursor()
    
    usuarios_defecto = [
        ("Esteban", "pepe12A", "Esteban García"),
        ("Belen", "admin123", "Belén Rodríguez"),
        ("Marcela", "pass456", "Marcela López"),
        ("Pola", "secret789", "Pola Martínez")
    ]
    
    for username, password, nombre in usuarios_defecto:
        # Hashear la contraseña
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            c.execute("INSERT INTO usuarios (username, password, nombre_completo) VALUES (?, ?, ?)",
                      (username, password_hash, nombre))
        except sqlite3.IntegrityError:
            pass  # Usuario ya existe
    
    conn.commit()
    conn.close()

def crear_productos_por_defecto():
    conn = conectar_db()
    c = conn.cursor()
    
    # Verificar si ya hay productos
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

crear_tablas()
crear_usuarios_por_defecto()
crear_productos_por_defecto()

# ========================= FUNCIONES DE USUARIOS =========================
def verificar_usuario(username, password):
    conn = conectar_db()
    c = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT nombre_completo FROM usuarios WHERE username=? AND password=?", (username, password_hash))
    resultado = c.fetchone()
    conn.close()
    return resultado[0] if resultado else None

# ========================= FUNCIONES DE PRODUCTOS =========================
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

# ========================= INTERFAZ PRINCIPAL =========================
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
        
        # Configurar estilos personalizados
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
        # Limpiar la ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal de login
        login_frame = tk.Frame(self.root, bg="#2C3E50")
        login_frame.pack(expand=True, fill="both")
        
        # Título
        title_label = ttk.Label(login_frame, text="🛍️ GESTOR DE INVENTARIO", style="Title.TLabel")
        title_label.pack(pady=(50, 10))
        
        subtitle_label = ttk.Label(login_frame, text="Sistema de Gestión de Productos", style="Subtitle.TLabel")
        subtitle_label.pack(pady=(0, 40))
        
        # Frame de login
        login_box = tk.Frame(login_frame, bg="#34495E", relief="raised", bd=2)
        login_box.pack(padx=50, pady=20)
        
        # Título del login
        tk.Label(login_box, text="Iniciar Sesión", font=("Helvetica", 16, "bold"), 
                bg="#34495E", fg="#ECF0F1").pack(pady=(20, 30))
        
        # Usuario
        tk.Label(login_box, text="Usuario:", font=("Helvetica", 12), 
                bg="#34495E", fg="#ECF0F1").pack(pady=(0, 5))
        self.username_entry = tk.Entry(login_box, font=("Helvetica", 12), width=20)
        self.username_entry.pack(pady=(0, 15))
        
        # Contraseña
        tk.Label(login_box, text="Contraseña:", font=("Helvetica", 12), 
                bg="#34495E", fg="#ECF0F1").pack(pady=(0, 5))
        self.password_entry = tk.Entry(login_box, show="*", font=("Helvetica", 12), width=20)
        self.password_entry.pack(pady=(0, 20))
        
        # Botón de login
        login_btn = ttk.Button(login_box, text="Ingresar", command=self.login, style="Login.TButton")
        login_btn.pack(pady=(0, 20))
        
        # Información de usuarios
        info_frame = tk.Frame(login_frame, bg="#2C3E50")
        info_frame.pack(pady=20)
        
        tk.Label(info_frame, text="Usuarios disponibles:", font=("Helvetica", 10, "bold"), 
                bg="#2C3E50", fg="#BDC3C7").pack()
        tk.Label(info_frame, text="Esteban (pepe12A) | Belen (admin123) | Marcela (pass456) | Pola (secret789)", 
                font=("Helvetica", 9), bg="#2C3E50", fg="#95A5A6").pack()
        
        # Bind Enter key
        self.root.bind('<Return>', lambda event: self.login())
        
        # Focus en el campo de usuario
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
        # Limpiar la ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#2C3E50")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Encabezado
        header_frame = tk.Frame(main_frame, bg="#2C3E50")
        header_frame.pack(fill="x", pady=(0, 30))
        
        title_label = ttk.Label(header_frame, text="🛍️ GESTOR DE INVENTARIO", style="Title.TLabel")
        title_label.pack()
        
        welcome_label = ttk.Label(header_frame, text=f"Bienvenido/a, {self.usuario_actual}", style="Subtitle.TLabel")
        welcome_label.pack(pady=(5, 0))
        
        # Frame de botones
        buttons_frame = tk.Frame(main_frame, bg="#2C3E50")
        buttons_frame.pack(expand=True, fill="both")
        
        # Configurar grid
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
            ("ℹ️ Acerca de", self.acerca_de, 2, 0),
            ("👤 Cambiar Usuario", self.mostrar_login, 2, 1),
            ("❌ Salir", self.salir_aplicacion, 2, 2),
        ]
        
        for (texto, comando, fila, columna) in botones:
            if texto == "❌ Salir":
                btn = ttk.Button(buttons_frame, text=texto, command=comando, style="Exit.TButton")
            else:
                btn = ttk.Button(buttons_frame, text=texto, command=comando, style="Custom.TButton")
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
                    messagebox.showerror("Error", "Por favor, complete todos los campos obligatorios correctamente")
                    return
                
                registrar_producto(nombre, descripcion, cantidad, precio, categoria, iva, fecha_venc)
                messagebox.showinfo("Éxito", "Producto registrado correctamente")
                limpiar_campos()
                
            except ValueError:
                messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos")

        top = tk.Toplevel(self.root)
        top.title("Registrar Nuevo Producto")
        top.geometry("500x600")
        top.configure(bg="#2C3E50")
        top.resizable(False, False)
        
        # Título
        tk.Label(top, text="📝 Registrar Nuevo Producto", font=("Helvetica", 16, "bold"), 
                bg="#2C3E50", fg="#ECF0F1").pack(pady=20)
        
        # Frame principal
        frame = tk.Frame(top, bg="#34495E", relief="raised", bd=2)
        frame.pack(padx=30, pady=20, fill="both", expand=True)
        
        # Variables
        nombre_var = tk.StringVar()
        desc_var = tk.StringVar()
        cant_var = tk.StringVar()
        precio_var = tk.StringVar()
        cat_var = tk.StringVar()
        iva_var = tk.StringVar(value="21.0")
        fecha_venc_var = tk.StringVar()
        
        variables = [nombre_var, desc_var, cant_var, precio_var, cat_var, iva_var, fecha_venc_var]
        
        # Campos
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
        
        tk.Button(btn_frame, text="Guardar", command=guardar, font=("Helvetica", 11, "bold"),
                 bg="#27AE60", fg="white", padx=20).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Limpiar", command=limpiar_campos, font=("Helvetica", 11, "bold"),
                 bg="#F39C12", fg="white", padx=20).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancelar", command=top.destroy, font=("Helvetica", 11, "bold"),
                 bg="#E74C3C", fg="white", padx=20).pack(side="left", padx=10)

    def ventana_visualizar(self):
        productos = obtener_productos()
        
        top = tk.Toplevel(self.root)
        top.title("Visualizar Productos")
        top.geometry("1200x600")
        top.configure(bg="#2C3E50")
        
        # Título
        tk.Label(top, text="📋 Lista de Productos", font=("Helvetica", 16, "bold"), 
                bg="#2C3E50", fg="#ECF0F1").pack(pady=20)
        
        if not productos:
            tk.Label(top, text="⚠️ No hay productos en el inventario", 
                    font=("Helvetica", 14), bg="#2C3E50", fg="#E74C3C").pack(pady=50)
            return
        
        # Frame para el Treeview
        frame = tk.Frame(top, bg="#2C3E50")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Crear Treeview
        columns = ("ID", "Nombre", "Descripción", "Cantidad", "Precio", "Categoría", "IVA", "Fecha Agregado", "Vencimiento")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        # Configurar columnas
        widths = [50, 150, 200, 80, 100, 120, 60, 120, 120]
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        h_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Posicionar elementos
        tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        
        # Insertar datos
        