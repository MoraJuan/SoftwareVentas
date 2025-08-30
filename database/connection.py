from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import sys
import platform
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

Base = declarative_base()

# Resolver ruta de base de datos en un directorio de datos del usuario (persistente y con permisos)
def _default_db_url() -> str:
    # Permitir sobreescritura por variable de entorno
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    system = platform.system()
    if system == "Windows":
        base = os.getenv("LOCALAPPDATA") or str(Path.home())
        app_dir = Path(base) / "SistemaVentas"
    else:
        # Linux/Mac
        app_dir = Path.home() / ".sistemaventas"

    try:
        app_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        # Fallback al directorio actual si no se puede crear
        app_dir = Path.cwd()

    db_path = app_dir / "ventas.db"
    # Guardar para logging o inspección externa
    globals()["DB_FILE_PATH"] = str(db_path)
    return f"sqlite:///{db_path}"

# Crear el motor de la base de datos
DATABASE_URL = _default_db_url()
engine = create_engine(DATABASE_URL, echo=False, future=True)

# Configurar la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Inicializa la base de datos creando todas las tablas"""
    # Importar todos los modelos aquí para asegurar que están registrados
    # Es importante importar Category antes que Product debido a la relación de clave foránea
    from models.Category import Category
    from models.Supplier import Supplier
    from models.User import User
    from models.Customer import Customer
    from models.Product import Product
    from models.Sale import Sale
    from models.SaleItem import SaleItem
    from models.Stock import Stock
    from models.CommercialInvoice import CommercialInvoice
    from models.Administrator import Administrator
    from models.Employee import Employee
    from models.Subcategory import Subcategory
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)

def get_db():
    """Proporciona una sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()