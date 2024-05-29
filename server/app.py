from flask import Flask, render_template, request, session, redirect, json, url_for, jsonify
import requests
from flask_cors import CORS
import sqlite3

app = Flask(__name__)

con = sqlite3.connect("database.db", check_same_thread=False)
cur = con.cursor()

@app.route("/")
def index():
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM bøker")
        response = cur.fetchall()
        books = []
        for row in response:
            book = {
                "bok_id": row[0],
                "bok_tittel": row[1],
                "bok_forfatter": row[2],
                "bok_nummer": row[3],
                "bok_isbn": row[4]
            }
            books.append(book)
        return jsonify(books)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/bok/<int:bok_nummer>")
def bok(bok_nummer):
    cur.execute("SELECT * FROM bøker WHERE bok_nummer = ?", (bok_nummer,))
    response = cur.fetchall()
    books = []
    for row in response:
        book = {
            "bok_id": row[0],
            "bok_tittel": row[1],
            "bok_forfatter": row[2],
            "bok_nummer": row[3],
            "bok_isbn": row[4]
        }
        books.append(book)
    return jsonify(books)

@app.route("/filter/<filter_streng>", methods=["GET"])
def filter(filter_streng):
    cur.execute("SELECT * FROM bøker WHERE LOWER(bok_tittel) = LOWER(?) OR LOWER(bok_forfatter) = LOWER(?)", (filter_streng, filter_streng))
    response = cur.fetchall()
    if not response:
        print("No books found with the given filter")
        return jsonify({"error": "Ingen bøker med denne tittelen/ forfatteren"}), 404
    books = []
    for row in response:
        book = {
            "bok_id": row[0],
            "bok_tittel": row[1],
            "bok_forfatter": row[2],
            "bok_nummer": row[3],
            "bok_isbn": row[4]
        }
        books.append(book)
    return jsonify(books)

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

@app.route("/se_brukere", methods = ["GET"])
def se_brukere():
    cur.execute("SELECT fornavn, etternavn FROM låntakere")
    users = cur.fetchall()
    user_list = [{"fornavn": user[0], "etternavn": user[1]} for user in users]
    return jsonify(user_list)

if __name__ == "__main__":
    app.run(debug=True, port=5020)