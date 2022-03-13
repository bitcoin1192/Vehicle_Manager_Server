from typing import Dict
import sqlite3

class LoginClass:
    jsonSchema = {
        "type" : "byte",
        "properties" : {
            "intent" : {"type" : "string"},
            "username" : {"type" : "string"},
            "password" : {"type" : "string"}
        }
    }

    def __init__(self, input: Dict[str,str]):
        self.intent = input["intent"]
        self.username = input["username"]
        self.password = input["password"]
    
    def authUserPass(self, sqliteConn: sqlite3.Connection):
        #check on sql to retreive both uid and create new authkey
        #then return the authkey to application
        sqlCursor = sqliteConn.cursor()
        sqlCursor.execute("SELECT UID FROM MSTblUserLogin WHERE username=:user AND password=:pass",{"user": self.username, "pass": self.password})
        return sqlCursor.fetchone()
        pass

    def newUserCreation(self):
        #insert to user MSTblUserLogin
        pass

    