from typing import Dict
import sqlite3
import ControllerException
from AppError import *

class VehicleClass:
    jsonSchema = {
        "type" : "byte",
        "properties" : {
            "VID" : {"type" : "string"},
            "request" : {"type" : "string"}
        }
    }
    latest_response = None
    UID = None
    def __init__(self, conn: sqlite3.Connection):
        self.sqlConn = conn
    
    def storeVID(self, input):
        self.VID = input["VID"]
        self.requestType = input["request"]
        self.bodyRequest = input["body"]

    def getMember(self):
        #check on sql to retreive both uid and create new authkey
        #then return the authkey to application
        sqlCursor = self.sqlConn.cursor()
        sqlCursor.execute("SELECT UIDMember FROM TRGIDMember WHERE VIDLease=:vehicle",{"vehicle": self.VID})
        result = sqlCursor.fetchall()
        if result is None:
            raise UserNotFound
        else:
            self.UID = result[0]
            self.latest_response = "Can't find UIDMember for selected VIDLease"
        
    def getOwner(self):
        sqlCursor = self.sqlConn.cursor()
        sqlCursor.execute("SELECT UIDMember FROM TRGIDMember WHERE VIDLease=:vehicle",{"vehicle": self.VID})
        result = sqlCursor.fetchone()
        if result is None:
            raise UserNotFound
        else:
            self.UID = result[0]
            self.latest_response = "Can't find UIDMember for selected VIDLease"

    def postRequestHandler(self):
        #insert to user MSTblUserLogin
        sqlCursor = self.sqlConn.cursor()
        try:
            sqlCursor.execute("INSERT INTO MSTblUserLogin(username,password) VALUES (:user,:pass)",{"user": self.username, "pass": self.password})
            UID = sqlCursor.lastrowid
            sqlCursor.execute("INSERT INTO GIDHeader(UIDOwner) VALUES (:uid)",{"uid": UID})
            self.sqlConn.commit()
            self.latest_response = "Users has been created. Login to use authenticated endpoint"
        except sqlite3.IntegrityError as e:
            raise UserExist