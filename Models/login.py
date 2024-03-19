from Class.nextbase import *

class empresa(NXBase):
    def __init__(self, codigo: int, nome: str, cnpj: str) -> None:
        self.codigo = codigo
        self.nome   = nome
        self.cnpj   = cnpj