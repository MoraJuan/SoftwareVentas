"""
Servicio para la gestión de proveedores
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from models.Supplier import Supplier

class SupplierService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_suppliers(self) -> List[Supplier]:
        """Obtiene todos los proveedores"""
        return self.db.query(Supplier).all()

    def get_supplier_by_id(self, supplier_id: int) -> Optional[Supplier]:
        """Obtiene un proveedor por su ID"""
        return self.db.query(Supplier).filter(Supplier.id == supplier_id).first()

    def create_supplier(self, supplier_data: dict) -> Supplier:
        """Crea un nuevo proveedor"""
        supplier = Supplier(**supplier_data)
        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    def update_supplier(self, supplier_id: int, supplier_data: dict) -> Optional[Supplier]:
        """Actualiza un proveedor existente"""
        supplier = self.get_supplier_by_id(supplier_id)
        if supplier:
            for key, value in supplier_data.items():
                setattr(supplier, key, value)
            self.db.commit()
            self.db.refresh(supplier)
        return supplier

    def delete_supplier(self, supplier_id: int) -> bool:
        """Elimina un proveedor"""
        supplier = self.get_supplier_by_id(supplier_id)
        if supplier:
            self.db.delete(supplier)
            self.db.commit()
            return True
        return False