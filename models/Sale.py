from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base

class Sale(Base):
    """
    Modelo que representa una venta en el sistema.
    """
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)
    status = Column(String, nullable=False)
    
    # Relaciones
    customer_id = Column(Integer, ForeignKey('customer.id'))
    customer = relationship('Customer', back_populates='sales')
    
    employee_id = Column(Integer, ForeignKey('employees.id'))
    employee = relationship('Employee', back_populates='sales')
    
    items = relationship('SaleItem', back_populates='sale', cascade="all, delete-orphan")
    
    # Validaciones
    __table_args__ = (
        CheckConstraint('total_amount >= 0', name='check_total_amount_positive'),
        CheckConstraint(
            "status IN ('pending', 'completed', 'cancelled')", 
            name='check_valid_status'
        ),
        CheckConstraint(
            "payment_method IN ('efectivo', 'tarjeta', 'transferencia')", 
            name='check_valid_payment_method'
        ),
    )
    
    def __repr__(self):
        return f"Venta(id={self.id}, total=${self.total_amount:.2f})"