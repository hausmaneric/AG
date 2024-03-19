SQL_NEXT_TOKEN_LOGIN = """SELECT * FROM NEXT_SYSTEM_ID WHERE ID = ? AND NEXT_Senha = ?"""
SQL_NX_COMPANIES     = """SELECT Codigo, CNPJ, Nome, MatrizFilial FROM Empresas WHERE (Ativa = 1) AND (EX = 0)"""
SQL_NX_COMPANY_ID    = """ AND ((CNPJ = '{}') OR (Codigo = {}))"""
SQL_USER_CHECK       = """SELECT * FROM Usuarios WHERE Nome = ? AND (EX = 0)"""
SQL_USER_INSERT      = """INSERT INTO Usuarios (Codigo, Nome, Nivel, Senha, Dica, Parceiro, Ativo, Interno, EX) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
SQL_USER_LOGIN       = """SELECT * FROM Usuarios WHERE ((ID = ?) OR (Nome = ?)) AND (Ativo = 1) AND (EX = 0) {}"""
SQL_USER_LOGIN_INT   = """ AND (Interno = 1)""" 
SQL_CONFIG           = """
    DECLARE @EMPRESA    VARCHAR(10)
    DECLARE @LOCAL      VARCHAR(MAX)
    DECLARE @USR        VARCHAR(10)
    SET     @EMPRESA    = ?
    SET     @LOCAL      = ?
    SET     @USR        = ?

    SELECT
        ID,
        Perfil,
        Perfil_ID,
        Secao,
        Chave,
        CAST(Valor AS nvarchar(MAX)) AS Valor,
        Bloco
    FROM
        Config
    WHERE
        ((Perfil = 1) AND (Perfil_ID = '')) OR
        ((Perfil = 1) AND (Perfil_ID = @EMPRESA)) OR
        ((Perfil = 2) AND (Perfil_ID = @LOCAL)) OR
        ((Perfil = 3) AND (Perfil_ID = @USR))
    ORDER BY
        Perfil,
        Perfil_ID,
        Secao,
        Chave 
"""

SQL_PERMISSIONS      = "SELECT * FROM Permissoes WHERE ISNULL(Recurso, '') <> '' ORDER BY Grupo, Modulo, Indice"
SQL_PERMISSIONS_USR  = "SELECT * FROM Usuarios_Permissoes WHERE Usuario = ? ORDER BY Esquema"



  
