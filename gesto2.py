# gestor_comercio_adriana.py

import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from tkinter import ttk
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import matplotlib.pyplot as plt
import os

# --------------------------- BASE DE DATOS ---------------------------
conn = sqlite3.connect("inventario.db")
cursor = conn.cursor()

def crear_tablas():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL,
            correo TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            categoria TEXT,
            fecha_agregado TEXT
        )
    ''')
    conn.commit()

def crear_datos_iniciales():
    # Usuario admin
    cursor.execute("SELECT * FROM usuarios WHERE usuario = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (usuario, contrasena, correo) VALUES (?, ?, ?)",
                       ("admin", "admin123", "admin@ejemplo.com"))
        conn.commit()

    # Productos de ejemplo
    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        productos = [
            ("Leche La Serenísima", "Entera 1L", 20, 1100, "Lácteos"),
            ("Pan Lactal Bimbo", "Doble salvado", 15, 950, "Panadería"),
            ("Detergente Magistral", "Limón 500ml", 10, 1300, "Limpieza"),
        ]
        for p in productos:
            cursor.execute("INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria, fecha_agregado) VALUES (?, ?, ?, ?, ?, ?)",
                           (p[0], p[1], p[2], p[3], p[4], datetime.now().strftime("%Y-%m-%d")))
        conn.commit()

# --------------------------- FUNCIONES DE CORREO ---------------------------
EMAIL_EMISOR = "vegetaaa666@gmail.com"
EMAIL_CONTRASENA = "tu_contraseña_de_aplicacion"

def enviar_correo(destinatario, asunto, cuerpo):
    try:
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_EMISOR
        mensaje['To'] = destinatario
        mensaje['Subject'] = asunto
        mensaje.attach(MIMEText(cuerpo, 'plain'))

        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(EMAIL_EMISOR, EMAIL_CONTRASENA)
        servidor.send_message(mensaje)
        servidor.quit()
        print("✅ Correo enviado correctamente")
    except Exception as e:
        print("❌ Error al enviar el correo:", e)

# --------------------------- FUNCIONES DEL SISTEMA ---------------------------
def login():
    usuario = entry_usuario.get()
    contrasena = entry_contra.get()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND contrasena = ?", (usuario, contrasena))
    if cursor.fetchone():
        ventana_login.destroy()
        abrir_panel(usuario)
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")

def registrar_usuario():
    usuario = simpledialog.askstring("Registro", "Nuevo nombre de usuario:")
    contrasena = simpledialog.askstring("Registro", "Nueva contraseña:", show="*")
    correo = simpledialog.askstring("Registro", "Correo (opcional):")
    if usuario and contrasena:
        try:
            cursor.execute("INSERT INTO usuarios (usuario, contrasena, correo) VALUES (?, ?, ?)",
                           (usuario, contrasena, correo))
            conn.commit()
            messagebox.showinfo("Éxito", "Usuario registrado correctamente")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El usuario ya existe")

def recuperar_contrasena():
    correo = simpledialog.askstring("Recuperación", "Ingresa tu correo registrado:")
    cursor.execute("SELECT usuario, contrasena FROM usuarios WHERE correo = ?", (correo,))
    datos = cursor.fetchone()
    if datos:
        asunto = "Recuperación de contraseña - Gestor Adriana"
        cuerpo = f"Hola {datos[0]}, tu contraseña es: {datos[1]}"
        enviar_correo(correo, asunto, cuerpo)
        messagebox.showinfo("Listo", "Tu contraseña fue enviada a tu correo")
    else:
        messagebox.showerror("Error", "Correo no encontrado")

# --------------------------- PANEL PRINCIPAL ---------------------------
def abrir_panel(usuario):
    panel = tk.Tk()
    panel.title("Gestor de Comercio Adriana")
    panel.geometry("700x600")
    panel.configure(bg="white")
    
    tk.Label(panel, text=f"Bienvenido, {usuario}", font=("Arial", 16), bg="white", fg="black").pack(pady=10)

    marco = tk.Frame(panel, bg="white")
    marco.pack(pady=10)

    botones = [
        ("📋 Ver Inventario", ver_productos),
        ("➕ Agregar Producto", agregar_producto),
        ("📝 Editar Producto", editar_producto),
        ("❌ Eliminar Producto", eliminar_producto),
        ("📁 Exportar Productos", exportar_productos),
        ("📈 Ver Estadísticas", ver_estadisticas),
        ("🚪 Salir", panel.quit)
    ]
    for texto, comando in botones:
        tk.Button(marco, text=texto, command=comando, width=30, height=2, bg="#dcd6f7", font=("Arial", 11)).pack(pady=5)

    panel.mainloop()

# --------------------------- INVENTARIO ---------------------------
def ver_productos():
    cursor.execute("SELECT * FROM productos")
    registros = cursor.fetchall()
    texto = "\n".join([f"ID:{r[0]} | {r[1]} | {r[2]} | Cant:{r[3]} | Precio:${r[4]} | Cat:{r[5]}" for r in registros])
    messagebox.showinfo("Inventario", texto if texto else "No hay productos")

def agregar_producto():
    nombre = simpledialog.askstring("Nombre", "Nombre del producto:")
    descripcion = simpledialog.askstring("Descripción", "Descripción:")
    cantidad = simpledialog.askinteger("Cantidad", "Cantidad:")
    precio = simpledialog.askfloat("Precio", "Precio:")
    categoria = simpledialog.askstring("Categoría", "Categoría:")
    fecha = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria, fecha_agregado) VALUES (?, ?, ?, ?, ?, ?)",
                  (nombre, descripcion, cantidad, precio, categoria, fecha))
    conn.commit()
    messagebox.showinfo("Listo", "Producto agregado")

def editar_producto():
    producto_id = simpledialog.askinteger("Editar", "ID del producto:")
    campo = simpledialog.askstring("Campo", "Campo a editar:")
    valor = simpledialog.askstring("Nuevo valor", f"Nuevo valor para {campo}:")
    if campo in ["cantidad"]:
        valor = int(valor)
    elif campo in ["precio"]:
        valor = float(valor)
    cursor.execute(f"UPDATE productos SET {campo}=? WHERE id=?", (valor, producto_id))
    conn.commit()
    messagebox.showinfo("Modificado", "Producto actualizado")

def eliminar_producto():
    producto_id = simpledialog.askinteger("Eliminar", "ID del producto a eliminar:")
    cursor.execute("DELETE FROM productos WHERE id=?", (producto_id,))
    conn.commit()
    messagebox.showinfo("Eliminado", "Producto eliminado")

def exportar_productos():
    archivo = filedialog.asksaveasfilename(defaultextension=".txt")
    cursor.execute("SELECT * FROM productos")
    registros = cursor.fetchall()
    with open(archivo, "w") as f:
        for r in registros:
            f.write(f"ID:{r[0]} | {r[1]} | {r[2]} | Cant:{r[3]} | Precio:${r[4]} | Cat:{r[5]}\n")
    messagebox.showinfo("Exportado", "Inventario exportado")

# --------------------------- ESTADÍSTICAS ---------------------------
def ver_estadisticas():
    cursor.execute("SELECT fecha_agregado, cantidad FROM productos")
    datos = cursor.fetchall()
    meses = {}
    for fecha, cantidad in datos:
        mes = fecha[:7]
        meses[mes] = meses.get(mes, 0) + cantidad
    
    plt.bar(meses.keys(), meses.values(), color="#8e44ad")
    plt.title("Productos agregados por mes")
    plt.xlabel("Mes")
    plt.ylabel("Cantidad")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# --------------------------- LOGIN ---------------------------
ventana_login = tk.Tk()
ventana_login.title("Login - Gestor Adriana")
ventana_login.geometry("400x300")
ventana_login.configure(bg="white")

tk.Label(ventana_login, text="Gestor de Comercio Adriana", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

tk.Label(ventana_login, text="Usuario", bg="white").pack()
entry_usuario = tk.Entry(ventana_login)
entry_usuario.pack(pady=5)

tk.Label(ventana_login, text="Contraseña", bg="white").pack()
entry_contra = tk.Entry(ventana_login, show="*")
entry_contra.pack(pady=5)

tk.Button(ventana_login, text="Ingresar", bg="#8e44ad", fg="white", command=login).pack(pady=10)
tk.Button(ventana_login, text="Registrarse", command=registrar_usuario).pack()
tk.Button(ventana_login, text="¿Olvidaste tu contraseña?", command=recuperar_contrasena, fg="blue", bg="white").pack(pady=5)

# --------------------------- EJECUCIÓN ---------------------------
crear_tablas()
crear_datos_iniciales()
ventana_login.mainloop()
