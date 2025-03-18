from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database.connection import Base

class Category(Base):
    """
    Modelo que representa una categoría de productos en el sistema.
    
    Atributos:
        id (int): Identificador único de la categoría
        name (str): Nombre de la categoría
        description (str): Descripción de la categoría
        active (bool): Indica si la categoría está activa
    """
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    
    products = relationship('Product', back_populates='category')
    
    def __repr__(self):
        return f"Categoría({self.name}, id={self.id})" 