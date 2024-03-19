from Class.nextbase import *
from Class.express import *
from Class.nextutils import *
from Class.agsql import *
from Class.myconnection import *

#region Modelos de Referência

class Family(NXBase):
    id     : int
    name   : str
    
    def __init__(self) -> None:
        self.id     = None
        self.name   = None
        
    @classmethod    
    def new(self, id: int, name: str) -> Any:
        f        = Family()
        f.id     = id
        f.name   = name
        return f     
#endregion   

def familys(cnx: MyConnection) -> NXResult: 
    __result = NXResult()   
    
    try:
        rs = cnx.xp.FDXQuery(SQL_AG_FAMILYS)
        if rs.dataset.recordcount == 0:
            __result.warning = True
            __result.message = 'Nenhum registro encontrado'
        else:
            list = []                     
            
            rs.dataset.first()
            
            while rs.dataset.eof == False:
                list.append(Family.new(
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

def family(cnx: MyConnection, id: int) -> NXResult: 
    __result = NXResult()   

    try:
        rs = cnx.xp.FDXQuery(SQL_AG_FAMILYS_ID, id)
        if rs.dataset.recordcount == 0:
            __result.warning = True
            __result.message = 'Nenhum registro encontrado'
        else:
           __result.status   = True
           __result.data     = Family.new(
               rs.dataset.fieldbyname('Id'),
               rs.dataset.fieldbyname('Name')).__dict__
            
    except Exception as e:
        __result.make_error(0, 'Erro ao carregar informações', str(e))  
    finally:
        pass
    
    return __result

def family_create(cnx: MyConnection, family: Family) -> NXResult: 
    __result = NXResult()  
    
    try:         
        i   = cnx.xp.AutoInc('[family]', 'Id')
        
        cnx.xp.FDXInsert('[family]', [
            FDFieldInfo('Id',     i),
            FDFieldInfo('Name',   family.name)
        ])
        
        Family.id        = i
        __result.status = True
        __result.data   = Family.__dict__
    
    except Exception as e:
        __result.make_error(0, 'Erro ao inserir dados', str(e))  
    finally:
        pass
    
    return __result

def family_update(cnx: MyConnection, family: Family, id: int) -> NXResult: 
    __result = NXResult()  
    
    l = []
    if family.name != None:
        l.append(FDFieldInfo('Name',  family.name))
    
    try: 
        cnx.xp.FDXUpdate('[family]', l, [FDFieldInfo('Id', id)])        
                
        family.id        = id
        __result.status = True
        __result.data   = Family.__dict__
    
    except Exception as e:
        __result.make_error(0, 'Erro ao inserir dados', str(e))  
    finally:
        pass
    
    return __result

def family_delete(cnx: MyConnection, id: int) -> NXResult:
    __result = NXResult()  
    
    try:  
        cnx.xp.FDXDelete('[family]', [FDFieldInfo('Id',  id)],)
        
        __result.info    = True
        __result.status  = True
        __result.message = "Usuário excluído com sucesso"
    
    except Exception as e:
        __result.make_error(0, 'Erro ao excluir dados', str(e))  
    finally:
        pass
    
    return __result  