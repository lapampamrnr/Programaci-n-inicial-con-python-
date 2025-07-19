# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sqlite3
import datetime
import os
import shutil

# Crear o conectar la base de datos
conn = sqlite3.connect("comercio.db")
c = conn.cursor()

# Crear tabla de usuarios
c.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL,
    contraseña TEXT NOT NULL,
    correo TEXT NOT NULL
)
""")

# Crear tabla de productos
c.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    categoria TEXT,
    precio REAL NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha TEXT
)
""")
conn.commit()

# Funciones principales
def registrar_usuario():
    def guardar():
        usuario = entry_usuario.get()
        contraseña = entry_contraseña.get()
        correo = entry_correo.get()
        if usuario and contraseña and correo:
            c.execute("INSERT INTO usuarios (usuario, contraseña, correo) VALUES (?, ?, ?)", (usuario, contraseña, correo))
            conn.commit()
            messagebox.showinfo("Registro", "Usuario registrado correctamente")
            ventana.destroy()
        else:
            messagebox.showwarning("Atención", "Complete todos los campos")

    ventana = tk.Toplevel()
    ventana.title("Registrar Usuario")

    tk.Label(ventana, text="Usuario").pack()
    entry_usuario = tk.Entry(ventana)
    entry_usuario.pack()

    tk.Label(ventana, text="Contraseña").pack()
    entry_contraseña = tk.Entry(ventana, show="*")
    entry_contraseña.pack()

    tk.Label(ventana, text="Correo").pack()
    entry_correo = tk.Entry(ventana)
    entry_correo.pack()

    tk.Button(ventana, text="Guardar", command=guardar).pack()

def iniciar_sesion():
    usuario = entry_usuario.get()
    contraseña = entry_contraseña.get()
    c.execute("SELECT * FROM usuarios WHERE usuario=? AND contraseña=?", (usuario, contraseña))
    if c.fetchone():
        messagebox.showinfo("Inicio de sesión", f"Bienvenido, {usuario}!")
        mostrar_menu_principal()
        login.destroy()
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")

def recuperar_contraseña():
    correo = entry_usuario.get()
    c.execute("SELECT contraseña FROM usuarios WHERE correo=?", (correo,))
    resultado = c.fetchone()
    if resultado:
        messagebox.showinfo("Recuperación", f"Tu contraseña es: {resultado[0]}")
    else:
        messagebox.showerror("Error", "Correo no encontrado")

def agregar_producto():
    def guardar():
        nombre = entry_nombre.get()
        categoria = entry_categoria.get()
        precio = float(entry_precio.get())
        cantidad = int(entry_cantidad.get())
        fecha = datetime.date.today().isoformat()
        c.execute("INSERT INTO productos (nombre, categoria, precio, cantidad, fecha) VALUES (?, ?, ?, ?, ?)",
                  (nombre, categoria, precio, cantidad, fecha))
        conn.commit()
        messagebox.showinfo("Producto", "Producto guardado correctamente")
        ventana.destroy()

    ventana = tk.Toplevel()
    ventana.title("Agregar Producto")

    tk.Label(ventana, text="Nombre").pack()
    entry_nombre = tk.Entry(ventana)
    entry_nombre.pack()

    tk.Label(ventana, text="Categoría").pack()
    entry_categoria = tk.Entry(ventana)
    entry_categoria.pack()

    tk.Label(ventana, text="Precio").pack()
    entry_precio = tk.Entry(ventana)
    entry_precio.pack()

    tk.Label(ventana, text="Cantidad").pack()
    entry_cantidad = tk.Entry(ventana)
    entry_cantidad.pack()

    tk.Button(ventana, text="Registrar Producto", command=guardar).pack()

def ver_productos():
    ventana = tk.Toplevel()
    ventana.title("Productos")

    tree = ttk.Treeview(ventana, columns=("ID", "Nombre", "Categoría", "Precio", "Cantidad", "Fecha"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    for row in c.execute("SELECT * FROM productos"):
        tree.insert("", "end", values=row)

def eliminar_producto():
    def eliminar():
        id_producto = entry_id.get()
        c.execute("DELETE FROM productos WHERE id=?", (id_producto,))
        conn.commit()
        messagebox.showinfo("Eliminar", "Producto eliminado")
        ventana.destroy()

    ventana = tk.Toplevel()
    ventana.title("Eliminar Producto")

    tk.Label(ventana, text="ID del producto a eliminar").pack()
    entry_id = tk.Entry(ventana)
    entry_id.pack()
    tk.Button(ventana, text="Eliminar", command=eliminar).pack()

def exportar_txt():
    with open("productos.txt", "w") as file:
        for row in c.execute("SELECT * FROM productos"):
            file.write(str(row) + "\n")
    messagebox.showinfo("Exportar", "Productos exportados a productos.txt")

def crear_backup():
    shutil.copy("comercio.db", "backup_comercio.db")
    messagebox.showinfo("Backup", "Backup creado exitosamente")

def mostrar_estadisticas():
    total_productos = c.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
    total_valor = c.execute("SELECT SUM(precio * cantidad) FROM productos").fetchone()[0]
    messagebox.showinfo("Estadísticas",
                        f"Total de productos: {total_productos}\nValor total: ${total_valor:.2f}")

def ver_usuarios():
    ventana = tk.Toplevel()
    ventana.title("Usuarios Registrados")
    for row in c.execute("SELECT id, usuario, correo FROM usuarios"):
        tk.Label(ventana, text=str(row)).pack()

def mostrar_menu_principal():
    menu = tk.Tk()
    menu.title("Gestor de Comercio Adriana")
    menu.geometry("600x500")
    menu.configure(bg="#d0e4f5")

    botones = [
        ("Agregar Usuario", registrar_usuario),
        ("Agregar Producto", agregar_producto),
        ("Ver Productos", ver_productos),
        ("Eliminar Producto", eliminar_producto),
        ("Exportar a TXT", exportar_txt),
        ("Crear Backup BD", crear_backup),
        ("Estadísticas", mostrar_estadisticas),
        ("Ver Usuarios", ver_usuarios),
        ("Salir", menu.quit)
    ]

    for texto, comando in botones:
        tk.Button(menu, text=texto, command=comando, width=30).pack(pady=5)

    menu.mainloop()

# Ventana de inicio de sesión
login = tk.Tk()
login.title("Login - Gestor Adriana")
login.geometry("400x300")

frame = tk.Frame(login)
frame.pack(pady=20)

label_usuario = tk.Label(frame, text="Usuario")
label_usuario.grid(row=0, column=0)
entry_usuario = tk.Entry(frame)
entry_usuario.grid(row=0, column=1)

label_contraseña = tk.Label(frame, text="Contraseña")
label_contraseña.grid(row=1, column=0)
entry_contraseña = tk.Entry(frame, show="*")
entry_contraseña.grid(row=1, column=1)

btn_login = tk.Button(login, text="Iniciar Sesión", command=iniciar_sesion)
btn_login.pack(pady=5)

btn_registro = tk.Button(login, text="Registrar Usuario", command=registrar_usuario)
btn_registro.pack(pady=5)

btn_olvido = tk.Button(login, text="Olvidé mi contraseña", command=recuperar_contraseña)
btn_olvido.pack(pady=5)

login.mainloop()
