from Class.nextbase import *
from Class.express import *
from Class.nextutils import *
from Class.agsql import *
from Class.myconnection import *

#region Modelos de Referência

class State(NXBase):
    id     : int
    name   : str
    
    def __init__(self) -> None:
        self.id     = None
        self.name   = None
        
    @classmethod    
    def new(self, id: int, name: str) -> Any:
        s        = State()
        s.id     = id
        s.name   = name
        return s     
#endregion   

def states(cnx: MyConnection) -> NXResult: 
    __result = NXResult()   
    
    try:
        rs = cnx.xp.FDXQuery(SQL_AG_STATES)
        if rs.dataset.recordcount == 0:
            __result.warning = True
            __result.message = 'Nenhum registro encontrado'
        else:
            list = []                     
            
            rs.dataset.first()
            
            while rs.dataset.eof == False:
                list.append(State.new(
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

def state(cnx: MyConnection, id: int) -> NXResult: 
    __result = NXResult()   

    try:
        rs = cnx.xp.FDXQuery(SQL_AG_STATES_ID, id)
        if rs.dataset.recordcount == 0:
            __result.warning = True
            __result.message = 'Nenhum registro encontrado'
        else:
           __result.status   = True
           __result.data     = State.new(
               rs.dataset.fieldbyname('Id'),
               rs.dataset.fieldbyname('Name')).__dict__
            
    except Exception as e:
        __result.make_error(0, 'Erro ao carregar informações', str(e))  
    finally:
        pass
    
    return __result

def state_create(cnx: MyConnection, state: State) -> NXResult: 
    __result = NXResult()  
    
    try:         
        i   = cnx.xp.AutoInc('[State]', 'Id')
        
        cnx.xp.FDXInsert('[state]', [
            FDFieldInfo('Id',     i),
            FDFieldInfo('Name',   state.name)
        ])
        
        state.id        = i
        __result.status = True
        __result.data   = state.__dict__
    
    except Exception as e:
        __result.make_error(0, 'Erro ao inserir dados', str(e))  
    finally:
        pass
    
    return __result

def state_update(cnx: MyConnection, state: State, id: int) -> NXResult: 
    __result = NXResult()  
    
    l = []
    if state.name != None:
        l.append(FDFieldInfo('Name',  state.name))
    
    try: 
        cnx.xp.FDXUpdate('[State]', l, [FDFieldInfo('Id', id)])        
                
        state.id        = id
        __result.status = True
        __result.data   = state.__dict__
    
    except Exception as e:
        __result.make_error(0, 'Erro ao inserir dados', str(e))  
    finally:
        pass
    
    return __result

def state_delete(cnx: MyConnection, id: int) -> NXResult:
    __result = NXResult()  
    
    try:  
        cnx.xp.FDXDelete('[State]', [FDFieldInfo('Id',  id)],)
        
        __result.info    = True
        __result.status  = True
        __result.message = "Usuário excluído com sucesso"
    
    except Exception as e:
        __result.make_error(0, 'Erro ao excluir dados', str(e))  
    finally:
        pass
    
    return __result  