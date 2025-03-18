from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base

class Expense(Base):
    """
    Modelo que representa un gasto o compra en el sistema.
    """
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)  # 'compra_inventario', 'operativo', 'salarios', etc.
    
    # Relaciones opcionales
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=True)
    supplier = relationship('Supplier')
    
    # Validaciones
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_amount_positive'),
        CheckConstraint(
            "category IN ('compra_inventario', 'operativo', 'salarios', 'servicios', 'otros')", 
            name='check_valid_category'
        ),
    )
    
    def __repr__(self):
        return f"Gasto(id={self.id}, monto=${self.amount:.2f}, fecha={self.date}, categoría={self.category})" 