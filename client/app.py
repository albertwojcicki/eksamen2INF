from flask import Flask, render_template, request, session, redirect, json, url_for, jsonify
import requests
from flask_cors import CORS
import sqlite3

app = Flask(__name__)


@app.route("/")
def index():
    data = requests.get("http://127.0.0.1:5020/").json()
    print(data)
    return render_template("index.html", data = data)

@app.route("/bok/<int:bok_nummer>", methods = ["POST"])
def bok(bok_nummer):
    response = requests.get(f"http://127.0.0.1:5020/bok/{bok_nummer}").json()
    print(response)
    return render_template("bok.html", data = response)

if __name__ == "__main__":
    app.run(debug=True)