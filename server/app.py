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

@app.route("/bok/<bok_nummer")
def bok(bok_nummer):
    cur.execute("SELECT * FROM bøker WHERE bok_nummer = )", (bok_nummer,))
    response = cur.fetchall()
    return jsonify(response)

@app.route("/filter/<streng>")
def filter(streng):
    cur.execute("SELECT * FROM bøker WHERE bok_tittel = ? OR bok_forfatter = ?", (streng,))
    response = cur.fetchall()
    return jsonify(response)

@app.route("/slettbok/<int:bok_nummer>", methods=["DELETE"])
def slettbok(bok_nummer):
    cur.execute("DELETE FROM bøker WHERE bok_nummer = ?", (bok_nummer,))
    con.commit()
    
    if cur.rowcount == 0:
        return jsonify({"error": "Boken finnes ikke i databasen"}), 404
    
    return jsonify({"message": "Boken ble slettet fra databasen"}), 200

@app.route("/leggtilbok", methods=["POST"])
def leggtilbok():
    data = request.get_json()
    bok_tittel = data["bok_tittel"]
    bok_forfatter = data["bok_forfatter"]
    bok_nummer = data["bok_nummer"]
    bok_isbn = data["bok_isbn"]
    cur.execute("SELECT * FROM bøker WHERE bok_nummer = ?", (bok_nummer,))
    existing_book = cur.fetchone()
    if existing_book:
        return jsonify({"resultat": f"Boken finnes fra før"}), 400

    cur.execute("INSERT INTO bøker (bok_tittel, bok_forfatter, bok_nummer, bok_isbn) VALUES (?, ?, ?, ?)",
                (bok_tittel, bok_forfatter, bok_nummer, bok_isbn))
    con.commit()

    suksessfull_melding = f"{bok_tittel} ble registrert"
    return jsonify({"resultat": suksessfull_melding}), 201

if __name__ == "__main__":
    app.run(debug=True)