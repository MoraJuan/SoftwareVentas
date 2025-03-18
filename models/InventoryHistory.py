from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base

class InventoryHistory(Base):
    """
    Modelo que representa el historial de cambios en el inventario.
    
    Atributos:
        id (int): Identificador único del registro
        product_id (int): ID del producto afectado
        previous_stock (int): Cantidad de stock antes del cambio
        new_stock (int): Cantidad de stock después del cambio
        change_amount (int): Cantidad de cambio (positivo para incrementos, negativo para decrementos)
        change_type (str): Tipo de cambio (venta, compra, ajuste, etc.)
        change_reason (str): Razón del cambio
        date (datetime): Fecha y hora del cambio
        user_id (int): ID del usuario que realizó el cambio
    """
    __tablename__ = 'inventory_history'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    previous_stock = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)
    change_amount = Column(Integer, nullable=False)
    change_type = Column(String, nullable=False)
    change_reason = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(Integer, ForeignKey('employees.id', ondelete='SET NULL'), nullable=True)
    
    # Relaciones
    product = relationship('Product', back_populates='inventory_history')
    user = relationship('Employee', back_populates='inventory_changes')
    
    def __repr__(self):
        return f"InventoryHistory(product_id={self.product_id}, change_amount={self.change_amount}, date={self.date})" 