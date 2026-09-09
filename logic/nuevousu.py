from pathlib import Path
import sys
import shutil
import face_recognition

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QFileDialog, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

# IMPORTANTE: Asegúrate de que el archivo de tu base de datos se llame 'database.py' 
# y esté en la misma carpeta, o ajusta la importación según el nombre que le hayas dado.
from database.database import Database

DIRECTORIO = Path(__file__).resolve().parent
RUTA_UI = DIRECTORIO.parent / "interface" / "interfaz_nuevo.ui"
CARPETA_CONOCIDOS = DIRECTORIO / "known_faces"

ruta_logo = DIRECTORIO / "imagenes" / "logo.png"

class VentanaNuevoUsuario(QWidget):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        self.ui = loader.load(str(RUTA_UI))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self.ui.setStyleSheet(f"""
            QWidget#{self.ui.objectName()} {{
                background-color: #0B192C;
            }}
        """)
        self.resize(500, 450) 
        if self.ui.windowTitle():
            self.setWindowTitle(self.ui.windowTitle())
       
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

        CARPETA_CONOCIDOS.mkdir(parents=True, exist_ok=True)

        self.ruta_foto_seleccionada = None

        self.ui.btn_seleccionar_foto.clicked.connect(self.seleccionar_foto)
        self.ui.btn_guardar.clicked.connect(self.guardar_usuario)

    
    def seleccionar_foto(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar fotografía del usuario",
            "",
            "Imágenes (*.png *.jpg *.jpeg)"
        )

        if archivo:
            self.ruta_foto_seleccionada = Path(archivo)
            
            pixmap = QPixmap(str(self.ruta_foto_seleccionada))
            pixmap = pixmap.scaled(
                self.ui.lbl_preview_foto.width(),
                self.ui.lbl_preview_foto.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.ui.lbl_preview_foto.setPixmap(pixmap)

    def guardar_usuario(self):
        # Obtener los datos de la interfaz
        nombre = self.ui.txt_nombre.text().strip()
        telefono = self.ui.txt_telefono.text().strip()
        contra = self.ui.txt_contra.text().strip()
        es_admin = self.ui.radio_admin.isChecked()

        if not nombre:
            QMessageBox.warning(self, "Atención", "Por favor ingresa el nombre del usuario.")
            return
        
        if not self.ruta_foto_seleccionada:
            QMessageBox.warning(self, "Atención", "Por favor selecciona una fotografía.")
            return

        # Validación del rostro en la foto
        try:
            imagen_temporal = face_recognition.load_image_file(str(self.ruta_foto_seleccionada))
            encodings = face_recognition.face_encodings(imagen_temporal)
            
            if not encodings:
                QMessageBox.critical(self, "Error", "No se detectó ningún rostro en la foto. Intenta con otra.")
                return
            
            encoding_bytes = encodings[0].tobytes()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo procesar la imagen: {e}")
            return

        # Guardado de foto local y en Base de Datos
        extension = self.ruta_foto_seleccionada.suffix.lower()
        ruta_destino = CARPETA_CONOCIDOS / f"{nombre}{extension}"

        try:
            #Guardar en la carpeta local (por si acaso)
            shutil.copy(self.ruta_foto_seleccionada, ruta_destino)

            # Preparar datos para la BD
            tipo_usuario = 'admin' if es_admin else 'asistente'

            # Instanciar la BD, comprobar tablas e insertar usuario
            db = Database()
            db.createTables()
            db.insertUser(
                Name=nombre, 
                Face=encoding_bytes, #Subimos el vector numérico, no la foto
                PhoneNumber=telefono, 
                Type=tipo_usuario, 
                Password=contra
            )

            QMessageBox.information(self, "Éxito", f"Usuario '{nombre}' registrado correctamente en la base de datos.")
            
            # Limpiar todos los campos del formulario tras el éxito
            self.ui.txt_nombre.clear()
            self.ui.txt_telefono.clear()
            self.ui.txt_contra.clear()
            self.ui.radio_alumno.setChecked(True)
            self.ui.lbl_preview_foto.clear()
            self.ui.lbl_preview_foto.setText("Vista previa")
            self.ruta_foto_seleccionada = None
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al guardar: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana_nueva = VentanaNuevoUsuario()
    ventana_nueva.show()
    sys.exit(app.exec())