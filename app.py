from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(_name_)
app.secret_key = "stocar_secret"

# -------------------------
# CONEXIÓN DB
# -------------------------
def conectar():
    return sqlite3.connect("stokAR.db")


def crear_db():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        precio REAL,
        stock INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto_id INTEGER,
        cantidad INTEGER
    )
    """)

    # usuario admin por defecto
    c.execute("SELECT * FROM usuarios WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO usuarios VALUES (NULL, 'admin', '1234')")

    conn.commit()
    conn.close()


crear_db()

# -------------------------
# LOGIN
# -------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]

        conn = conectar()
        c = conn.cursor()

        c.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (user, password))
        usuario = c.fetchone()

        conn.close()

        if usuario:
            session["user"] = user
            return redirect("/dashboard")
        else:
            return "Usuario o contraseña incorrectos"

    return render_template("login.html")


# -------------------------
# DASHBOARD
# -------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT * FROM productos")
    productos = c.fetchall()

    conn.close()

    return render_template("dashboard.html", productos=productos)


# -------------------------
# AGREGAR PRODUCTO
# -------------------------
@app.route("/agregar", methods=["POST"])
def agregar():
    nombre = request.form["nombre"]
    precio = request.form["precio"]
    stock = request.form["stock"]

    conn = conectar()
    c = conn.cursor()

    c.execute("INSERT INTO productos VALUES (NULL, ?, ?, ?)", (nombre, precio, stock))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# -------------------------
# VENDER PRODUCTO
# -------------------------
@app.route("/vender/<int:id>")
def vender(id):
    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT stock FROM productos WHERE id=?", (id,))
    resultado = c.fetchone()

    if resultado:
        stock = resultado[0]

        if stock > 0:
            c.execute("UPDATE productos SET stock = stock - 1 WHERE id=?", (id,))
            c.execute("INSERT INTO ventas VALUES (NULL, ?, 1)", (id,))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")