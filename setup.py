
import sqlite3
import pickle
import logging

logging.basicConfig(level=logging.INFO)


# Configure this

TOKEN = "698839060:AAEPazfjo1gvbO-DFxi6cbpq-rAOIVJPJ2g"


# Save Token

with open("token.pkl", "wb") as f:
    pickle.dump(TOKEN, f)
logging.info("Token saved as <{}>.".format(TOKEN))


# Setup SQL database

conn = sqlite3.connect("sql_data.db")
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS stars (id integer primary key autoincrement, user_name text, _date text, job text, stars integer);")

conn.commit()
conn.close()

logging.info("SQL Database set up.")