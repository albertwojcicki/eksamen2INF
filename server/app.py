from flask import Flask, render_template, request, session, redirect, json, url_for, jsonify
import requests
from flask_cors import CORS
import sqlite3
from datetime import datetime
import logging

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
    
@app.route("/loan_book/<int:bok_nummer>", methods=["POST"])
def loan_book(bok_nummer):
    data = request.get_json()
    logging.debug(f"Received loan_book request with data: {data}")
    
    if not data or "brukernavn" not in data:
        logging.error("Missing brukernavn in request")
        return jsonify({"error": "Missing brukernavn"}), 400

    brukernavn = data["brukernavn"]
    cur.execute("SELECT bruker_id FROM brukere WHERE brukernavn = ?", (brukernavn,))
    bruker = cur.fetchone()
    
    if not bruker:
        logging.error(f"Bruker not found: {brukernavn}")
        return jsonify({"error": "Bruker ikke funnet"}), 404

    bruker_id = bruker[0]
    dato_lånt = datetime.now()
    
    try:
        cur.execute("INSERT INTO lånte_bøker (bruker_id, bok_nummer, lånt, dato_lånt) VALUES (?, ?, ?, ?)",
                    (bruker_id, bok_nummer, 1, dato_lånt))
        con.commit()
        logging.info(f"Bok {bok_nummer} loaned by bruker {brukernavn}")
        return jsonify({"message": "Bok lånt suksessfullt"}), 200
    except Exception as e:
        logging.error(f"Error in loan_book: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/loaned_books/<int:bruker_id>", methods=["GET"])
def loaned_books(bruker_id):
    try:
        cur.execute("""
            SELECT b.bok_tittel, b.bok_forfatter, lb.dato_lånt, lb.dato_levert
            FROM bøker b
            JOIN lånte_bøker lb ON b.bok_nummer = lb.bok_nummer
            WHERE lb.bruker_id = ? AND lb.lånt = 1
        """, (bruker_id,))
        response = cur.fetchall()
        books = []
        for row in response:
            book = {
                "bok_tittel": row[0],
                "bok_forfatter": row[1],
                "dato_lånt": row[2],
                "dato_levert": row[3]
            }
            books.append(book)
        return jsonify(books), 200
    except Exception as e:
        logging.error(f"Error in loaned_books: {e}")
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

@app.route("/registrer", methods = ["POST"])
def registrer():
    brukernavn = request.get_json()["brukernavn"]
    passord = request.get_json()["passord"]
    cur.execute("INSERT INTO brukere (brukernavn, passord) VALUES (?, ?)", (brukernavn, passord))
    con.commit()
    return {"melding": "Bruker ble registrert"}, 200

@app.route("/logginn", methods = ["POST"])
def logginn():
    brukernavn = request.get_json()["brukernavn"]
    passord = request.get_json()["passord"]
    cur.execute("SELECT * FROM brukere WHERE brukernavn = ? AND passord = ?", (brukernavn, passord))
    bruker = cur.fetchone()
    return {"brukernavn": bruker[1], "id": bruker[0]}, 200

if __name__ == "__main__":
    app.run(debug=True, port=5020)