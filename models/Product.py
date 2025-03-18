from sqlalchemy import Column, Integer, String, Float, CheckConstraint, Boolean, Date, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class Product(Base):
    """
    Modelo que representa un producto en el sistema.
    
    Atributos:
        id (int): Identificador único del producto
        name (str): Nombre del producto
        description (str): Descripción del producto
        category (str): Categoría del producto
        price (float): Precio del producto
        stock (int): Cantidad disponible en inventario
        barcode (str): Código de barras del producto
        supplier (str): Proveedor del producto
        code (str): Código interno del producto
    """
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    barcode = Column(String, nullable=True)
    supplier = Column(String, nullable=True)
    code = Column(String, nullable=True)
    
    # Relaciones
    inventory_history = relationship('InventoryHistory', back_populates='product', cascade="all, delete-orphan", lazy="dynamic")
    
    __table_args__ = (
        CheckConstraint('price > 0', name='check_price_positive'),
        CheckConstraint('stock >= 0', name='check_stock_non_negative'),
    )
    
    def __repr__(self):
        return f"Producto({self.name}, stock={self.stock}, price={self.price}, id={self.id})"
        
    @property
    def is_low_stock(self):
        """Verifica si el producto tiene stock bajo"""
        return self.stock <= 5  # Valor predeterminado para stock mínimo