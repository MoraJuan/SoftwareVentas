from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from database.connection import Base
import bcrypt
from datetime import datetime
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"
    MANAGER = "manager"

class User(Base):
    """
    Modelo que representa un usuario en el sistema.
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.EMPLOYEE)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    employee_profile = relationship("Employee", back_populates="user", uselist=False)
    administrator_profile = relationship("Administrator", back_populates="user", uselist=False)
    
    def set_password(self, password: str):
        """Establece el hash de la contraseña usando bcrypt"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verifica si la contraseña es correcta"""
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def update_last_login(self):
        """Actualiza la fecha del último inicio de sesión"""
        self.last_login = datetime.utcnow()