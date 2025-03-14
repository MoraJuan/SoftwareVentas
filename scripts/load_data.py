import os
import sys

# Agregar el directorio raíz al PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from database.connection import SessionLocal, init_db

def main():
    """
    Script principal para cargar datos de ejemplo en la base de datos.
    """
    try:
        print("Iniciando carga de datos de ejemplo...")
        # Asegurarse de que la base de datos está inicializada
        init_db()
        # Crear una nueva sesión
        session = SessionLocal()
        
        from utils.load_sample_data import load_sample_data
        load_sample_data(session)
        
        print("Proceso completado exitosamente.")
    except Exception as e:
        print(f"Error durante la carga de datos: {str(e)}")
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    main() 