from typing import List, Optional
from sqlalchemy.orm import Session
from models.Customer import Customer

class CustomerService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_customers(self) -> List[Customer]:
        """Obtiene todos los clientes"""
        return self.db.query(Customer).all()

    def get_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        """Obtiene un cliente por su ID"""
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Obtiene un cliente por su email"""
        return self.db.query(Customer).filter(Customer.email == email).first()

    def create_customer(self, customer_data: dict) -> Customer:
        """Crea un nuevo cliente"""
        customer = Customer(**customer_data)
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def update_customer(self, customer_id: int, customer_data: dict) -> Optional[Customer]:
        """Actualiza un cliente existente"""
        customer = self.get_customer_by_id(customer_id)
        if customer:
            for key, value in customer_data.items():
                setattr(customer, key, value)
            self.db.commit()
            self.db.refresh(customer)
        return customer

    def delete_customer(self, customer_id: int) -> bool:
        """Elimina un cliente"""
        customer = self.get_customer_by_id(customer_id)
        if customer:
            self.db.delete(customer)
            self.db.commit()
            return True
        return False