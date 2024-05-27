from flask import Flask, render_template, request, session, redirect, json, url_for, jsonify
import requests
from flask_cors import CORS
import sqlite3

app = Flask(__name__)

con = sqlite3.connect("database.db", check_same_thread=False)
cur = con.cursor()


@app.route("/")
def index():
    cur.execute("SELECT * FROM bøker")
    response = cur.fetchall()
    return jsonify(response)



if __name__ == "__main__":
    app.run(debug=True)