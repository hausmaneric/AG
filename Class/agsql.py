SQL_AG_USERS          = """SELECT * FROM [User]"""
SQL_AG_USERS_ID       = """SELECT * FROM [User] WHERE Id = ?"""
SQL_AG_USERS_EMAIL    = """SELECT COUNT(*) AS Total FROM [User] WHERE Email = ?"""
SQL_AG_USERS_LOGIN    = """SELECT * FROM [User] WHERE Login = ? AND Psw = ?"""

SQL_AG_HITS           = """SELECT * FROM [Access]"""
SQL_AG_HITS_ID        = """SELECT * FROM [Access] WHERE Id = ?"""
SQL_AG_HITS_EMAIL     = """SELECT COUNT(*) AS Total FROM [Access] WHERE Email = ?"""
SQL_AG_HITS_LOGIN     = """SELECT * FROM [Access] WHERE Login = ? AND Psw = ?"""

SQL_AG_STATES         = """SELECT * FROM State"""
SQL_AG_STATES_ID      = """SELECT * FROM State WHERE Id = ?"""

SQL_AG_kINSHIPS       = """SELECT * FROM Kinship"""
SQL_AG_kINSHIPS_ID    = """SELECT * FROM Kinship WHERE Id = ?"""

SQL_AG_FAMILYS        = """SELECT * FROM Family"""
SQL_AG_FAMILYS_ID     = """SELECT * FROM Family WHERE Id = ?"""

SQL_AG_PERSONS        = """
                          SELECT 
                              p.*,
                              f.Name AS Family_Name,
                              s.Name AS State_Name
                          FROM Person AS p 
                          LEFT JOIN Family AS f ON p.Family = f.Id
                          LEFT JOIN State  AS s ON p.State  = s.Id
                        """
SQL_AG_PERSONS_ID     = """
                          SELECT 
                              p.*,
                              f.Name AS Family_Name,
                              s.Name AS State_Name
                          FROM Person AS p 
                          LEFT JOIN Family AS f ON p.Family = f.Id
                          LEFT JOIN State  AS s ON p.State  = s.Id
                          WHERE Id = ?
                        """
                      
SQL_AG_CONNECTIONS    = """
                          SELECT 
                              c.*,
                              p.Name AS Person_Name,
                              k.Name AS Kinship_Name
                          FROM Connection AS c 
                          LEFT JOIN Person  AS p ON c.Person   = p.Id
                          LEFT JOIN Kinship AS k ON c.Kinship  = k.Id
                        """
SQL_AG_CONNECTIONS_ID = """
                          SELECT 
                              c.*,
                              p.Name AS Person_Name,
                              k.Name AS Kinship_Name
                          FROM Connection AS c 
                          LEFT JOIN Person  AS p ON c.Person   = p.Id
                          LEFT JOIN Kinship AS k ON c.Kinship  = k.Id
                          WHERE Id = ?
                        """