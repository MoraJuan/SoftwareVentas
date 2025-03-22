from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.connection import Base

class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String, unique=True, nullable=False)
    address = Column(String, unique=True, nullable=False)
    description = Column(String)
    products = relationship('Product', back_populates='supplier')