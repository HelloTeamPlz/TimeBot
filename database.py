import sqlite3
from datetime import date
import pandas as pd

class pochBot_db():
        
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
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                payout REAL NOT NULL
            )
        ''')
        con.commit()
        con.close()

    def insert_new_site(user, time, payout):
        """
        inserts who ran the site, date, time, and payout into pochBotdb
        """
        con = sqlite3.connect('pochBot.db')
        cur = con.cursor()
        today = date.today()
        current_date = today.strftime("%Y-%m-%d")
        cur.execute("INSERT INTO sites (name, date, time, payout) VALUES (?, ?, ?, ?)", (user, current_date, time,payout))
        con.commit()
        con.close()

    def individual_sites_done(user):
        """
        Connect to db and query to get a count of the number of sites done
        """
        con = sqlite3.connect('pochBot.db')
        df = pd.read_sql_query(f"select name as Name, date as Date, payout as Payout from sites where name = '{user}'", con)
        con.close()
        df = pochBot_db.fix_names_from_db(df)
        return df
    
    def total_site_done():
        con = sqlite3.connect('pochBot.db')
        df = pd.read_sql_query(f"select date as Date, name as Name, count(payout) as TotalPayout from sites group by name", con)
        con.close()
        df = pochBot_db.fix_names_from_db(df)
        return df
    
    def fix_names_from_db(df):
        valid_names = []
        for i in df['Name']:
            name = i.split('#')
            valid_names.append(name[0])
        df['Name'] = df['Name'].str.replace(r'\d+', '', regex=True).str.replace('#', '')
        for i in df['Name']:
            if i not in valid_names:
                name_index = df[df['Name'] == i].index[0]
                if name_index != None:
                    df.loc[name_index, 'Name'] = valid_names[name_index]
                else:
                    continue
        return df  