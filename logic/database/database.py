import sqlite3
import face_recognition
import numpy as np
from pathlib import Path

class Database():
    TOLERANCIA = 0.6
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

    def insertUser(self, Name, Face, PhoneNumber,Type, Password):
        try:
            self.cursor.execute("Insert Into Usuarios (nombre, rostro, telefono, tipo, contrasenia) Values(?, ?, ?, ?, ?)",(Name, Face, PhoneNumber, Type, Password))
            self.connection.commit()
            print("Usuario Insertado jajaj XD")
            
        except Exception as e:
            print(f"No se pudo hacer la inserción: {e}")

    def insertClase(self, id_admin, nombre):
        try:
            self.cursor.execute("Insert Into Clase Values(Null, ?, ?)",(id_admin,nombre))
            self.connection.commit()
            print("Clase insertada jajaj xd")
        except Exception as e:
            print(f"No se pudo hacer la inserción: {e}")

    def loginAdmin(self, telefono, contrasenia):
        try:
            self.cursor.execute("""
                select 1 from Usuarios  where telefono = ? and contrasenia = ? and tipo = 'admin' """, (telefono, contrasenia))
            
            resultado = self.cursor.fetchone()
            
            if resultado:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error al verificar credenciales: {e}")
            return False

    def loginGeneral(self, telefono, contrasenia):
        try:
            self.cursor.execute("""
                select 1 from Usuarios  where telefono = ? and contrasenia = ? """, (telefono, contrasenia))
            
            resultado = self.cursor.fetchone()
            
            if resultado:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error al verificar credenciales: {e}")
            return False

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
            
            resultado = self.cursor.fetchone()
            
            if resultado:
                return resultado[0] 
            else:
                return None 
                
        except Exception as e:
            print(f"Error al buscar el registro de hoy: {e}")
            return None

    def getName(self, id_usuario):
        try:
            self.cursor.execute("Select nombre From Usuarios Where id = ?", (id_usuario,))
            resultado = self.cursor.fetchone()
            return resultado[0] if resultado else None
        except Exception as e:
            print(f"Error al buscar el nombre: {e}")
            return None

    #Esta func compara el rostro actual con todos los de la bd
    def faceCompare(self, frame_rgb):
        ubicaciones = face_recognition.face_locations(frame_rgb)
        if not ubicaciones:
            return None, None  # no hay ninguna cara en el frame

        #calcula el encoding de la cara encontrada
        encoding_desconocido = face_recognition.face_encodings(frame_rgb, ubicaciones)[0]

        #Saca todos los encodings de la bd
        filas = self.getAllFaces()  # [(id, blob), (id, blob), ...]
        if not filas:
            return None, None  #base de datos vacía

        #convierte el blob en un array de numpy
        ids = []
        encodings_conocidos = []
        #compara la cara desconocida con todas las caras de la bd
        for id_usuario, blob in filas:
            if blob is None or len(blob) !=1024: #tmb verifica que el blob sea de 128 / 1024bits
                continue
            encodings_conocidos.append(np.frombuffer(blob, dtype=np.float64))
            ids.append(id_usuario)

        if not encodings_conocidos:
            return None, None

        #calcula la distancia entre los otros encodings y el actual
        distancias = face_recognition.face_distance(encodings_conocidos, encoding_desconocido)

        #checa cual es la distancia mas cercana al cero
        idx = int(np.argmin(distancias))

        #debe ser menor a 0.6
        if distancias[idx] < self.TOLERANCIA:
            nom = self.getName(ids[idx])
            return nom, distancias[idx]

        return None, None  