from typing import Dict
from flask import make_response, json
import sqlite3
import requests
import ControllerException

from AppError import UserNotFound, UserExist, SIMNumberInvalid, InputIncomplete, MACAddressesNotMatch
from ControllerException import UnknownIntent

class LoginClass:
    jsonSchema = {
        "type" : "byte",
        "properties" : {
            "intent" : {"type" : "string"},
            "Username" : {"type" : "string"},
            "Password" : {"type" : "string"}
        }
    }

    def __init__(self, conn: sqlite3.Connection):
        self.sqlConn = conn
        self.latest_response = None
        self.UID = None    
        self.externalverifierendpoint = "http://[::1]:41312/verify"
    
    def storeUserPass(self, input:dict):
        self.intent = input["intent"]
        self.Username = input["username"]
        self.Password = input["password"]
        try:
            if self.intent is not None:
                if self.intent == "signup":
                    self.SimNumber = input["simnumber"]
                    self.macaddress = input["macaddress"]
                    self.newUserCreation()
                elif self.intent == "login":
                    self.macaddress = input["macaddress"]
                    self.authUserPass()
                else:
                    raise UnknownIntent(self.intent+" intent is not handle")
        except KeyError:
            raise InputIncomplete("Please fill all shown input field !")

    def authUserPass(self):
        #check on sql to retreive both uid and create new authkey
        #then return the authkey to application
        sqlCursor = self.sqlConn.cursor()
        sqlCursor.execute("""SELECT A.UID, B.UID, B.SessionMAC FROM MSTblUserLogin as A 
                    JOIN MSTblSessionDevice as B ON B.UID = A.UID
                    WHERE A.Username=:user and A.Password=:pass;""",{"user": self.Username, "pass": self.Password})
        result = sqlCursor.fetchone()
        if result is None:
            raise UserNotFound("User or Password is not matching!")
        else:
            if result[2] == self.macaddress:
                self.UID = result[0]
                resp = json.dumps({"success": True, "msg": "User is found and authorize. Save this cookies for future authenticated request!" ,"uid": self.UID})
                self.latest_response = resp
            else:
                raise MACAddressesNotMatch("Login account cannot be used on this phone")

    def newUserCreation(self):
        #insert to user MSTblUserLogin
        sqlCursor = self.sqlConn.cursor()
        try:
            if self.SimNumberVerifier(self.SimNumber):
                sqlCursor.execute("INSERT INTO MSTblUserLogin(Username,Password,SIMNumber) VALUES (:user,:pass,:simn)",{"user": self.Username, "pass": self.Password,"simn":self.SimNumber})
                self.UID = sqlCursor.lastrowid
                sqlCursor.execute("INSERT INTO MSTblSessionDevice(UID, SessionMAC) VALUES (:user,:macaddr)",{"user": self.UID, "macaddr": self.macaddress})
                self.sqlConn.commit()
                self.latest_response = json.dumps({"success": True, "msg": "Users has been created. Login to use authenticated endpoint"})
            else:
                raise SIMNumberInvalid("SIM number is not valid")
        except sqlite3.IntegrityError as e:
            if e.args[0] == "UNIQUE constraint failed: MSTblUserLogin.SIMNumber":
                raise SIMNumberInvalid("SIM number has been registered, please use different SIM number !")
            raise UserExist
    
    def SimNumberVerifier(self, input):
        response = requests.get(self.externalverifierendpoint,{"simnumber":input})
        if(response.json()["status"]=="invalid"):
            return False
        else:
            return True