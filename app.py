import os
import flask as Flask
from flask_cors import CORS
import pyrebase
import sys

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

@app.route('/get-rushees', methods=["POST"])
def get_brothers():
    org = Flask.request.get_json()['org']
    userToken = Flask.request.get_json()['userToken']

    rushees = db.child(org).child('rushees').get(userToken).val()
    return str(rushees)

"""
Main method starts the Flask server
"""
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    #TESTING ONLY! Leave commented in production
    #app.run(host='127.0.0.1', port=port)