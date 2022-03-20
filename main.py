"""
1. Create, Read, dan Update kepemilikan kendaraan pada tabel MSTblVehicleData
2. Create, Read, dan Update data login user pada tabel MSTblUserLogin
3. Create, Read, Update, Delete user dari kendaraan pada tabel JNTblFriendGroupData
"""
from cmath import e
from distutils.log import error
from tkinter import E
from flask import Flask, request, json, g, session
from flask_session import Session
from LoginClass import LoginClass
from UserClass import UserClass, UserExist, UserNotFound, ColumnNotExist
import sqlite3
app = Flask(__name__)
SESSION_PERMANENT = False
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
DATABASE = 'test.db'
Session(app)

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
    return 'Welcome to Sisalma-dev'

# Post API for CRU on vehicle entity
# Current feature : addVehicle, transferVehicle
@app.route('/vehicleOps',methods = ['POST'])
def postMessageVehicle():
    return 'Hello, World'

# Post API for CRU on login entity
# Current feature : signup, signin, edit
# Requirement : 
@app.route('/loginOps',methods = ['POST'])
def postMessageLogin():
    try:
        loginObj = LoginClass(get_db())
        loginObj.storeUserPass(request.get_json(force=True))
        if loginObj.intent.lower() == "login":
            loginObj.authUserPass()
            session['uid'] = loginObj.UID
        elif loginObj.intent.lower() == "signup":
            loginObj.newUserCreation()
        return json.dumps({"success": True, "msg": loginObj.latest_response})
    except UserNotFound or UserExist as e:
        return json.dumps({"success": False, "msg": e.error})

@app.route('/userOps',methods = ['POST'])
def postMessageUser():
    test = session.get('uid',None)
    if test is not None:
        user = UserClass(get_db(),session.get('uid'))
        try:
            user.storeRequestData(request.get_json(force=True))
            return json.dumps({"success": True, "msg": user.latest_response})
        except (sqlite3.Error,ColumnNotExist) as emm:    
            return json.dumps({"success": False, "msg": emm.args}),403    
    else:
        return json.dumps({"success": False, "msg": "No users over here, login first"}),403

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