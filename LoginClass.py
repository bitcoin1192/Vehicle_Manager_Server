from typing import Dict
import sqlite3
import ControllerException
from UserClass import UserNotFound, UserExist

class LoginClass:
    jsonSchema = {
        "type" : "byte",
        "properties" : {
            "intent" : {"type" : "string"},
            "Username" : {"type" : "string"},
            "Password" : {"type" : "string"}
        }
    }
    latest_response = None
    UID = None
    def __init__(self, conn: sqlite3.Connection):
        self.sqlConn = conn
    
    def storeUserPass(self, input:dict):
        self.intent = input["intent"]
        self.Username = input["username"]
        self.Password = input["password"]

    def authUserPass(self):
        #check on sql to retreive both uid and create new authkey
        #then return the authkey to application
        sqlCursor = self.sqlConn.cursor()
        sqlCursor.execute("SELECT UID FROM MSTblUserLogin WHERE Username=:user AND Password=:pass",{"user": self.Username, "pass": self.Password})
        result = sqlCursor.fetchone()
        if result is None:
            raise UserNotFound
        else:
            self.UID = result[0]
            self.latest_response = "User is found and authorize. Save this cookies for future authenticated request!"

    def newUserCreation(self):
        #insert to user MSTblUserLogin
        sqlCursor = self.sqlConn.cursor()
        try:
            sqlCursor.execute("INSERT INTO MSTblUserLogin(Username,Password) VALUES (:user,:pass)",{"user": self.Username, "pass": self.Password})
            self.UID = sqlCursor.lastrowid
            self.sqlConn.commit()
            self.latest_response = "Users has been created. Login to use authenticated endpoint"
        except sqlite3.IntegrityError as e:
            raise UserExist