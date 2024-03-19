from Class.nextbase import *
from Class.express import *
from Class.nextutils import *
from Class.agsql import *
from Class.myconnection import *

#region Modelos de Referência

class Kinship(NXBase):
    id     : int
    name   : str
    
    def __init__(self) -> None:
        self.id     = None
        self.name   = None
        
    @classmethod    
    def new(self, id: int, name: str) -> Any:
        s        = Kinship()
        s.id     = id
        s.name   = name
        return s     
#endregion   

def kinships(cnx: MyConnection) -> NXResult: 
    __result = NXResult()   
    
    try:
        rs = cnx.xp.FDXQuery(SQL_AG_kINSHIPS)
        if rs.dataset.recordcount == 0:
            __result.warning = True
            __result.message = 'Nenhum registro encontrado'
        else:
            list = []                     
            
            rs.dataset.first()
            
            while rs.dataset.eof == False:
                list.append(Kinship.new(
                    rs.dataset.fieldbyname('Id'), 
                    rs.dataset.fieldbyname('Name')))
                rs.dataset.next()
                
            __result.status = True
            __result.data   = list
            
    except Exception as e:
        __result.make_error(0, 'Erro ao carregar informações', str(e))  
    finally:
        pass

    return __result

def kinship(cnx: MyConnection, id: int) -> NXResult: 
    __result = NXResult()   

    try:
        rs = cnx.xp.FDXQuery(SQL_AG_kINSHIPS_ID, id)
        if rs.dataset.recordcount == 0:
            __result.warning = True
            __result.message = 'Nenhum registro encontrado'
        else:
           __result.status   = True
           __result.data     = Kinship.new(
               rs.dataset.fieldbyname('Id'),
               rs.dataset.fieldbyname('Name')).__dict__
            
    except Exception as e:
        __result.make_error(0, 'Erro ao carregar informações', str(e))  
    finally:
        pass
    
    return __result

def kinship_create(cnx: MyConnection, kinship: Kinship) -> NXResult: 
    __result = NXResult()  
    
    try:         
        i   = cnx.xp.AutoInc('[kinship]', 'Id')
        
        cnx.xp.FDXInsert('[kinship]', [
            FDFieldInfo('Id',     i),
            FDFieldInfo('Name',   kinship.name)
        ])
        
        kinship.id      = i
        __result.status = True
        __result.data   = kinship.__dict__
    
    except Exception as e:
        __result.make_error(0, 'Erro ao inserir dados', str(e))  
    finally:
        pass
    
    return __result

def kinship_update(cnx: MyConnection, kinship: Kinship, id: int) -> NXResult: 
    __result = NXResult()  
    
    l = []
    if kinship.name != None:
        l.append(FDFieldInfo('Name',  kinship.name))
    
    try: 
        cnx.xp.FDXUpdate('[kinship]', l, [FDFieldInfo('Id', id)])        
                
        kinship.id      = id
        __result.status = True
        __result.data   = kinship.__dict__
    
    except Exception as e:
        __result.make_error(0, 'Erro ao inserir dados', str(e))  
    finally:
        pass
    
    return __result

def kinship_delete(cnx: MyConnection, id: int) -> NXResult:
    __result = NXResult()  
    
    try:  
        cnx.xp.FDXDelete('[kinship]', [FDFieldInfo('Id',  id)],)
        
        __result.info    = True
        __result.status  = True
        __result.message = "Usuário excluído com sucesso"
    
    except Exception as e:
        __result.make_error(0, 'Erro ao excluir dados', str(e))  
    finally:
        pass
    
    return __result  