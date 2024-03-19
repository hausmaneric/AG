from Class.nextbase import *
from Class.express import *
from Class.nextutils import *
from Class.agsql import *
from Class.myconnection import *
import random
from Models.email import *

#region Modelos de Referência

class Access(NXBase):
    id     : int
    name   : str
    login  : str
    email  : str
    psw    : str
    family : int
    
    def __init__(self) -> None:
        self.id     = None
        self.name   = None
        self.login  = None
        self.email  = None
        self.psw    = None
        self.family = None              
    
    @classmethod    
    def new(self, id: int, name: str, login: str, email: str, psw: str, family: str) -> Any:
        u        = Access()
        u.id     = id
        u.name   = name
        u.login  = login
        u.email  = email
        u.psw    = psw
        u.family = family        
        
        return u     
#endregion   

verification_code = {}   

def hits(cnx: MyConnection) -> NXResult: 
    __result = NXResult()   
    
    try:
        rs = cnx.xp.FDXQuery(SQL_AG_HITS)
        if rs.dataset.recordcount == 0:
            __result.warning = True
            __result.message = 'Nenhum registro encontrado'
        else:
            list = []                     
            
            rs.dataset.first()
            
            while rs.dataset.eof == False:
                list.append(Access.new(
                    rs.dataset.fieldbyname('Id'), 
                    rs.dataset.fieldbyname('Login'), 
                    rs.dataset.fieldbyname('Email'), 
                    rs.dataset.fieldbyname('Name'), 
                    rs.dataset.fieldbyname('Psw'), 
                    rs.dataset.fieldbyname('Family')))
                rs.dataset.next()
                
            __result.status = True
            __result.data   = list
            
    except Exception as e:
        __result.make_error(0, 'Erro ao carregar informações', str(e))  
    finally:
        pass

    return __result

def access_email(cnx: MyConnection, email: str) -> int:
    __result = NXResult()   
    try:
        rs = cnx.xp.FDXQuery(SQL_AG_HITS_EMAIL , email)
        if rs.dataset.fieldbyname('Total') == 0:
            return 0
        else:
            return 1 
    except Exception as e:
        __result.make_error(0, 'Erro ao carregar informações', str(e)) 
    finally:
        pass
    
def access(cnx: MyConnection, id: int) -> NXResult: 
    __result = NXResult()   

    try:
        rs = cnx.xp.FDXQuery(SQL_AG_HITS_ID, id)
        if rs.dataset.recordcount == 0:
            __result.warning = True
            __result.message = 'Nenhum registro encontrado'
        else:
           __result.status   = True
           __result.data     = Access.new(
               rs.dataset.fieldbyname('Id'), 
               rs.dataset.fieldbyname('Login'), 
               rs.dataset.fieldbyname('Email'), 
               rs.dataset.fieldbyname('Name'), 
               rs.dataset.fieldbyname('Psw'), 
               rs.dataset.fieldbyname('Family')).__dict__
            
    except Exception as e:
        __result.make_error(0, 'Erro ao carregar informações', str(e))  
    finally:
        pass
    
    return __result     

def access_create(cnx: MyConnection, access: Access) -> NXResult: 
    __result = NXResult()  
    __email  = access_email(cnx, access.email)
    
    try: 
        if __email == 1:
            __result.status  = False
            __result.warning = True
            __result.message = 'Email já cadastrado'
        elif __email == 0:
            i   = cnx.xp.AutoInc('[Access]', 'Id')
            
            cnx.xp.FDXInsert('[Access]', [
                FDFieldInfo('Id',     i),
                FDFieldInfo('Login',  access.login),
                FDFieldInfo('Email',  access.email),
                FDFieldInfo('Name',   access.name),
                FDFieldInfo('Psw',    encode_b64(access.psw, True)),
                FDFieldInfo('Family', access.family)
            ])
            
            access.id       = i
            access.psw      = ''
            __result.status = True
            __result.data   = access.__dict__
    
    except Exception as e:
        __result.make_error(0, 'Erro ao inserir dados', str(e))  
    finally:
        pass
    
    return __result

def access_update(cnx: MyConnection, access: Access, id: int) -> NXResult: 
    __result = NXResult()  
    
    l = []
    if access.login  != None:
        l.append(FDFieldInfo('Login',  access.login))
    if access.email  != None:
        l.append(FDFieldInfo('Email',  access.email))
    if access.name   != None:
        l.append(FDFieldInfo('Name',  access.name))
    if access.psw    != None:
        l.append(FDFieldInfo('Psw',  encode_b64(access.psw, True)))
    if access.family != None:
        l.append(FDFieldInfo('Family',  access.family))
    
    try: 
        cnx.xp.FDXUpdate('[Access]', l, [FDFieldInfo('Id', id)])        
                
        access.psw      = ''
        access.id       = id
        __result.status = True
        __result.data   = access.__dict__
    
    except Exception as e:
        __result.make_error(0, 'Erro ao inserir dados', str(e))  
    finally:
        pass
    
    return __result

def code_update(cnx: MyConnection, email: str, code: int) -> NXResult:
    __result = NXResult()  
    
    l = []
    if code != None:
        l.append(FDFieldInfo('Code',  code))
        
    try: 
        cnx.xp.FDXUpdate('[Access]', l, [FDFieldInfo('Email', email)])        
                
        __result.status = True
        __result.data   = l.__dict__
    
    except Exception as e:
        __result.make_error(0, 'Erro ao inserir dados', str(e))  
    finally:
        pass
    
    return __result

def psw_updade(cnx: MyConnection, email: str, psw: str, confirm: str) -> NXResult:
    __result = NXResult()  
    
    l = []
    
    if confirm == psw:        
        if psw != None:
            l.append(FDFieldInfo('Psw',  encode_b64(psw, True)))
            
        try: 
            cnx.xp.FDXUpdate('[Access]', l, [FDFieldInfo('Email', email)])        
                    
            __result.status  = True
            __result.info    = True
            __result.message = 'Senha alterada com sucesso.'
        
        except Exception as e:
            __result.make_error(0, 'Erro ao inserir dados', str(e))  
        finally:
            pass
    else:
        __result.warning = True
        __result.message = 'Confirmação não corresponde a senha' 
    
    return __result

def access_delete(cnx: MyConnection, id: int) -> NXResult:
    __result = NXResult()  
    
    try:  
        cnx.xp.FDXDelete('[Access]', [FDFieldInfo('Id',  id)],)
        
        __result.info    = True
        __result.status  = True
        __result.message = "Usuário excluído com sucesso"
    
    except Exception as e:
        __result.make_error(0, 'Erro ao excluir dados', str(e))  
    finally:
        pass
    
    return __result  

def access_login(cnx: MyConnection, login: str, psw: str):
    __result = NXResult()   

    try:
        rs = cnx.xp.FDXQuery(SQL_AG_HITS_LOGIN, login, encode_b64(psw, True))
        if rs.dataset.recordcount == 0:
            __result.warning = True
            __result.message = 'Credênciais invalidas'
        else:                    
            __result.status  = True
            __result.data    = Access.new(
                rs.dataset.fieldbyname('Id'), 
                rs.dataset.fieldbyname('Login'), 
                rs.dataset.fieldbyname('Email'), 
                rs.dataset.fieldbyname('Name'), 
                rs.dataset.fieldbyname('Psw'), 
                rs.dataset.fieldbyname('Family')).__dict__
            
    except Exception as e:
        __result.make_error(0, 'Erro ao carregar informações', str(e))  
    finally:
        pass
    
    return __result   
            
def send_code(cnx: MyConnection, email: str) -> NXResult:
    __result = NXResult()  
    __email  = access_email(cnx, email)      
    
    try:
        if __email == 1:
            code = generate_code()
            send_verification_code_by_email(email, code)
            
            __result.status  = True
            __result.info    = True
            __result.message = 'Email enviado'
            # code_update(cnx, email, code)
        elif __email == 0:
            __result.warning = True
            __result.message = 'Email não localizado'
    except Exception as e:
        __result.make_error(0, 'Erro ao enviar o email', str(e))  
    finally:
        pass
    
    return __result 
    
def generate_code():
    return str(random.randint(1000, 9999))

def send_verification_code_by_email(email, codigo):
    verification_code[email]  = codigo

    email_obj                 = Email()
    email_obj.assunto         = 'Código de Verificação'
    email_obj.body            = f'Seu código de verificação é: {codigo}'
    email_obj.to              = email

    if sendEmail(email_obj):
        return True
    else:
        return False
    
def generate_psw(size):
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(size))    
    
def send_password_verification_by_email(email, senha):
    verification_code[email]  = senha

    email_obj                 = Email()
    email_obj.assunto         = 'Senha de Verificação'
    email_obj.body            = f'Sua senha de verificação é: {senha}'
    email_obj.to              = email

    if sendEmail(email_obj):
        return True
    else:
        return False

def checkcode(email, codigo) -> NXResult:
    __result    = NXResult()  
    stored_code = verification_code.get(email)
    
    try:    
        if stored_code and codigo == stored_code:
            del verification_code[email]
            __result.status  = True
            __result.info    = True
            __result.message = 'Código verificado com sucesso' 
    
    except Exception as e:
        __result.status  = False
        __result.make_error = (0, 'Erro ao tentar verificar codigo', str(e))
    finally:
        pass
    
    return __result