from Models.state import *
from __main__ import app
from flask import Flask, request, stream_with_context, Response
from Class.myconnection import *
from Class.nextutils import *

@app.route('/api/v1/states/',      methods = ['GET', 'POST']) 
@app.route('/api/v1/states/<id>',  methods = ['GET', 'PUT', 'DELETE'])
def _states(id = 0):
    __result = NXResult
    cnx      = MyConnection()
    __result = cnx.res
    
    if not __result.error:      
        if request.method == 'GET':  
            if id == 0:            
                __result = states(cnx)
                    
                return __result.toJSON()
            else:           
                __result = state(cnx, id)
                    
                return __result.toJSON()
            
        elif request.method == 'POST':         
            _state        = State()
            _state.jsonImport(request.data)  
                        
            __result = state_create(cnx, _state)
                
            return __result.toJSON()
            
        elif request.method == 'PUT':              
            _state        = State()
            _state.jsonImport(request.data)      
                     
            __result = state_update(cnx, _state, id)
                
            return __result.toJSON()   
            
        elif request.method == 'DELETE':               
            __result = state_delete(cnx, id)
                
            return __result.toJSON()  