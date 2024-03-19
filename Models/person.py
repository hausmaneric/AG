from Class.nextbase import *
from Class.express import *
from Class.nextutils import *
from Class.agsql import *
from Class.myconnection import *

#region Modelos de Referência

class Person(NXBase):
    id          : int
    name        : str
    family      : int
    state       : int
    age         : int
    description : str
    family_name : str
    state_name  : str
    
    def __init__(self) -> None:
        self.id          = None
        self.name        = None
        self.family      = None
        self.state       = None
        self.age         = None
        self.description = None
        
    @classmethod    
    def new(self, id: int, name: str, family: int, state: int, age: int, description: str, family_name: str, state_name: str) -> Any:
        p             = Person()
        p.id          = id
        p.name        = name
        p.family      = family
        p.state       = state
        p.age         = age
        p.description = description
        p.family_name = family_name
        p.state_name  = state_name
        return p  
#endregion   

def persons(cnx: MyConnection) -> NXResult: 
    __result = NXResult()   
    
    try:
        rs = cnx.xp.FDXQuery(SQL_AG_PERSONS)
        if rs.dataset.recordcount == 0:
            __result.warning = True
            __result.message = 'Nenhum registro encontrado'
        else:
            list = []                     
            
            rs.dataset.first()
            
            while rs.dataset.eof == False:
                list.append(Person.new(
                    rs.dataset.fieldbyname('Id'), 
                    rs.dataset.fieldbyname('Name'),
                    rs.dataset.fieldbyname('Family'),
                    rs.dataset.fieldbyname('State'),
                    rs.dataset.fieldbyname('Age'),
                    rs.dataset.fieldbyname('Description'),
                    rs.dataset.fieldbyname('Family_Name'),
                    rs.dataset.fieldbyname('State_Name')))
                rs.dataset.next()
                
            __result.status = True
            __result.data   = list
            
    except Exception as e:
        __result.make_error(0, 'Erro ao carregar informações', str(e))  
    finally:
        pass

    return __result

def person(cnx: MyConnection, id: int) -> NXResult: 
    __result = NXResult()   

    try:
        rs = cnx.xp.FDXQuery(SQL_AG_PERSONS_ID, id)
        if rs.dataset.recordcount == 0:
            __result.warning = True
            __result.message = 'Nenhum registro encontrado'
        else:
           __result.status = True
           __result.data   = Person.new(
                rs.dataset.fieldbyname('Id'), 
                rs.dataset.fieldbyname('Name'),
                rs.dataset.fieldbyname('Family'),
                rs.dataset.fieldbyname('State'),
                rs.dataset.fieldbyname('Age'),
                rs.dataset.fieldbyname('Description'),
                rs.dataset.fieldbyname('Family_Name'),
                rs.dataset.fieldbyname('State_Name')).__dict__
            
    except Exception as e:
        __result.make_error(0, 'Erro ao carregar informações', str(e))  
    finally:
        pass
    
    return __result

def person_create(cnx: MyConnection, person: Person) -> NXResult: 
    __result = NXResult()  
    
    try:         
        i   = cnx.xp.AutoInc('[Person]', 'Id')
        
        cnx.xp.FDXInsert('[Person]', [
            FDFieldInfo('Id',           i),
            FDFieldInfo('Name',         person.name),
            FDFieldInfo('Family',       person.family),
            FDFieldInfo('State',        person.state),
            FDFieldInfo('Age',          person.age),
            FDFieldInfo('Description',  person.description),
        ])
        
        person.id        = i
        __result.status = True
        __result.data   = person.__dict__
    
    except Exception as e:
        __result.make_error(0, 'Erro ao inserir dados', str(e))  
    finally:
        pass
    
    return __result

def person_update(cnx: MyConnection, person: Person, id: int) -> NXResult: 
    __result = NXResult()  
    
    l = []
    if person.name        != None:
        l.append(FDFieldInfo('Name',        person.name))
    if person.family      != None:
        l.append(FDFieldInfo('Family',      person.family))
    if person.state       != None:
        l.append(FDFieldInfo('State',       person.state))
    if person.age         != None:
        l.append(FDFieldInfo('Age',         person.age))
    if person.description != None:
        l.append(FDFieldInfo('Description', person.description))
    
    try: 
        cnx.xp.FDXUpdate('[Person]', l, [FDFieldInfo('Id', id)])        
                
        person.id       = id
        __result.status = True
        __result.data   = person.__dict__
    
    except Exception as e:
        __result.make_error(0, 'Erro ao inserir dados', str(e))  
    finally:
        pass
    
    return __result

def person_delete(cnx: MyConnection, id: int) -> NXResult:
    __result = NXResult()  
    
    try:  
        cnx.xp.FDXDelete('[Person]', [FDFieldInfo('Id',  id)],)
        
        __result.info    = True
        __result.status  = True
        __result.message = "Usuário excluído com sucesso"
    
    except Exception as e:
        __result.make_error(0, 'Erro ao excluir dados', str(e))  
    finally:
        pass
    
    return __result  