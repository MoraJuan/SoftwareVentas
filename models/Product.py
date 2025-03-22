from sqlalchemy import Column, Integer, String, Float, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base

class Product(Base):
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey('category.id', ondelete="CASCADE"), nullable=False)
    subcategory_id = Column(Integer, ForeignKey('subcategory.id', ondelete="CASCADE"), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    barcode = Column(String, nullable=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    code = Column(String, nullable=True)
    
    inventory_history = relationship('InventoryHistory', back_populates='product', cascade="all, delete-orphan", lazy="dynamic")
    category = relationship('Category', back_populates='products')
    subcategory = relationship('Subcategory', back_populates='products')  # Corregido
    supplier = relationship('Supplier', back_populates='products')
    
    __table_args__ = (
        CheckConstraint('price > 0', name='check_price_positive'),
        CheckConstraint('stock >= 0', name='check_stock_non_negative'),
    )
    
    def __repr__(self):
        return f"Producto({self.name}, stock={self.stock}, price={self.price}, id={self.id})"
        
    @property
    def is_low_stock(self):
        return self.stock <= 5