from datetime import datetime, timedelta
from models.Customer import Customer
from models.Supplier import Supplier
from models.Product import Product
from models.Sale import Sale
from models.SaleItem import SaleItem
from sqlalchemy.orm import Session
import random

def load_sample_data(session: Session):
    """
    Carga datos de ejemplo en la base de datos.
    Incluye clientes, proveedores, productos y ventas.
    """
    try:
        # Crear clientes de ejemplo
        customers = [
            Customer(
                name="Juan Pérez",
                email="juan.perez@email.com",
                phone="555-0001",
                address="Calle Principal 123"
            ),
            Customer(
                name="María García",
                email="maria.garcia@email.com",
                phone="555-0002",
                address="Avenida Central 456"
            ),
            Customer(
                name="Carlos López",
                email="carlos.lopez@email.com",
                phone="555-0003",
                address="Plaza Mayor 789"
            ),
            Customer(
                name="Ana Martínez",
                email="ana.martinez@email.com",
                phone="555-0004",
                address="Calle Secundaria 321"
            )
        ]
        session.add_all(customers)
        session.commit()

        # Crear proveedores de ejemplo
        suppliers = [
            Supplier(
                name="Distribuidora ABC",
                email="contacto@abc.com",
                phone="555-1001",
                address="Zona Industrial 1",
                description="Proveedor de electrónicos"
            ),
            Supplier(
                name="Mayorista XYZ",
                email="ventas@xyz.com",
                phone="555-1002",
                address="Zona Industrial 2",
                description="Proveedor de línea blanca"
            ),
            Supplier(
                name="Importadora 123",
                email="info@123.com",
                phone="555-1003",
                address="Zona Industrial 3",
                description="Proveedor de accesorios"
            )
        ]
        session.add_all(suppliers)
        session.commit()

        # Crear productos de ejemplo
        products = [
            Product(
                name="Televisor LED 55'",
                price=799.99,
                stock=10
            ),
            Product(
                name="Refrigeradora No Frost",
                price=999.99,
                stock=5
            ),
            Product(
                name="Laptop Core i5",
                price=699.99,
                stock=15
            ),
            Product(
                name="Smartphone Galaxy",
                price=499.99,
                stock=20
            ),
            Product(
                name="Tablet 10'",
                price=299.99,
                stock=12
            )
        ]
        session.add_all(products)
        session.commit()

        # Crear ventas de ejemplo
        # Generamos ventas para los últimos 30 días
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        for _ in range(20):  # Generamos 20 ventas de ejemplo
            sale_date = start_date + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            # Seleccionar un cliente aleatorio
            customer = random.choice(customers)

            # Crear la venta
            sale = Sale(
                date=sale_date,
                customer_id=customer.id,
                total_amount=0,  # Se actualizará después
                payment_method=random.choice(['efectivo', 'tarjeta', 'transferencia']),
                status='completed'
            )
            session.add(sale)
            session.flush()  # Para obtener el ID de la venta

            # Agregar entre 1 y 3 productos a la venta
            total_amount = 0
            for _ in range(random.randint(1, 3)):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                
                # Verificar stock disponible
                if product.stock >= quantity:
                    subtotal = product.price * quantity
                    
                    sale_detail = SaleItem(
                        sale_id=sale.id,
                        product_id=product.id,
                        quantity=quantity,
                        unit_price=product.price,
                        subtotal=subtotal
                    )
                    
                    # Actualizar el stock
                    product.stock -= quantity
                    total_amount += subtotal
                    
                    session.add(sale_detail)

            # Actualizar el total de la venta
            sale.total_amount = total_amount

        session.commit()
        print("Datos de ejemplo cargados exitosamente")
        
    except Exception as e:
        session.rollback()
        print(f"Error al cargar datos de ejemplo: {str(e)}")
        raise e 