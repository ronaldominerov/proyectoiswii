#EJECUTAR SOLO UNA VEZ PARA PASAR LAS FOTOS DE LA CARPETA A LA BD

from pathlib import Path
import face_recognition
from logic.database.database import Database

CARPETA_FOTOS = Path(__file__).resolve().parent / "known_faces"

def registerByFolder():
    db = Database()
    
    if not CARPETA_FOTOS.exists():
        print("No existe la carpeta")
        return
    inserts=0

    for arch in CARPETA_FOTOS.iterdir():
        if arch.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue

        nombre = arch.stem 
        image = face_recognition.load_image_file(str(arch))
        encodings= face_recognition.face_encodings(image)

        if not encodings:
            print(f"No se encontro cara en '{arch.name}'")
            continue

        encoding_bytes = encodings[0].tobytes()
        db.insertUser(
            Name = nombre,
            Face=encoding_bytes,
            PhoneNumber=None,
            Type="asistente",
            Password=None,
        )

        inserts+=1
    print(f"Listo: {inserts} usuario(s) registrado(s) desde {CARPETA_FOTOS}")
    
    
if __name__ == "__main__":
    registerByFolder()
    