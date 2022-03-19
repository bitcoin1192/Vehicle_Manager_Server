from typing import Dict
import sqlite3
from UserClass import UserNotFound, UserExist

class LoginClass:
    jsonSchema = {
        "type" : "byte",
        "properties" : {
            "intent" : {"type" : "string"},
            "username" : {"type" : "string"},
            "password" : {"type" : "string"}
        }
    }
    latest_response = None
    UID = None
    def __init__(self, conn: sqlite3.Connection):
        self.sqlConn = conn
    
    def storeUserPass(self, input):
        self.intent = input["intent"]
        self.username = input["username"]
        self.password = input["password"]

    def authUserPass(self):
        #check on sql to retreive both uid and create new authkey
        #then return the authkey to application
        sqlCursor = self.sqlConn.cursor()
        sqlCursor.execute("SELECT UID FROM MSTblUserLogin WHERE username=:user AND password=:pass",{"user": self.username, "pass": self.password})
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
            sqlCursor.execute("INSERT INTO MSTblUserLogin(username,password) VALUES (:user,:pass)",{"user": self.username, "pass": self.password})
            self.sqlConn.commit()
            self.latest_response = "Users has been created. Login to use authenticated endpoint"
        except sqlite3.IntegrityError as e:
            raise UserExist