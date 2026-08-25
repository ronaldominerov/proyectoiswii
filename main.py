from pathlib import Path
import sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

DIRECTORIO = Path(__file__).resolve().parent
RUTA_UI = DIRECTORIO / "interfazcamara.ui"


class MiVentana(QWidget):

    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        self.ui = loader.load(str(RUTA_UI))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  
        layout.addWidget(self.ui)

        self.resize(self.ui.sizeHint())
        if self.ui.windowTitle():
            self.setWindowTitle(self.ui.windowTitle())

        self.ui.lbl_camara.setText("Esperando señal de la cámara...")
        self.ui.veriButton.clicked.connect(self.verificar_asistencia)

    def verificar_asistencia(self):
        print("Botón presionado: Verificando...")
        self.ui.lbl_camara.setText("¡Verificación solicitada!")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    ventana = MiVentana()
    ventana.show()

    sys.exit(app.exec())