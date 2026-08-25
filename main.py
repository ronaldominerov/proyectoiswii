from pathlib import Path
import sys
import cv2
import numpy as np
import face_recognition
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap

DIRECTORIO = Path(__file__).resolve().parent
RUTA_UI = DIRECTORIO / "interfazcamara.ui"
CARPETA_CONOCIDOS = DIRECTORIO / "known_faces"
TOLERANCIA = 0.6


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

        # --- Estado para cámara y reconocimiento ---
        self.frame_actual = None  # último frame BGR capturado (numpy array)
        self.encodings_conocidos, self.nombres_conocidos = self.cargar_rostros_conocidos()

        # --- Captura de video ---
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.ui.lbl_camara.setText("No se pudo abrir la cámara")
        else:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.actualizar_frame)
            self.timer.start(30)  # ~33 fps

    # ------------------------------------------------------------------
    # Carga de rostros conocidos (igual que en el script standalone)
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Feed de video en vivo -> QLabel
    # ------------------------------------------------------------------
    def actualizar_frame(self):
        ok, frame = self.cap.read()
        if not ok:
            return

        self.frame_actual = frame  # guardamos el frame BGR crudo para el botón

        # Convertir BGR (OpenCV) -> RGB -> QImage -> QPixmap
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(
            self.ui.lbl_camara.width(),
            self.ui.lbl_camara.height(),
            Qt.KeepAspectRatio,
        )
        self.ui.lbl_camara.setPixmap(pixmap)

    # ------------------------------------------------------------------
    # Botón VERIFICAR
    # ------------------------------------------------------------------
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

        # Tomamos la primera cara detectada (podrías iterar todas si esperas varias)
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

    # ------------------------------------------------------------------
    # Liberar la cámara al cerrar la ventana
    # ------------------------------------------------------------------
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