import sqlite3

def create_site_table():
    """
    creates table if it doesnt exist
    """
    con = sqlite3.connect('pochBot.db')
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            time TEXT NOT NULL,
            payout REAL NOT NULL
        )
    ''')
    con.commit()
    con.close()

def insert_new_site(name, time, payout):
    """
    inserts who ran the site, time, and payout into pochBotdb
    """
    con = sqlite3.connect('pochBot.db')
    cur = con.cursor()
    cur.execute("INSERT INTO sites (name, time, payout) VALUES (?, ?, ?)", (name, time, payout))
    con.commit()
    con.close()
