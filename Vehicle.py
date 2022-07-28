import sqlite3
from uuid import uuid4
from ControllerException import UnknownIntent
from AppError import *

class VehicleClass:
    latest_response = None
    def __init__(self, conn: sqlite3.Connection, uid, msg) -> None:
        self.msg = msg
        self.sqlConn = conn
        self.curr = self.sqlConn.cursor()
        self.uid = uid

    def intentReader(self):
        intent = self.msg["intent"]
        groupMember = self.msg["changeMember"]
        for each in groupMember:
            if intent == "add":
                self.addFriend(each["VID"],each["UID"])
            elif intent == "delete":
                self.removeFriend(each["VID"],each["UID"])
            elif intent == "transfer":
                self.transferOwnership(each["UID"],each["VID"])
            else:
                raise UnknownIntent("No handler for received intent \""+intent+"\" !")
        self.sqlConn.commit()

    def transferOwnership(self,toUID,VID):
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
        self.latest_response = "Success updating ownership of vehicle and resetting vehicle members"
    
    def addFriend(self, VID, UID):
        self.curr.execute("""INSERT INTO TRVehicleLease (VID,UID,AccKey)
                                 values (:VID,:UID,:KEY)""",
                                 {"VID":VID,"UID":UID,"KEY":str(uuid4())})
        self.latest_response = "Member is added to vehicle user list"
            
    def removeFriend(self, VID, UID):
        self.curr.execute("""DELETE FROM TRVehicleLease
                                 WHERE UID=:UID and VID=:VID""",
                                 {"UID":UID,"VID":VID})
        self.latest_response = "Member is deleted from vehicle user list"
        if self.curr.rowcount < 1:
            raise ZeroRowAffected("No record is deleted for this request!")