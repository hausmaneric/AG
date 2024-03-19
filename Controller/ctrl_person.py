from Models.person import *
from __main__ import app
from flask import Flask, request, stream_with_context, Response
from Class.myconnection import *
from Class.nextutils import *

@app.route('/api/v1/persons/',      methods = ['GET', 'POST']) 
@app.route('/api/v1/persons/<id>',  methods = ['GET', 'PUT', 'DELETE'])
def _persons(id = 0):
    __result = NXResult
    cnx      = MyConnection()
    __result = cnx.res
    
    if not __result.error:      
        if request.method == 'GET':  
            if id == 0:            
                __result = persons(cnx)
                    
                return __result.toJSON()
            else:           
                __result = person(cnx, id)
                    
                return __result.toJSON()
            
        elif request.method == 'POST':         
            _person        = Person()
            _person.jsonImport(request.data) 
                        
            __result = person_create(cnx, _person)
                
            return __result.toJSON()
            
        elif request.method == 'PUT':              
            _person        = Person()
            _person.jsonImport(request.data)      
                     
            __result = person_update(cnx, _person, id)
                
            return __result.toJSON()   
            
        elif request.method == 'DELETE':               
            __result = person_delete(cnx, id)
                
            return __result.toJSON()  