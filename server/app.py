from flask import Flask, render_template, request, session, redirect, json, url_for, jsonify
import requests
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)

con = sqlite3.connect("database.db", check_same_thread=False)
cur = con.cursor()

@app.route("/")
def index():
    try:
        cur.execute("""
            SELECT bøker.*, 
                   CASE WHEN lånte_bøker.dato_returnert IS NULL AND lånte_bøker.bok_id IS NOT NULL THEN 'Yes' ELSE 'No' END AS loaned_out 
            FROM bøker 
            LEFT JOIN lånte_bøker ON bøker.bok_id = lånte_bøker.bok_id AND lånte_bøker.dato_returnert IS NULL
        """)
        response = cur.fetchall()
        books = []
        for row in response:
            book = {
                "bok_id": row[0],
                "bok_tittel": row[1],
                "bok_forfatter": row[2],
                "bok_nummer": row[3],
                "bok_isbn": row[4],
                "loaned_out": row[5]
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

@app.route("/se_brukere", methods=["GET"])
def se_brukere():
    cur.execute("SELECT nummer, fornavn, etternavn FROM låntakere")
    users = cur.fetchall()
    user_list = [{"nummer": user[0], "fornavn": user[1], "etternavn": user[2]} for user in users]
    return jsonify(user_list)

@app.route("/låntaker/<int:nummer>", methods=["GET"])
def get_låntaker(nummer):
    cur.execute("SELECT fornavn, etternavn FROM låntakere WHERE nummer = ?", (nummer,))
    user = cur.fetchone()
    if user:
        user_data = {
            "fornavn": user[0],
            "etternavn": user[1],
            "nummer": nummer
        }
        return jsonify(user_data)
    else:
        return jsonify({"error": "User not found"}), 404

@app.route("/loan_book/<int:bok_id>", methods=["POST"])
def loan_book(bok_id):
    data = request.get_json()
    brukernavn = data.get("brukernavn")
    if not brukernavn:
        return jsonify({"error": "brukernavn is required"}), 401

    cur.execute("SELECT nummer FROM låntakere WHERE nummer = ?", (brukernavn,))
    user = cur.fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if the book is already loaned
    cur.execute("SELECT * FROM lånte_bøker WHERE bok_id = ? AND dato_returnert IS NULL", (bok_id,))
    loaned_book = cur.fetchone()
    if loaned_book:
        return jsonify({"error": "Book is already loaned out"}), 400

    user_id = user[0]
    dato_lånt = datetime.now()

    cur.execute("INSERT INTO lånte_bøker (bruker_id, bok_id, dato_lånt) VALUES (?, ?, ?)", (user_id, bok_id, dato_lånt))
    con.commit()
    return jsonify({"message": "Book loaned successfully"}), 200

@app.route("/book/<int:bok_nummer>", methods=["GET"])
def get_book(bok_nummer):
    cur.execute("SELECT bok_id, bok_tittel, bok_forfatter, bok_nummer, bok_isbn FROM bøker WHERE bok_nummer = ?", (bok_nummer,))
    book = cur.fetchone()
    if book:
        book_data = {
            "bok_id": book[0],
            "bok_tittel": book[1],
            "bok_forfatter": book[2],
            "bok_nummer": book[3],
            "bok_isbn": book[4]
        }
        return jsonify(book_data)
    else:
        return jsonify({"error": "Book not found"}), 404
    

@app.route("/innlever", methods=["POST"])
def innlever():
    barcode = request.get_json()["barcode"]
    cur.execute("DELETE FROM lånte_bøker WHERE bok_id = ? AND dato_returnert IS NULL", (barcode,))
    con.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "Book not found or already returned"}), 404
    return jsonify({"message": "Book returned successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5020)