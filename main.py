from pathlib import Path
import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget

DIRECTORIO = Path(__file__).resolve().parent
RUTA_UI = DIRECTORIO / "interfazcamara.ui"


class MiVentana(QWidget):

  def __init__(self):
    super().__init__()

    uic.loadUi(RUTA_UI, self)

    self.lbl_camara.setText("Esperando señal de la cámara...")

    self.veriButton.clicked.connect(self.verificar_asistencia)

  def verificar_asistencia(self):
    print("Botón presionado: Verificando...")
    # Acción de prueba temporal
    self.lbl_camara.setText("¡Verificación solicitada!")


if __name__ == "__main__":
  app = QApplication(sys.argv)
  ventana = MiVentana()
  ventana.show()
  sys.exit(app.exec())