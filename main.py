"""
1. Create, Read, dan Update kepemilikan kendaraan pada tabel MSTblVehicleData
2. Create, Read, dan Update data login user pada tabel MSTblUserLogin
3. Create, Read, Update, Delete user dari kendaraan pada tabel JNTblFriendGroupData
"""
from flask import Flask, request, json
from LoginClass import LoginClass
from UserClass import UserClass
from jsonschema import validate
import sqlite3
app = Flask(__name__)
sqlite3Conn = sqlite3.connect("main.db")

@app.route('/')
def index():
    return 'Welcome to Sisalma-dev'

# Post API for CRU on vehicle entity
# Current feature : addVehicle, transferVehicle
@app.route('/vehicleOps',methods = ['POST'])
def postMessageVehicle():
    return 'Hello, World'

# Post API for CRU on user entity
# Current feature : signup, signin, edit
# Requirement : 
@app.route('/userOps',methods = ['POST'])
def postMessageUser():
    try:
        dataObj: LoginClass =  json.loads(request.data, object_hook=LoginClass)
        if dataObj.intent.lower() == "signin":
            dataUser: UserClass = UserClass(dataObj.authUserPass(sqlite3Conn))
            return dataUser.uid()
        elif dataObj.intent.lower() == "login":
            pass
        elif dataObj.intent.lower() == "edit":
            pass 
    except AttributeError as e:
        return repr(e)

# Post API for CRU on group entity
# Current feature : add user to group, delete user from group
# Requirement : UID and VID
@app.route('/groupOps',methods = ['POST'])
def postMessageGroup():
    return 'Hello, World'

# Post API for fetching packed user summary that contain
# FingerData and it's UID Owner. return file contain structured byte data
# Current feature : add user to group, delete user from group
# Requirement : UID and VID
@app.route('/packedUserSummary',methods = ['POST'])
def getPackedUserSummary():
    return 'Hello, World'

