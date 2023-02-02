import sqlite3
from flask import Flask, request, json, g
from random import randint, choice

app = Flask(__name__)
DATABASE = 'sim-whitelist-mock-1.db'
dbcheck = False

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def createTable(dbconn:sqlite3.Connection):
    dbcursor = dbconn.cursor()
    dbcursor.executescript("""
CREATE TABLE IF NOT EXISTS "WhiteListSIMNumber" (
	"UID"	INTEGER NOT NULL,
	"Nama"	TEXT NOT NULL UNIQUE,
	"SIMNumber"	TEXT NOT NULL,
	PRIMARY KEY("UID" AUTOINCREMENT)
);""")
    dbconn.commit()

def fillTable(dbconn:sqlite3.Connection):
	dbcursor = dbconn.cursor()
	listRecord = createRecordList()
	dbcursor.executemany("""INSERT INTO WhiteListSIMNumber(UID,Nama,SIMNumber) VALUES (?,?,?)""",listRecord)
	dbconn.commit()

def createRecordList():
    listName = ["Ariq","Ali","1","2","3","4","5"]
    listRecord = []
    for idx, name in enumerate(listName):
        rowRecord = (idx,name,simGenerator())
        listRecord.append(rowRecord)
    return listRecord

def simGenerator():
    #Format: xxxxyyyyzzzz...z atau 
    x = "0122"
    y = "1200"
    z = str(randint(12000,120110))
    return x+y+z

def get_db():
    global dbcheck
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.execute("PRAGMA foreign_keys = 1")
        curr = db.cursor()
        if dbcheck == False:
            curr.execute("SELECT name FROM sqlite_master WHERE type='table';")
            table_list = curr.fetchall()
            if table_list.__len__() <= 1:
                createTable(db)
                fillTable(db)
            dbcheck = True
    return db

@app.route('/', methods=['GET'])
def index():
    get_db()
    return 'Welcome to SIM Verifier',200

@app.route('/verify', methods=['GET'])
def verify():
    input = request.args.get('simnumber')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT SIMNumber from WhiteListSIMNumber where SIMNumber = :simnumber",{"simnumber":input})
    b = cursor.fetchall()
    if len(b)>=1:
        return {'status':'valid'},200
    else:
        return {'status':'invalid'},200

app.run("::", port=41312)