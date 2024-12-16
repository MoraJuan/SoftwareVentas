import flet as ft
from datetime import datetime
from sqlalchemy.orm import Session
from services.saleService import SaleService
from services.productService import ProductService
from services.customerService import CustomerService
from ui.components.alerts import show_success_message, show_error_message
from pages.dashboard.navigation import create_navigation_rail, get_route_for_index


class MakeSaleView(ft.View):
    def __init__(self, page: ft.Page, session):
        super().__init__(
            route="/realizar_venta",
            controls=[],
            padding=0,
            bgcolor=ft.colors.BACKGROUND
        )
        self.page = page
        self.session = session
        self.sale_service = SaleService(session)
        self.cart_items = []  # List to store cart items
        self.build_ui()  # Build UI without calling self.update()

    def build_ui(self):
        self.navigation_rail = create_navigation_rail(
            0, self.handle_navigation)
        # Cart table
        self.cart_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Cantidad")),
                ft.DataColumn(ft.Text("Precio Unitario")),
                ft.DataColumn(ft.Text("Subtotal")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )

        # Total text
        self.total_text = ft.Text("Total: $0.00", size=20)

        # Buttons to add product and finalize sale
        self.add_product_button = ft.ElevatedButton(
            "Agregar Producto",
            on_click=self.add_product
        )
        self.finalize_sale_button = ft.ElevatedButton(
            "Finalizar Venta",
            on_click=self.finalize_sale
        )

        # Layout of the view
        self.controls = [
            ft.Row([
                self.navigation_rail,
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("Realizar Venta", size=20, weight=ft.FontWeight.BOLD),
                    self.cart_table,
                    self.total_text,
                    ft.Row([
                        self.add_product_button,
                        self.finalize_sale_button
                    ], spacing=10)
                ], spacing=20)
            )])
        ]

    def add_product(self, e):
        # Implementa la lógica para agregar un producto al carrito
        pass

    def finalize_sale(self, e):
        # Implementa la lógica para finalizar la venta
        pass

    def update_cart_table(self):
        self.cart_table.rows.clear()
        total = 0

        for item in self.cart_items:
            subtotal = item["quantity"] * item["unit_price"]
            self.cart_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item["product_name"])),
                        ft.DataCell(ft.Text(str(item["quantity"]))),
                        ft.DataCell(ft.Text(f"${item['unit_price']:.2f}")),
                        ft.DataCell(ft.Text(f"${subtotal:.2f}")),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                tooltip="Eliminar",
                                on_click=lambda e, item=item: self.remove_from_cart(item)
                            )
                        ),
                    ]
                )
            )
            total += subtotal

        self.total_text.value = f"Total: ${total:.2f}"
        self.update()

    def remove_from_cart(self, item):
        self.cart_items.remove(item)
        self.update_cart_table()
    
    def handle_navigation(self, e):
        try:
            route = get_route_for_index(e.control.selected_index)
            self.page.go(route)
        except Exception as e:
            show_error_message(self.page, f"Navigation error: {str(e)}")