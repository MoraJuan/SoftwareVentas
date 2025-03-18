import logging
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.InventoryHistory import InventoryHistory
from models.Product import Product

class InventoryHistoryService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_history_by_product(self, product_id: int) -> List[InventoryHistory]:
        """Obtiene el historial de cambios de inventario para un producto específico"""
        try:
            return self.db.query(InventoryHistory).filter(
                InventoryHistory.product_id == product_id
            ).order_by(InventoryHistory.date.desc()).all()
        except Exception as e:
            logging.error(f"Error al obtener historial por producto: {str(e)}")
            return []
    
    def get_recent_history(self, limit: int = 50) -> List[InventoryHistory]:
        """Obtiene los cambios de inventario más recientes"""
        try:
            return self.db.query(InventoryHistory).order_by(
                InventoryHistory.date.desc()
            ).limit(limit).all()
        except Exception as e:
            logging.error(f"Error al obtener historial reciente: {str(e)}")
            return []
    
    def get_history_by_date_range(self, start_date: datetime, end_date: datetime) -> List[InventoryHistory]:
        """Obtiene el historial de cambios de inventario en un rango de fechas"""
        try:
            return self.db.query(InventoryHistory).filter(
                InventoryHistory.date >= start_date,
                InventoryHistory.date <= end_date
            ).order_by(InventoryHistory.date.desc()).all()
        except Exception as e:
            logging.error(f"Error al obtener historial por rango de fechas: {str(e)}")
            return []
    
    def get_history_by_type(self, change_type: str) -> List[InventoryHistory]:
        """Obtiene el historial de cambios de inventario por tipo de cambio"""
        try:
            return self.db.query(InventoryHistory).filter(
                InventoryHistory.change_type == change_type
            ).order_by(InventoryHistory.date.desc()).all()
        except Exception as e:
            logging.error(f"Error al obtener historial por tipo: {str(e)}")
            return []
    
    def record_inventory_change(self, product_id: int, change_amount: int, 
                               change_type: str, change_reason: str = None, 
                               user_id: int = None) -> InventoryHistory:
        """
        Registra un cambio en el inventario y actualiza el stock del producto
        
        Args:
            product_id: ID del producto
            change_amount: Cantidad de cambio (positivo para incrementos, negativo para decrementos)
            change_type: Tipo de cambio (venta, compra, ajuste, etc.)
            change_reason: Razón del cambio
            user_id: ID del usuario que realizó el cambio
            
        Returns:
            El registro de historial creado
        """
        try:
            # Obtener el producto
            product = self.db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise ValueError(f"Producto con ID {product_id} no encontrado")
            
            # Guardar el stock anterior
            previous_stock = product.stock
            
            # Actualizar el stock
            product.stock += change_amount
            
            # Crear registro de historial
            history_record = InventoryHistory(
                product_id=product_id,
                previous_stock=previous_stock,
                new_stock=product.stock,
                change_amount=change_amount,
                change_type=change_type,
                change_reason=change_reason,
                user_id=user_id
            )
            
            # Guardar cambios
            self.db.add(history_record)
            self.db.commit()
            self.db.refresh(history_record)
            
            return history_record
            
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error al registrar cambio de inventario: {str(e)}")
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