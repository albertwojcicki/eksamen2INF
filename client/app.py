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



if __name__ == "__main__":
    app.run(debug=True)