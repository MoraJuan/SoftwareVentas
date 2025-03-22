from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database.connection import Base

class Category(Base):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    
    subcategories = relationship('Subcategory', back_populates='category', cascade="all, delete-orphan")
    products = relationship('Product', back_populates='category')  # Relación directa con Product
    
    def __repr__(self):
        return f"Categoría({self.name}, id={self.id})"