import sqlite3
from UserClass import UserNotFound
from main import UnknownIntent

class GroupClass:
    latest_response = None
    def __init__(self,conn: sqlite3.Connection, uid, msg) -> None:
        self.msg = msg
        self.sqlConn = conn
        self.curr = self.sqlConn.cursor()
        sqlScript = self.curr.execute("SELECT MSTblUserLogin.UID, GID FROM GIDHEADER INNER JOIN MSTblUserLogin on MSTblUserLogin.UID = GIDHeader.UIDOwner")
        result = sqlScript.fetchone()
        self.uid = uid
        self.groupID = result[1]

    def intentReader(self):
        self.vehicleID = self.msg["VID"]
        self.friendUID = self.msg["UIDMember"]
        intent = self.msg["intent"]
        if intent == "add":
            self.addFriend()
            self.latest_response = "Member is added to group"
        elif intent == "Delete":
            self.removeFriend()
            self.latest_response = "Member is deleted from group"
        else:
            raise UnknownIntent
        
    def addFriend(self):
        try:
            self.curr.execute("INSERT INTO TRGIDMember (GID,VID,UIDMember) values (:GID,:VID,:UIDMember)",{"GID": self.groupID,"VID":self.vehicleID,"UIDMember":self.friendUID})
            self.sqlConn.commit()
        except sqlite3.IntegrityError as e:
            raise UserNotFound("UIDMember is not found")
    def removeFriend(self):
        try:
            self.curr.execute("DELETE FROM TRGIDMember WHERE UIDMember=:UIDMember",{"UIDMember":self.friendUID})
            self.sqlConn.commit()
        except sqlite3.OperationalError as e:
            raise UserNotFound("UIDMember is not found")