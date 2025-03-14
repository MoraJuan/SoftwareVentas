from sqlalchemy import Column, Integer, String, Float, CheckConstraint
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
        
    Validaciones:
        - El precio debe ser mayor a 0
        - El stock debe ser mayor o igual a 0
        - El nombre no puede estar vacío
    """
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    
    __table_args__ = (
        CheckConstraint('price > 0', name='check_price_positive'),
        CheckConstraint('stock >= 0', name='check_stock_non_negative'),
    )
    
    def __repr__(self):
        return f"Producto({self.name}, stock={self.stock}, price={self.price}, id={self.id})"