
import sqlite3, os
from .resp_config import REC_CONFIG

questions = '''
    CREATE TABLE "questions" (
	"id"	INTEGER NOT NULL UNIQUE,
	"qid"	TEXT NOT NULL,
	"text"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT))
    '''

response_codes = '''CREATE TABLE "response_codes" (
	"id"	INTEGER NOT NULL UNIQUE,
	"qid"	TEXT NOT NULL,
	"pid"	INTEGER NOT NULL,
	%s
	PRIMARY KEY("id" AUTOINCREMENT)
)'''

responses = '''CREATE TABLE "responses" (
	"id"	INTEGER NOT NULL UNIQUE,
	"pid"	INTEGER NOT NULL,
	"qid"	TEXT NOT NULL,
	"response"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
)'''

terms = '''CREATE TABLE "terms" (
	"id"	INTEGER NOT NULL UNIQUE,
	"term"	TEXT NOT NULL,
	"definition"	TEXT NOT NULL,
	"qid"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
)'''

coders = '''CREATE TABLE "coders" (
    "id"	INTEGER NOT NULL UNIQUE,
    "label"	TEXT NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT)
)'''

response_codes = '''CREATE TABLE "response_codes" (
	"id"	INTEGER NOT NULL UNIQUE,
    "pid"	INTEGER NOT NULL,
    "qid"	TEXT NOT NULL,
    "codes" TEXT NOT NULL,
    "coder_combo" TEXT NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT)
)'''

def clear_database(db_name):
	conn = sqlite3.connect(db_name)
	cursor = conn.cursor()

	cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
	tables = cursor.fetchall()
	for table in tables:
		if table[0] != "sqlite_sequence":
			cursor.execute(f"DROP TABLE IF EXISTS {table[0]};")  # Drop each table
	conn.commit()
	conn.close()

def main():

	path = REC_CONFIG.DB_PATH

	print(path)

	if os.path.exists(path): clear_database(path)

	conn = sqlite3.connect(path)
	cursor = conn.cursor()

	statements = [questions, responses, terms, coders, response_codes] 

	for statement in statements:

		cursor.execute(statement)
		conn.commit()

	conn.close()

	print("Database and schema created successfully.")