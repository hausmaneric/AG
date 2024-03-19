from __main__ import app
from Controller.nxc import *

@app.route('/') 
def root():
    return "API OK"
