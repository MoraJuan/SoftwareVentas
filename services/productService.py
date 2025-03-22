from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import logging
from sqlalchemy.orm import Session
from models.Product import Product
from services.inventoryHistoryService import InventoryHistoryService

class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.inventory_history_service = InventoryHistoryService(db)

    def get_all_products(self) -> List[Product]:
        """Obtiene todos los productos"""
        return self.db.query(Product).all()

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Obtiene un producto por su ID"""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_product_by_code(self, code: str) -> Optional[Product]:
        """Obtiene un producto por su código"""
        return self.db.query(Product).filter(Product.code == code).first()

    def get_products_by_name(self, name: str) -> List[Product]:
        """Obtiene productos por su nombre"""
        return self.db.query(Product).filter(Product.name.ilike(f"%{name}%")).all()

    def get_products_by_category(self, category_id: int) -> List[Product]:
        """Obtiene productos por su categoría"""
        return self.db.query(Product).filter(Product.category_id == category_id).all()

    def get_products_by_price_range(self, min_price: float, max_price: float) -> List[Product]:
        """Obtiene productos por rango de precio"""
        return self.db.query(Product).filter(Product.price >= min_price, Product.price <= max_price).all()

    def search_products(self, search_term: str) -> List[Product]:
        """Busca productos por nombre, descripción o código"""
        if not search_term:
            return self.get_all_products()
        
        return self.db.query(Product).filter(
            (Product.name.ilike(f"%{search_term}%")) |
            (Product.description.ilike(f"%{search_term}%")) |
            (Product.code.ilike(f"%{search_term}%"))
        ).all()

    def get_category_name_by_id(self, category_id: str) -> Optional[str]:
        """Obtiene el nombre de una categoría por su ID"""
        try:
            if not category_id or not str(category_id).isdigit() or category_id == "0":
                return None
                
            # Importar CategoryService aquí para evitar importación circular
            from services.categoryService import CategoryService
            category_service = CategoryService(self.db)
            
            category = category_service.get_category_by_id(int(category_id))
            return category.name if category else None
        except Exception as e:
            logging.error(f"Error al obtener nombre de categoría: {str(e)}")
            return None
        
    def get_subcategory_name_by_id(self, subcategory_id: str) -> Optional[str]:
        """Obtiene el nombre de una subcategoría por su ID"""
        try:
            if not subcategory_id or not str(subcategory_id).isdigit() or subcategory_id == "0":
                return None
                
            # Importar CategoryService aquí para evitar importación circular
            from services.subcategoryService import SubcategoryService
            subcategory_service = SubcategoryService(self.db)
            
            subcategory = subcategory_service.get_subcategory_by_id(int(subcategory_id))
            return subcategory.name if subcategory else None
        except Exception as e:
            logging.error(f"Error al obtener nombre de subcategoría: {str(e)}")
            return None
            
    def create_product(self, product_data: dict) -> Product:
        """Crea un nuevo producto"""
        try:
            # Si la categoría es un ID, convertirla al nombre
            if "category" in product_data and product_data["category"] and str(product_data["category"]).isdigit() and product_data["category"] != "0":
                category_name = self.get_category_name_by_id(product_data["category"])
                if category_name:
                    product_data["category"] = category_name
            
            if "subcategory" in product_data and product_data["subcategory"] and str(product_data["subcategory"]).isdigit() and product_data["subcategory"] != "0":
                subcategory_name = self.get_subcategory_name_by_id(product_data["subcategory"])
                if subcategory_name:
                    product_data["subcategory"] = subcategory_name

            product = Product(**product_data)
            self.db.add(product)
            self.db.commit()
            self.db.refresh(product)
            
            # Registrar en el historial como "creación"
            if product.stock > 0:
                self.inventory_history_service.record_inventory_change(
                    product_id=product.id,
                    change_amount=product.stock,
                    change_type="creación",
                    change_reason="Creación inicial del producto"
                )
                
            return product
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error al crear producto: {str(e)}")
            raise

    def update_product(self, product_id: int, product_data: dict) -> Optional[Product]:
        """Actualiza un producto existente"""
        try:
            product = self.get_product_by_id(product_id)
            if product:
                # Verificar si hay cambio en el stock
                old_stock = product.stock
                
                # Si la categoría es un ID, convertirla al nombre
                if "category" in product_data and product_data["category"] and str(product_data["category"]).isdigit() and product_data["category"] != "0":
                    category_name = self.get_category_name_by_id(product_data["category"])
                    if category_name:
                        product_data["category"] = category_name
                
                if "subcategory" in product_data and product_data["subcategory"] and str(product_data["subcategory"]).isdigit() and product_data["subcategory"] != "0":
                    subcategory_name = self.get_subcategory_name_by_id(product_data["subcategory"])
                    if subcategory_name:
                        product_data["subcategory"] = subcategory_name
                
                # Actualizar atributos
                for key, value in product_data.items():
                    setattr(product, key, value)
                
                # Guardar cambios
                self.db.commit()
                self.db.refresh(product)
                
                # Registrar cambio de stock si hubo
                if 'stock' in product_data and old_stock != product.stock:
                    change_amount = product.stock - old_stock
                    self.inventory_history_service.record_inventory_change(
                        product_id=product.id,
                        change_amount=change_amount,
                        change_type="ajuste",
                        change_reason="Actualización manual del producto"
                    )
                
            return product
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error al actualizar producto: {str(e)}")
            raise

    def delete_product(self, product_id: int) -> bool:
        """Elimina un producto"""
        try:
            product = self.get_product_by_id(product_id)
            if product:
                self.db.delete(product)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error al eliminar producto: {str(e)}")
            raise

    def delete_all_products(self) -> bool:
        """Elimina todos los productos"""
        try:
            self.db.query(Product).delete()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error al eliminar todos los productos: {str(e)}")
            raise
            
    def adjust_stock(self, product_id: int, new_stock: int, reason: str = None, user_id: int = None) -> Product:
        """
        Ajusta el stock de un producto directamente a un nuevo valor
        
        Args:
            product_id: ID del producto
            new_stock: Nuevo valor de stock
            reason: Razón del ajuste
            user_id: ID del usuario que realiza el ajuste
            
        Returns:
            El producto actualizado
        """
        try:
            product = self.get_product_by_id(product_id)
            if not product:
                raise ValueError(f"Producto con ID {product_id} no encontrado")
                
            # Calcular el cambio
            change_amount = new_stock - product.stock
            
            # Registrar el cambio en el historial
            self.inventory_history_service.record_inventory_change(
                product_id=product_id,
                change_amount=change_amount,
                change_type="ajuste",
                change_reason=reason,
                user_id=user_id
            )
            
            return product
        except Exception as e:
            logging.error(f"Error al ajustar stock: {str(e)}")
            raise
            
    def add_stock(self, product_id: int, amount: int, reason: str = "Reposición", user_id: int = None) -> Product:
        """
        Añade stock a un producto
        
        Args:
            product_id: ID del producto
            amount: Cantidad a añadir (debe ser positiva)
            reason: Razón de la adición
            user_id: ID del usuario que realiza la adición
            
        Returns:
            El producto actualizado
        """
        if amount <= 0:
            raise ValueError("La cantidad a añadir debe ser positiva")
            
        try:
            # Registrar el cambio en el historial (esto también actualiza el stock)
            self.inventory_history_service.record_inventory_change(
                product_id=product_id,
                change_amount=amount,
                change_type="entrada",
                change_reason=reason,
                user_id=user_id
            )
            
            # Obtener el producto actualizado
            return self.get_product_by_id(product_id)
        except Exception as e:
            logging.error(f"Error al añadir stock: {str(e)}")
            raise
            
    def remove_stock(self, product_id: int, amount: int, reason: str = "Salida", user_id: int = None) -> Product:
        """
        Reduce el stock de un producto
        
        Args:
            product_id: ID del producto
            amount: Cantidad a reducir (debe ser positiva)
            reason: Razón de la reducción
            user_id: ID del usuario que realiza la reducción
            
        Returns:
            El producto actualizado
        """
        if amount <= 0:
            raise ValueError("La cantidad a reducir debe ser positiva")
            
        try:
            product = self.get_product_by_id(product_id)
            if not product:
                raise ValueError(f"Producto con ID {product_id} no encontrado")
                
            # Verificar si hay suficiente stock
            if product.stock < amount:
                raise ValueError(f"Stock insuficiente. Stock actual: {product.stock}, Cantidad a reducir: {amount}")
                
            # Registrar el cambio en el historial (esto también actualiza el stock)
            self.inventory_history_service.record_inventory_change(
                product_id=product_id,
                change_amount=-amount,  # Negativo para reducción
                change_type="salida",
                change_reason=reason,
                user_id=user_id
            )
            
            # Obtener el producto actualizado
            return self.get_product_by_id(product_id)
        except Exception as e:
            logging.error(f"Error al reducir stock: {str(e)}")
            raise
            
    def get_low_stock_products(self) -> List[Product]:
        """Obtiene los productos con stock bajo (por debajo del mínimo)"""
        # Usar un valor fijo para el stock mínimo ya que no existe la columna min_stock
        min_stock_threshold = 5
        return self.db.query(Product).filter(
            Product.stock <= min_stock_threshold
        ).all()
        
    def get_expiring_products(self, days_threshold: int = 30) -> List[Product]:
        """
        Obtiene los productos perecederos que están próximos a caducar
        
        Args:
            days_threshold: Número de días para considerar un producto próximo a caducar
            
        Returns:
            Lista de productos próximos a caducar
        """
        # La tabla actual no tiene soporte para productos perecederos
        return []
    
    def get_expired_products(self) -> List[Product]:
        """Obtiene los productos perecederos que ya han caducado"""
        # La tabla actual no tiene soporte para productos perecederos
        return []
        
    def update_expiry_date(self, product_id: int, new_expiry_date: date) -> Product:
        """
        Actualiza la fecha de caducidad de un producto perecedero
        
        Args:
            product_id: ID del producto
            new_expiry_date: Nueva fecha de caducidad
            
        Returns:
            El producto actualizado
        """
        try:
            product = self.get_product_by_id(product_id)
            if not product:
                raise ValueError(f"Producto con ID {product_id} no encontrado")
                
            # Verificar si el producto es perecedero
            if not product.is_perishable:
                raise ValueError(f"El producto con ID {product_id} no es perecedero")
                
            # Actualizar fecha de caducidad
            product.expiry_date = new_expiry_date
            self.db.commit()
            self.db.refresh(product)
            
            return product
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error al actualizar fecha de caducidad: {str(e)}")
            raise
            
    def get_inventory_alerts(self) -> Dict[str, List[Product]]:
        """
        Obtiene todas las alertas de inventario (stock bajo, productos por caducar, productos caducados)
        
        Returns:
            Diccionario con las alertas
        """
        try:
            return {
                "low_stock": self.get_low_stock_products(),
                "expiring_soon": [],  # No hay soporte para productos perecederos
                "expired": []  # No hay soporte para productos perecederos
            }
        except Exception as e:
            logging.error(f"Error al obtener alertas de inventario: {str(e)}")
            return {
                "low_stock": [],
                "expiring_soon": [],
                "expired": []
            }
        
    def get_product_history(self, product_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene el historial completo de un producto
        
        Args:
            product_id: ID del producto
            
        Returns:
            Lista de eventos en el historial del producto
        """
        try:
            # Obtener el producto
            product = self.get_product_by_id(product_id)
            if not product:
                raise ValueError(f"Producto con ID {product_id} no encontrado")
                
            # Obtener historial de inventario
            inventory_history = self.inventory_history_service.get_history_by_product(product_id)
            
            # Formatear historial
            history = []
            for record in inventory_history:
                history.append({
                    "date": record.date,
                    "type": record.change_type,
                    "previous_stock": record.previous_stock,
                    "new_stock": record.new_stock,
                    "change_amount": record.change_amount,
                    "reason": record.change_reason
                })
                
            return history
        except Exception as e:
            logging.error(f"Error al obtener historial del producto: {str(e)}")
            raise

    def update_all_numeric_categories(self) -> int:
        """
        Actualiza todas las categorías numéricas en los productos existentes, 
        convirtiendo los IDs de categoría a nombres de categoría.
        
        Returns:
            Número de productos actualizados
        """
        try:
            # Obtener todos los productos
            all_products = self.get_all_products()
            count_updated = 0
            
            # Importar CategoryService aquí para evitar importación circular
            from services.categoryService import CategoryService
            category_service = CategoryService(self.db)
            
            for product in all_products:
                if product.category and str(product.category).isdigit():
                    # Encontrar la categoría correspondiente
                    category = category_service.get_category_by_id(int(product.category))
                    if category:
                        # Actualizar el producto con el nombre de la categoría
                        product.category = category.name
                        count_updated += 1
            
            # Guardar cambios
            if count_updated > 0:
                self.db.commit()
                
            return count_updated
            
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error al actualizar categorías numéricas: {str(e)}")
            return 0