from Models.family import *
from __main__ import app
from flask import Flask, request, stream_with_context, Response
from Class.myconnection import *
from Class.nextutils import *

@app.route('/api/v1/familys/',      methods = ['GET', 'POST']) 
@app.route('/api/v1/familys/<id>',  methods = ['GET', 'PUT', 'DELETE'])
def _familys(id = 0):
    __result = NXResult
    cnx      = MyConnection()
    __result = cnx.res
    
    if not __result.error:      
        if request.method == 'GET':  
            if id == 0:            
                __result = familys(cnx)
                    
                return __result.toJSON()
            else:           
                __result = family(cnx, id)
                    
                return __result.toJSON()
            
        elif request.method == 'POST':         
            _family        = Family()
            _family.jsonImport(request.data)
                        
            __result = family_create(cnx, _family)
                
            return __result.toJSON()
            
        elif request.method == 'PUT':              
            _family        = Family()
            _family.jsonImport(request.data)      
                     
            __result = family_update(cnx, _family, id)
                
            return __result.toJSON()   
            
        elif request.method == 'DELETE':               
            __result = family_delete(cnx, id)
                
            return __result.toJSON()  