import sqlite3
con = sqlite3.connect("database.db", check_same_thread=False)
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS bøker (
                bok_id INTEGER PRIMARY KEY, 
                bok_tittel TEXT,
                bok_forfatter TEXT,
                bok_nummer INTEGER,
                bok_isbn INTEGER
            );""")
con.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS låntakere (
            nummer INTEGER,
            fornavn TEXT,
            etternavn TEXT
); """)
con.commit()
brukere = [
    ("1", "Albert", "Wojcicki"),
    ("2", "Mats", "Vedal")
]
cur.executemany("INSERT INTO låntakere (nummer, fornavn, etternavn) VALUES (?, ?, ?)", brukere)
bøker = [
    ("Skråpånatta", "Lars Mytting", 1, 9788205548387),
    ("Skråpånatta", "Lars Mytting", 2, 9788205548387),
    ("Skråpånatta", "Lars Mytting", 3, 9788205548387),
    ("Atlas: Historien om Pa Salt", "Lucinda Riley", 4, 9788205548387),
    ("Maskiner som tenker", "Inga Strümke", 5, 9788248926741),
    ("Maskiner som tenker", "Inga Strümke", 6, 9788248926741),
    ("Maskiner som tenker", "Inga Strümke", 7, 9788248926741),
    ("Maskiner som tenker", "Inga Strümke", 8, 9788248926741),
    ("Maskiner som tenker", "Inga Strümke", 9, 9788248926741),
    ("Å vanne blomster om kvelden", "Valérie Perrin", 10, 9788205548387),
    ("Å vanne blomster om kvelden", "Valérie Perrin", 11, 9788205548387),
    ("Da vi var yngre", "Oliver Lovrenski", 12, 9788205548387),
    ("Da vi var yngre", "Oliver Lovrenski", 13, 9788205548387),
    ("Da vi var yngre", "Oliver Lovrenski", 14, 9788205548387)
]


cur.executemany("INSERT INTO bøker (bok_tittel, bok_forfatter, bok_nummer, bok_isbn) VALUES (?, ?, ?, ?)", bøker)
con.commit()