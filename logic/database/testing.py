from database import Database #Para poder crear el objeto de la base de datos

#Este archivo solo es de testeo, se ejecutará solo una vez si no se tiene la base de datos aún
database = Database()
database.createTables()