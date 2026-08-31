import sqlite3
from pathlib import Path

class Database():

    connection=None
    currentdir = Path(__file__).resolve().parent
    route = currentdir/"databaseFile"/"MainDatabase"
    cursor = None

    def __init__(self):
        try:
            self.connection = sqlite3.connect(self.route)

        except Exception as e:
            print(f"No se ha podido conectar o crear la base de datos: {e}")