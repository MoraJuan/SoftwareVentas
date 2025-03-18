import sys
import os
import sqlite3
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_inventory_history_table():
    """Crea la tabla de historial de inventario directamente con SQLite"""
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('ventas_new.db')
        cursor = conn.cursor()
        
        # Verificar si la tabla ya existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inventory_history'")
        if cursor.fetchone():
            logger.info("La tabla inventory_history ya existe")
        else:
            logger.info("Creando tabla inventory_history...")
            
            # Crear la tabla
            cursor.execute('''
            CREATE TABLE inventory_history (
                id INTEGER PRIMARY KEY,
                product_id INTEGER NOT NULL,
                previous_stock INTEGER NOT NULL,
                new_stock INTEGER NOT NULL,
                change_amount INTEGER NOT NULL,
                change_type TEXT NOT NULL,
                change_reason TEXT,
                date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                FOREIGN KEY(product_id) REFERENCES product(id),
                FOREIGN KEY(user_id) REFERENCES employees(id)
            )
            ''')
            
            logger.info("Tabla inventory_history creada correctamente")
        
        # Verificar la estructura de la tabla
        cursor.execute("PRAGMA table_info(inventory_history)")
        columns = cursor.fetchall()
        logger.info(f"Estructura de la tabla inventory_history: {columns}")
        
        # Cerrar conexión
        conn.commit()
        conn.close()
        
        logger.info("Proceso completado")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    create_inventory_history_table() 