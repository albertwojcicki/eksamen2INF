from flask import Flask, render_template, request, session, redirect, json, url_for, jsonify
import requests
from flask_cors import CORS
import sqlite3
from datetime import datetime

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

@app.route("/scan_user", methods=["GET", "POST"])
def scan_user():
    if request.method == "POST":
        barcode = request.form.get("barcode")
        if barcode:
            return redirect(url_for('låntaker_detail', nummer=barcode))
    return render_template("index.html")

@app.route("/låntaker/<int:nummer>", methods=["GET", "POST"])
def låntaker_detail(nummer):
    if request.method == "POST":
        book_barcode = request.form.get("book_barcode")
        if book_barcode:
            response = requests.get(f"http://127.0.0.1:5020/book/{book_barcode}")
            if response.status_code == 200:
                book = response.json()
                user_response = requests.get(f"http://127.0.0.1:5020/låntaker/{nummer}")
                user = user_response.json() if user_response.status_code == 200 else {}
                return render_template("confirm_loan.html", user=user, book=book)
            else:
                return render_template("låntaker_detail.html", error="Boken finnes ikke.", nummer=nummer)
    response = requests.get(f"http://127.0.0.1:5020/låntaker/{nummer}")
    if response.status_code == 200:
        user = response.json()
        return render_template("enkel_bruker.html", user=user)
    else:
        return render_template("enkel_bruker.html", error="Brukeren finnes ikke.")

@app.route("/show_unreturned_books", methods=["GET"])
def show_unreturned_books():
    try:
        response = requests.get("http://127.0.0.1:5020/unreturned_books")
        response.raise_for_status()
        unreturned_books = response.json()
        return render_template("unreturned_books.html", data=unreturned_books)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return render_template("unreturned_books.html", error="Failed to retrieve unreturned books.")



@app.template_filter('format_datetime')
def format_datetime(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')  # Adjust format if necessary
    return date_obj.strftime('%Y-%m-%d %H:%M')

# Register the filter
app.jinja_env.filters['format_datetime'] = format_datetime
@app.route("/confirm_loan", methods=["POST"])
def confirm_loan():
    user_id = request.form.get("user_id")
    book_id = request.form.get("book_id")
    if user_id and book_id:
        response = requests.post(f"http://127.0.0.1:5020/loan_book/{book_id}", json={"brukernavn": user_id})
        if response.status_code == 200:
            return render_template("loan_success.html", message="Boken er lånt ut.")
        elif response.status_code == 400:

            return render_template("confirm_loan.html", error="Boken er allere lånt ut")
        else:
            return render_template("confirm_loan.html", error="Kunne ikke låne bok.")
    return redirect(url_for('index'))

@app.route("/se_brukere", methods=["GET"])
def se_brukere():
    response = requests.get("http://127.0.0.1:5020/se_brukere")
    if response.status_code == 200:
        users = response.json()
        return render_template("brukere.html", data=users)
    else:
        return render_template("brukere.html", error="Kunne ikke hente brukere.")
    
@app.route("/innlever", methods=["GET", "POST"])
def innlever():
    if request.method == "GET":
        return render_template("lever_bok.html")
    if request.method == "POST":
        barcode = request.form.get("barcode")
        response = requests.post("http://127.0.0.1:5020/innlever", json={"barcode": barcode})
        if response.status_code == 200:
            return render_template("lever_bok.html", error = "Boken er levert inn")
        else:
            return render_template("lever_bok.html", error="Boken er ikke lånt ut.")
    

    
if __name__ == "__main__":
    app.run(debug=True)