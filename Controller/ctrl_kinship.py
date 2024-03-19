from Models.kinship import *
from __main__ import app
from flask import Flask, request, stream_with_context, Response
from Class.myconnection import *
from Class.nextutils import *

@app.route('/api/v1/kinships/',      methods = ['GET', 'POST']) 
@app.route('/api/v1/kinships/<id>',  methods = ['GET', 'PUT', 'DELETE'])
def _kinships(id = 0):
    __result = NXResult
    cnx      = MyConnection()
    __result = cnx.res
    
    if not __result.error:      
        if request.method == 'GET':  
            if id == 0:            
                __result = kinships(cnx)
                    
                return __result.toJSON()
            else:           
                __result = kinship(cnx, id)
                    
                return __result.toJSON()
            
        elif request.method == 'POST':         
            _kinship        = Kinship()
            _kinship.jsonImport(request.data)
                        
            __result = kinship_create(cnx, _kinship)
                
            return __result.toJSON()
            
        elif request.method == 'PUT':              
            _kinship        = Kinship()
            _kinship.jsonImport(request.data)      
                     
            __result = kinship_update(cnx, _kinship, id)
                
            return __result.toJSON()   
            
        elif request.method == 'DELETE':               
            __result = kinship_delete(cnx, id)
                
            return __result.toJSON()  