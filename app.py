import os
import flask as Flask
from flask_cors import CORS
import pyrebase
import sys
from datetime import datetime
import json

app = Flask.Flask(__name__, static_url_path='')
CORS(app)

config = {
    "apiKey": " AIzaSyBJjyzlDHxvM-IcxWZwzYY-cIvtMpVreQU",
    "authDomain": "rushdb-b1177.firebaseapp.com",
    "databaseURL": "https://rushdb-b1177.firebaseio.com",
    "storageBucket": "rushdb-b1177.appspot.com",
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

org = 'phikappasigmaan'

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/auth', methods=["POST"])
def auth():
    email = Flask.request.get_json()['email']
    password = Flask.request.get_json()['password']

    # Get a reference to the auth service
    auth = firebase.auth()

    # Log the user in
    user = auth.sign_in_with_email_and_password(email, password)

    return str(user['idToken'])

def remove_none(arr):
    if len(arr) >= 1:
        return arr[1:]
    else:
        return arr

@app.route('/get-rushees', methods=["POST"])
def get_brothers():
    #org = Flask.request.get_json()['org']
    userToken = Flask.request.get_json()['userToken']

    rushees = db.child(org).child('rushees').get(userToken).val()
    return json.dumps(rushees)

@app.route('/submit-rushee', methods=["POST"])
def submit_rushee():
    userToken = Flask.request.get_json()['userToken']
    rushee = {}
    
    for key, value in Flask.request.get_json().items():
        if not key == 'userToken':
            rushee[key] = value
    
    db.child(org).child('rushees').push(rushee, userToken)
    return "{\"success\" : true}"





#sys.stdout.flush()

    



"""
Main method starts the Flask server
"""
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    #TESTING ONLY! Leave commented in production
    #app.run(host='127.0.0.1', port=port)