import sys
import subprocess
from pathlib import Path

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QMessageBox)

from database.database import Database

DIRECTORIO = Path(__file__).resolve().parent
SCRIPT_NUEVO_USUARIO = DIRECTORIO / "nuevousu.py"

class VentanaConfirmacion(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Confirmación de Seguridad")
        self.setFixedSize(320, 250) 

        layout = QVBoxLayout(self)

        self.lbl_aviso = QLabel("Por seguridad, ingrese de nuevo sus datos\npara verificar que es administrador:")
        self.lbl_aviso.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        
        self.lbl_telefono = QLabel("Teléfono del administrador:")
        self.txt_telefono = QLineEdit()
        
        self.lbl_instruccion = QLabel("Contraseña:")
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password) 
        
        self.btn_ingresar = QPushButton("Verificar y Continuar")

        layout.addWidget(self.lbl_aviso)
        layout.addWidget(self.lbl_telefono)
        layout.addWidget(self.txt_telefono)
        layout.addWidget(self.lbl_instruccion)
        layout.addWidget(self.txt_password)
        layout.addWidget(self.btn_ingresar)

        self.btn_ingresar.clicked.connect(self.verificar_seguridad)
    
    def verificar_seguridad(self):
        telefono_ingresado = self.txt_telefono.text().strip()
        password_ingresada = self.txt_password.text().strip()

        if not telefono_ingresado or not password_ingresada:
            QMessageBox.warning(self, "Atención", "Por favor, completa ambos campos.")
            return

        db = Database()
        
        es_admin_valido = db.loginAdmin(telefono_ingresado, password_ingresada)

        if es_admin_valido:
            if SCRIPT_NUEVO_USUARIO.exists():
                subprocess.Popen([sys.executable, str(SCRIPT_NUEVO_USUARIO)])
                self.close() 
            else:
                QMessageBox.critical(self, "Error", f"No se encontró el script {SCRIPT_NUEVO_USUARIO.name}")
        else:
            QMessageBox.warning(self, "Acceso Denegado", "Datos incorrectos o no tienes permisos de administrador.")
            self.txt_password.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaConfirmacion()
    ventana.show()
    sys.exit(app.exec())