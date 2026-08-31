from pathlib import Path
import sys
import cv2
import numpy as np
import face_recognition
import subprocess 

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QMessageBox
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap

DIRECTORIO = Path(__file__).resolve().parent
RUTA_UI = DIRECTORIO / "interface/interfazcamara.ui"
CARPETA_CONOCIDOS = DIRECTORIO / "known_faces"
ruta_imagen = DIRECTORIO / "imagenes" / "fondo.jpeg"
ruta_logo = DIRECTORIO / "imagenes" / "logo.png"

SCRIPT_LOGIN = DIRECTORIO / "login.py"  

TOLERANCIA = 0.6


class MiVentana(QWidget):

    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        self.ui = loader.load(str(RUTA_UI))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.setFixedSize(600, 500)
        if self.ui.windowTitle():
            self.setWindowTitle(self.ui.windowTitle())

        # Fondo de la ventana
        ruta_css = ruta_imagen.as_posix()
        self.ui.setStyleSheet(f"""
            QWidget#{self.ui.objectName()} {{
                border-image: url({ruta_css}) 0 0 0 0 stretch stretch;
            }}
        """)

        # Logo
        if ruta_logo.exists():
            pixmap_logo = QPixmap(str(ruta_logo))
            pixmap_logo = pixmap_logo.scaled(
                self.ui.label_logo.width(),
                self.ui.label_logo.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.ui.label_logo.setPixmap(pixmap_logo)
        else:
            print(f"Aviso: no se encontró el logo en {ruta_logo}")

        self.ui.lbl_camara.setText("Esperando señal de la cámara...")
        
       
        self.ui.veriButton.clicked.connect(self.verificar_asistencia)
        
        
        if hasattr(self.ui, 'btn_login'):
            self.ui.btn_login.clicked.connect(self.abrir_login)
        else:
            print("Aviso: No se encontró un botón llamado 'btn_login' en la interfaz.")

        
        self.frame_actual = None  
        self.encodings_conocidos, self.nombres_conocidos = self.cargar_rostros_conocidos()

        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.ui.lbl_camara.setText("No se pudo abrir la cámara")
        else:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.actualizar_frame)
            self.timer.start(30)  # ~33 fps

    
    def abrir_login(self):
        """Abre la ventana de login como un proceso independiente."""
        if SCRIPT_LOGIN.exists():
            subprocess.Popen([sys.executable, str(SCRIPT_LOGIN)])
        else:
            QMessageBox.critical(self, "Error", f"No se encontró el archivo: {SCRIPT_LOGIN.name}")

    
    def cargar_rostros_conocidos(self):
        encodings, nombres = [], []
        if not CARPETA_CONOCIDOS.exists():
            print(f"Aviso: no existe la carpeta {CARPETA_CONOCIDOS}")
            return encodings, nombres

        for archivo in CARPETA_CONOCIDOS.iterdir():
            if archivo.suffix.lower() not in (".jpg", ".jpeg", ".png"):
                continue
            imagen = face_recognition.load_image_file(str(archivo))
            encs = face_recognition.face_encodings(imagen)
            if not encs:
                print(f"Aviso: no se detectó cara en {archivo.name}, se omite")
                continue
            encodings.append(encs[0])
            nombres.append(archivo.stem)

        print(f"Cargados {len(nombres)} rostros conocidos: {nombres}")
        return encodings, nombres

    
    def actualizar_frame(self):
        ok, frame = self.cap.read()
        if not ok:
            return

        self.frame_actual = frame 

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(
            self.ui.lbl_camara.width(),
            self.ui.lbl_camara.height(),
            Qt.KeepAspectRatio,
        )
        self.ui.lbl_camara.setPixmap(pixmap)

    
    def verificar_asistencia(self):
        print("Botón presionado: Verificando...")

        if self.frame_actual is None:
            self.ui.lbl_camara.setText("Sin imagen de cámara todavía")
            return

        if not self.encodings_conocidos:
            self.ui.lbl_camara.setText("No hay rostros conocidos cargados")
            return

        rgb = cv2.cvtColor(self.frame_actual, cv2.COLOR_BGR2RGB)
        ubicaciones = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, ubicaciones)

        if not encodings:
            self.mostrar_resultado_temporal("No se detectó ningún rostro")
            return

        distancias = face_recognition.face_distance(self.encodings_conocidos, encodings[0])
        idx = int(np.argmin(distancias))

        if distancias[idx] < TOLERANCIA:
            nombre = self.nombres_conocidos[idx]
            self.mostrar_resultado_temporal(f"¡Bienvenido, {nombre}! ✅")
        else:
            self.mostrar_resultado_temporal("Rostro no reconocido ❌")

    def mostrar_resultado_temporal(self, texto, duracion_ms=2000):
        """Muestra un texto sobre el feed unos segundos sin detener la cámara."""
        self.timer.stop()
        self.ui.lbl_camara.setText(texto)
        QTimer.singleShot(duracion_ms, self.timer.start)

    
    def closeEvent(self, event):
        if hasattr(self, "timer"):
            self.timer.stop()
        if self.cap.isOpened():
            self.cap.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    ventana = MiVentana()
    ventana.show()

    sys.exit(app.exec())