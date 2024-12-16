import os
import sys

# Agregar el directorio raíz al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import init_db, SessionLocal
from services.authService import AuthService

def create_admin():
    """Crea el usuario administrador inicial"""
    try:
        # Inicializar la base de datos
        init_db()
        
        # Crear sesión
        db = SessionLocal()
        auth_service = AuthService(db)
        
        # Datos del administrador
        admin_data = {
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",
            "role": "ADMIN"
        }
        
        # Registrar administrador
        admin = auth_service.register_user(admin_data)
        print(f"Administrador creado exitosamente: {admin.username}")
        
    except Exception as e:
        print(f"Error al crear administrador: {str(e)}")
        raise
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    create_admin()