from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/reportar")
def reportar():
    return "<h1>?? Reportar un problema</h1><p>Aquí irá el formulario.</p>"

@app.route("/problemas")
def problemas():
    return "<h1>?? Ver problemas</h1><p>Aquí irá la lista de problemas.</p>"

@app.route("/calendario")
def calendario():
    return "<h1>?? Calendario</h1><p>Aquí irán los eventos.</p>"

@app.route("/noticias")
def noticias():
    return "<h1>?? Noticias</h1><p>Aquí irán los avisos del colegio.</p>"

@app.route("/ideas")
def ideas():
    return "<h1>?? Ideas de estudiantes</h1><p>Aquí los estudiantes podrán enviar propuestas.</p>"

if __name__ == "__main__":
    app.run(debug=True)