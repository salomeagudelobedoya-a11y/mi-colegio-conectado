import os
import json
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "clave-secreta-colegio-2026"
app.config["UPLOAD_FOLDER"] = "static/uploads"

ADMIN_USUARIO = "admin"
ADMIN_CLAVE = "colegio123"

ARCHIVO_DATOS = "datos.json"


def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"reportes": [], "noticias": [], "eventos": [], "ideas": []}


def guardar_datos():
    datos = {
        "reportes": reportes,
        "noticias": noticias,
        "eventos": eventos,
        "ideas": ideas
    }
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


datos_guardados = cargar_datos()
reportes = datos_guardados["reportes"]
noticias = datos_guardados["noticias"]
eventos = datos_guardados["eventos"]
ideas = datos_guardados["ideas"]


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
        nombre_foto = None
        if foto and foto.filename != "":
            nombre_foto = foto.filename
            ruta = os.path.join(app.config["UPLOAD_FOLDER"], nombre_foto)
            foto.save(ruta)

        nuevo_id = len(reportes)
        reportes.append({
            "id": nuevo_id,
            "tipo": tipo,
            "lugar": lugar,
            "descripcion": descripcion,
            "estado": "Pendiente",
            "foto": nombre_foto
        })
        guardar_datos()
        return "<h1>Gracias por tu reporte!</h1><p>Ya lo registramos.</p><a href='/reportar'>Enviar otro</a>"
    return render_template("reportar.html")


@app.route("/problemas")
def problemas():
    es_admin = session.get("es_admin", False)
    return render_template("problemas.html", reportes=reportes, es_admin=es_admin)


@app.route("/problemas/estado/<int:reporte_id>", methods=["POST"])
def cambiar_estado(reporte_id):
    if not session.get("es_admin"):
        return redirect(url_for("problemas"))
    nuevo_estado = request.form["estado"]
    for r in reportes:
        if r["id"] == reporte_id:
            r["estado"] = nuevo_estado
            break
    guardar_datos()
    return redirect(url_for("problemas"))


@app.route("/problemas/borrar/<int:reporte_id>", methods=["POST"])
def borrar_reporte(reporte_id):
    if not session.get("es_admin"):
        return redirect(url_for("problemas"))
    global reportes
    reportes = [r for r in reportes if r["id"] != reporte_id]
    guardar_datos()
    return redirect(url_for("problemas"))


@app.route("/calendario", methods=["GET", "POST"])
def calendario():
    es_admin = session.get("es_admin", False)
    if request.method == "POST" and es_admin:
        fecha = request.form["fecha"]
        titulo = request.form["titulo"]
        descripcion = request.form["descripcion"]
        nuevo_id = len(eventos)
        eventos.append({"id": nuevo_id, "fecha": fecha, "titulo": titulo, "descripcion": descripcion})
        eventos.sort(key=lambda e: e["fecha"])
        guardar_datos()
    return render_template("calendario.html", eventos=eventos, es_admin=es_admin)


@app.route("/calendario/borrar/<int:evento_id>", methods=["POST"])
def borrar_evento(evento_id):
    if not session.get("es_admin"):
        return redirect(url_for("calendario"))
    global eventos
    eventos = [e for e in eventos if e["id"] != evento_id]
    guardar_datos()
    return redirect(url_for("calendario"))


@app.route("/noticias", methods=["GET", "POST"])
def pagina_noticias():
    es_admin = session.get("es_admin", False)
    if request.method == "POST" and es_admin:
        titulo = request.form["titulo"]
        contenido = request.form["contenido"]
        nuevo_id = len(noticias)
        noticias.insert(0, {"id": nuevo_id, "titulo": titulo, "contenido": contenido})
        guardar_datos()
    return render_template("noticias.html", noticias=noticias, es_admin=es_admin)


@app.route("/noticias/borrar/<int:noticia_id>", methods=["POST"])
def borrar_noticia(noticia_id):
    if not session.get("es_admin"):
        return redirect(url_for("pagina_noticias"))
    global noticias
    noticias = [n for n in noticias if n["id"] != noticia_id]
    guardar_datos()
    return redirect(url_for("pagina_noticias"))


@app.route("/ideas", methods=["GET", "POST"])
def pagina_ideas():
    if request.method == "POST":
        texto = request.form["idea"]
        nuevo_id = len(ideas)
        ideas.append({"id": nuevo_id, "texto": texto, "votos": 0})
        guardar_datos()
    ideas_ordenadas = sorted(ideas, key=lambda i: i["votos"], reverse=True)
    return render_template("ideas.html", ideas=ideas_ordenadas)


@app.route("/ideas/votar/<int:idea_id>", methods=["POST"])
def votar_idea(idea_id):
    for i in ideas:
        if i["id"] == idea_id:
            i["votos"] += 1
            break
    guardar_datos()
    return redirect(url_for("pagina_ideas"))


if __name__ == "__main__":
    app.run(debug=True)