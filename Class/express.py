# Fire Data Express for Python
# Copyright (c) 2022 Fabrício Hausman

from typing import Any, List, overload
from enum import Enum
from datetime import *
import pyodbc

class FDDataType(Enum):
    pass

class FDFieldMap: 
    var      : str
    field    : str
    required : bool
    text     : str

    def __init__(self, var: str, field: str, required: bool, text: str = '') -> None:
        self.var      = var
        self.field    = field
        self.required = required
        self.text     = text

class FDClass:
    classfieldmap  = []    
    required       = [str]

    # @classmethod
    def mapping(self, args: [FDFieldMap]):
        for f in args:
            self.classfieldmap.append(f)                

    # Verifica se existe algum valor nulo na lista. onlyrequired analisa somente os requeridos
    def nullable(self, onlyrequired: bool = True) -> bool:    
        r = False
        for f in self.classfieldmap:
            if ((onlyrequired == True) and (f.required == True) and (eval(f.var) == None)) or ((onlyrequired == False) and (eval(f.var) == None)):
                r = True
                break

        return r    
    
    # Verifica se existe algum valor nulo na lista. onlyrequired analisa somente os requeridos. Retorna lista de FDFieldMap
    def nullablelist(self, onlyrequired: bool = True) -> []:    
        r = []
        for f in self.classfieldmap:
            if ((onlyrequired == True) and (f.required == True) and (eval(f.var) == None)) or ((onlyrequired == False) and (eval(f.var) == None)):
                r.append(f)                

        return r    

    # Verifica se existe algum valor nulo na lista. onlyrequired analisa somente os requeridos. Retorna lista de nomes amigáveis dos campos
    def nullablelistfriendly(self, onlyrequired: bool = True) -> []:    
        r = []
        for f in self.classfieldmap:
            if ((onlyrequired == True) and (f.required == True) and (eval(f.var) == None)) or ((onlyrequired == False) and (eval(f.var) == None)):
                r.append(f.text)                

        return r     
    
    # Monta uma lista de FDFieldInfo. se notnull == True somente não nulos serão incluídos
    def makefieldinfo(self, notnull: bool = True) -> []:
        r = []
        for f in self.classfieldmap:
            if ((notnull == True) and (eval(f.var) != None)) or ((notnull == False)):
                r.append(FDFieldInfo(f.field, f.var))                

        return r            




    # l = []
    # if user.login  != None:
    #     l.append(FDFieldInfo('Login',  user.login))
    # if user.email  != None:
    #     l.append(FDFieldInfo('Email',  user.email))
    # if user.name   != None:
    #     l.append(FDFieldInfo('Name',  user.name))
    # if user.psw    != None:
    #     l.append(FDFieldInfo('Psw',  encode_b64(user.psw, True)))
    # if user.family != None:
    #     l.append(FDFieldInfo('Family',  user.family))    

class FDFieldInfo:
    name  : str
    value : None

    def __init__(self, name: str, value) -> None:
        self.name = name
        self.value = value

class FDDateTime:
    dt   : datetime
    date : None
    time : None

    def __init__(self) -> None:
        pass        

class FDDataSet(object):
    recordset   = None
    recordcount : int = 0
    recno       : int = -1
    fieldnames  = [] 
    fieldcount  = -1 
    eof         = False  

    def __init__(self, cursor: pyodbc.Cursor, leave: bool = False) -> None:
        self.recordset   = cursor.fetchall()
        self.recordcount = len(self.recordset)
        self.recno       = 0 if self.recordcount > 0 else -1
        self.fieldnames  = [column[0] for column in cursor.description]
        self.fieldcount  = len(self.fieldnames)
        if self.recordcount == 0:
            self.eof = True

        # Libera cursor
        if leave: 
            cursor.close()         

    def goto(self, index: input):
        if self.recordcount > 0:
            if index >= 0 & index < self.recordcount:
                self.recno = index 
    
    def first(self):        
        if self.recordcount > 0:
            self.recno = 0 
            self.eof   = False

    def last(self):        
        if self.recordcount > 0:
            self.eof   = True
            self.recno = self.recordcount -1

    def next(self):
        if self.recordcount > 0:
            if self.recno < (self.recordcount -1):
                self.recno += 1
            else:
                self.eof = True         

    def prior(self):
        if self.recno > 0 & self.recordcount > 0:
            self.recno -= 1                                

    def fieldbyname(self, name: str):
        found = False
        value = None
        for i, c in enumerate(self.fieldnames):
            if c.lower() == name.lower():
                if self.recordcount > 0:
                    value = self.recordset[self.recno][i]
                found = True
                break
        if not found:      
            raise ValueError(f'Field {name} not found on recordset')
        
        return value
    
    def fieldindex(self, name: str) -> int:
        found = False
        index = -1
        for i, c in enumerate(self.fieldnames):
            if c.lower() == name.lower():
                index = i
                found = True
                break

        if not found:      
            raise ValueError(f'Field {name} not found on recordset')
        
        return index
    
    def locate(self, fields = [], values = [], partialkey = True, caseinsensitive = True) -> bool:
        found = False
        if self.recordcount > 0:
            if len(fields) != len(values):
                raise ValueError('fields count differ of then values count')
            else:
                for rowid, row in enumerate(self.recordset):    
                    for i in range(len(fields)):
                        idx   = self.fieldindex(fields[i])    
                        found = False
                        
                        match type(values[i]).__name__ :
                            case 'str':                        
                                if partialkey == True and caseinsensitive == True:  
                                    if row[idx].lower().startswith(values[i].lower()):
                                        found = True
                                if partialkey == True and caseinsensitive == False: 
                                    if row[idx].startswith(values[i]):
                                        found = True
                                elif partialkey == False and caseinsensitive == True: 
                                    if row[idx].lower() == values[i].lower():
                                        found = True
                                elif partialkey == False and caseinsensitive == False: 
                                    if row[idx] == values[i]:
                                        found = True
                            case _: 
                                if row[idx] == values[i]:
                                    found = True        

                        if found == False:
                            break

                    if found == True:
                        self.goto(rowid)
                        break    
            return found                             
        
    def toJson(self, all: bool = False):
        js = ''
        if self.recordcount > 0:
            if all == True:            
                self.first()
                for i in range(self.recordcount):
                    js = js + self.__recToJson()
                    if self.recno < (self.recordcount -1): js += ','
                    self.next()

                self.first()
                js = '[' + js + ']'  
            else:
                js = self.__recToJson();    
        else:
            js = '[]'            
        
        return js   
    
    def __recToJson(self):
        r = ''
        if self.recordcount > 0:
            for i, c in enumerate(self.fieldnames):
                if self.recordset[self.recno][i]  is not None:
                    r     = r + '"{}": '.format(c.lower())
                    value = self.recordset[self.recno][i]
                    
                    match type(value).__name__ :
                        case 'str':  r = r + f'"{value}"'
                        case 'bool': 
                            if   value == True:  r = r + 'true'
                            elif value == False: r = r + 'false'
                        case _:      r = r + f"{value}"

                    if i < (self.fieldcount -1):
                        r = r + ', '

            r = '{' + r +'}'
        return r              

    # def Field(name: str) -> any: 

class FDResulSet(object):
    dataset = FDDataSet
    error   = False
    message = ''

    def __init__(self):  
        pass          

class FDConnection():
    conn = None
    def __init__(self, server: str, port: str, database: str, user: str, pwd: str) -> None:
        self.CONN_STR    = '{driver};{server};{port};{database};{uid};{pwd}'
        self.DRIVER      = 'DRIVER={SQL Server Native Client 11.0}'
        self.SERVER      = 'SERVER={}'.format(server)
        if port != '':
            self.PORT   = 'PORT={}'.format(port)
        else: 
            self.PORT    = ''
        self.DATABASE    = 'DATABASE={}'.format(database)   
        self.USER        = 'UID={}'.format(user) 
        self.PWD         = 'PWD={}'.format(pwd)   

        self.conn = pyodbc.connect(self.CONN_STR.format(driver = self.DRIVER, server = self.SERVER, port = self.PORT, database = self.DATABASE, uid = self.USER, pwd = self.PWD))    
        
class FDExpress(object):
    conn : pyodbc.Connection

    def __init__(self, connection: pyodbc.Connection) -> None:
        self.conn = connection        

    def FDXQuery(self, sql: str, *params: Any) -> FDResulSet:
        r = FDResulSet()
        try:
            cur = self.conn.cursor()    
            cur.execute(sql, params)            
            r.dataset = FDDataSet(cur)
        except Exception as e: 
            r.error   = True
            r.message = (str(e))   
        finally:        
            cur.close()

        return r    
    
    def FDXSQL(self, sql: str, *params: Any) -> FDResulSet:
        r = FDResulSet()
        try:
            cur = self.conn.cursor()    
            cur.execute(sql, params)            
            self.conn.commit()
        except Exception as e: 
            r.error   = True
            r.message = (str(e))   
        finally:        
            cur.close()

        return r  

    def FDXInsert(self, table: str, args = []) -> FDResulSet:
        r      = FDResulSet()
        sql    = 'INSERT INTO {} ('.format(table)
        values = '('
        params = []       

        for i in range(len(args)):
            sql    = sql    + args[i].name
            values = values + '?'
            params.append(args[i].value)

            if i < len(args) -1: 
                sql    = sql    + ', '
                values = values + ', '
            else: 
                sql    = sql    + ')'
                values = values + ')'
                
        sql = sql + ' VALUES ' + values

        try:
            cur = self.conn.cursor()    
            cur.execute(sql, params)            
            self.conn.commit()
        except Exception as e: 
            r.error   = True
            r.message = (str(e))   
        finally:        
            cur.close()     

        return r

    def FDXUpdate(self, table: str, args = [], keys = []):
        r      = FDResulSet()
        sql    = 'UPDATE {} SET '.format(table)        
        params = []


        for i in range(len(args)):
            sql = sql + args[i].name + ' = ?'
            
            params.append(args[i].value)

            if i < len(args) -1: 
                sql = sql + ', '
                
        if len(keys) > 0:
            sql = sql + ' WHERE '

            for i in range(len(keys)):
                sql = sql + '(' + keys[i].name + ' = ?)'
                
                params.append(keys[i].value)

                if i < len(keys) -1: 
                    sql = sql + ' AND '

        try:
            cur = self.conn.cursor()    
            cur.execute(sql, params)            
            self.conn.commit()
        except Exception as e: 
            r.error   = True
            r.message = (str(e))   
        finally:        
            cur.close()     

        return r    
   
    def FDXDelete(self, table: str, keys = []):
        r      = FDResulSet()
        sql    = 'DELETE {}'.format(table)        
        params = []               
        
        sql = sql + ' WHERE '

        for i in range(len(keys)):
            sql = sql + '(' + keys[i].name + ' = ?)'
            
            params.append(keys[i].value)

            if i < len(keys) -1: 
                sql = sql + ' AND '
                    
        try:
            cur = self.conn.cursor()    
            cur.execute(sql, params)            
            self.conn.commit()
        except Exception as e: 
            r.error   = True
            r.message = (str(e))   
        finally:        
            cur.close()     

        return r        

    def AutoInc(self, table, field, filter: str = '') -> int:
        k    = 0
        _SQL = "SELECT ISNULL(MAX({}), 0) AS PK FROM {}".format(field, table)
        if filter != '':
            _SQL = _SQL + ' WHERE {}'.format(filter)

        rs = self.FDXQuery(_SQL)

        if rs.error:
            raise ValueError(rs.message)

        if rs.dataset.recordcount == 0:
            k = 1
        else:                
            k = rs.dataset.fieldbyname('PK')
            k += 1        

        return k       

    def ServerNow(self) -> FDDateTime:
        r = FDDateTime()
        try:
            cur = self.conn.cursor()    
            cur.execute('SELECT GETDATE() AS NOW')            

            table      = FDDataSet(cur)
            r.dt       = table.fieldbyname('NOW') 
            r.date     = r.dt.date()
            r.time     = r.dt.time()

        except Exception as e: 
            print(str(e))
        finally:        
            cur.close()  
            