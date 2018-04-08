import os
import flask as Flask
from flask_cors import CORS
import pyrebase
import sys
from datetime import datetime
import json
from os import environ

def connect_to_storage():

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
    storage = service_firebase.storage()

    return storage

app = Flask.Flask(__name__, static_url_path='')
CORS(app)

config = {
    "apiKey": "AIzaSyBJjyzlDHxvM-IcxWZwzYY-cIvtMpVreQU",
    "authDomain": "rushdb-b1177.firebaseapp.com",
    "databaseURL": "https://rushdb-b1177.firebaseio.com",
    "storageBucket": "rushdb-b1177.appspot.com",
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
storage = connect_to_storage()

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
def get_rushees():
    #org = Flask.request.get_json()['org']
    userToken = Flask.request.get_json()['userToken']
    
    try:
        org = get_org(userToken)
        rushees = db.child(org).child('rushees').get(userToken).val()
        return json.dumps(rushees)
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

#sys.stdout.flush()

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

    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password(email, password)
    return str(user['idToken'])
    
#userToken = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImMwNmEyMTQ5YjdmOTU3MjgwNTJhOTg1YWRlY2JmNWRlMDQ3Y2RhNmYifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vcnVzaGRiLWIxMTc3IiwiYXVkIjoicnVzaGRiLWIxMTc3IiwiYXV0aF90aW1lIjoxNTIzMTQ4NDA4LCJ1c2VyX2lkIjoia2c2YVNrTnJRSmVpcURwM0VDWTl3WDVOd3djMiIsInN1YiI6ImtnNmFTa05yUUplaXFEcDNFQ1k5d1g1Tnd3YzIiLCJpYXQiOjE1MjMxNDg0MDgsImV4cCI6MTUyMzE1MjAwOCwiZW1haWwiOiJicm90aGVyZG9lQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJlbWFpbCI6WyJicm90aGVyZG9lQGdtYWlsLmNvbSJdfSwic2lnbl9pbl9wcm92aWRlciI6InBhc3N3b3JkIn19.o7fUoQiU63HBHlBq8H-BFi-A21RctxdrcFXHEOBL70qtlScfNmhLJvmbjhnv5YNJEstuo28M3Cmsw7xIDX946ngpbxDD7c30PuW5Bx_MDKc2n42kIjf7pGGzREYjLhF4rhWQwAoW4hZt6BdY3B28tU7tEJdtqGy13-jXSRSKw5sx7ELrq98R9k2aXY1t52_kQaTWCraWoI48ZpnvbtiClwc51wWtKvXIrrGVjlCq4ude91SDDN65_MZ6WayVg_-_iARxRYJr9nPcw_p0u6jg74r2WF4H3fDJZnbmnFA2wVNtu2jLCg027875JIdck5j6P5P9wooZFtnwrE8-c6d0uw"
#picture_name = "Tom-Hulce-as-Larry-Kroger-tom-hulce-38317385-500-270.jpg"
   
#url = storage.child('deltatauchi/' + picture_name).download("download.jpg")



"""
Main method starts the Flask server
"""
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    #TESTING ONLY! Leave commented in production
    #app.run(host='127.0.0.1', port=port)

    