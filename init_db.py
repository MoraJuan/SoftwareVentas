from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
import os

# Importar todos los modelos para que SQLAlchemy los registre
from models import *

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    try:
        # Crear el motor de base de datos
        engine = create_engine('sqlite:///ventas.db')
        
        # Crear todas las tablas
        from database.connection import Base
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
        
        # Crear cliente "Desconocido" por defecto
        from models.Customer import Customer
        unknown_customer = session.query(Customer).filter_by(id=0).first()
        if not unknown_customer:
            unknown_customer = Customer(
                id=0,
                name="Desconocido",
                email="desconocido@example.com"
            )
            session.add(unknown_customer)
            session.commit()
            logger.info("Cliente 'Desconocido' creado con éxito")
        
        # Crear productos de prueba
        from models.Product import Product
        
        # Verificar si ya existen productos
        products_count = session.query(Product).count()
        if products_count == 0:
            # Crear productos de ejemplo
            products = [
                Product(
                    name="Laptop HP",
                    description="Laptop HP Pavilion 15.6 pulgadas",
                    category="Computadoras",
                    price=899.99,
                    stock=10
                ),
                Product(
                    name="Monitor Dell",
                    description="Monitor Dell 24 pulgadas Full HD",
                    category="Monitores",
                    price=249.99,
                    stock=15
                ),
                Product(
                    name="Teclado Logitech",
                    description="Teclado mecánico Logitech G Pro",
                    category="Periféricos",
                    price=129.99,
                    stock=20
                ),
                Product(
                    name="Mouse Razer",
                    description="Mouse gaming Razer DeathAdder",
                    category="Periféricos",
                    price=69.99,
                    stock=25
                ),
                Product(
                    name="Impresora Epson",
                    description="Impresora multifuncional Epson EcoTank",
                    category="Impresoras",
                    price=349.99,
                    stock=8
                )
            ]
            
            for product in products:
                session.add(product)
            
            session.commit()
            logger.info(f"{len(products)} productos de prueba creados con éxito")
        
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