from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.connection import Base

class Subcategory(Base):
    __tablename__ = 'subcategory'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    category_id = Column(Integer, ForeignKey('category.id', ondelete="CASCADE"), nullable=False)
    
    category = relationship('Category', back_populates='subcategories')
    products = relationship('Product', back_populates='subcategory')
    
    def __repr__(self):
        return f"Subcategoría({self.name}, category_id={self.category_id}, id={self.id})"