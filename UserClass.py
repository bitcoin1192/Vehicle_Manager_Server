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
        self.logout = False
        self.sqlConn = conn
        self.uid = uid
        
    def storeRequestData(self, msg):
        self.intent = msg["intent"]
        self.changeData = msg["changeData"]
        if self.intent and self.changeData is not None:
            if self.intent == "edit":
                self.editUserData()
            elif self.intent == "getKnownVehicle":
                self.getKnownVehicle()
            elif self.intent == "searchUser":
                self.searchUserGlobal()
            elif self.intent == "logout":
                self.logoutSession()
            elif self.intent == "addVehicle":
                self.addVehicle()
            elif self.intent == "cookiesTest":
                self.verifyCookies()
            else:
                raise UnknownIntent(self.intent+" is not handle yet!")
        else:
            raise InputIncomplete
    
    def logoutSession(self):
        self.logout = True
        self.latest_response = {"response": "Session is clear, have a nice day!"}

    def verifyCookies(self):
        self.latest_response = {"response": "Cookies is valid !"}
    
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
    
    def getKnownVehicle(self):
        sqlCursor = self.sqlConn.cursor()
        #Select owned vehicle by current user UID
        sqlCursor.execute("""SELECT * FROM MSTblVehicleData WHERE UID=:uid;""",
                             {"uid": self.uid})
        ret_list_own_vid = convertSQLRowsToDict(sqlCursor)
        #Select borrowed vehicle in TRVehicleLease by current UID
        sqlCursor.execute("""SELECT A.VID, C.UID, B.Type, B.PoliceNum, B.BTMacAddress, A.AccKey
                             FROM TRVehicleLease as A 
                             INNER JOIN MSTblVehicleData as B ON B.VID = A.VID
                             JOIN MSTblUserLogin as C ON C.UID = B.UID
                             WHERE A.UID=:uid;""",
                             {"uid": self.uid})
        ret_list_borrowed_vid = convertSQLRowsToDict(sqlCursor)
        if ret_list_borrowed_vid.__len__() < 1 and ret_list_own_vid.__len__() < 1:
            self.latest_response = {"OwnedVehicle": [],"BorrowedVehicle": []}
        else:
            self.latest_response = {"OwnedVehicle": ret_list_own_vid,"BorrowedVehicle": ret_list_borrowed_vid}
    
    def searchUserGlobal(self):
        self.query = self.changeData[0]["query"]
        sqlCursor = self.sqlConn.cursor()
        #Select owned vehicle by current user UID
        sqlCursor.execute("""SELECT UID,Username FROM MSTblUserLogin
                             WHERE Username LIKE ?""",
                             (self.query,))
        ret_list_user = convertSQLRowsToDict(sqlCursor)
        if ret_list_user.__len__() != 1:
            raise UserNotFound("User is not found")
        self.latest_response = {"SearchUserResult":ret_list_user}
    
    def removeLoginRestriction(self):
        pass
    
    def addVehicle(self):
        self.query = self.changeData[0]
        vehicleMac = self.query["macaddress"]
        vehicleName = self.query["name"]
        vehicleOwner = self.uid
        try:
            sqlCursor = self.sqlConn.cursor()
            sqlCursor.execute("""INSERT INTO MSTblVehicleData(UID,PoliceNum,BTMacAddress,Type,AccKey)
                                        VALUES (:vehicleOwner,:vehiclename,:vehiclemac,:type,:acckey)""",{"vehicleOwner":vehicleOwner,"vehiclename":vehicleName,"vehiclemac":vehicleMac,"type":4,"acckey":"abc124"})
            self.sqlConn.commit()
            self.latest_response = {"response": "Vehicle is added"}
        except sqlite3.IntegrityError:
            raise VehicleExist("Cannot add vehicle belonging to other user")
            
        
        