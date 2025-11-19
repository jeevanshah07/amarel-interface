# Importing required functions
import amarel
import re
from flask import Flask, request, render_template

# Flask constructor
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

    return res
