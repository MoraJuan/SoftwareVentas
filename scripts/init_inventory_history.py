import sys
import os
import logging
from datetime import datetime, timedelta
import traceback

# Añadir el directorio raíz al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_db, Base, engine
from models.InventoryHistory import InventoryHistory
from models.Product import Product
from sqlalchemy import inspect, text

# Configurar logging más detallado
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_inventory_history():
    """Inicializa la tabla de historial de inventario"""
    try:
        # Verificar si la tabla existe
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.debug(f"Tablas existentes: {tables}")
        
        if 'inventory_history' not in tables:
            logger.info("La tabla inventory_history no existe, creándola...")
        else:
            logger.info("La tabla inventory_history ya existe")
        
        # Crear la tabla si no existe
        Base.metadata.create_all(bind=engine)
        logger.info("Tabla de historial de inventario creada correctamente")
        
        # Obtener sesión de base de datos
        db = next(get_db())
        
        # Verificar si ya hay registros en la tabla
        try:
            count = db.query(InventoryHistory).count()
            logger.debug(f"Registros actuales en inventory_history: {count}")
            
            if count > 0:
                logger.info(f"La tabla de historial de inventario ya tiene {count} registros")
                return
        except Exception as e:
            logger.error(f"Error al contar registros: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Intentar verificar la estructura de la tabla
            try:
                result = db.execute(text("PRAGMA table_info(inventory_history)")).fetchall()
                logger.debug(f"Estructura de la tabla inventory_history: {result}")
            except Exception as e2:
                logger.error(f"Error al verificar estructura de tabla: {str(e2)}")
        
        # Obtener todos los productos
        products = db.query(Product).all()
        if not products:
            logger.info("No hay productos para inicializar el historial")
            return
        
        logger.info(f"Encontrados {len(products)} productos para inicializar")
        
        # Mostrar algunos productos para depuración
        for i, product in enumerate(products[:5]):
            logger.debug(f"Producto {i+1}: ID={product.id}, Nombre={product.name}, Stock={product.stock}")
        
        # Crear registros de historial para cada producto
        records_created = 0
        for product in products:
            try:
                logger.debug(f"Procesando producto ID={product.id}, Nombre={product.name}")
                
                # Registro de creación
                creation_record = InventoryHistory(
                    product_id=product.id,
                    previous_stock=0,
                    new_stock=product.stock,
                    change_amount=product.stock,
                    change_type="creación",
                    change_reason="Inicialización del sistema",
                    date=datetime.now() - timedelta(days=30)  # Hace 30 días
                )
                db.add(creation_record)
                db.flush()  # Asegurar que se asigne un ID
                records_created += 1
                logger.debug(f"Creado registro de creación para producto ID={product.id}")
                
                # Hacer commit por cada producto para evitar perder todo si hay un error
                db.commit()
                logger.debug(f"Commit exitoso para producto ID={product.id}")
                
            except Exception as e:
                db.rollback()
                logger.error(f"Error al crear historial para producto {product.id}: {str(e)}")
                logger.error(traceback.format_exc())
                continue
        
        # Verificar que se hayan creado los registros
        try:
            final_count = db.query(InventoryHistory).count()
            logger.info(f"Se inicializaron {records_created} registros de historial para {len(products)} productos")
            logger.info(f"Conteo final de registros en inventory_history: {final_count}")
        except Exception as e:
            logger.error(f"Error al contar registros finales: {str(e)}")
            logger.error(traceback.format_exc())
        
    except Exception as e:
        logger.error(f"Error al inicializar historial de inventario: {str(e)}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    logger.info("Inicializando tabla de historial de inventario...")
    init_inventory_history()
    logger.info("Proceso completado") 