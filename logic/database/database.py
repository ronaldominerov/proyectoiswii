import sqlite3
from pathlib import Path

class Database():

    connection=None
    currentdir = Path(__file__).resolve().parent
    route = currentdir/"databaseFile"/"MainDatabase.db"
    cursor = None

    def __init__(self):
        try:
            self.connection = sqlite3.connect(self.route)
            self.cursor = self.connection.cursor()

        except Exception as e:
            print(f"No se ha podido conectar o crear la base de datos: {e}")

    def createTables(self):
        try:
            self.cursor.execute("pragma foreign_keys = ON;")

            self.cursor.execute("""
                Create Table If Not Exists Usuarios(
                    id Integer Primary Key Autoincrement,
                    nombre Text Not Null,
                    rostro Blob,
                    telefono Text,
                    tipo Text Not Null Check(tipo In ('admin', 'asistente')),
                    contrasenia Text
                )
            """)
            self.cursor.execute("""
                Create Table If Not Exists Clase(
                    id Integer Primary Key Autoincrement,
                    id_admin Integer Not Null,
                    nombre Text Not Null,
                    Foreign Key (id_admin) References Usuarios(id)  
                )
            """)
            self.cursor.execute("""
                Create Table If Not Exists Registro(
                    id Integer Primary Key Autoincrement,
                    id_admin Integer Not Null,
                    id_asistente Integer Not Null,
                    id_clase Integer Not Null,
                    fecha_hora Datetime Default CURRENT_TIMESTAMP,
                    asistencia BOOLEAN Not Null Default False,
                    Foreign Key (id_asistente) References Usuarios(id),
                    Foreign Key (id_admin) References Usuarios(id),
                    Foreign Key (id_clase) References Clase(id)
                )
            """)

            self.connection.commit()
            print("Tablas comprobadas/Añadidas")
        except Exception as e:
            print(f"Error al crear o verificar las tablas: {e}")

    #Función para agregar usuarios a la tabla "Usuarios", recibe cada uno de los datos para agregarlos a la tabla (Podríamos crear un objeto de tipo Usuario)
    #Ya está protegido contra inyecciones sql
    def insertUser(self, Name, Face, PhoneNumber,Type, Password):
        try:
            self.cursor.execute("Insert Into Usuarios (nombre, rostro, telefono, tipo, contrasenia) Values(?, ?, ?, ?, ?)",(Name, Face, PhoneNumber, Type, Password))
            self.connection.commit()
            print("Usuario Insertado jajaj XD")
            
        except Exception as e:
            print(f"No se pudo hacer la inserción: {e}")

    #Función para agregar clases/laboratorios a la tabla "Clase", recibe cada uno de los datos
    def insertClase(self, id_admin, nombre):
        try:
            self.cursor.execute("Insert Into Clase Values(Null, ?, ?)",(id_admin,nombre))
            self.connection.commit()
            print("Clase insertada jajaj xd")
        except Exception as e:
            print(f"No se pudo hacer la inserción: {e}")

    
    #Función para insertar los registros de asistencia a la tabla "Registro"
    #Esta es el primer paso, se crean todos los registros con la asistencia "False" y posteriormente cuando alguien registre asistencia 
    # se actualizará a True junto con la fecha y hora

    def insertReg(self, id_admin, id_asistente, id_clase):
        try:
            self.cursor.execute("Insert Into Registro (id_admin,id_asistente,id_clase) Values(?,?,?)", (id_admin, id_asistente, id_clase))
            self.connection.commit()
            print("Registro básico hecho")
        except Exception as e:
            print(f"No se pudo hace la inserción de registro: {e}")

    def confirmReg(self, id_reg):
        try:
            self.cursor.execute("Update Registro Set asistencia = 1, fecha_hora = CURRENT_TIMESTAMP Where id=?", (id_reg,))
            self.connection.commit()
            print("Registro confirmado")
        except Exception as e:
            print(f"No se pudo confirmar la asistencia: {e}")

    #Obtención de datos
    def getAllFaces(self):
        try:
            self.cursor.execute("Select id, rostro From Usuarios")
            return self.cursor.fetchall() 
        except Exception as e:
            print(f"Error al recuperar los rostros: {e}")
            return []
        
    def getRegister(self, id_asistente, id_clase):
        try:
            self.cursor.execute("Select id From Registro Where id_asistente = ? and id_clase = ? and Date(fecha_hora) = Date('now', 'localtime') ", (id_asistente, id_clase))
            
            #Usamos fetchone porque un alumno solo debe tener un registro por clase al día
            resultado = self.cursor.fetchone()
            
            if resultado:
                return resultado[0] #Retorna el identificador limpio
            else:
                return None #Retorna None si el profesor no ha creado los registros del día
                
        except Exception as e:
            print(f"Error al buscar el registro de hoy: {e}")
            return None



