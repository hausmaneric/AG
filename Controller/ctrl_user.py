from Models.user import *
from __main__ import app
from flask import Flask, request, stream_with_context, Response
from Class.myconnection import *
from Class.nextutils import *

@app.route('/api/v1/users/',      methods = ['GET', 'POST']) 
@app.route('/api/v1/users/<id>',  methods = ['GET', 'PUT', 'DELETE'])
def _users(id = 0):
    __result = NXResult
    cnx      = MyConnection()
    __result = cnx.res
    
    if not __result.error:      
        if request.method == 'GET':  
            if id == 0:            
                __result = users(cnx)
                    
                return __result.toJSON()
            else:           
                __result = user(cnx, id)
                    
                return __result.toJSON()
            
        elif request.method == 'POST':         
            _user        = User()
            _user.jsonImport(request.data)   
                        
            __result = user_create(cnx, _user)
                
            return __result.toJSON()
            
        elif request.method == 'PUT':              
            _user        = User()
            _user.jsonImport(request.data)      
                     
            __result = user_update(cnx, _user, id)
                
            return __result.toJSON()   
            
        elif request.method == 'DELETE':               
            __result = user_delete(cnx, id)
                
            return __result.toJSON()  

@app.route('/api/v1/login/',      methods = ['GET']) 
def __login():
    __result = NXResult
    cnx      = MyConnection()
    __result = cnx.res
    if not __result.error:      
        if request.method == 'GET': 
            login   = request.headers.get('Login')
            psw     = request.headers.get('Psw')
            
            if not request.data:
                request.data = b'{}'
                
            __result = user_login(cnx, login, psw)
            
            return __result.toJSON()
        
@app.route('/api/v1/sendcode/',   methods = ['GET']) 
def __sendcode():
    __result = NXResult
    cnx      = MyConnection()
    __result = cnx.res
    
    email    = request.headers.get('Email')
    
    if not __result.error: 
        __result = send_code(cnx, email)
                    
        return __result.toJSON()
    
@app.route('/api/v1/checkcode/',  methods = ['GET']) 
def __checkcode():
    __result = NXResult
    cnx      = MyConnection()
    __result = cnx.res
    
    email    = request.headers.get('Email')
    code     = request.headers.get('Code')    
            
    if email and code:
        __result = checkcode(email, code)
            
        return __result.toJSON()   
    
@app.route('/api/v1/recover/',    methods = ['PUT']) 
def __recover():
    __result = NXResult
    cnx      = MyConnection()
    __result = cnx.res
    
    email    = request.headers.get('Email')
    psw      = request.headers.get('Psw')
    confirm  = request.headers.get('Confirm')     
            
    if email and psw and confirm:
        __result = psw_updade(cnx, email, psw, confirm)
            
    return __result.toJSON()