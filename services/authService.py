from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from models.User import User, UserRole
from models.Employee import Employee
from models.Administrator import Administrator
from jose import JWTError, jwt
from config.settings import (
    SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES,
    EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Autentica un usuario por username/password"""
        user = self.db.query(User).filter(User.username == username).first()
        if user and user.check_password(password):
            user.update_last_login()
            self.db.commit()
            return user
        return None
    
    def create_access_token(self, user: User) -> str:
        """Crea un token JWT para el usuario"""
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": user.username,
            "exp": expire,
            "role": user.role.value,
            "user_id": user.id
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    def register_user(self, user_data: dict) -> User:
        """Registra un nuevo usuario"""
        # Verificar si el usuario ya existe
        existing_user = self.db.query(User).filter(
            (User.username == user_data["username"]) |
            (User.email == user_data["email"])
        ).first()
        
        if existing_user:
            raise ValueError("El usuario o email ya existe")
        
        # Crear usuario
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            role=UserRole[user_data.get("role", "EMPLOYEE").upper()]
        )
        user.set_password(user_data["password"])
        
        self.db.add(user)
        self.db.flush()  # Para obtener el ID del usuario
        
        # Crear perfil según el rol
        if user.role == UserRole.ADMIN:
            admin = Administrator(id=user.id, user=user)
            self.db.add(admin)
        else:
            employee = Employee(id=user.id, user=user)
            self.db.add(employee)
        
        self.db.commit()
        self.db.refresh(user)
        return user