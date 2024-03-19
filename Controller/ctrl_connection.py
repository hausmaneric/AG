from Models.connection import *
from __main__ import app
from flask import Flask, request, stream_with_context, Response
from Class.myconnection import *
from Class.nextutils import *

@app.route('/api/v1/connections/',      methods = ['GET', 'POST']) 
@app.route('/api/v1/connections/<id>',  methods = ['GET', 'PUT', 'DELETE'])
def _connections(id = 0):
    __result = NXResult
    cnx      = MyConnection()
    __result = cnx.res
    
    if not __result.error:      
        if request.method == 'GET':  
            if id == 0:            
                __result = connections(cnx)
                    
                return __result.toJSON()
            else:           
                __result = connection(cnx, id)
                    
                return __result.toJSON()
            
        elif request.method == 'POST':         
            _connection        = Connection()
            _connection.jsonImport(request.data)  
                        
            __result = connection_create(cnx, _connection)
                
            return __result.toJSON()
            
        elif request.method == 'PUT':              
            _connection        = Connection()
            _connection.jsonImport(request.data)      
                     
            __result = connection_update(cnx, _connection, id)
                
            return __result.toJSON()   
            
        elif request.method == 'DELETE':               
            __result = connection_delete(cnx, id)
                
            return __result.toJSON()  