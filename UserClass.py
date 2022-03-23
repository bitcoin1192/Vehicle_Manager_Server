from asyncio.windows_events import NULL
from ControllerException import UnknownIntent
import sqlite3
from tkinter import E
from types import NoneType

class UserClass:
    jsonSchema = {
        "type" : "byte",
        "properties" : {
            "intent" : {"type" : "string"},
            "changeData" : {"type" : "string"}
        }
    }
    latest_response = None
    def __init__(self, conn: sqlite3.Connection, uid):
        self.sqlConn = conn
        self.uid = uid
        
    def storeRequestData(self, msg):
        self.intent = msg["intent"]
        self.changeData = msg["changeData"]
        if self.intent and self.changeData is not None:
            if self.intent == "edit":
                self.editUserData()
            elif self.intent == "updateFace":
                pass
            else:
                raise UnknownIntent(self.intent+" is not handle yet!")
        else:
            raise InputIncomplete
    
    def editUserData(self):
        sqlCursor = self.sqlConn.cursor()
        for varname in self.changeData:
            if varname == "password":
                sqlCursor.execute("""UPDATE MSTblUserLogin 
                                    SET password=:password 
                                    WHERE UID=:user""",
                                    {"user": self.uid, "password": self.changeData[varname]})
                self.sqlConn.commit()
                self.latest_response = varname + " has been changed"
            else:
                raise ColumnNotExist("Key doesn't correspond to known column")
            #    print(e)
            
        #self.sqlConn.commit()
    
    def storeFaceSignature(self):
        pass

class UserNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.error = "Query show 0 records"

class UserExist(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.error = "Username is not available"

class InputIncomplete(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.error = "Input is missing from request data"

class ColumnNotExist(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.error = args[0]