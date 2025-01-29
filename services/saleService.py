import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from models.Sale import Sale
from models.Customer import Customer
from models.SaleItem import SaleItem
from models.Product import Product
from .productService import ProductService



class SaleService:
    def __init__(self, db: Session):
        self.db = db
        self.product_service = ProductService(db)

    def get_all_sales(self) -> List[Product]:
        return self.db.query(Sale).all()

    def create_sale(self, sale_data: dict) -> Sale:
        try:
            # Create sale
            sale = Sale(
                customer_id=int(sale_data['customer_id']),
                employee_id=int(sale_data['employee_id']),
                payment_method=str(sale_data['payment_method']),
                total_amount=float(sale_data['total']),
                status='pending'
            )

            self.db.add(sale)
            self.db.flush()  # Get sale.id

            # Process items
            for item in sale_data['items']:
                # Calculate subtotal
                quantity = int(item['quantity'])
                unit_price = float(item['price'])
                subtotal = quantity * unit_price

                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=int(item['product_id']),
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=subtotal  # Add subtotal
                )
                self.db.add(sale_item)

                # Update product stock
                product = self.product_service.get_product_by_id(
                    item['product_id'])
                if product:
                    product.stock -= quantity

            sale.status = 'completed'
            self.db.commit()
            return sale

        except Exception as e:
            self.db.rollback()
            logging.error(f"Error creating sale: {str(e)}")
            raise

    def get_current_employee_id(self) -> int:
        """Obtiene el ID del empleado actual. Implementa según tu lógica."""
        # Ejemplo: obtener desde almacenamiento del cliente
        # Esto necesita ser adaptado según cómo manejes la sesión del empleado
        employee_id = ...  # Implementa la lógica para obtener el employee_id
        if not employee_id:
            raise ValueError("ID de empleado no encontrado.")
        return employee_id

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

    def get_sales_filtered(self, from_date: Optional[datetime] = None, to_date: Optional[datetime] = None, customer_name: Optional[str] = None) -> List[Sale]:
        """Obtiene las ventas filtradas por rango de fechas y/o coincidencia parcial en el nombre del cliente."""
        try:
            query = self.db.query(Sale).join(Customer)  # Unir explícitamente con Customer

            if from_date and to_date:
                query = query.filter(Sale.date >= from_date, Sale.date <= to_date)

            if customer_name:
                query = query.filter(Customer.name.ilike(f"%{customer_name}%"))  # Búsqueda parcial

            return query.options(joinedload(Sale.customer)).all()

        except Exception as e:
            logging.error(f"Error fetching filtered sales: {str(e)}")
            return []

    def get_sales_between_dates(self, from_date: datetime, to_date: datetime) -> List[Sale]:
        """Obtiene las ventas entre dos fechas con información del cliente"""
        try:
            sales = self.db.query(Sale)\
                .join(Sale.customer)\
                .filter(
                    Sale.date >= from_date,
                    Sale.date <= to_date
            ).all()
            return sales
        except Exception as e:
            logging.error(f"Error fetching sales: {str(e)}")
            return []

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
