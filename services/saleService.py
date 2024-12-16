from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models.Sale import Sale
from models.SaleItem import SaleItem
from models.Product import Product
from .productService import ProductService

class SaleService:
    def __init__(self, db: Session):
        self.db = db
        self.product_service = ProductService(db)

    def create_sale(self, sale_data: dict) -> Sale:
        """Crea una nueva venta y actualiza el inventario"""
        try:
            # Crear la venta
            sale = Sale(
                customer_id=sale_data['customer_id'],
                employee_id=sale_data['employee_id'],
                payment_method=sale_data['payment_method'],
                total_amount=0,
                status='pending'
            )
            self.db.add(sale)
            self.db.flush()  # Obtener el ID de la venta

            total_amount = 0
            # Procesar cada item de la venta
            for item_data in sale_data['items']:
                product = self.product_service.get_product_by_id(item_data['product_id'])
                if not product or product.stock < item_data['quantity']:
                    raise ValueError(f"Stock insuficiente para el producto {product.name}")

                subtotal = product.price * item_data['quantity']
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=product.id,
                    quantity=item_data['quantity'],
                    unit_price=product.price,
                    subtotal=subtotal
                )
                
                # Actualizar stock
                product.stock -= item_data['quantity']
                total_amount += subtotal
                
                self.db.add(sale_item)

            sale.total_amount = total_amount
            sale.status = 'completed'
            self.db.commit()
            return sale

        except Exception as e:
            self.db.rollback()
            raise e

    def get_sale_by_id(self, sale_id: int) -> Optional[Sale]:
        """Obtiene una venta por su ID"""
        return self.db.query(Sale).filter(Sale.id == sale_id).first()

    def get_sales_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Sale]:
        """Obtiene las ventas en un rango de fechas"""
        return self.db.query(Sale).filter(
            Sale.date >= start_date,
            Sale.date <= end_date
        ).all()

    def get_total_sales_amount(self, start_date: datetime, end_date: datetime) -> float:
        """Calcula el total de ventas en un rango de fechas"""
        sales = self.get_sales_by_date_range(start_date, end_date)
        return sum(sale.total_amount for sale in sales)

    def cancel_sale(self, sale_id: int) -> bool:
        """Cancela una venta y restaura el inventario"""
        try:
            sale = self.get_sale_by_id(sale_id)
            if not sale or sale.status != 'completed':
                return False

            # Restaurar stock
            for item in sale.items:
                product = item.product
                product.stock += item.quantity

            sale.status = 'cancelled'
            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            raise e