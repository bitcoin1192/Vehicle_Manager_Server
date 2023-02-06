import sqlite3
from uuid import uuid4
from ControllerException import UnknownIntent
from HelperFunction import convertSQLRowsToDict
from AppError import *

class VehicleClass:
    latest_response = None
    def __init__(self, conn: sqlite3.Connection, uid, msg) -> None:
        self.msg = msg
        self.sqlConn = conn
        self.curr = self.sqlConn.cursor()
        self.uid = uid
        self.RequesterIsOwner = False
    def intentReader(self):
        intent = self.msg["intent"]
        groupMember = self.msg["changeMember"]
        for each in groupMember:
            self.RequesterIsOwner = self.OwnerCheck(each["VID"])
            if intent == "add":
                self.addFriend(each["VID"],each["UID"])
            elif intent == "delete":
                self.removeFriend(each["VID"],each["UID"])
            elif intent == "transfer":
                self.transferOwnership(each["UID"],each["VID"])
            elif intent == "member":
                self.getVehicleMember(each["VID"],self.uid)
            elif intent == "enable":
                self.enableVehicle(each["VID"])
            elif intent == "disable":
                self.disableVehicle(each["VID"])
            else:
                raise UnknownIntent("No handler for received intent \""+intent+"\" !")
        self.sqlConn.commit()

    def transferOwnership(self,toUID,VID):
        if self.RequesterIsOwner:
            self.curr.execute("""UPDATE MSTblVehicleData
                                    SET UID=:toUID
                                    WHERE UID=:fromUID AND VID=:VID""",
                                    {"toUID":toUID, "fromUID":self.uid, "VID":VID})
            if self.curr.rowcount < 1:
                raise ZeroRowAffected("No record is updated for this request!")
            else:
                self.curr.execute("""DELETE FROM TRVehicleLease
                                    WHERE VID=:VID""",
                                    {"VID":VID})
            self.latest_response = {"response":"Success updating ownership of vehicle and resetting vehicle members"}
        else:
            raise PermissionError("Requester UID is not VID Owner")
    
    def addFriend(self, VID, UID):
        if self.RequesterIsOwner:
            self.curr.execute("""INSERT INTO TRVehicleLease (VID,UID,AccKey)
                                    values (:VID,:UID,:KEY)""",
                                    {"VID":VID,"UID":UID,"KEY":str(uuid4())})
            self.latest_response = {"response":"Member is added to vehicle user list"}
        else:
            raise PermissionError("Requester UID is not VID Owner")
            
    def removeFriend(self, VID, UID):
        if self.RequesterIsOwner:
            self.curr.execute("""DELETE FROM TRVehicleLease
                                    WHERE UID=:UID and VID=:VID""",
                                    {"UID":UID,"VID":VID})
            self.latest_response = {"response":"Member is deleted from vehicle user list"}
            if self.curr.rowcount < 1:
                raise ZeroRowAffected("No record is deleted for this request!")
        else:
            raise PermissionError("Requester UID is not VID Owner")

    def getVehicleMember(self,VID,UIDRequester):
        if self.RequesterIsOwner:
            self.curr.execute("""SELECT A.UID, A.AccKey, B.Username
                             FROM TRVehicleLease as A
                             JOIN MSTblUserLogin as B ON B.UID = A.UID
                             WHERE A.VID=:VID""",{"VID":VID})
        else:
            self.curr.execute("""SELECT A.UID, A.AccKey, B.Username
                             FROM TRVehicleLease as A
                             JOIN MSTblUserLogin as B ON B.UID = A.UID
                             WHERE A.VID=:VID and A.UID=:UID""",{"VID":VID, "UID":UIDRequester})
        result = self.curr
        conversion = convertSQLRowsToDict(result)
        self.latest_response = {"VehicleMember": conversion}

    def enableVehicle(self,VID):
        if self.OwnerCheck(VID) or self.MemberCheck(VID):
            self.curr.execute("""SELECT BTMacAddress FROM MSTblVehicleData WHERE VID=:VID""",{"VID":VID})
            result = self.curr.fetchone()
            self.latest_response = {"VehicleEnable": True, "macaddress":result[0]}
        else:
            raise UserNotFound("You're not member of this Vehicle")
    
    def disableVehicle(self,VID):
        if self.OwnerCheck(VID) or self.MemberCheck(VID):
            self.curr.execute("""SELECT BTMacAddress FROM MSTblVehicleData WHERE VID=:VID""",{"VID":VID})
            result = self.curr.fetchone()
            self.latest_response = {"VehicleEnable": False, "macaddress":result[0]}
        else:
            raise UserNotFound("You're not member of this Vehicle")
    
    def OwnerCheck(self,VID):
        self.curr.execute("""SELECT UID FROM MSTblVehicleData WHERE VID=:VID""",{"VID":VID})
        VehicleOwner = self.curr.fetchone()
        if VehicleOwner is not None:
            if self.uid == VehicleOwner[0]:
                return True
            else:
                return False
        else:
            raise VehicleNotFound("Vehicle doesn't exist !")

    def MemberCheck(self,VID):
        self.curr.execute("""SELECT UID FROM TRVehicleLease WHERE VID=:VID""",{"VID":VID})
        VehicleUser = self.curr.fetchall()
        for user in VehicleUser:
            if user["UID"] == self.uid:
                return True
        return False