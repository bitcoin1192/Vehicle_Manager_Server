import sqlite3
from UserClass import UserNotFound
from ControllerException import UnknownIntent

class GroupClass:
    latest_response = None
    def __init__(self,conn: sqlite3.Connection, uid, msg) -> None:
        self.msg = msg
        self.sqlConn = conn
        self.curr = self.sqlConn.cursor()
        sqlScript = self.curr.execute("""SELECT MSTblUserLogin.UID, GID FROM GIDHEADER 
                                        INNER JOIN MSTblUserLogin on MSTblUserLogin.UID = GIDHeader.UIDOwner""")
        result = sqlScript.fetchone()
        self.uid = uid
        self.groupID = result[1]

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