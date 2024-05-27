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