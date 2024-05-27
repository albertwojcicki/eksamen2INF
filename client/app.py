from flask import Flask, render_template, request, session, redirect, json, url_for, jsonify
import requests
from flask_cors import CORS
import sqlite3

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    query = request.form.get("filter_streng")
    if query:
        response = requests.get(f"http://127.0.0.1:5020/filter/{query}")
    else:
        response = requests.get("http://127.0.0.1:5020/")
    books = response.json()
    return render_template("index.html", data=books)

@app.route("/bok/<int:bok_nummer>", methods=["POST"])
def bok(bok_nummer):
    response = requests.get(f"http://127.0.0.1:5020/bok/{bok_nummer}").json()
    return render_template("bok.html", data=response)

@app.route("/filter", methods = ["POST"])
def filter():
    filter_streng = request.form.get("filter_streng")
    response = requests.get(f"http://127.0.0.1:5020/filter/{filter_streng}").json()
    print(response)
    return render_template("index.html", data = response)

if __name__ == "__main__":
    app.run(debug=True)