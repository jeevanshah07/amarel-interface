import amarel
from datetime import datetime
from flask import (
    Flask,
    make_response,
    redirect,
    request,
    render_template,
    session,
    url_for,
)

app = Flask(__name__)
app.secret_key = "amarel"


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/read-form", methods=["POST"])
def read_form():
    data = request.form
    net_id = data["userNetID"]
    password = data["userPassword"]

    client = amarel.Amarel(net_id, password)
    if client.authenticate():
        session["user"] = net_id
        session["password"] = password
    else:
        return render_template("error.html")

    return render_template("dashboard.html")


@app.route("/upload", methods=["GET"])
def upload():
    return render_template("dashboard.html")


@app.route("/dashboard", methods=["POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("/"))

    file = request.files["userCode"]

    client = amarel.Amarel(session["user"], session["password"])
    res = client.run_file(file, file.filename)
    lines = res.splitlines()

    return render_template(
        "output.html",
        filename=file.filename,
        pipfile_contents=lines[0],
        output=lines[1:],
    )


@app.route("/download")
def download():
    output = request.args.get("data", "")
    filename = f"amarel-output-{datetime.today().strftime('%Y%m%d')}"

    response = make_response(output)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}.txt"
    response.headers["Content-Type"] = "text/plain"

    return response
