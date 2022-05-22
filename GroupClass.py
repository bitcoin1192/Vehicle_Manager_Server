import sqlite3
from UserClass import UserNotFound
from ControllerException import UnknownIntent

class GroupClass:
    latest_response = None
    def __init__(self,conn: sqlite3.Connection, uid, msg) -> None:
        self.msg = msg
        self.sqlConn = conn
        self.curr = self.sqlConn.cursor()
        sqlScript = self.curr.execute("""SELECT GID FROM GIDHEADER WHERE UIDOwner=:uid""",{"uid":uid})
        result = sqlScript.fetchone()
        self.uid = uid
        self.groupID = result[0]

    def intentReader(self):
        intent = self.msg["intent"]
        groupMember = self.msg["changeMember"]
        for each in groupMember:
            if intent == "add":
                self.addFriend(each["VID"],each["UID"])
                self.latest_response = "Member is added to group"
            elif intent == "delete":
                self.removeFriend(each["UID"])
                self.latest_response = "Member is deleted from group"
            else:
                raise UnknownIntent
        self.sqlConn.commit()
        
    def addFriend(self, VID, UIDMember):
        try:
            self.curr.execute("""INSERT INTO TRGIDMember (GID,VIDLease,UIDMember)
                                 values (:GID,:VID,:UIDMember)""",
                                 {"GID": self.groupID,"VID":VID,"UIDMember":UIDMember})
        except sqlite3.IntegrityError as e:
            raise UserNotFound("UIDMember is not found")
            
    def removeFriend(self, UIDMember):
        try:
            self.curr.execute("""DELETE FROM TRGIDMember
                                 WHERE UIDMember=:UIDMember and GID=:GID""",
                                 {"UIDMember":UIDMember,"GID":self.groupID})
        except sqlite3.OperationalError as e:
            raise UserNotFound("UIDMember is not found")

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
            return {"GID-"+str(self.groupID): {"OwnedVID": sumn}}
        except sqlite3.OperationalError as e:
            raise UserNotFound("GIDMember didn't have vehicle")