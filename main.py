import sys
from PyQt6.QtWidgets import QApplication, QDialog  # Importar QDialog
from PyQt6 import uic
from pathlib import Path

DIRECTORIO = Path(__file__).resolve().parent
RUTA_UI = DIRECTORIO / "interfazmain.ui"

class MiVentana(QDialog):  
    def __init__(self):
        super().__init__()
        uic.loadUi(RUTA_UI, self)
        
        self.buttonBox.clicked.connect(self.al_hacer_clic)

    def al_hacer_clic(self):
        self.lblResultado.setText("¡Conectado exitosamente!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MiVentana()
    ventana.show()
    sys.exit(app.exec())