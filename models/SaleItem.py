from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base

class SaleItem(Base):
    __tablename__ = 'sale_items'
    
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    
    # Relaciones
    sale_id = Column(Integer, ForeignKey('sales.id'))
    sale = relationship('Sale', back_populates='items')
    
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship('Product')
    
    def __repr__(self):
        return f"Item de Venta(producto_id={self.product_id}, cantidad={self.quantity})"