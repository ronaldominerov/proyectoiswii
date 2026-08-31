import sys
import subprocess
from pathlib import Path

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QMessageBox)

DIRECTORIO = Path(__file__).resolve().parent
ARCHIVO_PASS = DIRECTORIO / "interface/admin32.txt"
SCRIPT_NUEVO_USUARIO = DIRECTORIO / "logic/nuevousu.py"

class VentanaLogin(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Acceso de Administrador")
        self.setFixedSize(300, 150) # Una ventanita pequeña

        layout = QVBoxLayout(self)

        self.lbl_instruccion = QLabel("Introduce la contraseña de administrador:")
        
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password) 
        
        self.btn_ingresar = QPushButton("Ingresar")

        layout.addWidget(self.lbl_instruccion)
        layout.addWidget(self.txt_password)
        layout.addWidget(self.btn_ingresar)

        # 4. Conectar el botón a la función
        self.btn_ingresar.clicked.connect(self.verificar_password)

    
    def verificar_password(self):
        if not ARCHIVO_PASS.exists():
            QMessageBox.critical(self, "Error", f"Falta el archivo de configuración: {ARCHIVO_PASS.name}")
            return

        try:
            with open(ARCHIVO_PASS, "r", encoding="utf-8") as archivo:
                password_correcta = archivo.readline().strip()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo leer el archivo: {e}")
            return

        password_ingresada = self.txt_password.text().strip()

        if password_ingresada == password_correcta:
            if SCRIPT_NUEVO_USUARIO.exists():
                subprocess.Popen([sys.executable, str(SCRIPT_NUEVO_USUARIO)])
                self.close() 
            else:
                QMessageBox.critical(self, "Error", f"No se encontró el script {SCRIPT_NUEVO_USUARIO.name}")
        else:
            QMessageBox.warning(self, "Acceso Denegado", "Contraseña incorrecta.")
            self.txt_password.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaLogin()
    ventana.show()
    sys.exit(app.exec())