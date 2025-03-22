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
        
        # Crear cliente "Desconocido" por defecto
        unknown_customer = session.query(Customer).filter_by(id=0).first()
        if not unknown_customer:
            unknown_customer = Customer(
                id=0,
                name="Desconocido",
                email="desconocido@example.com",
                address="Sin dirección",
                phone="000-0000"
            )
            session.add(unknown_customer)
            session.commit()
            logger.info("Cliente 'Desconocido' creado con éxito")
        
        # Crear productos de prueba
        # Verificar si ya existen productos
        products_count = session.query(Product).count()
        if products_count == 0:
            # Crear categorías de ejemplo
            categories = {
                "Computadoras": Category(name="Computadoras", description="Equipos de cómputo", active=True),
                "Monitores": Category(name="Monitores", description="Pantallas y monitores", active=True),
                "Periféricos": Category(name="Periféricos", description="Accesorios y periféricos", active=True),
                "Impresoras": Category(name="Impresoras", description="Impresoras y escáneres", active=True)
            }
            
            # Crear proveedor de ejemplo
            supplier = Supplier(
                name="TechStore",
                email="info@techstore.com",
                phone="123-456-7890",
                address="Calle Principal 123"
            )
            
            # Agregar categorías y proveedor
            for category in categories.values():
                session.add(category)
            session.add(supplier)
            session.flush()  # Para obtener los IDs
            
            # Crear productos de ejemplo
            products = [
                Product(
                    name="Laptop HP",
                    description="Laptop HP Pavilion 15.6 pulgadas",
                    category_id=categories["Computadoras"].id,
                    price=899.99,
                    stock=10,
                    supplier_id=supplier.id,
                    code="LAP-001"
                ),
                Product(
                    name="Monitor Dell",
                    description="Monitor Dell 24 pulgadas Full HD",
                    category_id=categories["Monitores"].id,
                    price=249.99,
                    stock=15,
                    supplier_id=supplier.id,
                    code="MON-001"
                ),
                Product(
                    name="Teclado Logitech",
                    description="Teclado mecánico Logitech G Pro",
                    category_id=categories["Periféricos"].id,
                    price=129.99,
                    stock=20,
                    supplier_id=supplier.id,
                    code="TEC-001"
                ),
                Product(
                    name="Mouse Razer",
                    description="Mouse gaming Razer DeathAdder",
                    category_id=categories["Periféricos"].id,
                    price=69.99,
                    stock=25,
                    supplier_id=supplier.id,
                    code="MOU-001"
                ),
                Product(
                    name="Impresora Epson",
                    description="Impresora multifuncional Epson EcoTank",
                    category_id=categories["Impresoras"].id,
                    price=349.99,
                    stock=8,
                    supplier_id=supplier.id,
                    code="IMP-001"
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