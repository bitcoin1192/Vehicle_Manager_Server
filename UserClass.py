import json
from HelperFunction import convertSQLRowsToDict
from uuid import uuid4
from ControllerException import UnknownIntent
from AppError import *
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
            elif self.intent == "getKnownVehicle":
                self.getKnownVehicle()
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
                proc_column += str(varname) + ", "
            else:
                raise ColumnNotExist("Key doesn't correspond to known column")
        self.sqlConn.commit()
        self.latest_response = "Affected column is " + proc_column
    
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
                sqlCursor.execute("""INSERT INTO MSTblFaceSignature(UID,FaceSignaturePath)
                                     VALUES (:user,:filepath)""",
                                    {"user": self.uid, "filepath": filename})
        self.sqlConn.commit()
        self.latest_response = "Insertion finish"
    
    def getKnownVehicle(self):
        sqlCursor = self.sqlConn.cursor()
        #Select owned vehicle by current user UID
        sqlCursor.execute("""SELECT VID, UID, Type, Manufacturer, Model, PoliceNum, AccKey
                             FROM MSTblVehicleData WHERE UID=:uid;""",
                             {"uid": self.uid})
        ret_list_own_vid = convertSQLRowsToDict(sqlCursor)
        #Select borrowed vehicle in TRVehicleLease by current UID
        sqlCursor.execute("""SELECT A.VID, C.Username, B.Type, B.Manufacturer, B.PoliceNum, B.Model, A.AccKey
                             FROM TRVehicleLease as A 
                             INNER JOIN MSTblVehicleData as B ON B.VID = A.VID
                             JOIN MSTblUserLogin as C ON C.UID = B.UID
                             WHERE A.UID!=:uid;""",
                             {"uid": self.uid})
        ret_list_borrowed_vid = convertSQLRowsToDict(sqlCursor)
        if ret_list_borrowed_vid.__len__() < 1 and ret_list_own_vid.__len__() < 1:
            raise ZeroRowAffected("No vehicle record found under your name.")
        self.latest_response = {"OwnedVehicle": ret_list_own_vid,"BorrowedVehicle": ret_list_borrowed_vid}