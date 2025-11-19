import amarel
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/read-form", methods=["POST"])
def read_form():
    data = request.form
    file = request.files["userCode"]
    net_id = data["userNetID"]
    password = data["userPassword"]

    client = amarel.Amarel(net_id, password)

    res = client.run_file(file, file.filename)
    lines = res.splitlines()

    return render_template(
        "output.html",
        filename=file.filename,
        pipfile_contents=lines[0],
        output=lines[1:],
    )
