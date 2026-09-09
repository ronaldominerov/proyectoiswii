#Librerías
from pathlib import Path #manejo de rutas
import sys #para cerrar la app
import cv2 #procesa los fotogramas, enciende y apaga la camara
import numpy as np 
import face_recognition #detecta y compara rostros a traves de un mapa de 128 valores (el encoding)
import subprocess #para abrir otros scripts
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QMessageBox
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap

from logic.database.database import Database

DIRECTORIO = Path(__file__).resolve().parent
RUTA_UI = DIRECTORIO / "interface" / "interfazcamara.ui"
ruta_imagen = DIRECTORIO / "imagenes" / "fondo.jpeg"
ruta_logo = DIRECTORIO / "imagenes" / "logo.png"

SCRIPT_CONTRAS = DIRECTORIO / "logic/contras.py"  
SCRIPT_LOGIN = DIRECTORIO / "logic/login.py"
#CARPETA_CONOCIDOS = DIRECTORIO / "known_faces"
#TOLERANCIA = 0.6

class MiVentana(QWidget):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        self.ui = loader.load(str(RUTA_UI))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.resize(600,500)
        if self.ui.windowTitle():
            self.setWindowTitle(self.ui.windowTitle())

        ruta_css = ruta_imagen.as_posix()
        self.ui.setStyleSheet(f"""
            QWidget#{self.ui.objectName()} {{
                border-image: url({ruta_css}) 0 0 0 0 stretch stretch;
            }}
        """)

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

        
        self.ui.lbl_camara.setText("Esperando señal de la camara...")
        
        self.ui.veriButton.clicked.connect(self.verificar_asistencia)
        self.db = Database()
        
        if hasattr(self.ui, 'btn_login'):
            self.ui.btn_login.clicked.connect(self.abrir_contras)
        else:
            print("Aviso: No se encontró un botón llamado 'btn_login' en la interfaz.")

        if hasattr(self.ui, 'cerrar'):
            self.ui.cerrar.clicked.connect(self.cerrar_sesion)
        else:
            print("Aviso: No se encontró un botón llamado 'cerrar' en la interfaz.")

        self.frame_actual = None  
        self.encodings_conocidos, self.nombres_conocidos = self.cargar_rostros_conocidos()

        #camara
        self.frame_actual = None  #Guarda el último fotograma 
        #llama la función para cargar los rostros conocidos y sus nombres
        
        #self.ids_conocidos, self.nombres_conocidos, self.encodings_conocidos = self.cargar_desde_bd()
           
        self.cap = cv2.VideoCapture(0) #enciende la camara web principal (0)
        if not self.cap.isOpened():
            self.ui.lbl_camara.setText("No se pudo abrir la camara")
        else:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.actualizar_frame)
            self.timer.start(30)  #cada 30ms actualiza el frame


    def abrir_contras(self):
        if SCRIPT_CONTRAS.exists():
            subprocess.Popen([sys.executable, str(SCRIPT_CONTRAS)])
        else:
            QMessageBox.critical(self, "Error", f"No se encontró el archivo: {SCRIPT_CONTRAS.name}")

    def cerrar_sesion(self):
        if SCRIPT_LOGIN.exists():
            subprocess.Popen([sys.executable, str(SCRIPT_LOGIN)])
            self.close()
        else:
            QMessageBox.critical(self, "Error", f"No se encontró el archivo: {SCRIPT_LOGIN.name}")

    def actualizar_frame(self):
            ok, frame = self.cap.read() #toma una foto de la camara
            if not ok:
                return
            self.frame_actual = frame #guarda la foto
    
            #Qt necesita la imagen en RGB, mientras que OpenCV la da en BGR
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #convierte la foto de BGR a RGB para que Qt la pueda mostrar
            h, w, ch = rgb.shape
            #convierte la matriz de nums a un objeto QImage y luego a QPixmap para mostrarlo en la interfaz
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg).scaled(
                self.ui.lbl_camara.width(),
                self.ui.lbl_camara.height(),
                Qt.KeepAspectRatio,
            )
            self.ui.lbl_camara.setPixmap(pixmap)

    

    #Aquí es donde se compara el rostro !!!
    def verificar_asistencia(self):
        print("Boton presionado: Verificando...")

        if self.frame_actual is None:
            self.ui.lbl_camara.setText("Sin imagen de camara todavia")
            return

        #if not self.encodings_conocidos:
        #    self.ui.lbl_camara.setText("No hay rostros conocidos cargados")
        #    return

        rgb = cv2.cvtColor(self.frame_actual, cv2.COLOR_BGR2RGB)
        nom, distancia = self.db.faceCompare(rgb)

        if nom is not None:
            self.mostrar_resultado_temporal(f"Usuario {nom} reconocido")
        else:S
            self.mostrar_resultado_temporal("Rostro no reconocido")
        
    #muestra un mensaje temporal
    def mostrar_resultado_temporal(self, texto, duracion_ms=2000):
        self.timer.stop()
        self.ui.lbl_camara.setText(texto)
        QTimer.singleShot(duracion_ms, self.timer.start)

    #libera la camara al cerrar la ventana
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
