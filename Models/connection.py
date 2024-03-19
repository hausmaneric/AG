from Class.nextbase import *
from Class.express import *
from Class.nextutils import *
from Class.agsql import *
from Class.myconnection import *

#region Modelos de Referência

class Connection(NXBase):
    id          : int
    person      : int
    kinship     : int
    
    def __init__(self) -> None:
        self.id          = None
        self.person      = None
        self.kinship     = None
        
    @classmethod    
    def new(self, id: int, person: int, kinship: int, ) -> Any:
        c             = Connection()
        c.id          = id
        c.person      = person
        c.kinship     = kinship
        return c 
#endregion   

def connections(cnx: MyConnection) -> NXResult: 
    __result = NXResult()   
    
    try:
        rs = cnx.xp.FDXQuery(SQL_AG_CONNECTIONS)
        if rs.dataset.recordcount == 0:
            __result.warning = True
            __result.message = 'Nenhum registro encontrado'
        else:
            list = []                     
            
            rs.dataset.first()
            
            while rs.dataset.eof == False:
                list.append(Connection.new(
                    rs.dataset.fieldbyname('Id'), 
                    rs.dataset.fieldbyname('Person'),
                    rs.dataset.fieldbyname('Kinship')))
                rs.dataset.next()
                
            __result.status = True
            __result.data   = list
            
    except Exception as e:
        __result.make_error(0, 'Erro ao carregar informações', str(e))  
    finally:
        pass

    return __result

def connection(cnx: MyConnection, id: int) -> NXResult: 
    __result = NXResult()   

    try:
        rs = cnx.xp.FDXQuery(SQL_AG_CONNECTIONS_ID, id)
        if rs.dataset.recordcount == 0:
            __result.warning = True
            __result.message = 'Nenhum registro encontrado'
        else:
           __result.status = True
           __result.data   = Connection.new(
                rs.dataset.fieldbyname('Id'),
                rs.dataset.fieldbyname('Person'),
                rs.dataset.fieldbyname('Kinship')).__dict__
            
    except Exception as e:
        __result.make_error(0, 'Erro ao carregar informações', str(e))  
    finally:
        pass
    
    return __result

def connection_create(cnx: MyConnection, connection: Connection) -> NXResult: 
    __result = NXResult()  
    
    try:         
        i   = cnx.xp.AutoInc('[Connection]', 'Id')
        
        cnx.xp.FDXInsert('[Connection]', [
            FDFieldInfo('Id',           i),
            FDFieldInfo('Person',       connection.person),
            FDFieldInfo('Kinship',      connection.kinship)
        ])
        
        connection.id   = i
        __result.status = True
        __result.data   = connection.__dict__
    
    except Exception as e:
        __result.make_error(0, 'Erro ao inserir dados', str(e))  
    finally:
        pass
    
    return __result

def connection_update(cnx: MyConnection, connection: Connection, id: int) -> NXResult: 
    __result = NXResult()  
    
    l = []
    if connection.person  != None:
        l.append(FDFieldInfo('Person',      connection.person))
    if connection.kinship != None:
        l.append(FDFieldInfo('Kinship',     connection.kinship))
    
    try: 
        cnx.xp.FDXUpdate('[Connection]', l, [FDFieldInfo('Id', id)])        
                
        connection.id   = id
        __result.status = True
        __result.data   = connection.__dict__
    
    except Exception as e:
        __result.make_error(0, 'Erro ao inserir dados', str(e))  
    finally:
        pass
    
    return __result

def connection_delete(cnx: MyConnection, id: int) -> NXResult:
    __result = NXResult()  
    
    try:  
        cnx.xp.FDXDelete('[Connection]', [FDFieldInfo('Id',  id)],)
        
        __result.info    = True
        __result.status  = True
        __result.message = "Usuário excluído com sucesso"
    
    except Exception as e:
        __result.make_error(0, 'Erro ao excluir dados', str(e))  
    finally:
        pass
    
    return __result  