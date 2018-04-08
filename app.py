import os
import flask as Flask
from flask_cors import CORS
import pyrebase
import sys
from datetime import datetime
import json
from os import environ

app = Flask.Flask(__name__, static_url_path='')
CORS(app)

def connect_to_admin_database():

    # Must read from environment variables for security
    auth_dict = {}
    auth_dict['type'] = environ.get('type')
    auth_dict['project_id'] = environ.get('project_id')
    auth_dict['private_key_id'] = environ.get('private_key_id')
    auth_dict['private_key'] = environ.get('private_key')
    auth_dict['client_email'] = environ.get('client_email')
    auth_dict['client_id'] = environ.get('client_id')
    auth_dict['auth_uri'] = environ.get('auth_uri')
    auth_dict['token_uri'] = environ.get('token_uri')
    auth_dict['auth_provider_x509_cert_url'] = environ.get('auth_provider_x509_cert_url')
    auth_dict['client_x509_cert_url'] = environ.get('client_x509_cert_url')

    with open('temp_auth.json', 'w') as outfile:
        json.dump(auth_dict, outfile)

    with open('temp_auth.json') as infile:
        outfile = open("auth.json", "w")

        output = ""
        for line in infile:
            output += line

        output = output.replace('\\n', 'n')
        outfile.write(output)
        outfile.close()


    service_config = {
        "apiKey": "AIzaSyBJjyzlDHxvM-IcxWZwzYY-cIvtMpVreQU",
        "authDomain": "rushdb-b1177.firebaseapp.com",
        "databaseURL": "https://rushdb-b1177.firebaseio.com",
        "storageBucket": "rushdb-b1177.appspot.com",
        "serviceAccount": "./auth.json"
    }

    service_firebase = pyrebase.initialize_app(service_config)
    db = service_firebase.database()

    return db

config = {
    "apiKey": "AIzaSyBJjyzlDHxvM-IcxWZwzYY-cIvtMpVreQU",
    "authDomain": "rushdb-b1177.firebaseapp.com",
    "databaseURL": "https://rushdb-b1177.firebaseio.com",
    "storageBucket": "rushdb-b1177.appspot.com",
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
admin_db = connect_to_admin_database()

@app.route('/')
def hello():
    return 'Hello World!'

def remove_none(arr):
    if len(arr) >= 1:
        return arr[1:]
    else:
        return arr

@app.route('/get-rushees', methods=["POST"])
def get_rushees():
    #org = Flask.request.get_json()['org']
    userToken = Flask.request.get_json()['userToken']
    
    try:
        org = get_org(userToken)
        rushees = db.child(org).child('rushees').get(userToken).val()

        # Convert to list for front-end processing
        rushees_list = []
        for key, value in rushees.items():
            new_value = dict(value)
            new_value['key'] = key
            rushees_list.append(new_value)

        return json.dumps(rushees_list)
    except:
        return "{\"success\" : false}"
    

@app.route('/submit-rushee', methods=["POST"])
def submit_rushee():
    userToken = Flask.request.get_json()['userToken']
    rushee = {}
    
    for key, value in Flask.request.get_json().items():
        if not key == 'userToken':
            rushee[key] = value
    
    try:
        org = get_org(userToken)
        db.child(org).child('rushees').push(rushee, userToken)
        return "{\"success\" : true}"
    except:
        return "{\"success\" : false}"

@app.route('/edit-rushee', methods=["POST"])
def edit_rushee():
    userToken = Flask.request.get_json()['userToken']
    userKey = Flask.request.get_json()['userKey']
    rushee = {}
    
    for key, value in Flask.request.get_json().items():
        if not (key == 'userToken' or key == 'userKey'):
            rushee[key] = value
    
    try:
        org = get_org(userToken)
        db.child(org).child('rushees').child(userKey).update(rushee, userToken)
        return "{\"success\" : true}"
    except:
        return "{\"success\" : false}"

@app.route('/get-org', methods=["POST"])
def get_org(userToken):
    orgs = db.child('organizations').get().val()
    
    #userToken = Flask.request.get_json()['userToken']
    auth = firebase.auth()
    account = auth.get_account_info(userToken)
    userId = account['users'][0]['localId']
    
    correct_org = None
    for org, value in orgs.items():
        for org_userId, _ in value['brothers'].items():
            if org_userId == userId:
                return org
    
    return "Error"

@app.route('/get-brothers', methods=["POST"])
def get_brothers():    
    userToken = Flask.request.get_json()['userToken']

    try:
        org = get_org(userToken)
        brothers = db.child('organizations').child(org).child('brothers').get().val()
        return json.dumps(brothers)
    except:
        return "{\"success\" : false}" 

@app.route('/get-picture', methods=["POST"])
def get_picture():    
    userToken = Flask.request.get_json()['userToken']
    picture_name = "Tom-Hulce-as-Larry-Kroger-tom-hulce-38317385-500-270.jpg"
    
    url = storage.child('deltatauchi/' + picture_name).download("download.jpg")

    return url

@app.route('/login', methods=["POST"])
def login():
    email = Flask.request.get_json()['email']
    password = Flask.request.get_json()['password']

    try:
        auth = firebase.auth()
        user = auth.sign_in_with_email_and_password(email, password)
        return "{\"userToken\" : \""+ str(user['idToken']) + "\"}"
    except:
        return "{\"userToken\" : false}"
    
@app.route('/get-org-password', methods=["POST"])
def get_org_password():
    userToken = Flask.request.get_json()['userToken']
    
    try:
        org = get_org(userToken)
        password = admin_db.child('org_passwords').child(org).get().val()
        return "{\"password\" : " + password + "}"
    except:
        return "{\"password\" : false}"

@app.route('/create-new-user', methods=["POST"])
def create_new_user():
    org = Flask.request.get_json()['org']
    org_password = Flask.request.get_json()['orgPassword']
    email = Flask.request.get_json()['email']
    password = Flask.request.get_json()['password']
    name = Flask.request.get_json()['name']

    correct_org_password = admin_db.child('org_passwords').child(org).get().val()
    if org_password == correct_org_password:
        try:
            auth = firebase.auth()
            user = {}
            try:
                user = auth.create_user_with_email_and_password(email, password)
            except:
                return "{\"userToken\" : false, \"reason\" : \"User already exists\"}"
        
            uid = str(user['localId'])
            userToken = str(user['idToken'])
        
            admin_db.child('organizations').child(org).child('brothers').child(uid).set(name)
            return "{\"userToken\" : \"" + userToken + "\"}"
        except:
            return "{\"userToken\" : false, \"reason\" : \"Something went wrong\"}"
    else:
        return "{\"userToken\" : false, \"reason\" : \"Invalid organization password\"}"

@app.route('/get-org-list', methods=["POST"])
def get_org_list():
    orgs = db.child('organizations').get().val()

    org_list = []
    for key, value in orgs.items():
        org_map = {}
        org_map['key'] = key
        org_map['name'] = value['name']
        org_list.append(org_map)

    return json.dumps(org_list)


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

    