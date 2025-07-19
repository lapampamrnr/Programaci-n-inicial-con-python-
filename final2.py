# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
import sqlite3, datetime, os, shutil

# --- Configuración base de datos ---
DB = "gestor_adriana.db"
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     usuario TEXT UNIQUE, contrasena TEXT, correo TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS productos (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     nombre TEXT, descripcion TEXT, categoria TEXT,
     precio REAL, cantidad INTEGER, fecha TEXT)""")
conn.commit()

# --- Carga inicial de productos de ejemplo ---
if c.execute("SELECT COUNT(*) FROM productos").fetchone()[0] == 0:
    ejemplos = [
        ("Leche", "Entera 1L", "Lácteos", 1100.0, 20),
        ("Pan Lactal", "Grande", "Panadería", 950.0, 25),
        ("Película Batman", "DVD", "Películas", 2500.0, 5),
    ]
    hoy = datetime.date.today().isoformat()
    for n,d,cat,p,q in ejemplos:
        c.execute("INSERT INTO productos VALUES (NULL,?,?,?,?,?,?)",
                  (n,d,cat,p,q,hoy))
    conn.commit()

# --- Funciones ---
def registrar_usuario():
    v = tk.Toplevel(); v.title("Registrar Usuario")
    for text in ["Usuario","Contraseña","Correo (opcional)"]:
        tk.Label(v, text=text).pack()
        tk.Entry(v).pack()
    en_u, en_p, en_c = v.winfo_children()[1], v.winfo_children()[3], v.winfo_children()[5]
    def guardar():
        u,p,corr = en_u.get(), en_p.get(), en_c.get()
        if not(u and p): messagebox.showwarning("Datos", "Usuario y contraseña obligatorios"); return
        try:
            c.execute("INSERT INTO usuarios (usuario,contrasena,correo) VALUES (?,?,?)",(u,p,corr))
            conn.commit(); messagebox.showinfo("OK","Usuario registrado"); v.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error","Ese usuario ya existe")
    tk.Button(v, text="Guardar", command=guardar).pack(pady=5)

def iniciar_sesion():
    u,p = en_user.get(), en_pass.get()
    if c.execute("SELECT * FROM usuarios WHERE usuario=? AND contrasena=?",(u,p)).fetchone():
        messagebox.showinfo("Bienvenida", f"¡Bienvenida, {u}!")
        login.destroy(); menu_principal(u)
    else:
        messagebox.showerror("Error", "Credenciales incorrectas")

def recuperar_contrasena():
    u = simpledialog.askstring("Recuperar", "Ingrese su usuario:")
    res = c.execute("SELECT correo,contrasena FROM usuarios WHERE usuario=?", (u,)).fetchone()
    if res:
        correo, cont = res
        if correo:
            messagebox.showinfo("Contraseña", f"Se envió a {correo} (simulado): {cont}")
        else:
            messagebox.showwarning("Sin correo","El usuario no tiene correo")
    else:
        messagebox.showerror("Error","Usuario no encontrado")

def agregar_producto():
    v = tk.Toplevel(); v.title("Agregar Producto")
    labels = ["Nombre","Descripción","Categoría","Precio","Cantidad"]
    entries = []
    for t in labels:
        tk.Label(v,text=t).pack(); entries.append(tk.Entry(v)); entries[-1].pack()
    def guardar():
        try:
            n,d,cat,p,q = [e.get() for e in entries]
            p=float(p); q=int(q)
        except:
            messagebox.showwarning("Error","Verifique datos"); return
        fecha = datetime.date.today().isoformat()
        c.execute("""INSERT INTO productos
                     (nombre,descripcion,categoria,precio,cantidad,fecha)
                     VALUES (?,?,?,?,?,?)""",(n,d,cat,p,q,fecha))
        conn.commit(); messagebox.showinfo("OK","Producto agregado"); v.destroy()
    tk.Button(v,text="Guardar",command=guardar).pack(pady=5)

def ver_productos():
    v = tk.Toplevel(); v.title("Lista de Productos")
    cols=["ID","Nombre","Desc","Cat","Precio","Cant","Fecha"]
    tree = ttk.Treeview(v,columns=cols,show="headings")
    for col in cols: tree.heading(col,text=col)
    for row in c.execute("SELECT * FROM productos"): tree.insert("",tk.END,values=row)
    tree.pack(expand=True,fill="both")

def eliminar_producto():
    pid = simpledialog.askinteger("Eliminar","Ingrese ID del producto:")
    if pid:
        if c.execute("SELECT * FROM productos WHERE id=?", (pid,)).fetchone():
            c.execute("DELETE FROM productos WHERE id=?", (pid,))
            conn.commit(); messagebox.showinfo("OK","Producto eliminado")
        else:
            messagebox.showwarning("Error","ID no encontrado")

def actualizar_producto():
    pid = simpledialog.askinteger("Actualizar","ID del producto a actualizar:")
    row = c.execute("SELECT * FROM productos WHERE id=?", (pid,)).fetchone()
    if not row:
        return messagebox.showwarning("Error","ID no encontrado")
    v = tk.Toplevel(); v.title("Actualizar Producto")
    labels=["Nombre","Descripción","Categoría","Precio","Cantidad"]
    entries = []
    for i,t in enumerate(labels, start=1):
        tk.Label(v,text=t).pack()
        e=tk.Entry(v); e.insert(0,row[i]); e.pack()
        entries.append(e)
    def guardar():
        try:
            n,d,cat,p,q=[e.get() for e in entries]; p=float(p); q=int(q)
        except:
            return messagebox.showwarning("Error","Verifique datos")
        c.execute("""UPDATE productos
                     SET nombre=?,descripcion=?,categoria=?,precio=?,cantidad=?
                     WHERE id=?""",(n,d,cat,p,q,pid))
        conn.commit(); messagebox.showinfo("OK","Producto actualizado"); v.destroy()
    tk.Button(v,text="Actualizar",command=guardar).pack(pady=5)

def buscar_producto():
    pid = simpledialog.askinteger("Buscar","ID del producto:")
    row = c.execute("SELECT * FROM productos WHERE id=?", (pid,)).fetchone()
    if row:
        messagebox.showinfo("Producto", str(row))
    else:
        messagebox.showwarning("No encontrado","ID no existe")

def generar_reporte():
    rows = c.execute("SELECT id,nombre,categoria,cantidad,precio FROM productos").fetchall()
    with open("reporte_resto.txt","w") as f:
        for r in rows: f.write(f"{r}\n")
    messagebox.showinfo("Reporte","Archivo reporte_resto.txt generado")

def ver_estadisticas():
    tot = c.execute("SELECT COUNT(*),SUM(cantidad),SUM(precio*cantidad) FROM productos").fetchone()
    messagebox.showinfo("Estadísticas",
        f"Productos distintos: {tot[0]}\nTotal unidades: {tot[1] or 0}\nValor total: ${tot[2] or 0:.2f}")

def ver_estadisticas_mensuales_anuales():
    rows = c.execute("SELECT fecha,cantidad,precio FROM productos").fetchall()
    mes = {}
    ani = {}
    for f,cant,pr in rows:
        a,m,_ = f.split("-")
        total = cant*pr
        mes[m]=mes.get(m,0)+total
        ani[a]=ani.get(a,0)+total
    text = "⭐ Por mes:\n"+ "\n".join(f"{m}: ${v:.2f}" for m,v in mes.items())
    text += "\n\n⭐ Por año:\n" + "\n".join(f"{a}: ${v:.2f}" for a,v in ani.items())
    messagebox.showinfo("Estadísticas Detalladas", text)

def exportar_txt(): generar_reporte()
def crear_backup():
    conn.close(); shutil.copy(DB, "backup_"+DB); messagebox.showinfo("Backup","Copia creada")
def acerca_de():
    messagebox.showinfo("Acerca de","Gestor Adriana\nAutora: Marcela Adriana Serrano")

def ver_usuarios():
    rows = c.execute("SELECT id,usuario,correo FROM usuarios").fetchall()
    text = "\n".join(str(r) for r in rows)
    messagebox.showinfo("Usuarios", text)

# --- Interfaz principal (post-login) ---
def menu_principal(u):
    m = tk.Tk(); m.title("Gestor Comercio Adriana"); m.geometry("500x600")
    botones = [
        ("➕ Agregar Usuario", registrar_usuario),
        ("🛒 Agregar Producto", agregar_producto),
        ("📦 Ver Productos", ver_productos),
        ("🗑️ Eliminar Producto", eliminar_producto),
        ("🔄 Actualizar Producto", actualizar_producto),
        ("🔍 Buscar por ID", buscar_producto),
        ("📝 Generar Reporte", generar_reporte),
        ("📤 Exportar TXT", exportar_txt),
        ("📊 Estadísticas", ver_estadisticas),
        ("📆 Estadísticas Mens/Anual", ver_estadisticas_mensuales_anuales),
        ("💾 Crear Backup", crear_backup),
        ("ℹ️ Acerca de", acerca_de),
        ("🚪 Salir", m.destroy),
    ]
    if u == "admin":
        botones.insert(1, ("👤 Ver Usuarios", ver_usuarios))
    for txt,cmd in botones:
        tk.Button(m, text=txt, width=30, command=cmd).pack(pady=5)
    m.mainloop()

# --- Ventana de login ---
login = tk.Tk(); login.title("Login - Gestor Adriana"); login.geometry("400x300")
frame = tk.Frame(login); frame.pack(pady=20)
tk.Label(frame,text="Usuario").grid(row=0,column=0); en_user=tk.Entry(frame); en_user.grid(row=0,column=1)
tk.Label(frame,text="Contraseña").grid(row=1,column=0); en_pass=tk.Entry(frame,show="*"); en_pass.grid(row=1,column=1)
tk.Button(login,text="Iniciar Sesión",command=iniciar_sesion).pack(pady=5)
tk.Button(login,text="Registrar Usuario",command=registrar_usuario).pack(pady=3)
tk.Button(login,text="Olvidé mi contraseña",command=recuperar_contrasena).pack(pady=3)
login.mainloop()
