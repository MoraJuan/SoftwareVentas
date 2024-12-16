from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database.connection import Base

class Administrator(Base):
    """
    Modelo que representa un administrador en el sistema.
    """
    __tablename__ = 'administrators'
    
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    admin_functions = Column(String)
    
    # Relaciones
    user = relationship("User", back_populates="administrator_profile")

    def __repr__(self):
        return f"Administrator(id={self.id})"