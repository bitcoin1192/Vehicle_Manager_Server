from asyncio.windows_events import NULL
from fileinput import filename
from uuid import uuid4
from ControllerException import UnknownIntent
import sqlite3
import os

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
            elif self.intent == "storeFace":
                self.storeFaceSignature()
            else:
                raise UnknownIntent(self.intent+" is not handle yet!")
        else:
            raise InputIncomplete
    
    def editUserData(self):
        sqlCursor = self.sqlConn.cursor()
        proc_column = ""
        for varname in self.changeData[0]:
            if varname == "password":
                sqlCursor.execute("""UPDATE MSTblUserLogin 
                                    SET password=:password 
                                    WHERE UID=:user""",
                                    {"user": self.uid, "password": self.changeData[0][varname]})
                proc_column += str(varname) + " "
            else:
                raise ColumnNotExist("Key doesn't correspond to known column")
        self.sqlConn.commit()
        self.latest_response = varname + " has been changed"
    
    #Accept csv value as input. The value then will be written to file
    #inside faceSignature folder into it's separate unique file.
    #file name will be recorded inside faceSignature table.
    def storeFaceSignature(self):
        faceSignatureArray = self.changeData
        folder = "faceSignature/"
        sqlCursor = self.sqlConn.cursor()
        try:
            os.mkdir(folder)
        except:
            print("Folder is created")
        for signatureObject in faceSignatureArray:
            filename = folder+str(uuid4())
            with open(filename, 'w') as f:
                value = signatureObject["value"]
                f.write(value)
                f.close()
                sqlCursor.execute("""INSERT INTO MSTblFaceSignature(UIDOwner,FaceSignaturePath)
                                     VALUES (:user,:password)""",
                                    {"user": self.uid, "password": filename})
        self.sqlConn.commit()
        self.latest_response = "Insertion finish"
        


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