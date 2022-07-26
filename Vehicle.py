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
                self.removeFriend(each["UID"])
            elif intent == "transfer":
                self.transferOwnership(each["UID"])
            else:
                raise UnknownIntent
        self.sqlConn.commit()

    def transferOwnership(self,toUID):
        self.curr.execute("""UPDATE MSTblVehicleData
                                 SET UID=:toUID
                                 WHERE UID=:fromUID""",
                                 {"toUID":toUID,"fromUID":self.uid})
    
    def addFriend(self, VID, UID):
        try:
            self.curr.execute("""INSERT INTO TRVehicleLease (VID,UID,AccKey)
                                 values (:VID,:UID,:KEY)""",
                                 {"VID":VID,"UID":UID,"KEY":str(uuid4())})
            self.latest_response = "Member is added to vehicle user list"
        except sqlite3.IntegrityError as e:
            raise ForeignKeyNotFound("Vehicle or User doesn't not exist")
            
    def removeFriend(self, VID, UID):
        try:
            self.curr.execute("""DELETE FROM TRVehicleLease
                                 WHERE UID=:UID and VID=:VID""",
                                 {"UID":UID,"VID":VID})
            self.latest_response = "Member is deleted from vehicle user list"
        except sqlite3.OperationalError as e:
            raise UserNotFound("User is not found")