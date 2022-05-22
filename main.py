"""
1. Create, Read, dan Update kepemilikan kendaraan pada tabel MSTblVehicleData
2. Create, Read, dan Update data login user pada tabel MSTblUserLogin
3. Create, Read, Update, Delete user dari kendaraan pada tabel JNTblFriendGroupData
"""
import sqlite3
from time import sleep
import firebase_admin
from firebase_admin import credentials, db as fba_db
from flask import Flask, request, json, g, session
from flask_session import Session
from GroupClass import GroupClass
from LoginClass import LoginClass
from UserClass import UserClass, UserExist, UserNotFound, ColumnNotExist
from ControllerException import UnknownIntent
from firebase_admin import credentials, db
from VehicleClass import VehicleClass
from cloudflareupdate import main as update, setup_parser

args = setup_parser()
update(6, 'AAAA', args)

app = Flask(__name__)
SESSION_PERMANENT = False
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
DATABASE = 'test-1.db'
Session(app)
cred = credentials.Certificate("latihanKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':'https://latihan-34c76-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return 'Welcome to Sisalma-dev',200

# Post API for CRU on vehicle entity
# Current feature : addVehicle, transferVehicle
@app.route('/vehicleOps',methods = ['GET'])
def postMessageVehicle():
    test = session.get('uid',None)
    if test is not None:
        try:
            vehicleObj = VehicleClass(get_db)
            vehicleObj.storeVID(request.)
        except (UserNotFound,UserExist,UnknownIntent) as e:
            return json.dumps({"success": False, "errmsg": e.error}),403
    else:
        return json.dumps({"success": False, "errMsg": "Cookies is missing, try reauthenticating to loginOps endpoint"}),403

# Post API for CRU on login entity
# Current feature : signup, signin, edit authenticated user data
# Requirement : Username and password
@app.route('/loginOps',methods = ['POST'])
def postMessageLogin():
    try:
        loginObj = LoginClass(get_db())
        loginObj.storeUserPass(request.get_json(force=True))
        if loginObj.intent.lower() == "login":
            loginObj.authUserPass()
            session['uid'] = loginObj.UID
            updateFirebase(loginObj)
            sleep(1)
        elif loginObj.intent.lower() == "signup":
            loginObj.newUserCreation()
            updateFirebase(loginObj)
            sleep(1)
        else:
            raise UnknownIntent(loginObj.intent+" intent is not handle")
        return json.dumps({"success": True, "msg": loginObj.latest_response ,"uid": loginObj.UID})
    except (UserNotFound,UserExist,UnknownIntent) as e:
        return json.dumps({"success": False, "errmsg": e.error}),403

@app.route('/userOps',methods = ['POST'])
def postMessageUser():
    test = session.get('uid',None)
    if test is not None:
        user = UserClass(get_db(),session.get('uid'))
        try:
            user.storeRequestData(request.get_json(force=True))
            return json.dumps({"success": True, "msg": user.latest_response})
        except (sqlite3.Error,ColumnNotExist) as emm:    
            return json.dumps({"success": False, "errMsg": emm.args}),403    
    else:
        return json.dumps({"success": False, "errMsg": "Cookies is missing, try reauthenticating to loginOps endpoint"}),403

# Post API for CRU on group entity
# Current feature : add user to group, delete user from group
# Requirement : UID and VID
@app.route('/groupOps',methods = ['POST'])
def postMessageGroup():
    test = session.get('uid',None)
    if test is not None:
        try:
            groupOwner = GroupClass(get_db(),session.get('uid'),request.get_json(force=True))
            groupOwner.intentReader()
            return json.dumps({"success": True, "msg": groupOwner.latest_response})
        except (UnknownIntent,UserNotFound) as e:
            return json.dumps({"success": False, "errMsg": e.error}),403
    else:
        return json.dumps({"success": False, "errMsg": "Cookies is missing, try reauthenticating to loginOps endpoint"}),403

# Post API for fetching packed user summary that contain
# TrainedNN and it's UID Owner. return file contain structured byte data
# Requirement : UID and VID
@app.route('/packedUserSummary',methods = ['POST'])
def getPackedUserSummary():
    return 'Hello, World'


def updateFirebase(loginObj:LoginClass):
    userObj = UserClass(get_db(),loginObj.UID)
    groupObj = GroupClass(get_db(),loginObj.UID,None)
    ref = fba_db.reference("Userdata")
    ref.update(userObj.getFBAPresentation())
    ref = fba_db.reference("GIDMember")
    ref.update(groupObj.getFBAPresentation())