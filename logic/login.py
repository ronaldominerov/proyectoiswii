import sys
import subprocess
from pathlib import Path

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QMessageBox)

from database.database import Database

DIRECTORIO = Path(__file__).resolve().parent
SCRIPT_MAIN = DIRECTORIO.parent / "main.py"

class VentanaLogin(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Inicio de Sesión")
        self.setFixedSize(300, 200) 

        layout = QVBoxLayout(self)

        self.lbl_telefono = QLabel("Introduce el teléfono:")
        self.txt_telefono = QLineEdit()
        
        self.lbl_instruccion = QLabel("Introduce la contraseña:")
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password) 
        
        self.btn_ingresar = QPushButton("Ingresar")

        layout.addWidget(self.lbl_telefono)
        layout.addWidget(self.txt_telefono)
        layout.addWidget(self.lbl_instruccion)
        layout.addWidget(self.txt_password)
        layout.addWidget(self.btn_ingresar)

        self.btn_ingresar.clicked.connect(self.verificar_credenciales)
    
    def verificar_credenciales(self):
        telefono_ingresado = self.txt_telefono.text().strip()
        password_ingresada = self.txt_password.text().strip()

        if not telefono_ingresado or not password_ingresada:
            QMessageBox.warning(self, "Atención", "Por favor, completa ambos campos.")
            return

        db = Database()
        
        acceso_concedido = db.loginGeneral(telefono_ingresado, password_ingresada)

        if acceso_concedido:
            if SCRIPT_MAIN.exists():
                #Aqui esta la funcion de navegar
                subprocess.Popen([sys.executable, str(SCRIPT_MAIN)])
                self.close() 
            else:
                QMessageBox.critical(self, "Error", f"No se encontró el script {SCRIPT_MAIN.name}")
        else:
            QMessageBox.warning(self, "Acceso Denegado", "Teléfono o contraseña incorrectos.")
            self.txt_password.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaLogin()
    ventana.show()
    sys.exit(app.exec())