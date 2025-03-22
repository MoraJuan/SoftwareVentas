from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
import os

# Importar los modelos en el orden correcto
from database.connection import Base
# Es importante importar Category antes que Product debido a la relación de clave foránea
from models.Category import Category
from models.Supplier import Supplier
from models.Customer import Customer
from models.Product import Product

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    try:
        # Crear el motor de base de datos
        engine = create_engine('sqlite:///ventas.db')
        
        # Crear todas las tablas
        Base.metadata.create_all(engine)
        
        # Crear una sesión
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Verificar si ya existe un usuario administrador
        from models.User import User, UserRole
        admin = session.query(User).filter(User.role == UserRole.ADMIN).first()
        
        if not admin:
            # Crear usuario administrador por defecto
            from models.User import User, UserRole
            from models.Administrator import Administrator
            
            admin_user = User(
                username="admin",
                email="admin@example.com",
                role=UserRole.ADMIN
            )
            admin_user.set_password("admin123")
            
            session.add(admin_user)
            session.flush()  # Para obtener el ID
            
            # Crear perfil de administrador
            admin_profile = Administrator(id=admin_user.id, user=admin_user)
            session.add(admin_profile)
            
            session.commit()
            logger.info("Usuario administrador creado con éxito")
        else:
            logger.info("El usuario administrador ya existe")
        
        logger.info("Base de datos inicializada correctamente")
        
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {str(e)}")
        raise

if __name__ == "__main__":
    # Eliminar la base de datos si ya existe
    if os.path.exists("ventas.db"):
        os.remove("ventas.db")
        logger.info("Base de datos anterior eliminada")
    
    # Inicializar la base de datos
    init_database()