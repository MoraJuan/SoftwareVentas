from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

Base = declarative_base()

# Crear el motor de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")
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
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)

def get_db():
    """Proporciona una sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()