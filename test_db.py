from sqlalchemy.orm import sessionmaker
from database.connection import engine
from models import User, Supplier, Category, Subcategory, Product, Customer, Sale, SaleItem, Stock, InventoryHistory
import random
from datetime import datetime, timedelta

db_session = sessionmaker(bind=engine)
session = db_session()

# Crear proveedores
suppliers = [
    Supplier(name="Proveedor A", phone="123456789", email="proveedorA@example.com", address="Calle 123, Ciudad", description="Proveedor de electrónica"),
    Supplier(name="Proveedor B", phone="987654321", email="proveedorB@example.com", address="Avenida 456, Ciudad", description="Proveedor de muebles"),
    Supplier(name="Proveedor C", phone="555123456", email="proveedorC@example.com", address="Calle 789, Ciudad", description="Proveedor de alimentos"),
    Supplier(name="Proveedor D", phone="444987654", email="proveedorD@example.com", address="Boulevard 101, Ciudad", description="Proveedor de ropa"),
    Supplier(name="Proveedor E", phone="333666999", email="proveedorE@example.com", address="Callejón 202, Ciudad", description="Proveedor de herramientas"),
    Supplier(name="Proveedor F", phone="222111444", email="proveedorF@example.com", address="Plaza 303, Ciudad", description="Proveedor de libros"),
    Supplier(name="Proveedor G", phone="111222333", email="proveedorG@example.com", address="Avenida 505, Ciudad", description="Proveedor de juguetes"),
    Supplier(name="Proveedor H", phone="999888777", email="proveedorH@example.com", address="Calle 606, Ciudad", description="Proveedor de electrónica"),
    Supplier(name="Proveedor I", phone="444555666", email="proveedorI@example.com", address="Boulevard 707, Ciudad", description="Proveedor de muebles"),
    Supplier(name="Proveedor J", phone="333444555", email="proveedorJ@example.com", address="Callejón 808, Ciudad", description="Proveedor de alimentos"),
]
session.add_all(suppliers)
session.commit()

# Crear categorías y subcategorías
categories = [
    Category(name="Electrónica"),
    Category(name="Ropa"),
    Category(name="Muebles"),
    Category(name="Alimentos"),
    Category(name="Juguetes"),
    Category(name="Libros"),
    Category(name="Herramientas"),
]
session.add_all(categories)
session.commit()

subcategories = [
    Subcategory(name="Celulares", description="Móviles y accesorios", category_id=categories[0].id),
    Subcategory(name="Laptops", description="Portátiles y accesorios", category_id=categories[0].id),
    Subcategory(name="Televisores", description="Smart TVs y accesorios", category_id=categories[0].id),
    Subcategory(name="Camisetas", description="Ropa casual", category_id=categories[1].id),
    Subcategory(name="Pantalones", description="Ropa casual", category_id=categories[1].id),
    Subcategory(name="Muebles de oficina", description="Muebles para oficina", category_id=categories[2].id),
    Subcategory(name="Muebles de cocina", description="Muebles para cocina", category_id=categories[2].id),
    Subcategory(name="Muebles de sala", description="Muebles para sala", category_id=categories[2].id),
    Subcategory(name="Muebles de dormitorio", description="Muebles para dormitorio", category_id=categories[2].id),
    Subcategory(name="Frutas y verduras", description="Alimentos frescos", category_id=categories[3].id),
]
session.add_all(subcategories)
session.commit()

# Crear productos
products = [
    Product(name="iPhone 13", description="Smartphone de última generación de Apple", price=999.99, stock=10, supplier_id=suppliers[0].id, subcategory_id=subcategories[0].id, category_id=categories[0].id, barcode="1234567890123", code="IPHN13"),
    Product(name="Samsung Galaxy S21", description="Smartphone Android de gama alta", price=899.99, stock=15, supplier_id=suppliers[0].id, subcategory_id=subcategories[0].id, category_id=categories[0].id, barcode="2345678901234", code="SAMS21"),
    Product(name="MacBook Pro", description="Laptop profesional de Apple", price=1999.99, stock=5, supplier_id=suppliers[0].id, subcategory_id=subcategories[1].id, category_id=categories[0].id, barcode="3456789012345", code="MACBP"),
    Product(name="Dell XPS 13", description="Laptop ultradelgada de alto rendimiento", price=1499.99, stock=8, supplier_id=suppliers[7].id, subcategory_id=subcategories[1].id, category_id=categories[0].id, barcode="4567890123456", code="DXP13"),
    Product(name="Camiseta Nike", description="Camiseta deportiva de algodón", price=29.99, stock=50, supplier_id=suppliers[3].id, subcategory_id=subcategories[3].id, category_id=categories[1].id, barcode="5678901234567", code="NIKCM"),
    Product(name="Pantalón Adidas", description="Pantalón deportivo cómodo y ligero", price=49.99, stock=40, supplier_id=suppliers[3].id, subcategory_id=subcategories[4].id, category_id=categories[1].id, barcode="6789012345678", code="ADIPT"),
    Product(name="Mesa de oficina", description="Mesa de trabajo espaciosa y resistente", price=149.99, stock=20, supplier_id=suppliers[1].id, subcategory_id=subcategories[5].id, category_id=categories[2].id, barcode="7890123456789", code="MOFCN"),
    Product(name="Silla de oficina", description="Silla ergonómica con soporte lumbar", price=99.99, stock=30, supplier_id=suppliers[1].id, subcategory_id=subcategories[5].id, category_id=categories[2].id, barcode="8901234567890", code="SOFCN"),
    Product(name="Sofá de sala", description="Sofá de 3 plazas con tapizado de alta calidad", price=499.99, stock=15, supplier_id=suppliers[1].id, subcategory_id=subcategories[7].id, category_id=categories[2].id, barcode="9012345678901", code="SFSAL"),
    Product(name="Cama King", description="Cama de matrimonio amplia y confortable", price=699.99, stock=10, supplier_id=suppliers[8].id, subcategory_id=subcategories[8].id, category_id=categories[2].id, barcode="0123456789012", code="CMKNG"),
]   
session.add_all(products)
session.commit()

# Crear clientes
customers = [
    Customer(name="Juan Perez", email="juan@example.com", address="Calle Principal 123", phone="555-1234"),
    Customer(name="Maria Gonzalez", email="maria@example.com", address="Avenida Central 456", phone="555-2345"),
    Customer(name="Pedro Ramirez", email="pedro@example.com", address="Boulevard Norte 789", phone="555-3456"),
    Customer(name="Ana Torres", email="ana@example.com", address="Calle 10 #45", phone="555-4567"),
    Customer(name="Luis Fernandez", email="luis@example.com", address="Avenida Sur 12", phone="555-5678"),
    Customer(name="Laura Gomez", email="laura@example.com", address="Plaza Principal 78", phone="555-6789"),
    Customer(name="Carlos Lopez", email="carlos@example.com", address="Calle Roble 90", phone="555-7890"),
    Customer(name="Sofia Herrera", email="sofia@example.com", address="Avenida Pinos 121", phone="555-8901"),
    Customer(name="Miguel Torres", email="miguel@example.com", address="Boulevard Este 33", phone="555-9012"),
    Customer(name="Jorge Martinez", email="jorge@example.com", address="Calle Girasol 55", phone="555-0123"),
    Customer(name="Camila Rodriguez", email="camila@example.com", address="Avenida Palmas 77", phone="555-1234"),
    Customer(name="Diego Silva", email="diego@example.com", address="Plaza Central 99", phone="555-2345"),
    Customer(name="Valeria Castro", email="valeria@example.com", address="Calle Nogal 11", phone="555-3456"),
    Customer(name="Sebastian Vargas", email="sebastian@example.com", address="Avenida Arce 22", phone="555-4567"),
    Customer(name="Isabella Silva", email="isabella@example.com", address="Boulevard Oeste 44", phone="555-5678"),
]
session.add_all(customers)
session.commit()

# Fechas para las ventas (desde hace un año hasta hoy)
now = datetime.now()
dates = []
for i in range(15):
    # Generar fechas distribuidas a lo largo del año
    days_ago = random.randint(1, 365)
    sale_date = now - timedelta(days=days_ago)
    dates.append(sale_date)

# Ordenar fechas (más recientes primero)
dates.sort(reverse=True)

# Crear ventas
sales = [
    Sale(customer_id=customers[0].id, total_amount=1029.98, payment_method="tarjeta", status="completed", date=dates[0]),
    Sale(customer_id=customers[1].id, total_amount=1999.99, payment_method="efectivo", status="completed", date=dates[1]),
    Sale(customer_id=customers[2].id, total_amount=579.97, payment_method="tarjeta", status="completed", date=dates[2]),
    Sale(customer_id=customers[3].id, total_amount=999.99, payment_method="efectivo", status="completed", date=dates[3]),
    Sale(customer_id=customers[4].id, total_amount=149.99, payment_method="tarjeta", status="completed", date=dates[4]),
    Sale(customer_id=customers[5].id, total_amount=399.96, payment_method="efectivo", status="completed", date=dates[5]),
    Sale(customer_id=customers[0].id, total_amount=699.99, payment_method="tarjeta", status="completed", date=dates[6]),
    Sale(customer_id=customers[2].id, total_amount=899.99, payment_method="efectivo", status="completed", date=dates[7]),
    Sale(customer_id=customers[4].id, total_amount=99.99, payment_method="tarjeta", status="completed", date=dates[8]),
    Sale(customer_id=customers[6].id, total_amount=129.97, payment_method="efectivo", status="completed", date=dates[9]),
]
session.add_all(sales)
session.commit()

# Agregar items a las ventas
sale_items = [
    # Primera venta
    SaleItem(sale_id=sales[0].id, product_id=products[0].id, quantity=1, unit_price=999.99, subtotal=999.99),
    SaleItem(sale_id=sales[0].id, product_id=products[4].id, quantity=1, unit_price=29.99, subtotal=29.99),
    
    # Segunda venta
    SaleItem(sale_id=sales[1].id, product_id=products[2].id, quantity=1, unit_price=1999.99, subtotal=1999.99),
    
    # Tercera venta
    SaleItem(sale_id=sales[2].id, product_id=products[8].id, quantity=1, unit_price=499.99, subtotal=499.99),
    SaleItem(sale_id=sales[2].id, product_id=products[4].id, quantity=2, unit_price=29.99, subtotal=59.98),
    SaleItem(sale_id=sales[2].id, product_id=products[5].id, quantity=0.4, unit_price=49.99, subtotal=20.00),
    
    # Cuarta venta
    SaleItem(sale_id=sales[3].id, product_id=products[0].id, quantity=1, unit_price=999.99, subtotal=999.99),
    
    # Quinta venta
    SaleItem(sale_id=sales[4].id, product_id=products[6].id, quantity=1, unit_price=149.99, subtotal=149.99),
    
    # Sexta venta
    SaleItem(sale_id=sales[5].id, product_id=products[7].id, quantity=4, unit_price=99.99, subtotal=399.96),
    
    # Séptima venta
    SaleItem(sale_id=sales[6].id, product_id=products[9].id, quantity=1, unit_price=699.99, subtotal=699.99),
    
    # Octava venta
    SaleItem(sale_id=sales[7].id, product_id=products[1].id, quantity=1, unit_price=899.99, subtotal=899.99),
    
    # Novena venta
    SaleItem(sale_id=sales[8].id, product_id=products[7].id, quantity=1, unit_price=99.99, subtotal=99.99),
    
    # Décima venta
    SaleItem(sale_id=sales[9].id, product_id=products[4].id, quantity=3, unit_price=29.99, subtotal=89.97),
    SaleItem(sale_id=sales[9].id, product_id=products[5].id, quantity=0.8, unit_price=49.99, subtotal=40.00),
]
session.add_all(sale_items)
session.commit()

# Crear algunos registros de historial de inventario
inventory_history = []
today = datetime.now()

for i in range(20):
    # Seleccionar un producto aleatorio
    product = random.choice(products)
    
    # Determinar el tipo de cambio
    change_type = random.choice(["entrada", "salida", "ajuste"])
    
    # Generar cantidades aleatorias
    if change_type == "entrada":
        change_amount = random.randint(5, 30)
        previous_stock = product.stock - change_amount
        new_stock = product.stock
    elif change_type == "salida":
        change_amount = -random.randint(1, 5)
        previous_stock = product.stock - change_amount
        new_stock = product.stock
    else:  # ajuste
        change_amount = random.randint(-5, 5)
        previous_stock = product.stock - change_amount
        new_stock = product.stock
    
    # Generar fecha (últimos 30 días)
    days_ago = random.randint(0, 30)
    history_date = today - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
    
    # Crear el registro de historial
    entry = InventoryHistory(
        product_id=product.id,
        change_type=change_type,
        change_amount=change_amount,
        previous_stock=previous_stock,
        new_stock=new_stock,
        notes=f"Cambio de inventario automático ({change_type})",
        date=history_date
    )
    
    inventory_history.append(entry)

session.add_all(inventory_history)
session.commit()

print("Base de datos de prueba creada exitosamente.")