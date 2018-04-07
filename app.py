import os
import flask as Flask
from flask_cors import CORS

app = Flask.Flask(__name__, static_url_path='')
CORS(app)

@app.route('/')
def hello():
    return 'Hello World!'

"""
Main method starts the Flask server
"""
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    #TESTING ONLY! Leave commented in production
    #app.run(host='127.0.0.1', port=port)