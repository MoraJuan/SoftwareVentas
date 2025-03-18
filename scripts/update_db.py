import os
import sys
import logging
from sqlalchemy import create_engine, text

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_db_path():
    """Configura la ruta a la base de datos"""
    try:
        # Agregar el directorio raíz al path
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        
        # Importar modelos para que SQLAlchemy los reconozca
        from models.Product import Product
        from models.Category import Category
        from database.connection import Base
        
        return 'sqlite:///ventas.db'
    except Exception as e:
        logger.error(f"Error al configurar ruta de la base de datos: {str(e)}")
        sys.exit(1)

def update_database(db_url):
    """Actualiza la estructura de la base de datos"""
    try:
        from database.connection import Base
        
        # Crear motor de SQLAlchemy
        engine = create_engine(db_url)
        
        # Aplicar cambios al esquema
        logger.info("Aplicando cambios al esquema de la base de datos...")
        Base.metadata.create_all(engine)
        
        # Ejecutar SQL personalizado para actualizar la tabla product si es necesario
        with engine.connect() as conn:
            # Verificar si las columnas existen
            existing_columns = conn.execute(text("PRAGMA table_info(product)")).fetchall()
            column_names = [col[1] for col in existing_columns]
            
            # Agregar columnas si no existen
            if 'barcode' not in column_names:
                logger.info("Agregando columna 'barcode' a la tabla 'product'")
                conn.execute(text("ALTER TABLE product ADD COLUMN barcode TEXT"))
                
            if 'supplier' not in column_names:
                logger.info("Agregando columna 'supplier' a la tabla 'product'")
                conn.execute(text("ALTER TABLE product ADD COLUMN supplier TEXT"))
                
            if 'code' not in column_names:
                logger.info("Agregando columna 'code' a la tabla 'product'")
                conn.execute(text("ALTER TABLE product ADD COLUMN code TEXT"))
            
            # Verificar si la tabla category existe
            tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='category'")).fetchall()
            if not tables:
                logger.info("Creando tabla 'category'")
                conn.execute(text("""
                CREATE TABLE category (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    active BOOLEAN NOT NULL DEFAULT 1
                )
                """))
                
                # Insertar algunas categorías predeterminadas
                default_categories = [
                    ("Electrónicos", "Productos electrónicos y gadgets"),
                    ("Ropa", "Prendas de vestir"),
                    ("Alimentos", "Productos alimenticios"),
                    ("Hogar", "Artículos para el hogar"),
                    ("Papelería", "Artículos de oficina y papelería"),
                    ("Otros", "Productos que no entran en otras categorías")
                ]
                
                for name, description in default_categories:
                    conn.execute(
                        text("INSERT INTO category (name, description, active) VALUES (:name, :description, 1)"),
                        {"name": name, "description": description}
                    )
                
                logger.info(f"Se han agregado {len(default_categories)} categorías predeterminadas")
            
            conn.commit()
        
        logger.info("Base de datos actualizada correctamente.")
        return True
    except Exception as e:
        logger.error(f"Error al actualizar la base de datos: {str(e)}")
        return False

if __name__ == "__main__":
    db_url = setup_db_path()
    success = update_database(db_url)
    
    if success:
        logger.info("Actualización de la base de datos completada con éxito.")
    else:
        logger.error("No se pudo completar la actualización de la base de datos.")
        sys.exit(1) 