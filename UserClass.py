from asyncio.windows_events import NULL
import sqlite3
from types import NoneType

class UserClass:
    jsonSchema = {
        "type" : "byte",
        "properties" : {
            "intent" : {"type" : "string"},
            "changeData" : {"type" : "string"}
        }
    }
    def __init__(self, conn: sqlite3.Connection, uid):
        self.sqlConn = conn
        self.uid = uid
        
    def storeRequestData(self, msg):
        self.intent = msg["intent"]
        self.changeData = msg["changeData"]
        if self.intent and self.changeData is not None:
            if self.intent == "edit":
                pass
            elif self.intent == "":
                pass
        else:
            raise InputIncomplete
        
    def addFriend(self):
        pass
    def removeFriend(self):
        pass
    def editUserData(self):
        pass
    def uploadFaceSignature(self):
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