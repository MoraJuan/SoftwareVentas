import random
from datetime import datetime, timedelta
import sys
import os

# Añadir el directorio raíz al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from models.Product import Product
from models.Customer import Customer
from models.Supplier import Supplier
from models.Category import Category
from services.productService import ProductService
from services.categoryService import CategoryService
from services.supplierService import SupplierService
from services.customerService import CustomerService

def load_sample_data(db: Session):
    """Carga datos de ejemplo en la base de datos"""
    # Crear categorías
    categories = create_sample_categories(db)
    
    # Crear proveedores
    suppliers = create_sample_suppliers(db)
    
    # Crear productos
    products = create_sample_products(db, categories, suppliers)
    
    # Crear clientes
    customers = create_sample_customers(db)
    
    return {
        "categories": categories,
        "suppliers": suppliers,
        "products": products,
        "customers": customers
    }

def create_sample_categories(db: Session):
    """Crea categorías de ejemplo"""
    category_service = CategoryService(db)
    
    category_names = [
        "Electrónica", 
        "Hogar", 
        "Oficina", 
        "Herramientas", 
        "Alimentos",
        "Bebidas",
        "Ropa"
    ]
    
    categories = []
    
    for name in category_names:
        try:
            # Verificar si ya existe
            existing = category_service.get_category_by_name(name)
            if existing:
                categories.append(existing)
                continue
                
            # Crear nueva categoría
            category = category_service.create_category({
                "name": name,
                "description": f"Categoría de {name.lower()}"
            })
            categories.append(category)
        except Exception as e:
            print(f"Error al crear categoría {name}: {str(e)}")
    
    return categories

def create_sample_suppliers(db: Session):
    """Crea proveedores de ejemplo"""
    supplier_service = SupplierService(db)
    
    supplier_data = [
        {
            "name": "TechSolutions SA",
            "email": "info@techsolutions.com",
            "phone": "123-456-7890",
            "address": "Av. Tecnología 123"
        },
        {
            "name": "Distribuidora Global",
            "email": "ventas@distglobal.com",
            "phone": "987-654-3210",
            "address": "Calle Comercio 456"
        },
        {
            "name": "Importadora FastShip",
            "email": "contacto@fastship.com",
            "phone": "555-123-4567",
            "address": "Av. Importación 789"
        },
        {
            "name": "Mayorista Express",
            "email": "mayorista@express.com",
            "phone": "777-888-9999",
            "address": "Blvd. Comercial 1010"
        }
    ]
    
    suppliers = []
    
    for data in supplier_data:
        try:
            # Verificar si ya existe
            existing = supplier_service.get_supplier_by_email(data["email"])
            if existing:
                suppliers.append(existing)
                continue
                
            # Crear nuevo proveedor
            supplier = supplier_service.create_supplier(data)
            suppliers.append(supplier)
        except Exception as e:
            print(f"Error al crear proveedor {data['name']}: {str(e)}")
    
    return suppliers

def create_sample_products(db: Session, categories, suppliers):
    """Crea productos de ejemplo"""
    product_service = ProductService(db)
    
    # Crear mapeos de nombres a IDs para categorías y proveedores
    category_map = {c.name: c.id for c in categories}
    supplier_map = {s.name: s.id for s in suppliers}
    
    product_data = [
        {
            "name": "Laptop HP Pavilion",
            "description": "Laptop con procesador i5, 8GB RAM, 512GB SSD",
            "category_id": category_map.get("Electrónica"),
            "price": 799.99,
            "stock": 15,
            "code": "LAP-001",
            "supplier_id": supplier_map.get("TechSolutions SA")
        },
        {
            "name": "Monitor LG 24 pulgadas",
            "description": "Monitor LED Full HD 1080p",
            "category_id": category_map.get("Electrónica"),
            "price": 149.99,
            "stock": 25,
            "code": "MON-002",
            "supplier_id": supplier_map.get("TechSolutions SA")
        },
        {
            "name": "Teclado Mecánico RGB",
            "description": "Teclado gaming con switches Blue",
            "category_id": category_map.get("Electrónica"),
            "price": 59.99,
            "stock": 30,
            "code": "TEC-003",
            "supplier_id": supplier_map.get("Distribuidora Global")
        },
        {
            "name": "Silla de Oficina Ergonómica",
            "description": "Silla ajustable con soporte lumbar",
            "category_id": category_map.get("Oficina"),
            "price": 129.99,
            "stock": 10,
            "code": "SIL-004",
            "supplier_id": supplier_map.get("Mayorista Express")
        },
        {
            "name": "Escritorio de Madera",
            "description": "Escritorio con dos cajones",
            "category_id": category_map.get("Oficina"),
            "price": 199.99,
            "stock": 8,
            "code": "ESC-005",
            "supplier_id": supplier_map.get("Mayorista Express")
        },
        {
            "name": "Licuadora Oster",
            "description": "Licuadora de 3 velocidades",
            "category_id": category_map.get("Hogar"),
            "price": 49.99,
            "stock": 20,
            "code": "LIC-006",
            "supplier_id": supplier_map.get("Importadora FastShip")
        },
        {
            "name": "Juego de Sartenes",
            "description": "Set de 3 sartenes antiadherentes",
            "category_id": category_map.get("Hogar"),
            "price": 34.99,
            "stock": 15,
            "code": "SAR-007",
            "supplier_id": supplier_map.get("Importadora FastShip")
        },
        {
            "name": "Juego de Destornilladores",
            "description": "Kit de 12 destornilladores de precisión",
            "category_id": category_map.get("Herramientas"),
            "price": 19.99,
            "stock": 40,
            "code": "DEST-008",
            "supplier_id": supplier_map.get("Distribuidora Global")
        },
        {
            "name": "Taladro Inalámbrico",
            "description": "Taladro recargable 12V con accesorios",
            "category_id": category_map.get("Herramientas"),
            "price": 89.99,
            "stock": 12,
            "code": "TAL-009",
            "supplier_id": supplier_map.get("Distribuidora Global")
        },
        {
            "name": "Café Orgánico Premium",
            "description": "Café en grano de origen único, 500g",
            "category_id": category_map.get("Alimentos"),
            "price": 12.99,
            "stock": 50,
            "code": "CAF-010",
            "supplier_id": supplier_map.get("Importadora FastShip")
        },
        {
            "name": "Agua Mineral 6 Pack",
            "description": "Pack de 6 botellas de 1L",
            "category_id": category_map.get("Bebidas"),
            "price": 5.99,
            "stock": 100,
            "code": "AGU-011",
            "supplier_id": supplier_map.get("Mayorista Express")
        },
        {
            "name": "Camiseta 100% Algodón",
            "description": "Camiseta talla M varios colores",
            "category_id": category_map.get("Ropa"),
            "price": 15.99,
            "stock": 60,
            "code": "CAM-012",
            "supplier_id": supplier_map.get("Distribuidora Global")
        },
        {
            "name": "Producto sin nombre",
            "description": "Producto de prueba",
            "category_id": None,
            "price": 100.0,
            "stock": 5,
            "code": "TEST-013",
            "supplier_id": None
        }
    ]
    
    products = []
    
    for data in product_data:
        try:
            # Verificar si ya existe por código
            existing = product_service.get_product_by_code(data["code"])
            if existing:
                products.append(existing)
                continue
            
            # Verificar que la categoría y proveedor existen
            if not data.get("category_id"):
                # Si no hay categoría, usar la primera disponible
                if categories:
                    data["category_id"] = categories[0].id
                    
            if not data.get("supplier_id"):
                # Si no hay proveedor, usar el primero disponible
                if suppliers:
                    data["supplier_id"] = suppliers[0].id
                    
            # Crear nuevo producto
            product = product_service.create_product(data)
            products.append(product)
        except Exception as e:
            print(f"Error al crear producto {data['name']}: {str(e)}")
    
    return products

def create_sample_customers(db: Session):
    """Crea clientes de ejemplo"""
    customer_service = CustomerService(db)
    
    customer_data = [
        {
            "name": "Juan Pérez",
            "email": "juan.perez@example.com",
            "phone": "123-456-7890",
            "address": "Calle Principal 123"
        },
        {
            "name": "María García",
            "email": "maria.garcia@example.com",
            "phone": "234-567-8901",
            "address": "Av. Central 456"
        },
        {
            "name": "Carlos Rodríguez",
            "email": "carlos.rodriguez@example.com",
            "phone": "345-678-9012",
            "address": "Plaza Mayor 789"
        },
        {
            "name": "Ana Martínez",
            "email": "ana.martinez@example.com",
            "phone": "456-789-0123",
            "address": "Blvd. Norte 1010"
        },
        {
            "name": "Empresa ABC",
            "email": "contacto@empresaabc.com",
            "phone": "567-890-1234",
            "address": "Zona Industrial 2525"
        }
    ]
    
    customers = []
    
    for data in customer_data:
        try:
            # Verificar si ya existe
            existing = customer_service.get_customer_by_email(data["email"])
            if existing:
                customers.append(existing)
                continue
                
            # Crear nuevo cliente
            customer = customer_service.create_customer(data)
            customers.append(customer)
        except Exception as e:
            print(f"Error al crear cliente {data['name']}: {str(e)}")
    
    return customers

if __name__ == "__main__":
    # Si se ejecuta este archivo directamente, cargar datos de muestra
    from database.connection import SessionLocal
    
    db = SessionLocal()
    try:
        print("Cargando datos de ejemplo...")
        result = load_sample_data(db)
        print(f"Se han cargado {len(result['categories'])} categorías")
        print(f"Se han cargado {len(result['suppliers'])} proveedores")
        print(f"Se han cargado {len(result['products'])} productos")
        print(f"Se han cargado {len(result['customers'])} clientes")
        print("Datos de ejemplo cargados con éxito")
    finally:
        db.close() 