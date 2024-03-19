import json
import jsonpickle
from typing import Any, overload
from datetime import datetime
from enum import Enum
from Class.express import *
from Class.express import Any

#region Rotinas objetos para JSON e JSON para objetos

class DatetimeHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        #return obj.strftime('%Y-%m-%d %H:%M:%S')
        return obj.isoformat() # ISO 8601

def objToJSON(o, native = True):
    """Gera o json de uma instância
       Se native = True gera json com referência a classe python py/object...
    """
    jsonpickle.handlers.registry.register(datetime, DatetimeHandler)
    return jsonpickle.encode(o, unpicklable=native)

def jsonToObj(s) -> Any:    
    """Transforma json em objeto"""    
    return jsonpickle.decode(s)

#endregion

# Classe primária com rotinas de conversão JSON
class NXBase:    
    __json      = None # __ convenção para campo privado
    __jsonError = None  
    def __init__(self, *args: Any, **kwds: Any) -> Any:
        """ **Kwds 'json' se informado uma string json monta o objeto com o json fornecido"""        
        self._json = kwds.get('json') 
        self.jsonImport()

    def __enter__(self):
        return self        

    def __exit__(self, type, value, traceback):
        pass        

    def __str__(self) -> str:
        return self.__class__          
                
    def jsonImport(self, js = None):   
        if js != None: # criado parametro js pois ao setar dados no atributo privado __json não reflete na classe pai 
           self.__json = js            

        if self.__json != '' and self.__json != None:         
            o = jsonToObj(self.__json)
            if type(o) is self.__class__:
                self.__dict__.update(self.__dict__)
                self.__jsonError = False
            elif type(o) is dict:
                self.__dict__.update(o)
                self.__jsonError = False    
            else:
                self.__jsonError = True   
        self.__json = None         
    
    def jsonError(self):
        return self.__jsonError     
    
    def toJSON(self):             
        # remove campos pivados da classe no json
        data = {
            key: value
            for key, value in self.__dict__.items()
            if not key.startswith('_')
        }                   
        return json.dumps(data, default=lambda o: o.__dict__, sort_keys=False, indent=4) 
    
    # @staticmethod -> não acessa attributos da classe e nem da instância
    # @classmethod  -> acessa atributos da classe mas não da instância 

    # # Exemplo de uso *args e **Kwargs
    # def doArgsKw(self, *args, **Kwargs):
    #     for x in args:
    #         print(x)
    #     a = Kwargs.get('str1')
    #     b = Kwargs.get('str2')
    #     print(a)
    #     print(b)

class NXDataClass(NXBase, FDClass):

    def __init__(self) -> Any:
        super().__init__()         

class NXResult(NXBase):
    """Classe referente a __resultado de função"""
    nx_result = True
    status    = False
    code      = -1
    info      = False
    warning   = False
    error     = False    
    message   = ''
    error_msg = ''
    data      = None
    
    def __init__(self, *args: Any, **kwds: Any) -> Any:        
        super().__init__(*args, **kwds)  
        self.nx_result = True
        self.status    = False
        self.code      = -1
        self.info      = False
        self.warning   = False
        self.error     = False            


    def make_error(self, code, message, error_msg = ''):      
        self.status    = False  
        self.code      = code
        self.error     = True
        self.message   = message
        self.error_msg = error_msg

