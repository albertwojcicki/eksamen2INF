from flask import Flask, render_template, request, session, redirect, json, url_for, jsonify
import requests
from flask_cors import CORS
import sqlite3

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    query = request.form.get("filter_streng")
   
    try:
        if query:
            response = requests.get(f"http://127.0.0.1:5020/filter/{query}")
        else:
            response = requests.get("http://127.0.0.1:5020/")
        
        response.raise_for_status()  # Raise an exception for HTTP errors
        books = response.json()
        print("Books:", books)  # Debugging statement
        return render_template("index.html", data=books, filter_streng = query)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return render_template("index.html", error="Failed to retrieve books.")
    
@app.route("/bok/<int:bok_nummer>", methods=["POST", "GET"])
def bok(bok_nummer):
    response = requests.get(f"http://127.0.0.1:5020/bok/{bok_nummer}").json()
    print(response)
    return render_template("bok.html", data=response)

@app.route("/filter_view/<filter_streng>", methods=["GET"])
def filter_view(filter_streng):
    try:
        response = requests.get(f"http://127.0.0.1:5020/filter/{filter_streng}")
        response.raise_for_status()  # Raise an exception for HTTP errors
        books = response.json()
        return render_template("index.html", data=books)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return render_template("index.html", error="Failed to filter books.")

@app.route("/slettbok/<int:bok_nummer>", methods = ["POST"])
def slettbok(bok_nummer):
    response = requests.delete(f"http://127.0.0.1:5020/slettbok/{bok_nummer}").json()
    return redirect(url_for("index",response = response ))

@app.route("/leggtilbok", methods = ["POST"])
def leggtilbok():
    bok_tittel = request.form.get("bok_tittel")
    bok_forfatter = request.form.get("bok_forfatter")
    bok_nummer = request.form.get("bok_nummer")
    bok_isbn = request.form.get("bok_isbn")
    data = {
        "bok_tittel": bok_tittel,
        "bok_forfatter": bok_forfatter,
        "bok_nummer": bok_nummer,
        "bok_isbn": bok_isbn
    }
    response = requests.post("http://127.0.0.1:5020/leggtilbok", json=data).json()
    return render_template("legg_til_bok.html", response = response)

@app.route("/leggtilbok_side")
def leggtilbok_side():
    return render_template("legg_til_bok.html")

@app.route("/søk_barcode", methods = ["GET"])
def søk_barcode():
    barcode = request.args.get("barcode")
    print(barcode)
    return redirect(url_for("bok", bok_nummer = int(barcode)))



@app.route("/se_brukere", methods=["GET"])
def se_brukere():
    response = requests.get("http://127.0.0.1:5020/se_brukere")
    if response.status_code == 200:
        users = response.json()
        return render_template("brukere.html", data=users)
    else:
        return render_template("brukere.html", error="Failed to retrieve users.")
if __name__ == "__main__":
    app.run(debug=True)