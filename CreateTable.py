from random import randint, choice
from uuid import uuid4
import sqlite3
import string

chars=string.ascii_uppercase

def createTable(dbconn:sqlite3.Connection):
    dbcursor = dbconn.cursor()
    dbcursor.executescript("""
CREATE TABLE IF NOT EXISTS "MSTblUserLogin" (
	"UID"	INTEGER NOT NULL,
	"Username"	TEXT NOT NULL UNIQUE,
	"Password"	TEXT NOT NULL,
	"SIMNumber"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("UID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "MSTblSessionDevice" (
	"SessionMAC" TEXT NOT NULL UNIQUE,
	"UID" INTEGER NOT NULL,
	FOREIGN KEY ("UID") REFERENCES "MSTblUserLogin"("UID"),
	PRIMARY KEY("UID")
);
CREATE TABLE IF NOT EXISTS "MSTblVehicleData" (
	"VID"	INTEGER NOT NULL,
	"UID"	INTEGER NOT NULL,
	"Type"	TEXT NOT NULL,
	"PoliceNum"	TEXT NOT NULL UNIQUE,
	"BTMacAddress" TEXT NOT NULL,
	"AccKey"	TEXT NOT NULL UNIQUE,
	FOREIGN KEY("UID") REFERENCES "MSTblUserLogin"("UID"),
	PRIMARY KEY("VID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "TRVehicleLease" (
	"AccKey"	TEXT NOT NULL,
	"UID"	INTEGER NOT NULL,
	"VID"	INTEGER NOT NULL,
	PRIMARY KEY("UID","VID"),
	FOREIGN KEY("VID") REFERENCES "MSTblVehicleData"("VID"),
	FOREIGN KEY("UID") REFERENCES "MSTblUserLogin"("UID")
);
CREATE TABLE IF NOT EXISTS "MSTblFaceSignature" (
	"FID"	INTEGER NOT NULL,
	"UID"	INTEGER NOT NULL,
	"FaceSignaturePath"	BLOB NOT NULL,
	PRIMARY KEY("FID" AUTOINCREMENT),
	FOREIGN KEY("UID") REFERENCES "MSTblUserLogin"("UID")
);""")
    dbconn.commit()

# Automate record filling for table MSTblVehicle to simulate external
# software. User admin is created in order to satisfy foreign key constraint
# in case of vehicle is input from
# external software.
def fillTable(dbconn:sqlite3.Connection):
	dbcursor = dbconn.cursor()
	dbcursor.execute("""INSERT INTO MSTblUserLogin(username,password) 
						VALUES (:user,:pass);"""
						,{"user":"administrator","pass":"123abc"})
	listRecord = createRecordList()
	dbcursor.executemany("""INSERT INTO MSTblVehicleData(UID,Type,PoliceNum,MacAddress,AccKey) 
						VALUES (?,?,?,?,?,?,?,?)""",listRecord)
	dbconn.commit()

def createRecordList():
	manufacturerLineup = {"Yamaha": ["Fazzio EV","Gear 125"]#"FreeGo","XSR-155","Vixion","MT-25","Lexi"]
							,"Honda": ["BeAT","Genio"]#,"PCX","CB150R","CB150X"]
							,"Piaggio":["LX125 I-GET"]#,"GTV","GTS Super"]
							,"Gesits":["Black","White"]#,"Red"]
							}
	listRecord = []
	for manufacturer in manufacturerLineup.keys():
		for lineup in manufacturerLineup[manufacturer]:
			for _ in range(5):
				rowRecord = (1,2,plateGenerator(),randint(2019,2025),manufacturer,lineup,"B8:27:EB:2C:F8:74",str(uuid4()))
				listRecord.append(rowRecord)
	return listRecord

def plateGenerator():
	number = str(randint(1000,2000))
	backstr = " "
	for _ in range(3):
		backstr = backstr+choice(chars)
	res = "B "+number+backstr
	return res

print(plateGenerator())