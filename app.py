import os
import psycopg2
import psycopg2.extras
import cloudinary
import cloudinary.uploader
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "clave-secreta-colegio-2026"

ADMIN_USUARIO = "admin"
ADMIN_CLAVE = "colegio123"

DATABASE_URL = os.environ.get("DATABASE_URL")
import os
import cloudinary

cloudinary.config(
    cloudinary_url=os.environ.get("CLOUDINARY_URL"),
    secure=True
)

def get_conexion():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)


def crear_tablas():
    conexion = get_conexion()
    cur = conexion.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reportes (
            id SERIAL PRIMARY KEY,
            tipo TEXT,
            lugar TEXT,
            descripcion TEXT,
            estado TEXT,
            foto TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS noticias (
            id SERIAL PRIMARY KEY,
            titulo TEXT,
            contenido TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id SERIAL PRIMARY KEY,
            fecha TEXT,
            titulo TEXT,
            descripcion TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ideas (
            id SERIAL PRIMARY KEY,
            texto TEXT,
            votos INTEGER DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bullying (
            id SERIAL PRIMARY KEY,
            grado TEXT,
            descripcion TEXT,
            estado TEXT
        )
    """)
    conexion.commit()
    cur.close()
    conexion.close()


crear_tablas()


@app.route("/")
def seleccion():
    return render_template("seleccion.html")


@app.route("/estudiante")
def modo_estudiante():
    session.pop("es_admin", None)
    return redirect(url_for("inicio"))


@app.route("/inicio")
def inicio():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]
        if usuario == ADMIN_USUARIO and clave == ADMIN_CLAVE:
            session["es_admin"] = True
            return redirect(url_for("inicio"))
        else:
            error = "Usuario o clave incorrectos"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("es_admin", None)
    return redirect(url_for("seleccion"))


@app.route("/reportar", methods=["GET", "POST"])
def reportar():
    if request.method == "POST":
        tipo = request.form["tipo"]
        lugar = request.form["lugar"]
        descripcion = request.form["descripcion"]

        foto = request.files.get("foto")
        url_foto = None
        if foto and foto.filename != "":
            resultado = cloudinary.uploader.upload(foto)
            url_foto = resultado["secure_url"]

        conexion = get_conexion()
        cur = conexion.cursor()
        cur.execute(
            "INSERT INTO reportes (tipo, lugar, descripcion, estado, foto) VALUES (%s, %s, %s, %s, %s)",
            (tipo, lugar, descripcion, "Pendiente", url_foto)
        )
        conexion.commit()
        cur.close()
        conexion.close()
        return "<h1>Gracias por tu reporte!</h1><p>Ya lo registramos.</p><a href='/reportar'>Enviar otro</a>"
    return render_template("reportar.html")


@app.route("/problemas")
def problemas():
    es_admin = session.get("es_admin", False)
    conexion = get_conexion()
    cur = conexion.cursor()
    cur.execute("SELECT * FROM reportes ORDER BY id")
    reportes = cur.fetchall()
    cur.close()
    conexion.close()
    return render_template("problemas.html", reportes=reportes, es_admin=es_admin)


@app.route("/problemas/estado/<int:reporte_id>", methods=["POST"])
def cambiar_estado(reporte_id):
    if not session.get("es_admin"):
        return redirect(url_for("problemas"))
    nuevo_estado = request.form["estado"]
    conexion = get_conexion()
    cur = conexion.cursor()
    cur.execute("UPDATE reportes SET estado = %s WHERE id = %s", (nuevo_estado, reporte_id))
    conexion.commit()
    cur.close()
    conexion.close()
    return redirect(url_for("problemas"))


@app.route("/problemas/borrar/<int:reporte_id>", methods=["POST"])
def borrar_reporte(reporte_id):
    if not session.get("es_admin"):
        return redirect(url_for("problemas"))
    conexion = get_conexion()
    cur = conexion.cursor()
    cur.execute("DELETE FROM reportes WHERE id = %s", (reporte_id,))
    conexion.commit()
    cur.close()
    conexion.close()
    return redirect(url_for("problemas"))


@app.route("/calendario", methods=["GET", "POST"])
def calendario():
    es_admin = session.get("es_admin", False)
    conexion = get_conexion()
    cur = conexion.cursor()
    if request.method == "POST" and es_admin:
        fecha = request.form["fecha"]
        titulo = request.form["titulo"]
        descripcion = request.form["descripcion"]
        cur.execute(
            "INSERT INTO eventos (fecha, titulo, descripcion) VALUES (%s, %s, %s)",
            (fecha, titulo, descripcion)
        )
        conexion.commit()
    cur.execute("SELECT * FROM eventos ORDER BY fecha")
    eventos = cur.fetchall()
    cur.close()
    conexion.close()
    return render_template("calendario.html", eventos=eventos, es_admin=es_admin)


@app.route("/calendario/borrar/<int:evento_id>", methods=["POST"])
def borrar_evento(evento_id):
    if not session.get("es_admin"):
        return redirect(url_for("calendario"))
    conexion = get_conexion()
    cur = conexion.cursor()
    cur.execute("DELETE FROM eventos WHERE id = %s", (evento_id,))
    conexion.commit()
    cur.close()
    conexion.close()
    return redirect(url_for("calendario"))


@app.route("/noticias", methods=["GET", "POST"])
def pagina_noticias():
    es_admin = session.get("es_admin", False)
    conexion = get_conexion()
    cur = conexion.cursor()
    if request.method == "POST" and es_admin:
        titulo = request.form["titulo"]
        contenido = request.form["contenido"]
        cur.execute(
            "INSERT INTO noticias (titulo, contenido) VALUES (%s, %s)",
            (titulo, contenido)
        )
        conexion.commit()
    cur.execute("SELECT * FROM noticias ORDER BY id DESC")
    noticias = cur.fetchall()
    cur.close()
    conexion.close()
    return render_template("noticias.html", noticias=noticias, es_admin=es_admin)


@app.route("/noticias/borrar/<int:noticia_id>", methods=["POST"])
def borrar_noticia(noticia_id):
    if not session.get("es_admin"):
        return redirect(url_for("pagina_noticias"))
    conexion = get_conexion()
    cur = conexion.cursor()
    cur.execute("DELETE FROM noticias WHERE id = %s", (noticia_id,))
    conexion.commit()
    cur.close()
    conexion.close()
    return redirect(url_for("pagina_noticias"))


@app.route("/ideas", methods=["GET", "POST"])
def pagina_ideas():
    es_admin = session.get("es_admin", False)
    clave_votos = "ideas_votadas_admin" if es_admin else "ideas_votadas_estudiante"
    ideas_votadas = session.get(clave_votos, [])
    conexion = get_conexion()
    cur = conexion.cursor()
    if request.method == "POST":
        texto = request.form["idea"]
        cur.execute("INSERT INTO ideas (texto, votos) VALUES (%s, 0)", (texto,))
        conexion.commit()
    cur.execute("SELECT * FROM ideas ORDER BY votos DESC, id")
    ideas = cur.fetchall()
    cur.close()
    conexion.close()
    return render_template("ideas.html", ideas=ideas, es_admin=es_admin, ideas_votadas=ideas_votadas)


@app.route("/ideas/votar/<int:idea_id>", methods=["POST"])
def votar_idea(idea_id):
    es_admin = session.get("es_admin", False)
    clave_votos = "ideas_votadas_admin" if es_admin else "ideas_votadas_estudiante"
    ideas_votadas = session.get(clave_votos, [])
    if idea_id not in ideas_votadas:
        conexion = get_conexion()
        cur = conexion.cursor()
        cur.execute("UPDATE ideas SET votos = votos + 1 WHERE id = %s", (idea_id,))
        conexion.commit()
        cur.close()
        conexion.close()
        ideas_votadas.append(idea_id)
        session[clave_votos] = ideas_votadas
    return redirect(url_for("pagina_ideas"))


@app.route("/ideas/borrar/<int:idea_id>", methods=["POST"])
def borrar_idea(idea_id):
    if not session.get("es_admin"):
        return redirect(url_for("pagina_ideas"))
    conexion = get_conexion()
    cur = conexion.cursor()
    cur.execute("DELETE FROM ideas WHERE id = %s", (idea_id,))
    conexion.commit()
    cur.close()
    conexion.close()
    return redirect(url_for("pagina_ideas"))


@app.route("/bullying", methods=["GET", "POST"])
def pagina_bullying():
    es_admin = session.get("es_admin", False)
    conexion = get_conexion()
    cur = conexion.cursor()
    if request.method == "POST":
        grado = request.form["grado"]
        descripcion = request.form["descripcion"]
        cur.execute(
            "INSERT INTO bullying (grado, descripcion, estado) VALUES (%s, %s, %s)",
            (grado, descripcion, "Pendiente")
        )
        conexion.commit()
    cur.execute("SELECT * FROM bullying ORDER BY id")
    bullying = cur.fetchall()
    cur.close()
    conexion.close()
    return render_template("bullying.html", bullying=bullying, es_admin=es_admin)


@app.route("/bullying/estado/<int:reporte_id>", methods=["POST"])
def cambiar_estado_bullying(reporte_id):
    if not session.get("es_admin"):
        return redirect(url_for("pagina_bullying"))
    nuevo_estado = request.form["estado"]
    conexion = get_conexion()
    cur = conexion.cursor()
    cur.execute("UPDATE bullying SET estado = %s WHERE id = %s", (nuevo_estado, reporte_id))
    conexion.commit()
    cur.close()
    conexion.close()
    return redirect(url_for("pagina_bullying"))


@app.route("/bullying/borrar/<int:reporte_id>", methods=["POST"])
def borrar_bullying(reporte_id):
    if not session.get("es_admin"):
        return redirect(url_for("pagina_bullying"))
    conexion = get_conexion()
    cur = conexion.cursor()
    cur.execute("DELETE FROM bullying WHERE id = %s", (reporte_id,))
    conexion.commit()
    cur.close()
    conexion.close()
    return redirect(url_for("pagina_bullying"))


if __name__ == "__main__":
    app.run(debug=True)
