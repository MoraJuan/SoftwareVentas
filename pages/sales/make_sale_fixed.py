import flet as ft
import logging
from datetime import datetime
from services.productService import ProductService
from services.saleService import SaleService
from ui.components.navigation import create_navigation_rail, ThemeIconButton
from ui.components.alerts import show_error_message, show_success_message

class MakeSaleView(ft.View):
    def __init__(self, page: ft.Page, session):
        super().__init__(
            route="/realizar_venta",
            padding=0,
            bgcolor=ft.colors.SURFACE
        )
        self.page = page
        self.session = session
        self.product_service = ProductService(session)
        self.sale_service = SaleService(session)
        self.cart = []
        self.build_ui()

    def build_ui(self):
        # Implementación existente...
        pass
        
    # Otros métodos existentes...
    
    def decrease_quantity(self, product):
        try:
            for item in self.cart:
                if item["product"].id == product.id:
                    if item["quantity"] > 1:
                        item["quantity"] -= 1
                    else:
                        self.cart.remove(item)
                    break

            self.update_cart()

        except Exception as e:
            logging.error(f"Error al disminuir cantidad: {str(e)}")
            show_error_message(self.page, f"Error al disminuir cantidad: {str(e)}")
    
    def increase_quantity(self, product):
        try:
            for item in self.cart:
                if item["product"].id == product.id:
                    # Verificar stock
                    if item["quantity"] >= item["product"].stock:
                        show_error_message(self.page, "No hay suficiente stock")
                        return
                    
                    item["quantity"] += 1
                    break
            
            self.update_cart()
            
        except Exception as e:
            logging.error(f"Error al aumentar cantidad: {str(e)}")
            show_error_message(self.page, f"Error al aumentar cantidad: {str(e)}") 