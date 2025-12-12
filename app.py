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


@app.route("/status")
def status():
    if "user" not in session:
        return redirect(url_for("/"))

    client = amarel.Amarel(session["user"], session["password"])
    job_name = request.args.get("name")

    status = client.check_status(job_name or "")
    if len(status) == 0:
        return render_template(
            "output.html",
            filename=job_name,
            pipfile_contents="",
            output="",
            status=False,
        )
    else:
        return render_template(
            "output.html",
            filename=job_name,
            pipfile_contents=status[0],
            output=status[1:],
            status=True,
        )


@app.route("/main")
def main():
    if "user" not in session:
        return redirect(url_for("/"))

    client = amarel.Amarel(session["user"], session["password"])
    jobs = client.get_jobs()
    succ = True

    return render_template("main.html", jobs=jobs, succ=succ)


@app.route("/read-form", methods=["POST"])
def read_form():
    data = request.form
    net_id = data["userNetID"]
    password = data["userPassword"]

    client = amarel.Amarel(net_id, password)
    if client.authenticate():
        session["user"] = net_id
        session["password"] = password
        client.create_table()
    else:
        return render_template("error.html")

    jobs = client.get_jobs()
    succ = True

    return render_template("main.html", jobs=jobs, succ=succ)


@app.route("/upload", methods=["GET"])
def upload():
    return render_template("dashboard.html")


@app.route("/dashboard", methods=["POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("/"))

    data = request.form

    file = request.files["userCode"]
    partition = data["partition"]
    filename = data["jobName"]
    nodes = data["numNodes"]
    ram = data["ram"]
    tasks = data["numTasks"]
    cores = data["numCores"]
    runtime = data["time"]

    client = amarel.Amarel(session["user"], session["password"])
    client.run_file(
        file,
        filename=filename,
        nodes=nodes,
        tasks=tasks,
        cores=cores,
        mem=ram,
        runtime=runtime,
        partition=partition,
    )
    succ = client.write_job(filename or "", "active")

    jobs = client.get_jobs()

    return render_template("main.html", jobs=jobs, succ=succ)

    # lines = res.splitlines()
    #
    # return render_template(
    #     "output.html",
    #     filename=file.filename,
    #     pipfile_contents=lines[0],
    #     output=lines[1:],
    # )


@app.route("/download")
def download():
    output = request.args.get("data", "")
    filename = f"amarel-output-{datetime.today().strftime('%Y%m%d')}"

    response = make_response(output)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}.txt"
    response.headers["Content-Type"] = "text/plain"

    return response
