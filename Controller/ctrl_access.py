from Models.access import *
from __main__ import app
from flask import Flask, request, stream_with_context, Response
from Class.myconnection import *
from Class.nextutils import *

@app.route('/api/v1/hits/',      methods = ['GET', 'POST']) 
@app.route('/api/v1/hits/<id>',  methods = ['GET', 'PUT', 'DELETE'])
def _hits(id = 0):
    __result = NXResult
    cnx      = MyConnection()
    __result = cnx.res
    
    if not __result.error:      
        if request.method == 'GET':  
            if id == 0:            
                __result = hits(cnx)
                    
                return __result.toJSON()
            else:           
                __result = access(cnx, id)
                    
                return __result.toJSON()
            
        elif request.method == 'POST':         
            _access        = Access()
            _access.jsonImport(request.data)   
                        
            __result = access_create(cnx, _access)
                
            return __result.toJSON()
            
        elif request.method == 'PUT':              
            _access        = Access()
            _access.jsonImport(request.data)      
                     
            __result = access_update(cnx, _access, id)
                
            return __result.toJSON()   
            
        elif request.method == 'DELETE':               
            __result = access_delete(cnx, id)
                
            return __result.toJSON()  

@app.route('/api/v1/login_access/',      methods = ['GET']) 
def __access_login():
    __result = NXResult
    cnx      = MyConnection()
    __result = cnx.res
    if not __result.error:      
        if request.method == 'GET': 
            login   = request.headers.get('Login')
            psw     = request.headers.get('Psw')
            
            if not request.data:
                request.data = b'{}'
                
            __result = access_login(cnx, login, psw)
            
            return __result.toJSON()
        
@app.route('/api/v1/sendcode_access/',      methods = ['GET']) 
def __access_sendcode():
    __result = NXResult
    cnx      = MyConnection()
    __result = cnx.res
    
    email    = request.headers.get('Email')
    
    if not __result.error: 
        __result = send_code(cnx, email)
                    
        return __result.toJSON()
    
@app.route('/api/v1/checkcode_access/',      methods = ['GET']) 
def __access_checkcode():
    __result = NXResult
    cnx      = MyConnection()
    __result = cnx.res
    
    email    = request.headers.get('Email')
    code     = request.headers.get('Code')    
            
    if email and code:
        __result = checkcode(email, code)
            
        return __result.toJSON()   
    
@app.route('/api/v1/recover_access/',      methods = ['GET']) 
def __access_recover():
    __result = NXResult
    cnx      = MyConnection()
    __result = cnx.res
    
    email    = request.headers.get('Email')
    psw      = request.headers.get('Psw')
    confirm  = request.headers.get('Confirm')     
            
    if email and psw and confirm:
        __result = psw_updade(cnx, email, psw, confirm)
            
    return __result.toJSON()