from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base

class Employee(Base):
    """
    Modelo que representa un empleado en el sistema.
    """
    __tablename__ = 'employees'
    
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    employee_functions = Column(String)
    
    # Relaciones
    user = relationship("User", back_populates="employee_profile")
    sales = relationship("Sale", back_populates="employee")

    def __repr__(self):
        return f"Employee(id={self.id})"