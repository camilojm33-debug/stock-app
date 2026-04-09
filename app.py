from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "stokar_secret"


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

    c.execute("SELECT * FROM usuarios WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO usuarios VALUES(NULL,'admin','1234')")

    conn.commit()
    conn.close()


crear_db()


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pass"]

        conn = conectar()
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (user, pwd))
        user_db = c.fetchone()
        conn.close()

        if user_db:
            session["user"] = user_db[1]
            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT * FROM productos")
    productos = c.fetchall()

    c.execute("SELECT COUNT(*) FROM ventas")
    ventas = c.fetchone()[0]

    conn.close()

    return render_template("dashboard.html", productos=productos, ventas=ventas)


@app.route("/agregar", methods=["POST"])
def agregar():
    conn = conectar()
    c = conn.cursor()

    c.execute(
        "INSERT INTO productos VALUES(NULL,?,?,?)",
        (
            request.form["nombre"],
            request.form["precio"],
            request.form["stock"]
        )
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


@app.route("/vender/<int:id>")
def vender(id):
    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT stock FROM productos WHERE id=?", (id,))
    stock = c.fetchone()[0]

    if stock > 0:
        c.execute("UPDATE productos SET stock=? WHERE id=?", (stock - 1, id))
        c.execute("INSERT INTO ventas VALUES(NULL,?,1)", (id,))
        conn.commit()

    conn.close()
    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/test")
def test():
    return "FUNCIONA FLASK"


if __name__ == "__main__":
    app.run(debug=True)