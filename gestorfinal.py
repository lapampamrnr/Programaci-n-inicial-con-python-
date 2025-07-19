import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import matplotlib.pyplot as plt

# -------------------- BASE DE DATOS -------------------- #
conexion = sqlite3.connect("comercio.db")
cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE,
    contrasena TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    descripcion TEXT,
    cantidad INTEGER,
    precio REAL,
    categoria TEXT,
    fecha TEXT
)
""")

# Productos precargados solo una vez
cursor.execute("SELECT COUNT(*) FROM productos")
if cursor.fetchone()[0] == 0:
    productos_ejemplo = [
        ("Leche La Serenísima", "Entera 1L", 20, 1100, "Lácteos", datetime.date.today()),
        ("Pan Lactal Bimbo", "Doble salvado", 15, 950, "Panadería", datetime.date.today()),
        ("Detergente Magistral", "Limón 500ml", 10, 1300, "Limpieza", datetime.date.today()),
        ("Batman", "Película DVD", 8, 2500, "Películas", datetime.date.today())
    ]
    cursor.executemany("INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria, fecha) VALUES (?, ?, ?, ?, ?, ?)", productos_ejemplo)
    conexion.commit()

# Usuario admin por defecto
try:
    cursor.execute("INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)", ("admin", "admin123"))
    conexion.commit()
except:
    pass

conexion.close()

# -------------------- FUNCIONES -------------------- #
def abrir_panel(usuario_actual):
    ventana_login.destroy()
    panel = tk.Tk()
    panel.title("Gestor de Comercio Adriana")
    panel.geometry("1000x600")
    panel.config(bg="white")

    tk.Label(panel, text=f"Bienvenido/a: {usuario_actual}", bg="white", fg="black", font=("Arial", 12)).pack(pady=10)

    marco_botones = tk.Frame(panel, bg="white")
    marco_botones.pack(pady=20)

    def boton(texto, comando):
        return tk.Button(marco_botones, text=texto, width=20, height=2, bg="#E6E6FA", fg="black", font=("Arial", 10), command=comando)

    def ver_productos():
        conexion = sqlite3.connect("comercio.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()
        conexion.close()

        top = tk.Toplevel(panel)
        top.title("Lista de Productos")

        tree = ttk.Treeview(top, columns=("ID", "Nombre", "Descripción", "Cantidad", "Precio", "Categoría", "Fecha"), show='headings')
        for col in tree["columns"]:
            tree.heading(col, text=col)
        for p in productos:
            tree.insert('', 'end', values=p)
        tree.pack(expand=True, fill="both")

    def agregar_producto():
        def guardar():
            datos = (nombre.get(), desc.get(), int(cant.get()), float(precio.get()), cat.get(), datetime.date.today())
            conexion = sqlite3.connect("comercio.db")
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria, fecha) VALUES (?, ?, ?, ?, ?, ?)", datos)
            conexion.commit()
            conexion.close()
            messagebox.showinfo("Éxito", "Producto agregado")
            top.destroy()

        top = tk.Toplevel(panel)
        top.title("Agregar Producto")

        nombre = tk.Entry(top)
        desc = tk.Entry(top)
        cant = tk.Entry(top)
        precio = tk.Entry(top)
        cat = tk.Entry(top)

        for i, txt in enumerate(["Nombre", "Descripción", "Cantidad", "Precio", "Categoría"]):
            tk.Label(top, text=txt).grid(row=i, column=0)
        for i, ent in enumerate([nombre, desc, cant, precio, cat]):
            ent.grid(row=i, column=1)

        tk.Button(top, text="Guardar", command=guardar).grid(row=5, column=0, columnspan=2)

    def eliminar_producto():
        def eliminar():
            conexion = sqlite3.connect("comercio.db")
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM productos WHERE id = ?", (int(entry.get()),))
            conexion.commit()
            conexion.close()
            messagebox.showinfo("Éxito", "Producto eliminado")
            top.destroy()

        top = tk.Toplevel(panel)
        top.title("Eliminar Producto")
        tk.Label(top, text="ID del producto a eliminar:").pack()
        entry = tk.Entry(top)
        entry.pack()
        tk.Button(top, text="Eliminar", command=eliminar).pack()

    def exportar_txt():
        conexion = sqlite3.connect("comercio.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()
        conexion.close()
        with open("inventario.txt", "w") as f:
            for p in productos:
                f.write(f"{p}\n")
        messagebox.showinfo("Exportado", "Inventario exportado como TXT")

    def ver_estadisticas():
        conexion = sqlite3.connect("comercio.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT fecha, cantidad FROM productos")
        datos = cursor.fetchall()
        conexion.close()

        meses = {}
        for fecha, cant in datos:
            mes = fecha[:7]  # YYYY-MM
            meses[mes] = meses.get(mes, 0) + cant

        plt.bar(meses.keys(), meses.values())
        plt.title("Estadísticas de productos por mes")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def salir():
        panel.destroy()

    botones = [
        ("Ver Productos", ver_productos),
        ("Agregar Producto", agregar_producto),
        ("Eliminar Producto", eliminar_producto),
        ("Exportar a TXT", exportar_txt),
        ("Ver Estadísticas", ver_estadisticas),
        ("Salir", salir)
    ]

    for i, (txt, cmd) in enumerate(botones):
        boton(txt, cmd).grid(row=i//2, column=i%2, padx=10, pady=10)

    panel.mainloop()

# -------------------- LOGIN -------------------- #
ventana_login = tk.Tk()
ventana_login.title("Ingreso al Gestor de Comercio")
ventana_login.geometry("400x300")
ventana_login.config(bg="#E6E6FA")

usuario = tk.Entry(ventana_login)
contrasena = tk.Entry(ventana_login, show="*")

usuario.insert(0, "admin")
contrasena.insert(0, "admin123")

tk.Label(ventana_login, text="Usuario", bg="#E6E6FA").pack()
usuario.pack()
tk.Label(ventana_login, text="Contraseña", bg="#E6E6FA").pack()
contrasena.pack()

def login():
    u = usuario.get()
    c = contrasena.get()
    conexion = sqlite3.connect("comercio.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND contrasena=?", (u, c))
    if cursor.fetchone():
        abrir_panel(u)
    else:
        messagebox.showerror("Error", "Credenciales incorrectas")
    conexion.close()

def registrar():
    u = usuario.get()
    c = contrasena.get()
    conexion = sqlite3.connect("comercio.db")
    cursor = conexion.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)", (u, c))
        conexion.commit()
        messagebox.showinfo("Registrado", "Usuario registrado")
    except:
        messagebox.showerror("Error", "Ese usuario ya existe")
    conexion.close()

tk.Button(ventana_login, text="Ingresar", command=login, bg="#D8BFD8").pack(pady=5)
tk.Button(ventana_login, text="Registrarse", command=registrar, bg="#D8BFD8").pack(pady=5)

ventana_login.mainloop()
