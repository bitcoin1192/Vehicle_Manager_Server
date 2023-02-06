"""
1. Create, Read, dan Update kepemilikan kendaraan pada tabel MSTblVehicleData
2. Create, Read, dan Update data login user pada tabel MSTblUserLogin
3. Create, Read, Update, Delete user dari kendaraan pada tabel JNTblFriendGroupData
"""
import sqlite3

from flask import Flask, request, json, g, session, make_response
from flask_session import Session
from Vehicle import VehicleClass
from LoginClass import LoginClass
from UserClass import UserClass, UserExist, UserNotFound, ColumnNotExist
from ControllerException import UnknownIntent

from cloudflareupdate import main as update, setup_parser
from AppError import *
from CreateTable import *

args = setup_parser()
#update(6, 'AAAA', args)

app = Flask(__name__)
SESSION_PERMANENT = False
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
DATABASE = 'doav8.db'
Session(app)
dbcheck = False

def get_db():
    global dbcheck
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.execute("PRAGMA foreign_keys = 1")
        curr = db.cursor()
        if dbcheck == False:
            curr.execute("SELECT name FROM sqlite_master WHERE type='table';")
            table_list = curr.fetchall()
            if table_list.__len__() <= 1:
                createTable(db)
                #fillTable(db)
            dbcheck = True
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    get_db()
    resp = make_response("Welcome to Sisalma-Dev")
    resp.set_cookie(key="uid",value="test",expires=None,)
    return resp

# Post API for CRU on login entity
# Current feature : signup, signin, edit authenticated user data
# Requirement : Username and password
@app.route('/loginOps',methods = ['POST'])
def postMessageLogin():
    try:
        loginObj = LoginClass(get_db())
        loginObj.storeUserPass(request.get_json(force=True))
        session['uid'] = loginObj.UID
        return loginObj.latest_response
    except (UserNotFound,UserExist,UnknownIntent,SIMNumberInvalid,InputIncomplete,MACAddressesNotMatch) as e:
        return json.dumps({"success": False, "errMsg": e.error}),403

@app.route('/userOps',methods = ['POST'])
def postMessageUser():
    test = session.get('uid',None)
    if test is not None:
        user = UserClass(get_db(),session.get('uid'))
        try:
            user.storeRequestData(request.get_json(force=True))
            return json.dumps({"success": True, "msg": user.latest_response})
        except (sqlite3.Error,ColumnNotExist,UserNotFound,VehicleExist) as emm:    
            return json.dumps({"success": False, "errMsg": emm.args[0]}),403 
    else:
        return json.dumps({"success": False, "errMsg": "Cookies is missing, try reauthenticating to loginOps endpoint"}),403

# Post API for CRU on vehicle entity
# Current feature : add and delete user, transfer ownership
@app.route('/vehicleOps',methods = ['POST'])
def postVehicle():
    test = session.get('uid',None)
    if test is not None:
        try:
            vehicleObj = VehicleClass(get_db(),session.get('uid'),request.get_json(force=True))
            vehicleObj.intentReader()
            return json.dumps({"success": True, "msg": vehicleObj.latest_response})
        except (UnknownIntent,sqlite3.Error,PermissionError, VehicleNotFound) as e:
            return json.dumps({"success": False, "errMsg": e.args[0]}),403
    else:
        return json.dumps({"success": False, "errMsg": "Cookies is missing, try reauthenticating to loginOps endpoint"}),403

# Post API for fetching packed user summary that contain
# TrainedNN and it's UID Owner. return file contain structured byte data
# Requirement : UID and VID
@app.route('/packedUserSummary',methods = ['POST'])
def getPackedUserSummary():
    return 'Hello, World'

app.run("::", port=41313)