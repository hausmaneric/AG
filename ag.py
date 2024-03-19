from flask import Flask, request, stream_with_context, Response
from flask_cors import CORS

app  = Flask(__name__)
cors = CORS(app, resources={r"/api/v1/*": {"origins": "*", "methods": "GET, POST, PUT, DELETE", "headers": "Origin, Content-Type, X-Auth-Token, charset=utf-8"}})
app.config['JSON_AS_ASCII'] = False

# Rotas
import Controller.ctrl_user
import Controller.ctrl_access
import Controller.ctrl_family
import Controller.ctrl_connection
import Controller.ctrl_kinship
import Controller.ctrl_person
import Controller.ctrl_state
import Controller.ctrl_main
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)