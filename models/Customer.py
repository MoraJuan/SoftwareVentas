from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database.connection import Base
from datetime import datetime

class Customer(Base):
    """
    Modelo que representa un cliente en el sistema.
    
    Atributos:
        id (int): Identificador único del cliente
        name (str): Nombre del cliente
        email (str): Correo electrónico del cliente (único)
        created_at (datetime): Fecha de registro del cliente
        
    Relaciones:
        - commercial_invoice: Relación con facturas comerciales
        - sales: Relación con las ventas realizadas
        
    Validaciones:
        - El email debe ser único
        - El nombre no puede estar vacío
    """
    __tablename__ = 'customer'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    commercial_invoice = relationship('CommercialInvoice', back_populates='customer')
    sales = relationship('Sale', back_populates='customer', cascade="all, delete-orphan")

    def __repr__(self):
        return f"Cliente(nombre={self.name})"