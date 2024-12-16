from typing import List, Optional
from sqlalchemy.orm import Session
from models.Product import Product

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_products(self) -> List[Product]:
        """Obtiene todos los productos"""
        return self.db.query(Product).all()

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Obtiene un producto por su ID"""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def create_product(self, product_data: dict) -> Product:
        """Crea un nuevo producto"""
        product = Product(**product_data)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update_product(self, product_id: int, product_data: dict) -> Optional[Product]:
        """Actualiza un producto existente"""
        product = self.get_product_by_id(product_id)
        if product:
            for key, value in product_data.items():
                setattr(product, key, value)
            self.db.commit()
            self.db.refresh(product)
        return product

    def delete_product(self, product_id: int) -> bool:
        """Elimina un producto"""
        product = self.get_product_by_id(product_id)
        if product:
            self.db.delete(product)
            self.db.commit()
            return True
        return False

    def delete_all_products(self) -> bool:
        """Elimina todos los productos"""
        try:
            self.db.query(Product).delete()
            self.db.commit()
            return True
        except:
            return False