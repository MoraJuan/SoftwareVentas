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

    def get_all_sales(self) -> List[Sale]:
        """Obtiene todas las ventas con sus relaciones cargadas"""
        return self.db.query(Sale).options(
            joinedload(Sale.customer),
            joinedload(Sale.items).joinedload(SaleItem.product)
        ).all()

    def create_sale(self, sale_data: dict) -> Sale:
        try:
            # Calcular el total de la venta
            total_amount = 0
            for item in sale_data['items']:
                quantity = int(item['quantity'])
                unit_price = float(item['price'])
                total_amount += quantity * unit_price
            
            # Crear venta
            sale = Sale(
                date=datetime.now(),
                total_amount=total_amount,
                status='completed'
            )
            
            # Agregar información del cliente si está disponible
            if sale_data.get('customer_id') and sale_data['customer_id'].strip():
                sale.customer_id = int(sale_data['customer_id'])
            else:
                # Usar cliente "Desconocido" (ID 0) si no se proporciona
                sale.customer_id = 0
                
            # Agregar información del empleado si está disponible
            if sale_data.get('employee_id') and sale_data['employee_id'].strip():
                sale.employee_id = int(sale_data['employee_id'])
                
            # Agregar método de pago si está disponible
            if sale_data.get('payment_method'):
                sale.payment_method = sale_data['payment_method']
            else:
                sale.payment_method = 'efectivo'  # Valor por defecto

            self.db.add(sale)
            self.db.flush()  # Obtener sale.id

            # Procesar items
            for item in sale_data['items']:
                # Calcular subtotal
                quantity = int(item['quantity'])
                unit_price = float(item['price'])
                subtotal = quantity * unit_price

                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=int(item['product_id']),
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=subtotal
                )
                
                self.db.add(sale_item)
                
                # Actualizar stock del producto
                product = self.product_service.get_product_by_id(item['product_id'])
                if product:
                    product.stock -= quantity
                    
            # Confirmar cambios
            self.db.commit()
            
            # Recargar la venta con sus relaciones
            self.db.refresh(sale)
            
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

    def get_sales_by_category(self, category: str) -> List[Sale]:
        """Obtiene ventas que contienen productos de una categoría específica"""
        try:
            return self.db.query(Sale).join(
                SaleItem, Sale.id == SaleItem.sale_id
            ).join(
                Product, SaleItem.product_id == Product.id
            ).filter(
                Product.category.ilike(f"%{category}%")
            ).options(
                joinedload(Sale.customer),
                joinedload(Sale.items).joinedload(SaleItem.product)
            ).distinct().all()
        except Exception as e:
            logging.error(f"Error al obtener ventas por categoría: {str(e)}")
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

    def get_sales_by_customer_name(self, customer_name: str) -> List[Sale]:
        """Obtiene las ventas filtradas por coincidencia parcial en el nombre del cliente."""
        try:
            query = self.db.query(Sale).join(Customer)
            query = query.filter(Customer.name.ilike(f"%{customer_name}%"))
            return query.options(
                joinedload(Sale.customer),
                joinedload(Sale.items).joinedload(SaleItem.product)
            ).all()
        except Exception as e:
            logging.error(f"Error al buscar ventas por cliente: {str(e)}")
            return []

    def filter_sales(self, date_from: str = None, date_to: str = None, customer_name: str = None) -> List[Sale]:
        """
        Filtra las ventas según los criterios proporcionados.
        Este método es llamado desde la interfaz de usuario.
        """
        try:
            # Convertir strings de fecha a objetos datetime si están presentes
            from_date = None
            to_date = None
            
            if date_from and date_from.strip():
                try:
                    from_date = datetime.strptime(date_from, "%Y-%m-%d")
                except ValueError:
                    logging.warning(f"Formato de fecha inválido para date_from: {date_from}")
            
            if date_to and date_to.strip():
                try:
                    # Añadir 23:59:59 para incluir todo el día
                    to_date = datetime.strptime(date_to, "%Y-%m-%d")
                    to_date = to_date.replace(hour=23, minute=59, second=59)
                except ValueError:
                    logging.warning(f"Formato de fecha inválido para date_to: {date_to}")
            
            # Usar el método existente para filtrar
            return self.get_sales_filtered(from_date, to_date, customer_name)
            
        except Exception as e:
            logging.error(f"Error en filter_sales: {str(e)}")
            return []
            
    def get_sale_items(self, sale_id: int) -> List[SaleItem]:
        """Obtiene los items de una venta específica"""
        try:
            return self.db.query(SaleItem).filter(
                SaleItem.sale_id == sale_id
            ).options(
                joinedload(SaleItem.product)
            ).all()
        except Exception as e:
            logging.error(f"Error al obtener items de venta: {str(e)}")
            return []
