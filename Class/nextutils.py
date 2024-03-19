# NEXT Project 
# NEXTUtils (c) 2021 Fabrício Hausman
#           (c) Hausman Systems

# Ctrl+Del
# Ctrl+Shift+K

import base64
import zlib
from datetime import datetime
from typing import Any, List
from enum import Enum
import pyodbc
import string
import secrets
import locale
from Class.nextbase import *
from Class.nextsql import *
from Class.express import *
from Controller import nxc 
from Models.login import *

#region Rotinas Base64 e zlib
def encode_b64(source: str, compress: bool = False):    
    """
    Codifica str em base64 utf-8
    """

    if compress == True: 
        s = base64.urlsafe_b64encode(zlib.compress(source.encode('utf-8')))
    else:
        s = base64.urlsafe_b64encode(source.encode('utf-8'))
    
    return s
    
def decode_b64(source: str, uncompress: bool = False):   
    """
    Decodifica str base64 utf-8
    """

    if uncompress == True:        
        s = zlib.decompress(base64.urlsafe_b64decode(source)).decode('utf-8')        
    else:
        s = base64.urlsafe_b64decode(source).decode('utf-8')           
    
    return s    
#endregion  

# Tipos
class NXLoginType(Enum):
    NONE        = 0
    NEXT        = 1
    SYSTEM      = 2
    SYSTEM_AUTO = 3

class NXTokenStatus(Enum):
    NONE        = 0
    ATIVO       = 1
    INATIVO     = 2
    BLOQUEADO   = 3    

# next        - login na base NEXT, configurada a conexão do cliente e retornado lista de empresas
# system      - login na base NEXT, configurada a conexão do cliente e efetuado login do usuário na empresa informada
# system-auto - login na base NEXT, configurada a conexão do cliente e efetuado login do usuário na empresa informada 
#               (não necessita de senha e usuário deve estar configurado para autologin
#                requer informações para controle de sessão)    

class NXToken(NXBase): 
    __token       : str
    isValid       : bool
    tokenId       : int  # Código do toke ex.: 10001
    tokenPwd      : str  # Senha do token
    userCode      : int  # Código do usuário
    userName      : str  # Nome do usuário
    userPwd       : str  # Senha do usuário
    companyId     : int  # Código da empresa
    deviceID      : str  # Identificação do dispositivo
    appName       : str  # Nome da aplicação cliente
    appVersion    : str  # Versão da aplicação cliente
    locationLat   : int  # Latitude
    LocationLong  : int  # Longitude
    sidClient     : str
    sidServer     : str     

    # @property
    # def isValid(self):
    #     return self.__isValid        
 
    def __init__(self, token: str) -> None:  
      
        self.isValid       = bool
        self.tokenId       = 0  
        self.tokenPwd      = ''
        self.userCode      = 0 
        self.userName      = ''
        self.userPwd       = ''
        self.companyId     = 0 
        self.deviceID      = ''
        self.appName       = ''
        self.appVersion    = ''
        self.locationLat   = 0 
        self.LocationLong  = 0 
        self.sidClient     = ''
        self.sidServer     = ''         

        if token != '':
            self.isValid = False
            self.__token  = token  
            self.__token_decode()
        else:
            self.isValid = False   
    
    def __token_decode(self):
        try:              
            s = decode_b64(self.__token, True)   
        except:
            s = None     

        if s != '' and s != None:  
            self.jsonImport(s)
            self.isValid = True
    
    def token_encode(self):
        try:
            s = self.toJSON()              
            s = encode_b64(s, True)            
            return s
        except:            
            return ''

    # Como no Delphi - property, set, get    
    # @property
    # def id(self):
    #     return self.tokenId
    # @id.getter
    # def id(self):
    #     return self.tokenId        
    # @id.setter    
    # def id(self, value: int):
    #     self.tokenId = value    

    # def __getattr__(self, name):
    #     pass
    # if hasattr(self.<att>, name):
    #    return getattr(self.<att>, name)
    # else:
    #    raise AttributeError    

    # def __setattr__(self, name, value):
    #     pass      

class NXConfigPerfil(Enum): 
    INDEFINIDO = 0 
    SYSTEM     = 1
    LOCAL      = 2
    USER     = 3

class NXConfigDataType(Enum):
    STRING  = 0
    INTEGER = 1
    DOUBLE  = 2
    BOOLEAN = 3    

class NXConfigRecordType(Enum):
    DATA = 0
    VAR  = 1

class NXConfigRecord(NXBase):  
    # name        : str
    # group       : str
    session     : str
    key         : str
    datatype    : int
    perfil      : int #NXConfigPerfil
    perfilid    : str 
    defaultValue: None
    recordtype  : int #NXConfigRecordType
    value       : None   
    loaded      : bool
    changed     : bool 

    def __init__(self, section: str, key: str, datatype: int, perfil: int, perfilid: str, defaultvalue: None, recordtype: int = 0) -> Any:
        super().__init__()  
        self.session      = section
        self.key          = key
        self.datatype     = datatype
        self.perfil       = perfil
        self.perfilid     = perfilid
        self.defaultValue = defaultvalue
        self.recordType   = recordtype
        self.value        = defaultvalue
        self.loaded       = False
        self.changed      = False

class NXConfig(NXBase):
    wsid      : str
    companyid : str
    userid    : str
    records   = []  
    # nxconn    = None 

    def __init__(self, wsid: str, companyid: str, userid: str) -> None:
        self.wsid      = wsid
        self.companyid = companyid
        self.userid    = userid
        self.nxconn    = NXConnection
        self.schema()

    # Monta esquema de configurações
    def schema(self):
        __str     = NXConfigDataType.STRING.value
        __int     = NXConfigDataType.INTEGER.value
        __dec     = NXConfigDataType.DOUBLE.value
        __bool    = NXConfigDataType.BOOLEAN.value

        __indf    = NXConfigPerfil.INDEFINIDO.value
        __sys     = NXConfigPerfil.SYSTEM.value
        __local   = NXConfigPerfil.LOCAL.value
        __user    = NXConfigPerfil.USER.value

        wsid      = self.wsid
        companyid = self.companyid
        userid    = self.userid

        self.records = []

        self.records.append(NXConfigRecord('Sistema',                'Grade.Salvar',                 __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema',                'Grade.Contraste',              __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema',                'Grade.Contraste.Menor',        __str,  __sys, '',           '$20F5F6F7'))
        self.records.append(NXConfigRecord('Sistema',                'Grade.Contraste.Maior',        __str,  __sys, '',           '$20F5F6F7'))
        self.records.append(NXConfigRecord('Sistema',                'Repositorio',                  __str,  __sys, '',           ''))

        # Cadastros -- Parceiros
        self.records.append(NXConfigRecord('Sistema.Cadastros',      'Parceiros.Endereço',           __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Cadastros',      'Parceiros.CPF_CNPJ',           __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Cadastros',      'Parceiros.CPF_CNPJ.Duplicado', __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Cadastros',      'Parceiros.IE.Duplicado',       __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Cadastros',      'Parceiros.Nome.Duplicado',     __bool, __sys, '',           True))

        # Estoque -- Produtos
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.CBarras',             __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Duplicado',           __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Recalcular',          __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Desconto',            __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Bonificacao',         __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Tabelas',             __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Operacao',            __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Sugestoes',           __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Similares',           __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Identificacao',       __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Descricoes',          __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Producao',            __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Execucao',            __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Controle',            __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Controle.Modulo',     __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Complementos',        __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Relacionar.GSbT',     __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Relacionar.CSc',      __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Kit',                 __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Kit_Itens',           __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Kit.Movimento',       __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Producao.Movimento',  __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.VDesconto',           __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.VDesconto.Valor',     __dec,  __sys, '',           0))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.VBonificacao',        __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.VBonificacao.Valor',  __dec,  __sys, '',           0))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.VMargem',             __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.VMargem.Valor',       __dec,  __sys, '',           0))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.VDMaximo',            __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.VDMaximo.Valor',      __dec,  __sys, '',           0))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.VDGerencial',         __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.VDGerencial.Valor',   __dec,  __sys, '',           0))
        self.records.append(NXConfigRecord('Local.Estoque',          'Produtos.Etiquetadora',        __bool, __local,    wsid,      False))
        self.records.append(NXConfigRecord('Local.Estoque',          'Produtos.Etiquetadora.Modelo', __int,  __local,    wsid,      0))
        self.records.append(NXConfigRecord('Local.Estoque',          'Produtos.Etiquetadora.Porta',  __str,  __local,    wsid,      'COM1'))
        self.records.append(NXConfigRecord('Local.Estoque',          'Produtos.Etiquetadora.Avanco', __int,  __local,    wsid,      600))
        self.records.append(NXConfigRecord('Sistema.Estoque',        'Produtos.Web.Sincronizar',     __bool,  __sys, '',          False))

        # Compras -- Ordem de Compra
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.Tipo',                      __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.Tipo.Valor',                __str,  __sys, '',           0))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.Atualiza_Custo',            __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.Atualiza_Custo.Valor',      __str,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.CFOP_M',                    __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.CFOP_M.Valor',              __str,  __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.CFOP_C',                    __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.CFOP_C.Valor',              __str,  __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.CFOP_I',                    __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.CFOP_I.Valor',              __str,  __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.CFOP_S',                    __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.CFOP_S.Valor',              __str,  __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.Autorizar',                 __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.Confirmar',                 __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.Rateio',                    __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.Rateio.Custo',              __int,  __sys, '',           0))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.Rateio.CTB',                __str,  __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.NFe.Fornecedor',            __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.NFe.Transportadora',        __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.NFe.CNFe_CB',               __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.NFe.CNFe_CB',               __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.NFe.CNFe_Ref',              __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.NFe.CNFe_Ref',              __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.NFe.EANNFe_CB',             __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.NFe.EANNFe_EAN',            __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.NFe.Codigo',                __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.NFe.S.Codigo',              __int,  __sys, '',           4))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.NFe.EAN',                   __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.NFe.S.EAN',                 __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.NFe.Descricao',             __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Compras',        'OC.NFe.S.Descricao',           __int,  __sys, '',           2))

        # Comercial -- Pedidos
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Cliente',              __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Vendedor',             __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.OpPagto',              __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Reserva',              __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Data',                 __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.NFe.Habilitar',        __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.NFSe.Habilitar',       __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Validade',             __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Validade.Dias',        __int,  __sys, '',           7))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Restricao',            __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Credito',              __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Tipo',                 __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Tipo.Valor',           __int,  __sys, '',           0))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Entrega',              __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Entrega.Valor',        __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Aviso',                __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Bloqueio',             __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Grade',                __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Lote',                 __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Volumes',              __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Produtos.InfoNS',      __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Produtos.InfoNSEsp',   __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Produtos.Filial',      __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Produtos.Exibicao',    __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Produtos.Impressao',   __int,  __sys, '',           3))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Estoque',              __int,  __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Pedidos.Estoque.Bloqueio',     __int,  __sys, '',           False))

        # Aplicativo
        self.records.append(NXConfigRecord('Sistema.Comercial',      'App.Clientes.Vendedores',      __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'App.Catalogo.Precos',          __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'App.Pedidos.Remover',          __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'App.Pedidos.Tipo',             __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'App.Pedidos.Tipo.Valor',       __int,  __sys, '',           0))

        # Agenciamento
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Agenciamento.Habilitar',       __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Agenciamento.CTe',             __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Agenciamento.CTe.Tipo',        __int,  __sys, '',           0))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Agenciamento.CTe.Servico',     __int,  __sys, '',           0))

        # -- PDV
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Tipo.Valor',               __int,  __sys, '',           0))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Entrega',                  __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Entrega.Valor',            __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Cliente',                  __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Vendedor',                 __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Senha',                    __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Desconto.Limitar',         __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Desconto.Maximo',          __dec,  __sys, '',           0))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Caixa.Cliente',            __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Caixa.Vendedor',           __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Caixa.Resumo',             __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Caixa.Reirada',            __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Caixa.NFCartao',           __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Caixa.SemNFCe',            __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Restricao',                __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Credito',                  __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Conta',                    __int,  __sys, '',           0))
        self.records.append(NXConfigRecord('Local.Lojas',            'PDV.Ativar',                   __bool, __local,    wsid,      False))

        # PDV Produtos
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Consulta',                 __int,  __sys, '',           3))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Tabela',                   __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Reexibir',                 __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.ExibirTabela',             __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.CB',                       __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.CB.Tipo',                  __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.CB.IniCodigo',             __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.CB.DigCodigo',             __int,  __sys, '',           6))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.CB.IniValor',              __int,  __sys, '',           8))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.CB.DigValor',              __int,  __sys, '',           6))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Grade.Codigo',             __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Grade.CBarras',            __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Grade.NFabrica',           __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Grade.Referencia',         __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Grade.Referencia',         __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Grade.Complemento',        __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Grade.Preco2',             __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Grade.Desconto',           __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Aviso',                    __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Bloqueio',                 __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Grade',                    __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Lote',                     __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Exibicao',                 __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Complemento',              __int,  __sys, '',           1))
        # PDV Impressão
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.Visualizar',      __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.DadosCliente',    __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.Simulador',       __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.Imprimir',        __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.Confirmacao',     __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.IdGrupo',         __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.PrecoNormal',     __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.Adicionais',      __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.CupomLinha',      __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.Parcelamento',    __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.2Vias',           __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.Carne',           __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.Promissoria',     __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.OrdemEntrega',    __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.ReciboCliente',   __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.Requisicao',      __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.Codigo',          __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.CBarras',         __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.NFabrica',        __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.ReferenciaA',     __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.ReferenciaB',     __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.Marca',           __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.Local',           __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Imprimir.Ordem',           __int,  __sys, '',           3))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'Caixa.Imprimir.Abertura',      __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'Caixa.Imprimir.Suprimento',    __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'Caixa.Imprimir.Retirada',      __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'Caixa.Imprimir.Retirada2X',    __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'Caixa.Imprimir.Resumo',        __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'Caixa.Imprimir.RetiradasDet',  __bool, __sys, '',           False))
        # PDV Formulário
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Form.Cabecalho',           __str,  __sys, companyid,  ''))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Form.Rodape.O',            __str,  __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Form.Rodape.V',            __str,  __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Form.Rodape.E',            __str,  __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Form.Rodape.B',            __str,  __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Lojas',          'PDV.Form.Adicional',           __str,  __sys, '',           ''))

        # Trocas e Devoluções
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Devolucoes.SimplesD',          __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Devolucoes.SimplesT',          __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Devolucoes.SimplesR',          __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Devolucoes.Faturar',           __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Devolucoes.Prazo.T',           __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Devolucoes.Prazo.D',           __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Devolucoes.Prazo.R',           __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Devolucoes.Prazo.T.Valor',     __int,  __sys, '',           7))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Devolucoes.Prazo.D.Valor',     __int,  __sys, '',           3))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Devolucoes.Prazo.R.Valor',     __int,  __sys, '',           3))
        self.records.append(NXConfigRecord('Local.Comercial',        'Devolucoes.I.Dispositivo',     __int,  __local,   wsid,       1))
        self.records.append(NXConfigRecord('Local.Comercial',        'Devolucoes.I.Modelo',          __int,  __local,   wsid,       -1))
        self.records.append(NXConfigRecord('Local.Comercial',        'Devolucoes.I.Guilhotina',      __bool, __local,   wsid,       False))
        self.records.append(NXConfigRecord('Local.Comercial',        'Devolucoes.I.Gaveta',          __bool, __local,   wsid,       False))
        self.records.append(NXConfigRecord('Local.Comercial',        'Devolucoes.I.Porta',           __str,  __local,   wsid,       ''))
        self.records.append(NXConfigRecord('Local.Comercial',        'Devolucoes.I.Layout',          __int,  __local,   wsid,       1))
        self.records.append(NXConfigRecord('Local.Comercial',        'Devolucoes.I.Copias',          __int,  __local,   wsid,       1))

        # Comércio Eletrônico
        self.records.append(NXConfigRecord('Sistema.Comercial',      'ECommerce.NEXTVS.Habilitar',   __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'ECommerce.NEXTVS.URL',         __str,  __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'ECommerce.NEXTVS.CK',          __str,  __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'ECommerce.NEXTVS.CS',          __str,  __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'ECommerce.NEXTVS.WPU',         __str,  __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'ECommerce.NEXTVS.WPP',         __str,  __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'ECommerce.NEXTVS.Tabela',      __bool, __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'ECommerce.NEXTVS.TabelaID',    __int,  __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'ECommerce.NEXTVS.SSL2',        __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'ECommerce.NEXTVS.SSL3',        __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'ECommerce.NEXTVS.TLS1',        __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'ECommerce.NEXTVS.TLS11',       __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'ECommerce.NEXTVS.TLS12',       __bool, __sys, '',           True))

        # Serviços -- OS
        self.records.append(NXConfigRecord('Sistema.Servicos',       'OS.Cliente',                   __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Servicos',       'OS.Tecnico',                   __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Servicos',       'OS.Vendedor',                  __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Servicos',       'OS.OpPagto',                   __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Servicos',       'OS.Posicao',                   __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Servicos',       'OS.Kit',                       __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Servicos',       'OS.Perfil',                    __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Servicos',       'OS.Insumos.Baixar',            __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Servicos',       'OS.Faturar.Entrada',           __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Servicos',       'OS.Faturar.Saida',             __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Servicos',       'OS.Faturar.Venda',             __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Servicos',       'OS.Produtos.Aprovar',          __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Servicos',       'OS.Produtos.Receber',          __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Servicos',       'OS.Servicos.Aprovar',          __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Servicos',       'OS.Servicos.Concluir',         __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'OS.Aviso',                     __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'OS.Bloqueio',                  __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'OS.Grade',                     __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'OS.Lote',                      __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'OS.Produtos.Exibicao',         __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'OS.Produtos.Impressao',        __int,  __sys, '',           3))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'OS.Email',                     __int,  __sys, '',           0))

        # Operacional -- Propostas
        # decrepted *** deletar após migração
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Propostas.ImpCondicao',        __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Propostas.ImpItemTotal',       __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Comercial',      'Propostas.Email',              __int,  __sys, '',           0))
        # ***
        self.records.append(NXConfigRecord('Sistema.Operacional',    'Propostas.Parceiro',           __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'Propostas.Vendedor',           __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'Propostas.Gerente',            __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'Propostas.Formulario',         __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'Propostas.ImpCondicao',        __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'Propostas.ImpItemTotal',       __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'Propostas.Email',              __int,  __sys, '',           0))

        # Operacional -- Contratos
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.Vendedor',                  __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.Atualizar',                 __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.Decimais',                  __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.Decimais.Valor',            __int,  __sys, '',           2))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.VDecimais.Valor',           __int,  __sys, '',           2))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.Proporcional',              __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.Detalhes',                  __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.Faturamento.Dias',          __int,  __sys, '',           0))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.Faturamento.Extra',         __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.Periodo',                   __int,  __sys, '',           2))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.Duracao',                   __int,  __sys, '',           12))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.Reajuste',                  __int,  __sys, '',           12))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.Pedido',                    __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.Pedido.Tipo',               __int,  __sys, '',           0))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.CR.Posicao',                __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.CR',                        __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.CR.Historico',              __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Operacional',    'CT.CP.CTB',                    __str,  __sys, '',           ''))

        # Obras -- Orçamentos
        self.records.append(NXConfigRecord('Sistema.Obras',          'Orcamentos.Orcamentista',      __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Obras',          'Orcamentos.Vendedor',          __bool, __sys, '',           True))
        self.records.append(NXConfigRecord('Sistema.Obras',          'Orcamentos.Validade',          __int,  __sys, '',           7))
        self.records.append(NXConfigRecord('Sistema.Obras',          'Orcamentos.Informacoes',       __str,  __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Obras',          'Orcamentos.Adicional',         __str,  __sys, '',           ''))
        self.records.append(NXConfigRecord('Sistema.Obras',          'Orcamentos.Imp.Modelo',        __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('Sistema.Obras',          'Orcamentos.Imp.Condicoes',     __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Obras',          'Orcamentos.Imp.Contrato',      __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('Sistema.Obras',          'Orcamentos.Email',             __int,  __sys, '',           0))

        # Gestão de Pessoas
        self.records.append(NXConfigRecord('RH.Ponto',               'E1AD',                         __str,  __sys, '',           '00:00:00'))
        self.records.append(NXConfigRecord('RH.Ponto',               'E1AT',                         __str,  __sys, '',           '00:00:00'))
        self.records.append(NXConfigRecord('RH.Ponto',               'S1AD',                         __str,  __sys, '',           '00:00:00'))
        self.records.append(NXConfigRecord('RH.Ponto',               'S1AT',                         __str,  __sys, '',           '00:00:00'))
        self.records.append(NXConfigRecord('RH.Ponto',               'E2AD',                         __str,  __sys, '',           '00:00:00'))
        self.records.append(NXConfigRecord('RH.Ponto',               'E2AT',                         __str,  __sys, '',           '00:00:00'))
        self.records.append(NXConfigRecord('RH.Ponto',               'S2AD',                         __str,  __sys, '',           '00:00:00'))
        self.records.append(NXConfigRecord('RH.Ponto',               'S2AT',                         __str,  __sys, '',           '00:00:00'))
        self.records.append(NXConfigRecord('RH.Ponto',               'AN',                           __str,  __sys, '',           '00:00:00'))
        self.records.append(NXConfigRecord('RH.Ponto',               'IJ',                           __str,  __sys, '',           '11:00:00'))
        self.records.append(NXConfigRecord('RH.Ponto',               'TD',                           __str,  __sys, '',           '00:10:00'))
        self.records.append(NXConfigRecord('RH.Ponto',               'LimiteTotal',                  __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('RH.Ponto',               'Flex',                         __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('RH.Ponto',               'Periodo',                      __int,  __sys, '',           1))
        self.records.append(NXConfigRecord('RH.Padronizados',        'CTExperiencia',                __int,  __sys, '',           0))
        self.records.append(NXConfigRecord('RH.Padronizados',        'CTDeterminado',                __int,  __sys, '',           0))
        self.records.append(NXConfigRecord('RH.Padronizados',        'CTIndeterminado',              __int,  __sys, '',           0))
        self.records.append(NXConfigRecord('RH.Padronizados',        'CTIntermitente',               __int,  __sys, '',           0))
        self.records.append(NXConfigRecord('RH.Padronizados',        'CTBancoHoras',                 __int,  __sys, '',           0))
        self.records.append(NXConfigRecord('RH.Folha',               'Salario',                      __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('RH.Folha',               'Salario.Evento',               __int,  __sys, '',           0))
        self.records.append(NXConfigRecord('RH.Folha',               'Salario.Custo',                __int,  __sys, '',           0))
        self.records.append(NXConfigRecord('RH.Folha',               'Salario.CTB',                  __str,  __sys, '',           ''))
        self.records.append(NXConfigRecord('RH.Folha',               'Vale',                         __bool, __sys, '',           False))
        self.records.append(NXConfigRecord('RH.Folha',               'Vale.Evento',                  __int,  __sys, '',           0))

        # Contas a Receber
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Posicao',                   __int,  __sys, '',          1))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Situacao',                  __int,  __sys, '',          0))

        # Contas a Receber -- Taxas
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Desconto',                  __bool, __sys, '',          False))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Desconto.TC',               __int,  __sys, '',          0))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Desconto.VL',               __dec,  __sys, '',          0))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Multa',                     __bool, __sys, '',          False))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Multa.TC',                  __int,  __sys, '',          0))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Multa.VL',                  __dec,  __sys, '',          0))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Juros',                     __bool, __sys, '',          False))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Juros.TC',                  __int,  __sys, '',          0))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Juros.VL',                  __dec,  __sys, '',          0))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Taxas.Alterar',             __bool, __sys, '',          True))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Taxas.Desconto',            __bool, __sys, '',          False))

        # Contas a Receber -- Rateio
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Rateio',                    __bool, __sys, '',          False))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Rateio.Custo',              __int,  __sys, '',          0))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Rateio.CTB',                __str,  __sys, '',          ''))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.RateioMJ',                  __bool, __sys, '',          False))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Rateio.CustoMJ',            __int,  __sys, '',          0))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Rateio.CTBMJ',              __str,  __sys, '',          ''))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Retorno.Compensacao',       __int,  __sys, '',          0))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Retorno.DiasUteis',         __bool, __sys, '',          True))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CR.Baixa.Parcial',             __bool, __sys, '',          False))

        # Contas a Receber -- Cobrança
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'COB.NF',                       __bool, __sys, '',          False))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'COB.Protesto',                 __bool, __sys, '',          False))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'COB.Protesto.Dias',            __int,  __sys, '',          0))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'COB.Boleto',                   __int,  __sys, '',          0))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'COB.Envelope',                 __int,  __sys, '',          1))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'COB.Etiqueta',                 __int,  __sys, '',          1))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'COB.PDF',                      __str,  __sys, '',          ''))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'COB.Remessa',                  __str,  __sys, '',          ''))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'COB.Retorno',                  __str,  __sys, '',          ''))

        # Contas a Receber -- Cobrança (E-mail)
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'COB.EMail',                    __int,  __sys, '',          0))

        # Contas a Receber -- Carnê
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'COB.Carnê',                    __int,  __sys, '',          1))

        # Contas a Receber -- Email
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'COB.Email.Aviso',              __str,  __sys, '',          ''))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'COB.Email.Atraso',             __str,  __sys, '',          ''))

        # Contas a Pagar
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CP.Posicao',                   __int,  __sys, '',          1))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CP.Situacao',                  __int,  __sys, '',          0))

        # Contas a Pagar -- Rateio
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CP.Rateio',                    __bool, __sys, '',          False))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CP.Rateio.Custo',              __int,  __sys, '',          0))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CP.Rateio.CTB',                __str,  __sys, '',          ''))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CP.RateioMJ',                  __bool, __sys, '',          False))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CP.Rateio.CustoMJ',            __int,  __sys, '',          0))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CP.Rateio.CTBMJ',              __str,  __sys, '',          ''))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CP.Baixa.Parcial',             __bool, __sys, '',          False))

        # Contas Lançamentos
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CC.Situacao',                  __int,  __sys, '',          1))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CC.Rateio',                    __bool, __sys, '',          False))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CC.Rateio.Custo_C',            __int,  __sys, '',          0))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CC.Rateio.CTB_C',              __str,  __sys, '',          ''))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CC.Rateio.Custo_D',            __int,  __sys, '',          0))
        self.records.append(NXConfigRecord('Sistema.Financeiro',     'CC.Rateio.CTB_D',              __str,  __sys, '',          ''))

        # Nota Fiscal Eletrônica
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFe.CSerie.' + companyid,      __str,  __local,   wsid,      ''))
        self.records.append(NXConfigRecord('Sistema.Fiscal',         'NFe.Ambiente',                 __int,  __sys, companyid, 0))
        self.records.append(NXConfigRecord('Sistema.Fiscal',         'NFe.UF',                       __str,  __sys, companyid, ''))
        self.records.append(NXConfigRecord('Sistema.Fiscal',         'NFe.Danfe',                    __int,  __sys, companyid, 1))
        self.records.append(NXConfigRecord('Sistema.Fiscal',         'NFe.DanfeFonte',               __int,  __sys, companyid, 10))
        self.records.append(NXConfigRecord('Sistema.Fiscal',         'NFe.Emissao',                  __int,  __sys, companyid, 0))
        self.records.append(NXConfigRecord('Sistema.Fiscal',         'NFe.Serie',                    __str,  __sys, companyid, '1'))
        self.records.append(NXConfigRecord('Sistema.Fiscal',         'NFe.Logo',                     __str,  __sys, companyid, ''))
        self.records.append(NXConfigRecord('Sistema.Fiscal',         'NFe.Pasta',                    __str,  __sys, '',          ''))

        # NFC-e
        self.records.append(NXConfigRecord('Sistema.Fiscal',         'NFCe.Serie',                   __int,  __sys, companyid, 1))
        self.records.append(NXConfigRecord('Sistema.Fiscal',         'NFCe.CSCID',                   __str,  __sys, companyid, ''))
        self.records.append(NXConfigRecord('Sistema.Fiscal',         'NFCe.CSC',                     __str,  __sys, companyid, ''))
        self.records.append(NXConfigRecord('Sistema.Fiscal',         'NFCe.CSCIDTeste',              __str,  __sys, companyid, ''))
        self.records.append(NXConfigRecord('Sistema.Fiscal',         'NFCe.CSCTeste',                __str,  __sys, companyid, ''))
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFCe.Danfe',                   __int,  __local,   wsid,       1))
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFCe.Impressora',              __int,  __local,   wsid,      -1))
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFCe.Impressora.Porta',        __str,  __local,   wsid,      ''))
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFCe.Impressora.Guilhotina',   __bool, __local,   wsid,      False))
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFCe.Impressora.Gaveta',       __bool, __local,   wsid,      False))

        # NF-e Email
        self.records.append(NXConfigRecord('Sistema.Fiscal',         'NFe.EmailEnviar',              __bool, __sys, companyid, False))
        self.records.append(NXConfigRecord('Sistema.Fiscal',         'NFe.Email',                    __int,  __sys, companyid, 0))

        # NF-e Avançado
        self.records.append(NXConfigRecord('Sistema.Fiscal',         'NFe.Versao',                   __int,  __sys, '',          3))
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFe.SSLLib',                   __int,  __local,   wsid,      4))
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFe.CryptLib',                 __int,  __local,   wsid,      3))
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFe.HttpLib',                  __int,  __local,   wsid,      2))
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFe.XMLLib',                   __int,  __local,   wsid,      2))
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFe.WSMsg',                    __bool, __local,   wsid,      False))
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFe.WSSoap',                   __bool, __local,   wsid,      False))
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFe.WSAguada',                 __bool, __local,   wsid,      True))
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFe.WSTimeout',                __int,  __local,   wsid,      5000))
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFe.WSTentativas',             __int,  __local,   wsid,      5))
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFe.WSTempoTentativas',        __int,  __local,   wsid,      1000))
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFe.WSTempoEspera',            __int,  __local,   wsid,      5000))
        self.records.append(NXConfigRecord('Local.Fiscal',           'NFe.WSSSLType',                __int,  __local,   wsid,      0))

        # Internet
        self.records.append(NXConfigRecord('Local.Internet',         'Net.ProxyHost',                __str,  __local,   wsid,      ''))
        self.records.append(NXConfigRecord('Local.Internet',         'Net.ProxyPorta',               __str,  __local,   wsid,      ''))
        self.records.append(NXConfigRecord('Local.Internet',         'Net.ProxyUsuario',             __str,  __local,   wsid,      ''))
        self.records.append(NXConfigRecord('Local.Internet',         'Net.ProxySenha',               __str,  __local,   wsid,      ''))

        # Interface do Usuário
        self.records.append(NXConfigRecord('Usuario.Interface',      'Menu.Inicio',                  __str,  __user,    userid,     ''))     
        
    # Carrega configurações do banco de dados
    def load(self) -> NXResult:
        result = NXResult()
        s      : str

        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        try:
            r = self.nxconn.xp_nx.FDXQuery(SQL_CONFIG, self.companyid, self.wsid, self.userid)
            if r.error == True:
                raise ValueError(r.message)
            else:
                for i, row in enumerate(self.records):
                    if r.dataset.locate(['Secao', 'Chave', 'Perfil', 'Perfil_ID'], [row.session, row.key, row.perfil, row.perfilid]):

                        s = r.dataset.fieldbyname('valor')      

                        match NXConfigDataType(row.datatype):
                            case NXConfigDataType.STRING:
                                row.value = s
                            case NXConfigDataType.INTEGER: 
                                s = s.strip()
                                if s != '': row.value = int(s)
                            case NXConfigDataType.DOUBLE: 
                                s = s.strip()
                                if s != '': row.value = locale.atof(s)  
                            case NXConfigDataType.BOOLEAN: 
                                s = s.strip()
                                if s != '': 
                                    if   s == '0': row.value = False
                                    elif s == '1': row.value = True  

                        row.loaded  = True
                        row.changed = False

            result.status = True            
        except Exception as e:
            result.make_error(0, 'Falha ao carregar configurações do sistema', str(e))
        finally:
            pass                

        return result

    def read(self, session: str, key: str) -> Any:
        r     = None
        found = False
        for i, row in enumerate(self.records):
            if self.records[i].session.lower() == session.lower() and self.records[i].key.lower() == key.lower():
                r     = self.records[i].value
                found = True
                break
        return r   

    def write(self, session: str, key: str, value: Any):
        found = False
        for i, row in enumerate(self.records):
            if self.records[i].session.lower() == session.lower() and self.records[i].key.lower() == key.lower():
                if self.records[i].value != value:
                    self.records[i].value   = value
                    self.records[i].changed = True
                found = True
                break

class NXPermissionRecord(NXBase):
    id       : int
    group    : int
    class_   : int
    module   : str
    mid      : str
    index    : int
    resource : str
    value    : bool
    loaded   : bool
    changed  : bool

    def __init__(self, id: int, group: int, class_: int, module: str, mid: str, index: int, resource: str, value: bool) -> Any:
        self.id       = id
        self.group    = group
        self.class_   = class_
        self.module   = module
        self.mid      = mid
        self.index    = index
        self.resource = resource 
        self.value    = value
        self.loaded   = False
        self.changed  = False        
        
class NXPermissions(NXBase):
    nxconn  = None
    records = [NXPermissionRecord]

    def __init__(self, conn) -> None:
        self.nxconn = conn

    def load(self, userid: int) -> NXResult:
        result = NXResult()

        try:
            # Carrega esquema de permissões na base share
            r = self.nxconn.xp_sh.FDXQuery(SQL_PERMISSIONS)        
            if r.error == True:
                raise ValueError(r.message)
            else:
                if len(self.records) > 0:
                    self.records.clear()
                if r.dataset.recordcount > 0:
                    r.dataset.first()
                    while r.dataset.eof == False:
                        self.records.append(NXPermissionRecord(
                            r.dataset.fieldbyname('ID'), 
                            r.dataset.fieldbyname('Grupo'), 
                            r.dataset.fieldbyname('Classe'), 
                            r.dataset.fieldbyname('Modulo'), 
                            r.dataset.fieldbyname('MID'), 
                            r.dataset.fieldbyname('Indice'), 
                            r.dataset.fieldbyname('Recurso'),
                            r.dataset.fieldbyname('Permissao')))
                        r.dataset.next()

                # Carrega permissões do usuário 
                r = None  
                r = self.nxconn.xp_nx.FDXQuery(SQL_PERMISSIONS_USR, userid)  

                if r.error == True:
                    raise ValueError(r.message)
                else:                                        
                    r.dataset.first()
                    while r.dataset.eof == False:
                        for i, row in enumerate(self.records):                                                  
                            if row.id == r.dataset.fieldbyname('Esquema'):                                
                                row.value  = r.dataset.fieldbyname('Permissao')
                                row.loaded = True 
                                break

                        r.dataset.next()  

                    result.status = True        

        except Exception as e:
            result.make_error(0, 'Falha ao carregar permissões do usuário', str(e))
        finally:
            pass                

        return result            

    def read(self, mid: str, resource: str) -> bool:     
        r = False           
        for i, row in enumerate(self.records):
            if self.records[i].mid.lower() == mid.lower() and self.records[i].resource.lower() == resource.lower():
                r     = self.records[i].value
                break
        return r   
    
class NXSession(object):
    companyid   : int
    userid      : int
    wsid        : str    
    config      : NXConfig 
    permissions : NXPermissions    

    def __init__(self) -> None:
        self.nxconn : NXConnection

    def start(self, conn, companyid: int, userid: int, wsid: str) -> NXResult:        
        result         = NXResult()
        self.nxconn    = conn
        self.companyid = companyid
        self.userid    = userid
        self.wsid      = wsid    

        self.config = NXConfig('', '4', '1')
        self.config.nxconn = conn
        result             = self.config.load() 
        

        if result.status == True:
            self.permissions = NXPermissions(self.config.nxconn) 
            result           = self.permissions.load(self.userid)

        return result

class NXConnection(object):
    token     = NXToken
    conn      = None
    conn_sh   = None    
    conn_nx   = None 
    result    = NXResult()   
    started   = False  
    xp        = FDExpress
    xp_sh     = FDExpress
    xp_nx     = FDExpress
    companies = None
    activate  = False
    session   = NXSession

    def __init__(self) -> None:
        self.CONN_STR    = '{driver};{server};{port};{database};{uid};{pwd}'
        self.DRIVER      = 'DRIVER={SQL Server Native Client 11.0}'
        self.SERVER      = 'SERVER={}'.format(nxc.NEXT_SERVER)
        self.PORT        = 'PORT={}'.format(nxc.NEXT_PORT)
        self.DATABASE    = 'DATABASE={}'.format(nxc.NEXT_DATABASE)
        self.SH_DBASE    = 'DATABASE={}'.format(nxc.NEXT_SH_DATABASE)
        self.USER        = 'UID={}'.format(nxc.NEXT_USER)
        self.PWD         = 'PWD={}'.format(nxc.NEXT_PWD)
        self.NX_SERVER   = 'SERVER={}'    
        self.NX_DATABASE = 'DATABASE={}'      
        self.NX_USER     = 'UID={}'
        self.NX_PWD      = 'PWD={}'  

    def start(self):            
        # Base NEXT
        try:
            self.conn = pyodbc.connect(self.CONN_STR.format(driver = self.DRIVER, server = self.SERVER, port = self.PORT, database = self.DATABASE, uid = self.USER, pwd = self.PWD))                
            self.xp   = FDExpress(self.conn)            

        except Exception as e: 
            self.result.make_error(0, 'Falha na conexão com a base NEXT', str(e))
            
        if self.result.error == False:    
            
            # Base SHARE
            try:
                self.conn_sh = pyodbc.connect(self.CONN_STR.format(driver = self.DRIVER, server = self.SERVER, port = self.PORT, database = self.SH_DBASE, uid = self.USER, pwd = self.PWD))     
                self.xp_sh   = FDExpress(self.conn_sh)           
                self.result.status = True    
                self.started       = True  

            except Exception as e: 
                self.result.make_error(0, 'Falha na conexão com a base SHARE', str(e))           

    def stop(self):
        if self.started: 
            self.conn.close()
            self.conn_sh.close()

        if self.activate:
            self.conn_nx.close() 
    
    # Login na plataforma
    def login(self, type: NXLoginType, token: str) -> NXResult:
        __result   = NXResult()    
        self.token = NXToken(token) # decodifca token        

        if self.token.isValid == True:
            try:
                self.start() # Efetua conexão com a base NEXT                         

                if not self.result.error:
                    # Efetua login na base NEXT                    
                    __result = self.__login(self.token)                                      

                    if __result.status == True:
                        if type == NXLoginType.NEXT:                        
                            try:
                                rs = self.xp_nx.FDXQuery(SQL_NX_COMPANIES) # Consulta empresas                            
                                
                                if rs.dataset.recordcount == 0: 
                                    __result.make_error(0, 'Nenhuma empresa registrada para este Token')
                                else:
                                    self.companies = rs.dataset
                                    self.companies.first()
                                    list = []
                                    while self.companies.eof == False:
                                        list.append(empresa(self.companies.fieldbyname('Codigo'), self.companies.fieldbyname('Nome'), self.companies.fieldbyname('CNPJ')))
                                        self.companies.next()

                                    __result.status = True 
                                    __result.data   = list 

                            except Exception as e: 
                                __result.make_error(0, 'Erro ao carregar lista de empresas', str(e))         
                            finally:

                                pass                      
                        elif type == NXLoginType.SYSTEM or type == NXLoginType.SYSTEM_AUTO:
                            try:
                                rs = self.xp_nx.FDXQuery(SQL_NX_COMPANIES + SQL_NX_COMPANY_ID.format(self.token.companyId, self.token.companyId)) # Consulta empresas                            
                                
                                if rs.dataset.recordcount == 0: 
                                    __result.make_error(0, 'Empresa não encontrada neste Token')
                                else:
                                    self.companies = rs.dataset

                                    # Login do usuário 
                                    self.session_login_prepare()
                                    __result = self.session_login(self.token.userName, self.token.userPwd, self.token.companyId, type == NXLoginType.SYSTEM_AUTO)                                

                            except Exception as e: 
                                __result.make_error(0, 'Erro ao carregar lista de empresas', str(e))         
                            finally:
                                pass   
                        else:
                            __result.make_error(0, 'Tipo de login incorreto')    
                else:
                    __result = self.result                                    
            except:
                pass
        else:
            __result.make_error(0, 'Token inválido') 

        return  __result

    def __login(self, token: NXToken) -> NXResult:
        result = NXResult()
        try:  
            rs = self.xp.FDXQuery(SQL_NEXT_TOKEN_LOGIN, token.tokenId, encode_b64(token.tokenPwd, True))

            if rs.error: 
                raise ValueError(rs.message) 

            if rs.dataset.recordcount == 0:
                result.make_error(0, 'Token não encontrado ou senha inválida')
            else:                                
                match NXTokenStatus(rs.dataset.fieldbyname('Status')):
                    case NXTokenStatus.NONE:      result.make_error(0, 'O Token não foi habilidado, contate o suporte técnico')
                    case NXTokenStatus.ATIVO:     result.status = True 
                    case NXTokenStatus.INATIVO:   result.make_error(0, 'O Token encontra-se inativo')                
                    case NXTokenStatus.BLOQUEADO: result.make_error(0, 'O Token encontra-se bloqueado, contate o suporte técnico')
                
                # Prepara conexão com a base do usuário 
                if result.status == True:
                    self.NX_SERVER   = self.NX_SERVER.  format(rs.dataset.fieldbyname('Conn_Host'))   
                    self.NX_DATABASE = self.NX_DATABASE.format(rs.dataset.fieldbyname('Conn_Base'))        
                    self.NX_USER     = self.NX_USER.    format(rs.dataset.fieldbyname('Conn_User'))   
                    self.NX_PWD      = self.NX_PWD.     format(decode_b64(rs.dataset.fieldbyname('Conn_Pwd'), True))    

                    # Efetua conexão com a base do usuário
                    result = self.active()            
                                    
        except Exception as e: 
            result.make_error(0, 'Falha na autenticação do token', str(e))
        finally:
            pass            

        return result      

    # Ativa conxão com Base do usuário
    def active(self) -> NXResult:
        r = NXResult()        
        try:
            self.conn_nx  = pyodbc.connect(self.CONN_STR.format(driver = self.DRIVER, server = self.NX_SERVER, port = '', database = self.NX_DATABASE, uid = self.NX_USER, pwd = self.NX_PWD))  
            self.xp_nx    = FDExpress(self.conn_nx) 
            self.activate = True # Seção ativa
            self.session  = NXSession()

            r.status      = True
        except Exception as e: 
            self.result.make_error(0, 'Falha na conexão com a base de dados', str(e))  

        return r    
    
    # Prepara tabela de usuários
    def session_login_prepare(self, adminPwd: str = 'admin'): 
        
        # Verifica se usupario ADMIN existe se não existir cria
        rs = self.xp_nx.FDXQuery(SQL_USER_CHECK, 'ADMIN')
        
        if rs.dataset.recordcount == 0: 
            id = self.xp_nx.AutoInc(table='Usuarios', field='Codigo')
            rs = self.xp_nx.FDXSQL(SQL_USER_INSERT, id, 'ADMIN', 3, encode_b64('admin', True), 'Senha Padrão', '', 1, 0, 0)

        # Verifica se usupario NEXTAutoLogin existe, se não existir cria
        rs = self.xp_nx.FDXQuery(SQL_USER_CHECK, 'NEXTAutoLogin')

        if rs.dataset.recordcount == 0: 
            id = self.xp_nx.AutoInc(table='Usuarios', field='Codigo')
            rs = self.xp_nx.FDXSQL(SQL_USER_INSERT, id + 1, 'NEXTAutoLogin', 1, encode_b64(self.pwd_gen(12), True), '', '', 1, 1, 0)      

    # Login do usuário na empresa
    def session_login(self, user: str, pwd: str, company: int, auto: bool = False) -> NXResult:
        r = NXResult()
        try:    
            if auto: s = SQL_USER_LOGIN_INT
            else:    s = '';    
            
            rs     = self.xp_nx.FDXQuery(SQL_USER_LOGIN.format(s), user, user) 
            userid = rs.dataset.fieldbyname('Codigo')

            if rs.error:
                raise ValueError(rs.message) 

            if rs.dataset.recordcount == 0:
                r.make_error(0, 'Usuário não encontrado')
            else:
                if pwd == decode_b64(rs.dataset.fieldbyname('Senha'), True) or auto:
                    #r.status = True

                    # Carrega dados da session
                    r = self.session.start(self, company, userid, '')
                else:
                    r.make_error(0, 'Senha do usuário não está correta')  

        except Exception as e:
            r.make_error(0, 'Erro na autenticação do Usuário', str(e))
        finally:
            pass 

        return r       
    
    @classmethod
    def pwd_gen(self, size: int = 20) -> str:
        alphabet = string.ascii_letters + string.digits + '-_@#$!'

        while True:
            password = ''.join(secrets.choice(alphabet) for i in range(size))
            if (sum(c.islower() for c in password) >= 4 and sum(c.isupper() for c in password) >= 4 and sum(c.isdigit() for c in password) >= 4):
                break  

        return password                      