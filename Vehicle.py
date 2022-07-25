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
            else:
                raise UnknownIntent
        self.sqlConn.commit()
        
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

    def getFBAPresentation(self):
        try:
            self.curr.execute("""SELECT VID,
                                 MSTblVehicleData.Type,
                                 MSTblVehicleData.TrainedNNPath,
                                 MSTblVehicleData.PoliceNum,
                                 MSTblVehicleData.TahunProduksi,
                                 MSTblVehicleData.Manufacturer 
                                 FROM MSTblVehicleData WHERE UIDOwner=:UID""",
                                {"UID": self.uid})
            res = self.curr.fetchall()
            sumn = []
            for record in res:
                temp = {"VID": record[0],"Type":record[1],"TrainedNNPath":record[2],"PoliceNum":record[3],"Tahun":record[4],"Merk":record[5]}
                sumn.append(temp)
            return {"-"+str(self.groupID): {"OwnedVID": sumn}}
        except sqlite3.OperationalError as e:
            raise UserNotFound("Member didn't have vehicle")