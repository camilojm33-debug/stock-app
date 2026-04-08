from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "stocar_secret"


# ---------------------------
# DB
# ---------------------------
def conectar():
    return sqlite3.connect("stokaR.db")


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

    c.execute("SELECT * FROM usuarios WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO usuarios VALUES (NULL, 'admin', '1234')")

    conn.commit()
    conn.close()


# ---------------------------
# LOGIN
# ---------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")

        conn = conectar()
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (user, pwd))
        usuario = c.fetchone()
        conn.close()

        if usuario:
            session["usuario"] = user
            return redirect("/dashboard")

    return render_template("login.html")


# ---------------------------
# DASHBOARD
# ---------------------------
@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect("/")

    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT * FROM productos")
    productos = c.fetchall()

    c.execute("SELECT * FROM ventas")
    ventas = c.fetchall()

    conn.close()

    return render_template("dashboard.html", productos=productos, ventas=ventas)


# ---------------------------
# AGREGAR PRODUCTO
# ---------------------------
@app.route("/agregar", methods=["POST"])
def agregar():
    if "usuario" not in session:
        return redirect("/")

    nombre = request.form.get("nombre")
    precio = request.form.get("precio")
    stock = request.form.get("stock")

    conn = conectar()
    c = conn.cursor()

    c.execute("INSERT INTO productos VALUES (NULL, ?, ?, ?)", (nombre, precio, stock))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------------------------
# VENDER PRODUCTO
# ---------------------------
@app.route("/vender/<int:id>")
def vender(id):
    if "usuario" not in session:
        return redirect("/")

    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT stock FROM productos WHERE id=?", (id,))
    stock = c.fetchone()

    if stock and stock[0] > 0:
        nuevo_stock = stock[0] - 1

        c.execute("UPDATE productos SET stock=? WHERE id=?", (nuevo_stock, id))
        c.execute("INSERT INTO ventas VALUES (NULL, ?, 1)", (id,))

        conn.commit()

    conn.close()

    return redirect("/dashboard")


# ---------------------------
# LOGOUT
# ---------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------------------
# RUN
# ---------------------------
if __name__ == "_main_":
    crear_db()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)