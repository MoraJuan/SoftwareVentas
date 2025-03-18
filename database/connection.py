from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

Base = declarative_base()

# Crear el motor de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ventas_new.db")
engine = create_engine(DATABASE_URL, echo=True)

# Configurar la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Inicializa la base de datos creando todas las tablas"""
    # Importar todos los modelos aquí para asegurar que están registrados
    from models.User import User
    from models.Customer import Customer
    from models.Product import Product
    from models.Sale import Sale
    from models.SaleItem import SaleItem
    from models.Stock import Stock
    from models.Supplier import Supplier
    from models.CommercialInvoice import CommercialInvoice
    from models.Administrator import Administrator
    from models.Employee import Employee
    from models.Category import Category
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)

    # Insertar "desconocido"
    db = SessionLocal()
    try:
        unknown = db.query(Customer).filter_by(name="Desconocido").first()
        if not unknown:
            unknown = Customer(
                id=0,
                name="Desconocido",
                email="desconocido@example.com",
                phone="000-0000",
                address="Sin dirección"
            )
            db.add(unknown)
            db.commit()
    finally:
        db.close()

def get_db():
    """Proporciona una sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()