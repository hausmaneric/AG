from Class.nextbase import *
from Class.express import *
from Class.nextutils import *

class MyConnection:
    cnx = FDConnection
    xp  = FDExpress
    res = NXResult()    
    
    def __init__(self) -> None:
        try:
            self.cnx = FDConnection('localhost\HSMNSQLEX', '62863', 'Genealogy', 'sa', '30062001Ee@')
            self.xp  = FDExpress(self.cnx.conn)
            
        except Exception as e:
            self.res.make_error(0, 'Erro de conexão ao banco', str(e))    